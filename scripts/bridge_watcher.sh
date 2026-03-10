#!/usr/bin/env bash
# bridge_watcher.sh — Monitor bridge/outbox/ for new files, notify oyabun via tmux
#
# Usage:
#   ./scripts/bridge_watcher.sh [--interval SECONDS] [--bridge-path PATH]
#
# Modes:
#   - inotifywait (preferred): Event-driven, zero polling cost
#   - Fallback: Poll every INTERVAL seconds (default: 60)
#
# Features:
#   - Auto-Rally Mode: detect auto_rally:true outbox files, enforce hop limits,
#     single concurrent session, idempotency via processed_hops.tsv
#
# Zero API cost — pure shell, no LLM calls.

set -euo pipefail

# === Configuration ===
BRIDGE_PATH="${BRIDGE_PATH:-/mnt/c/tools/bridge}"
OUTBOX_DIR="${BRIDGE_PATH}/outbox"
INTERVAL=60
SEEN_FILE="/tmp/bridge_watcher_seen.txt"
OYABUN_PANE="oyabun"
LOG_FILE="/mnt/c/tools/neko-multi-agent/logs/bridge_watcher.log"
PROCESSED_HOPS_FILE="/mnt/c/tools/neko-multi-agent/status/processed_hops.tsv"
ACTIVE_RALLY_FILE="/tmp/bridge_watcher_active_rally.txt"
NEKO_SOUND_NOTIFY="${NEKO_SOUND_NOTIFY:-false}"

# === Parse arguments ===
while [[ $# -gt 0 ]]; do
  case "$1" in
    --interval)
      INTERVAL="$2"
      shift 2
      ;;
    --bridge-path)
      BRIDGE_PATH="$2"
      OUTBOX_DIR="${BRIDGE_PATH}/outbox"
      shift 2
      ;;
    *)
      echo "Unknown option: $1" >&2
      echo "Usage: $0 [--interval SECONDS] [--bridge-path PATH]" >&2
      exit 1
      ;;
  esac
done

# === Ensure directories exist ===
if [[ ! -d "$OUTBOX_DIR" ]]; then
  echo "ERROR: Outbox directory not found: $OUTBOX_DIR" >&2
  exit 1
fi

mkdir -p "$(dirname "$LOG_FILE")"
touch "$SEEN_FILE"

# === Logging ===
log() {
  local msg="$(date '+%Y-%m-%dT%H:%M:%S') [bridge_watcher] $1"
  echo "$msg" >> "$LOG_FILE"
  echo "$msg"
}

# === Sound notification (toggleable via NEKO_SOUND_NOTIFY=true) ===
# NOTE: Only works in foreground terminal. Under nohup/redirect, BEL goes to log file.
notify_sound() {
  if [[ "$NEKO_SOUND_NOTIFY" == "true" ]]; then printf '\a'; fi
}

# === Extract field from bridge markdown file ===
extract_field() {
  local filepath="$1"
  local field="$2"
  grep -m1 "^- ${field}:" "$filepath" 2>/dev/null | sed "s/^- ${field}: *//" | tr -d '[:space:]' || echo ""
}

# === Auto-Rally: Idempotency via processed_hops.tsv ===
is_hop_processed() {
  local rally_id="$1"
  local hop_id="$2"
  grep -qP "^${rally_id}\t${hop_id}\t" "$PROCESSED_HOPS_FILE" 2>/dev/null
}

record_hop() {
  local rally_id="$1"
  local hop_id="$2"
  local from="$3"
  local to="$4"
  printf '%s\t%s\t%s\t%s\t%s\n' "$rally_id" "$hop_id" "$from" "$to" "$(date '+%Y-%m-%dT%H:%M:%S')" >> "$PROCESSED_HOPS_FILE"
}

# === Auto-Rally: Single concurrent session enforcement ===
is_rally_active() {
  if [[ -f "$ACTIVE_RALLY_FILE" ]] && [[ -s "$ACTIVE_RALLY_FILE" ]]; then
    return 0
  fi
  return 1
}

