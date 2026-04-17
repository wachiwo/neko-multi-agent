#!/usr/bin/env bash
# hook-precompact.sh - PreCompact hook
# Purpose: Just before context is compacted, inject a compact state snapshot
# into the transcript so the summary retains "who I am, what's running, what's next".
# Addresses memory note: "Do NOT immediately act on summary's next steps".

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Detect persona from tmux pane (same source as detect-persona.sh)
PERSONA=$(tmux display-message -p '#W' 2>/dev/null || echo "unknown")

# Build snapshot (stdout of hook becomes additional context per docs)
{
  echo "=== PreCompact Snapshot ($(date -Iseconds)) ==="
  echo "Persona: ${PERSONA}"
  echo ""

  # Current cmd queue (head only — kashira dispatch state)
  if [ -f "${REPO_ROOT}/queue/oyabun_to_kashira.yaml" ]; then
    echo "--- Active cmds (status != done) ---"
    awk '
      /^  - id:/ { id=$0; status=""; next }
      /^    status:/ { status=$2 }
      /^  - id:/ || /^$/ {
        if (id != "" && status != "done") print id " [" status "]"
        id=""; status=""
      }
      END { if (id != "" && status != "done") print id " [" status "]" }
    ' "${REPO_ROOT}/queue/oyabun_to_kashira.yaml" | head -10
    echo ""
  fi

  # Last 3 inbox entries for this persona
  INBOX="${REPO_ROOT}/queue/inbox/${PERSONA}.queue"
  if [ -f "$INBOX" ]; then
    echo "--- Last 3 inbox entries (${PERSONA}) ---"
    tail -3 "$INBOX"
    echo ""
  fi

  # Reminder
  echo "--- Recovery Rule ---"
  echo "After compaction: re-read instructions/${PERSONA}.md (or kashira_core.md for kashira)."
  echo "Do NOT act on summary's 'next steps' until persona is reconfirmed."
} 2>/dev/null

exit 0
