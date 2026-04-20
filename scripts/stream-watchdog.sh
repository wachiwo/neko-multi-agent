#!/usr/bin/env bash
# stream-watchdog.sh — Background daemon (cmd_199 P0-b / subtask_199_002_p0b)
#
# Why this exists
# ---------------
# The Claude stream on each pane times out after roughly 1h of no tool_use
# traffic. cmd_186 050 burned 1h of real time on this: a worker ran a Python
# convert script, then fell into a long silent "reasoning + Playwright verify"
# gap. No tool_use → cache miss → stream disconnect → full replay.
#
# This daemon injects a cheap heartbeat (`echo heartbeat_<time>`) into any pane
# that has been silent longer than threshold_seconds. That tool_use event is
# enough to keep the stream warm until the next genuine call.
#
# Hook events (PreToolUse/PostToolUse/SessionStart) only fire on specific
# triggers, so "N seconds with nothing happening" cannot be detected from a
# hook — a background process is required. This daemon is started once from
# SessionStart via nohup+setsid and self-deduplicates via a PID file.
#
# False-positive guards (acceptance criteria):
#   - pane at ❯ prompt    → skip (already idle, timeout irrelevant)
#   - pane showing busy   → skip (tool is running, stream is warm)
#   - pane in cooldown    → skip (we just fired ≤ cooldown_after_heartbeat ago)
#
# Lifecycle:
#   - start:   bash scripts/stream-watchdog.sh &    (SessionStart hook)
#   - stop:    bash scripts/stop-watchdog.sh
#   - logs:    logs/hook_stream_watchdog.log
#              ISO8601|pane|event|elapsed_seconds|reason

set -uo pipefail

# Optional flags:
#   --dry-run-once  Run a single check cycle with no real send-keys calls.
#                   Logs DRY_FIRE instead of HEARTBEAT. Used by verification
#                   harness to exercise the full decision path without
#                   disturbing live panes.
DRY_RUN_ONCE=0
if [ "${1:-}" = "--dry-run-once" ]; then
  DRY_RUN_ONCE=1
fi

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG_FILE="${REPO_ROOT}/scripts/watchdog-config.yaml"