get_active_rally() {
  cat "$ACTIVE_RALLY_FILE" 2>/dev/null || echo ""
}

set_rally_active() {
  echo "$1" > "$ACTIVE_RALLY_FILE"
}

clear_rally_active() {
  : > "$ACTIVE_RALLY_FILE"
}

# === Notify oyabun via tmux ===
notify_oyabun() {
  local task_id="$1"
  local from_system="$2"

  # Check if oyabun pane exists
  if ! tmux has-session -t oyabun 2>/dev/null; then
    log "WARN: oyabun session not found, skipping notification for $task_id"
    return
  fi

  # Send notification (2-call method)
  tmux send-keys -t "$OYABUN_PANE" "Bridge outbox: new response ${task_id} from ${from_system}. Check /mnt/c/tools/bridge/outbox/${task_id}.md"
  sleep 0.5
  tmux send-keys -t "$OYABUN_PANE" Enter

  log "Notified oyabun: $task_id from $from_system"
}

# === Auto-Rally: Auto-respond via oyabun ===
notify_oyabun_rally() {
  local task_id="$1"
  local rally_id="$2"
  local hop_id="$3"
  local rally_max="$4"
  local from_system="$5"

  if ! tmux has-session -t oyabun 2>/dev/null; then
    log "WARN: oyabun session not found, skipping rally notification for $task_id"
    return
  fi

  local max_hops=$(( rally_max * 2 ))
  local next_hop=$(( hop_id + 1 ))
  local outbox_file="${BRIDGE_PATH}/outbox/${task_id}.md"
  local inbox_file="${BRIDGE_PATH}/inbox/${task_id}.md"

  # Send auto-reply instruction to oyabun (2-call method)
  tmux send-keys -t "$OYABUN_PANE" "AUTO-RALLY hop ${hop_id}/${max_hops}: Read ${outbox_file} and ${inbox_file}. Write a thoughtful reply to the next hop (hop_id=${next_hop}) as inbox. Use the neko-bridge-connector skill rally operation. rally_id=${rally_id} rally_max=${rally_max} origin_task_id=${task_id}. Think carefully about the content and respond substantively to what Codex wrote."
  sleep 0.5
  tmux send-keys -t "$OYABUN_PANE" Enter

  log "AUTO-RALLY auto-respond: $task_id rally=$rally_id hop=$hop_id/$max_hops -> oyabun instructed to reply"
}

# === Auto-Rally: Notify oyabun that rally limit reached ===
notify_oyabun_rally_limit() {
  local task_id="$1"
  local rally_id="$2"
  local hop_id="$3"
  local rally_max="$4"

  if ! tmux has-session -t oyabun 2>/dev/null; then
    log "WARN: oyabun session not found, skipping rally-limit notification"
    return
  fi

  tmux send-keys -t "$OYABUN_PANE" "RALLY-LIMIT: ${rally_id} reached ${rally_max} round-trips (hop=${hop_id}). Ask goshujinsama: continue or stop? File: /mnt/c/tools/bridge/outbox/${task_id}.md"
  sleep 0.5
  tmux send-keys -t "$OYABUN_PANE" Enter

  log "RALLY-LIMIT reached: rally=$rally_id hop=$hop_id limit=$rally_max"
  clear_rally_active
}

