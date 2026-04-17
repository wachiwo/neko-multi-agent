#!/usr/bin/env bash
# hook-userpromptsubmit.sh - UserPromptSubmit hook
# Purpose: When goshujinsama submits a prompt, auto-inject current state
# (active cmds + inbox tail) so oyabun does not have to grep/check each turn.
# Only fires for oyabun persona (kashira/workers don't need this overhead).

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PERSONA=$(tmux display-message -p '#W' 2>/dev/null || echo "unknown")

# Only run for oyabun to keep workers quiet
[ "$PERSONA" != "oyabun" ] && exit 0

{
  echo "=== Current State (auto-injected) ==="

  # Active cmds not done
  if [ -f "${REPO_ROOT}/queue/oyabun_to_kashira.yaml" ]; then
    active=$(awk '
      /^  - id:/ { id=$0; status=""; next }
      /^    status:/ { status=$2 }
      /^  - id:/ || /^$/ {
        if (id != "" && status != "done") print id " [" status "]"
        id=""; status=""
      }
      END { if (id != "" && status != "done") print id " [" status "]" }
    ' "${REPO_ROOT}/queue/oyabun_to_kashira.yaml")
    if [ -n "$active" ]; then
      echo "Active cmds:"
      echo "$active" | head -5
    else
      echo "Active cmds: (none)"
    fi
  fi

  # Oyabun inbox tail (reports from kashira)
  INBOX="${REPO_ROOT}/queue/inbox/oyabun.queue"
  if [ -f "$INBOX" ]; then
    unread_today=$(grep -c "^$(date +%Y-%m-%d)" "$INBOX" 2>/dev/null || echo 0)
    echo "Oyabun inbox today: ${unread_today} entries"
    if [ "${unread_today}" -gt 0 ]; then
      grep "^$(date +%Y-%m-%d)" "$INBOX" | tail -3
    fi
  fi
} 2>/dev/null

exit 0