# ─── minimal yaml reader ───────────────────────────────────────────────────
# One key:value per line. target_panes is a flat list of "- name|tmux_target".
# Avoids yq dependency so the daemon has zero non-coreutils requirements.
cfg_scalar() {
  local key="$1"
  awk -v k="$key" '
    /^[[:space:]]*#/ { next }
    $0 ~ "^"k":" {
      sub("^"k":[[:space:]]*", "")
      sub(/[[:space:]]*#.*$/, "")
      gsub(/^[[:space:]]+|[[:space:]]+$/, "")
      gsub(/^"|"$/, "")
      print
      exit
    }
  ' "$CONFIG_FILE"
}

cfg_target_panes() {
  awk '
    /^target_panes:/ { in_list = 1; next }
    in_list && /^[^[:space:]-]/ { in_list = 0 }
    in_list && /^[[:space:]]*-[[:space:]]/ {
      sub(/^[[:space:]]*-[[:space:]]*/, "")
      gsub(/^[[:space:]]+|[[:space:]]+$/, "")
      print
    }
  ' "$CONFIG_FILE"
}

# ─── load config ───────────────────────────────────────────────────────────
THRESHOLD_SECONDS=$(cfg_scalar threshold_seconds)
CHECK_INTERVAL_SECONDS=$(cfg_scalar check_interval_seconds)
COOLDOWN_AFTER_HEARTBEAT=$(cfg_scalar cooldown_after_heartbeat)
HEARTBEAT_COMMAND=$(cfg_scalar heartbeat_command)
PROMPT_WAITING_SKIP=$(cfg_scalar prompt_waiting_skip)
BUSY_SKIP=$(cfg_scalar busy_skip)
PID_FILE=$(cfg_scalar pid_file)
LOG_REL=$(cfg_scalar log_file)

: "${THRESHOLD_SECONDS:=240}"
: "${CHECK_INTERVAL_SECONDS:=30}"
: "${COOLDOWN_AFTER_HEARTBEAT:=300}"
: "${HEARTBEAT_COMMAND:=echo heartbeat_\$(date +%H:%M:%S)}"
: "${PROMPT_WAITING_SKIP:=true}"
: "${BUSY_SKIP:=true}"
: "${PID_FILE:=/tmp/neko_watchdog.pid}"
: "${LOG_REL:=logs/hook_stream_watchdog.log}"

LOG_FILE="${REPO_ROOT}/${LOG_REL}"
mkdir -p "$(dirname "$LOG_FILE")"

# ─── duplicate-start guard (skipped in dry-run-once) ───────────────────────
if [ "$DRY_RUN_ONCE" -eq 0 ]; then
  if [ -f "$PID_FILE" ]; then
    existing_pid=$(cat "$PID_FILE" 2>/dev/null || echo "")
    if [ -n "$existing_pid" ] && kill -0 "$existing_pid" 2>/dev/null; then
      echo "[stream-watchdog] already running (pid=$existing_pid) — not spawning another" >&2
      exit 0
    fi
  fi
  echo "$$" > "$PID_FILE"
fi

# ─── logging helper ────────────────────────────────────────────────────────
log_line() {
  local pane="$1" event="$2" elapsed="$3" reason="$4"
  printf '%s|%s|%s|%s|%s\n' \
    "$(date -Iseconds)" "$pane" "$event" "$elapsed" "$reason" >> "$LOG_FILE"
}

if [ "$DRY_RUN_ONCE" -eq 1 ]; then
  log_line daemon DRY_RUN_START 0 "single cycle, no real send-keys"
else
  log_line daemon START 0 \
    "threshold=${THRESHOLD_SECONDS}s interval=${CHECK_INTERVAL_SECONDS}s cooldown=${COOLDOWN_AFTER_HEARTBEAT}s pid=$$"
fi

# ─── per-pane cooldown bookkeeping ────────────────────────────────────────
# Stored in /tmp so it survives within the session but not across reboots.
cooldown_file() {
  echo "/tmp/neko_watchdog_cooldown_${1}.timestamp"
}

# ─── pane state classifier ────────────────────────────────────────────────
# Returns one of: idle|busy|unknown|missing.
#
# NOTE: notify-idle.sh also keys on `⏵⏵ (accept|bypass)` to detect a
# human-waiting permission prompt, but Claude Code renders that text in its
# bottom bar *unconditionally* (it is the permission-mode indicator, not a
# prompt). Matching on it here would flag every pane as "prompt" and disable
# the watchdog. So this classifier deliberately ignores that marker; real
# tool-execution prompts still show busy markers (esc to interrupt, etc.).
classify_pane() {
  local target="$1"
  # Strict existence check: tmux display-message silently falls back to the
  # current pane when -t points to an out-of-range pane_index (session:window
  # is still valid), so we verify by listing panes in the window instead.
  local session_win="${target%.*}"
  local pane_idx="${target##*.}"
  if ! tmux list-panes -t "$session_win" -F '#{pane_index}' 2>/dev/null \
       | grep -qx "$pane_idx"; then
    echo "missing"; return
  fi
  local tail
  tail=$(tmux capture-pane -t "$target" -p -S -30 2>/dev/null | tail -12)

  # Busy markers: tool actively running, stream is warm → skip
  if echo "$tail" | grep -qE '(esc to interrupt|Running…|Skedaddling…|↻|✽)'; then
    echo "busy"; return
  fi
  # Idle: a line starting with ❯ and containing no alphanumeric content
  # exists in the recent tail, and no busy marker is present. We look
  # anywhere in the tail (not just the very last line) because Claude Code
  # always renders a cosmetic bottom bar (⏵⏵ mode indicator) below the
  # prompt, so the ❯ is never the strict last line. The [^[:alnum:]] tail
  # also handles the non-breaking space (U+00A0) Claude Code appends after
  # ❯, which POSIX [[:space:]] does not match.
  if echo "$tail" | grep -qE '^❯[^[:alnum:]]*$'; then
    echo "idle"; return
  fi
  # Anything else: pane is working but producing no tool_use events (the exact
  # cmd_186 050 pattern — silent reasoning / subprocess wait). Fire-eligible.
  echo "unknown"
}

# ─── shutdown handler (skipped in dry-run-once) ────────────────────────────
if [ "$DRY_RUN_ONCE" -eq 0 ]; then
  cleanup() {
    log_line daemon STOP 0 "signal=$1 pid=$$"
    rm -f "$PID_FILE" 2>/dev/null || true
    exit 0
  }
  trap 'cleanup SIGTERM' SIGTERM
  trap 'cleanup SIGINT' SIGINT
  trap 'cleanup EXIT' EXIT
fi

# ─── main loop ─────────────────────────────────────────────────────────────
mapfile -t TARGET_LINES < <(cfg_target_panes)

while true; do
  now=$(date +%s)

  for line in "${TARGET_LINES[@]}"; do
    pane_name="${line%%|*}"
    tmux_target="${line#*|}"
    [ -z "$pane_name" ] || [ -z "$tmux_target" ] && continue

    ts_file="/tmp/neko_last_tool_call_${pane_name}.timestamp"
    # If tick has never fired, seed it so we don't fire immediately at boot.
    if [ ! -f "$ts_file" ]; then
      touch "$ts_file" 2>/dev/null || true
      continue
    fi

    last=$(stat -c %Y "$ts_file" 2>/dev/null || echo "$now")
    elapsed=$(( now - last ))

    if [ "$elapsed" -le "$THRESHOLD_SECONDS" ]; then
      continue
    fi

    # Past threshold — evaluate guards before firing.
    state=$(classify_pane "$tmux_target")

    if [ "$state" = "missing" ]; then
      log_line "$pane_name" SKIP "$elapsed" "pane_missing"
      continue
    fi
    if [ "$PROMPT_WAITING_SKIP" = "true" ] && [ "$state" = "idle" ]; then
      log_line "$pane_name" SKIP "$elapsed" "idle_prompt_waiting"
      continue
    fi
    if [ "$BUSY_SKIP" = "true" ] && [ "$state" = "busy" ]; then
      log_line "$pane_name" SKIP "$elapsed" "busy_running"
      continue
    fi

    cd_file=$(cooldown_file "$pane_name")
    if [ -f "$cd_file" ]; then
      cd_last=$(stat -c %Y "$cd_file" 2>/dev/null || echo 0)
      cd_elapsed=$(( now - cd_last ))
      if [ "$cd_elapsed" -lt "$COOLDOWN_AFTER_HEARTBEAT" ]; then
        log_line "$pane_name" SKIP "$elapsed" "cooldown_${cd_elapsed}s"
        continue
      fi
    fi

    if [ "$DRY_RUN_ONCE" -eq 1 ]; then
      # Dry-run: log the decision without touching the pane.
      log_line "$pane_name" DRY_FIRE "$elapsed" "would_fire state=${state}"
    else
      # Fire heartbeat via neko 2-call protocol (message, then Enter).
      tmux send-keys -t "$tmux_target" "$HEARTBEAT_COMMAND" 2>/dev/null || true
      tmux send-keys -t "$tmux_target" Enter 2>/dev/null || true

      touch "$cd_file" 2>/dev/null || true
      # Also refresh the tick file so elapsed resets even before PostToolUse
      # re-touches it (defensive against the tick hook failing to fire).
      touch "$ts_file" 2>/dev/null || true

      log_line "$pane_name" HEARTBEAT "$elapsed" "fired state=${state}"
    fi
  done

  if [ "$DRY_RUN_ONCE" -eq 1 ]; then
    log_line daemon DRY_RUN_END 0 "cycle complete"
    exit 0
  fi

  sleep "$CHECK_INTERVAL_SECONDS"
done