# === Process new outbox files ===
check_new_files() {
  for filepath in "$OUTBOX_DIR"/bridge_*.md; do
    [[ -f "$filepath" ]] || continue

    local filename
    filename="$(basename "$filepath")"
    local task_id="${filename%.md}"

    # Skip if already seen
    if grep -qxF "$filename" "$SEEN_FILE" 2>/dev/null; then
      continue
    fi

    # Extract fields
    local from_system
    from_system="$(extract_field "$filepath" "from")"
    if [[ -z "$from_system" ]]; then from_system="unknown"; fi

    # Mark as seen
    echo "$filename" >> "$SEEN_FILE"
    log "New outbox file: $filename (from: $from_system)"
    notify_sound

    # Check auto-rally fields
    local auto_rally
    auto_rally="$(extract_field "$filepath" "auto_rally")"

    if [[ "$auto_rally" == "true" ]]; then
      local rally_id hop_id rally_max status
      rally_id="$(extract_field "$filepath" "rally_id")"
      hop_id="$(extract_field "$filepath" "hop_id")"
      rally_max="$(extract_field "$filepath" "rally_max")"
      rally_max="${rally_max:-5}"
      status="$(extract_field "$filepath" "status")"

      # Idempotency: skip if already processed
      if is_hop_processed "$rally_id" "$hop_id"; then
        log "AUTO-RALLY skip: already processed rally=$rally_id hop=$hop_id"
        continue
      fi

      # Single concurrent session enforcement
      if is_rally_active; then
        local active_rally
        active_rally="$(get_active_rally)"
        if [[ "$active_rally" != "$rally_id" ]]; then
          log "AUTO-RALLY reject: active=$active_rally, new=$rally_id"
          notify_oyabun "$task_id" "$from_system (RALLY REJECTED: concurrent session $active_rally active)"
          continue
        fi
      fi

      # Record hop + set active
      record_hop "$rally_id" "$hop_id" "$from_system" "$(extract_field "$filepath" "to")"
      set_rally_active "$rally_id"

      # Immediate stop on done/blocked
      if [[ "$status" == "done" || "$status" == "blocked" ]]; then
        log "AUTO-RALLY stop: status=$status for rally=$rally_id"
        clear_rally_active
        notify_oyabun "$task_id" "$from_system (RALLY ENDED: status=$status)"
        continue
      fi

      # Check hop limit
      if (( hop_id >= rally_max * 2 )); then
        notify_oyabun_rally_limit "$task_id" "$rally_id" "$hop_id" "$rally_max"
      else
        notify_oyabun_rally "$task_id" "$rally_id" "$hop_id" "$rally_max" "$from_system"
      fi
    else
      # Normal (non-rally) notification
      notify_oyabun "$task_id" "$from_system"
    fi
  done
}

# === Main ===
log "Started. Watching: $OUTBOX_DIR (interval: ${INTERVAL}s)"

# Ensure processed_hops.tsv exists with header
if [[ ! -f "$PROCESSED_HOPS_FILE" ]]; then
  mkdir -p "$(dirname "$PROCESSED_HOPS_FILE")"
  printf 'rally_id\thop_id\tfrom\tto\ttimestamp\n' > "$PROCESSED_HOPS_FILE"
  log "Created $PROCESSED_HOPS_FILE"
fi

# Clear stale active rally marker on startup
: > "$ACTIVE_RALLY_FILE"

# Seed seen file with existing outbox files (don't alert on startup)
for f in "$OUTBOX_DIR"/bridge_*.md; do
  if [[ -f "$f" ]]; then echo "$(basename "$f")" >> "$SEEN_FILE"; fi
done
# Deduplicate
sort -u "$SEEN_FILE" -o "$SEEN_FILE"
log "Seeded ${SEEN_FILE} with $(wc -l < "$SEEN_FILE") existing files"

# Choose monitoring mode
if command -v inotifywait &>/dev/null; then
  log "Using inotifywait (event-driven mode)"

  inotifywait -m -e create -e moved_to --format '%f' "$OUTBOX_DIR" 2>/dev/null | while read -r filename; do
    # Only process bridge_*.md files
    if [[ "$filename" == bridge_*.md ]]; then
      # Small delay to ensure file is fully written
      sleep 1
      check_new_files
    fi
  done
else
  log "inotifywait not available, using polling (${INTERVAL}s interval)"

  while true; do
    check_new_files
    sleep "$INTERVAL"
  done
fi
