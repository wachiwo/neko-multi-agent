#!/usr/bin/env bash
# notify-idle.sh - Event-driven idle notifier (NOT a polling loop)
#
# Called ONCE on demand (e.g. from a pane-hook, or oyabun's /idle-check). For
# each target pane, compares current state vs last recorded state:
#   - if last was 'busy' and current is 'idle' → append notification to the
#     watcher's inbox, update state file.
#   - otherwise: just update state file, no notification.
#
# F004 compliance: this script does NOT loop. It is invoked per event
# (user prompt, slash command, hook firing). State is stored in
# status/pane_state.yaml so successive calls can detect transitions.
#
# Usage:
#   scripts/notify-idle.sh                    # check all panes once
#   scripts/notify-idle.sh multiagent:0.0     # check single pane

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STATE_DIR="${REPO_ROOT}/status"
STATE_FILE="${STATE_DIR}/pane_state.tsv"
WATCHER_INBOX="${REPO_ROOT}/queue/inbox/oyabun.queue"

mkdir -p "$STATE_DIR" "$(dirname "$WATCHER_INBOX")" 2>/dev/null || true
touch "$STATE_FILE"

# Target panes: kashira + workers (default) or single arg
if [ $# -ge 1 ]; then
  PANES=("$1")
else
  PANES=(multiagent:0.0 multiagent:0.1 multiagent:0.2 multiagent:0.3 multiagent:0.4)
fi

pane_to_name() {
  case "$1" in
    multiagent:0.0) echo "kashira" ;;
    multiagent:0.1) echo "worker1" ;;
    multiagent:0.2) echo "worker2" ;;
    multiagent:0.3) echo "worker3" ;;
    multiagent:0.4) echo "worker4" ;;
    *) echo "pane-${1}" ;;
  esac
}

classify_pane() {
  local pane="$1"
  if ! tmux display-message -t "$pane" -p '#{pane_id}' >/dev/null 2>&1; then
    echo "missing"
    return
  fi
  local tail
  tail=$(tmux capture-pane -t "$pane" -p -S -30 2>/dev/null | tail -12)

  # Busy signals first (order matters)
  if echo "$tail" | grep -qE '(esc to interrupt|Running…|Skedaddling…|↻|✽)'; then
    echo "busy"; return
  fi
  # Permission prompt also counts as busy (waiting on human)
  if echo "$tail" | grep -qE '⏵⏵ (accept|bypass)'; then
    echo "prompt"; return
  fi
  # Idle: last non-empty line is lone ❯
  local last
  last=$(echo "$tail" | awk 'NF{line=$0} END{print line}')
  if echo "$last" | grep -qE '^❯\s*$'; then
    echo "idle"; return
  fi
  echo "unknown"
}

read_prev_state() {
  local pane="$1"
  awk -v p="$pane" '$1==p {print $2}' "$STATE_FILE" | tail -1
}

write_state() {
  local pane="$1" state="$2" ts
  ts=$(date -Iseconds)
  # Strip previous line for this pane, append new
  tmp=$(mktemp)
  grep -v "^${pane}	" "$STATE_FILE" > "$tmp" 2>/dev/null || true
  echo -e "${pane}\t${state}\t${ts}" >> "$tmp"
  mv "$tmp" "$STATE_FILE"
}

notifications=0
for pane in "${PANES[@]}"; do
  prev=$(read_prev_state "$pane")
  curr=$(classify_pane "$pane")
  name=$(pane_to_name "$pane")

  if [ "$prev" = "busy" ] && [ "$curr" = "idle" ]; then
    ts=$(date -Iseconds)
    echo "${ts}|notify-idle|${name}_idle_transition|${name} went busy→idle" >> "$WATCHER_INBOX"
    notifications=$(( notifications + 1 ))
    echo "[notify-idle] ${name}: busy → idle (logged to oyabun inbox)"
  elif [ "$prev" != "$curr" ]; then
    echo "[notify-idle] ${name}: ${prev:-<new>} → ${curr}"
  fi

  write_state "$pane" "$curr"
done

echo "[notify-idle] ${notifications} transition(s) logged"
exit 0
