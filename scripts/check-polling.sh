#!/bin/bash
# check-polling.sh — PreToolUse hook: polling pattern detector
#
# Claude Code invokes this hook before every Bash tool call.
# Input: JSON on stdin with tool_name and tool_input.command.
# Output:
#   exit 0 → allow
#   exit 2 → block (Claude sees stderr as feedback and retries differently)
#
# Polling is forbidden (F004) because it wastes API credits and blocks the agent.
# Legit use cases: monitoring a background task (use Monitor tool), one-shot wait
# (single sleep), or inbox/queue file check (not a tmux poll).
#
# Detects these patterns in a single Bash command:
#   - while/until loop with sleep + tmux capture-pane/grep
#   - for loop with sleep + capture-pane
#   - chained `sleep N && sleep M && ...` (back-to-back waiting)
#   - sleep followed by capture-pane multiple times separated by ; or &&
#
# Does NOT block:
#   - single `sleep N` (legitimate brief wait)
#   - single `tmux capture-pane` (legitimate status check)
#   - `sleep N && command` with a single non-polling command

set -uo pipefail
# Note: -e is off because grep -q returns non-zero on no-match, which is normal

# Read JSON input from stdin
INPUT=$(cat)

# Extract command. Use python3 for reliable JSON parsing.
COMMAND=$(python3 -c "
import json, sys
try:
    data = json.loads(sys.stdin.read())
    tool_name = data.get('tool_name', '')
    if tool_name != 'Bash':
        print('')  # Not a Bash call, skip
        sys.exit(0)
    cmd = data.get('tool_input', {}).get('command', '')
    print(cmd)
except Exception as e:
    print('', file=sys.stderr)
    sys.exit(0)
" <<< "$INPUT")

# Not a Bash call → allow
if [[ -z "$COMMAND" ]]; then
  exit 0
fi

# ── Pattern checks ────────────────────────────────────────────

# Pattern 1: loop constructs (while/until/for) combined with sleep and capture/grep
if echo "$COMMAND" | grep -qE '(while|until|for)[[:space:]].*\bsleep\b' && \
   echo "$COMMAND" | grep -qE '(capture-pane|tmux.*display-message|grep|tail -f)'; then
  echo "POLLING BLOCKED: loop + sleep + capture/grep detected (F004 violation)." >&2
  echo "Command: $COMMAND" >&2
  echo "" >&2
  echo "Polling wastes API credits and blocks you." >&2
  echo "Alternatives:" >&2
  echo "  - Background task: start with run_in_background=true, use Monitor tool for events" >&2
  echo "  - One-shot wait: single 'sleep N' is fine" >&2
  echo "  - Inbox check: read queue/inbox/*.queue (file-based, no polling)" >&2
  echo "  - Task completion wait: write inbox + send-keys, return to idle — target notifies you" >&2
  exit 2
fi

# Pattern 2: chained sleeps (back-to-back waiting = disguised polling)
SLEEP_COUNT=$(echo "$COMMAND" | grep -oE '\bsleep[[:space:]]+[0-9]+' | wc -l)
if [[ $SLEEP_COUNT -ge 3 ]]; then
  echo "POLLING BLOCKED: $SLEEP_COUNT sleep calls in one command (chained waiting = polling)." >&2
  echo "Command: $COMMAND" >&2
  echo "" >&2
  echo "If you need to wait longer than a single sleep, use run_in_background + Monitor." >&2
  exit 2
fi

# Pattern 3: tight repeat of capture-pane/display-message (e.g., via semicolon or &&)
CAPTURE_COUNT=$(echo "$COMMAND" | grep -oE 'tmux[[:space:]]+(capture-pane|display-message)' | wc -l)
if [[ $CAPTURE_COUNT -ge 3 ]]; then
  echo "POLLING BLOCKED: $CAPTURE_COUNT tmux capture/display calls in one command." >&2
  echo "Command: $COMMAND" >&2
  echo "" >&2
  echo "Reading the same pane multiple times in one call is polling. Read once, or use inbox." >&2
  exit 2
fi

# Allow
exit 0
