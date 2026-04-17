#!/usr/bin/env bash
# check-notification.sh - PreToolUse hook (Bash matcher)
#
# Purpose: When a `tmux send-keys` command is about to fire AND the message text
# indicates it's an action-requiring notification (e.g. 【親分→kashira】, 【kashira→親分】),
# emit a stderr warning if no matching inbox append is detected in recent history.
#
# This is a non-blocking warning. It does NOT block the send-keys — only nudges
# the operator to also write to queue/inbox/<target>.queue for reliable delivery.
# Rationale: 2026-04-17 incident — kashira→oyabun notifications were lost because
# send-keys-only left no inbox trace.

# NOTE: -e is intentionally omitted; grep -q returning 1 on no-match must not
#       terminate the hook.
set -uo pipefail

# Hook receives tool input via stdin JSON: {"tool_name":"Bash","tool_input":{"command":"..."}}
INPUT=$(cat 2>/dev/null || true)

COMMAND=$(echo "$INPUT" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    if d.get('tool_name') == 'Bash':
        print(d.get('tool_input', {}).get('command', ''))
except Exception:
    pass
" 2>/dev/null)

# Only check send-keys invocations
if ! echo "$COMMAND" | grep -q 'tmux send-keys'; then
  exit 0
fi

# Detect action-requiring patterns in the message body. We match on bracketed
# role-transition markers used throughout the neko protocol.
if ! echo "$COMMAND" | grep -qE '【(親分|kashira|oyabun|頭|worker[1-4]|子分)→(親分|kashira|oyabun|頭|worker[1-4]|子分)】'; then
  # Not an action-requiring notification (idle ping / informational only) → skip
  exit 0
fi

# Find the target persona from the send-keys pane target, e.g. "-t multiagent:0.0"
# and reverse-map to queue name.
TARGET_PANE=$(echo "$COMMAND" | grep -oE -- '-t[[:space:]]+[a-zA-Z0-9:.]+' | head -1 | awk '{print $2}')
case "$TARGET_PANE" in
  multiagent:0.0) TARGET="kashira" ;;
  multiagent:0.1) TARGET="worker1" ;;
  multiagent:0.2) TARGET="worker2" ;;
  multiagent:0.3) TARGET="worker3" ;;
  multiagent:0.4) TARGET="worker4" ;;
  oyabun:*)       TARGET="oyabun" ;;
  *)              TARGET="" ;;
esac

[ -z "$TARGET" ] && exit 0

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INBOX="${REPO_ROOT}/queue/inbox/${TARGET}.queue"

# Check: was there an append to this inbox within the last 60 seconds?
if [ -f "$INBOX" ]; then
  # Last line timestamp check
  LAST=$(tail -1 "$INBOX" 2>/dev/null | cut -d'|' -f1)
  if [ -n "$LAST" ]; then
    # Compare seconds since last append
    NOW_EPOCH=$(date +%s)
    LAST_EPOCH=$(date -d "$LAST" +%s 2>/dev/null || echo 0)
    DIFF=$(( NOW_EPOCH - LAST_EPOCH ))
    if [ "$DIFF" -le 60 ]; then
      # Recent pairing exists → OK, silently pass
      exit 0
    fi
  fi
fi

# No recent pairing — warn on stderr (non-blocking)
cat >&2 <<EOF
[check-notification] WARNING: action-requiring send-keys to ${TARGET} detected,
but no inbox append within last 60s to ${INBOX}.

Protocol requires inbox + send-keys pairing for reliable delivery.
Run BEFORE the send-keys Call 1:

    echo "\$(date -Iseconds)|\$(whoami)|<event>|<detail>" >> queue/inbox/${TARGET}.queue

(See instructions/_rules/send_keys_protocol.md § "Reliability".)
EOF

# Non-blocking: exit 0 so the Bash call proceeds.
exit 0
