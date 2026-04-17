#!/usr/bin/env bash
# log-skill-usage.sh - PostToolUse hook for Skill tool
# Records skill invocations to logs/skill_usage.log for self_audit consumption.
#
# Hook input (stdin JSON): {"tool_name": "Skill", "tool_input": {"skill": "...", "args": "..."}}

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG="${REPO_ROOT}/logs/skill_usage.log"

mkdir -p "$(dirname "$LOG")"

# Read hook input
INPUT=$(cat)

# Extract skill name (portable JSON parse via python3)
SKILL=$(echo "$INPUT" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    if d.get('tool_name') == 'Skill':
        print(d.get('tool_input', {}).get('skill', ''))
except Exception:
    pass
" 2>/dev/null)

# Detect persona from tmux pane (same as detect-persona.sh logic)
PERSONA=$(tmux display-message -p '#W' 2>/dev/null || echo "unknown")

if [ -n "$SKILL" ]; then
  TS=$(date -Iseconds)
  echo "${TS}|${PERSONA}|${SKILL}" >> "$LOG"
fi

# Never block; always exit 0
exit 0
