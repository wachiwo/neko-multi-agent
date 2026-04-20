#!/usr/bin/env bash
# stream-watchdog-tick.sh — PostToolUse hook (cmd_199 P0-b / subtask_199_002_p0b)
#
# Fired on every tool_use completion. Touches
# /tmp/neko_last_tool_call_<pane_name>.timestamp so the watchdog daemon can
# compute "time since last tool call" per pane.
#
# Identity resolution matches detect-persona.sh:
#   - session "multiagent" + pane_index (0..4)  → kashira / worker1..worker4
#   - session "oyabun"                           → oyabun
# Any other shape → no-op (hook must never block or fail a tool call).

set -uo pipefail

# Resolve session + pane_index via $TMUX_PANE (e.g. %2). #W is unreliable —
# every pane in this repo shares window_name=agents.
SESSION_NAME=$(tmux display-message -p '#S' 2>/dev/null || echo "")
PANE_INDEX=""
if [ -n "${TMUX_PANE:-}" ]; then
  PANE_INDEX=$(tmux list-panes -a -F '#{pane_id} #{pane_index}' 2>/dev/null \
    | awk -v p="$TMUX_PANE" '$1 == p { print $2 }')
fi
[ -z "$PANE_INDEX" ] && PANE_INDEX=$(tmux display-message -p '#{pane_index}' 2>/dev/null || echo "")

PANE_NAME=""
case "$SESSION_NAME" in
  multiagent)
    case "$PANE_INDEX" in
      0) PANE_NAME="kashira" ;;
      1) PANE_NAME="worker1" ;;
      2) PANE_NAME="worker2" ;;
      3) PANE_NAME="worker3" ;;
      4) PANE_NAME="worker4" ;;
    esac
    ;;
  oyabun) PANE_NAME="oyabun" ;;
esac

# Unknown pane → silent no-op (do not fail the tool_use chain).
[ -z "$PANE_NAME" ] && exit 0

TS_FILE="/tmp/neko_last_tool_call_${PANE_NAME}.timestamp"
touch "$TS_FILE" 2>/dev/null || true

exit 0
