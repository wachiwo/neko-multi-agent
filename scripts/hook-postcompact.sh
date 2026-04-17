#!/usr/bin/env bash
# hook-postcompact.sh - PostCompact hook
# Purpose: After compaction completes, re-inject the persona reminder so the
# agent does not follow the summary's "next steps" blindly. Mirrors SessionStart
# detect-persona logic but runs post-compaction.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PERSONA=$(tmux display-message -p '#W' 2>/dev/null || echo "unknown")

# Map persona → instruction file path
case "$PERSONA" in
  oyabun)   INST="instructions/oyabun.md" ;;
  kashira)  INST="instructions/kashira_core.md + instructions/kashira_policies.md" ;;
  worker1)  INST="instructions/1gou-neko.md" ;;
  worker2)  INST="instructions/2gou-inu.md" ;;
  worker3)  INST="instructions/3gou-neko.md" ;;
  worker4)  INST="instructions/4gou-neko.md" ;;
  *)        INST="(pane name '${PERSONA}' not mapped — check CLAUDE.md)" ;;
esac

{
  echo "=== PostCompact Recovery Reminder ==="
  echo "Persona: ${PERSONA}"
  echo "Read first: ${INST}"
  echo ""
  echo "Critical rules to re-confirm:"
  echo "- forbidden_actions (see your instruction file)"
  echo "- Do NOT act on summary's 'next steps' until persona + task state are reconfirmed"
  echo "- tmux send-keys: 2 separate Bash calls (message, then Enter)"
} 2>/dev/null

exit 0
