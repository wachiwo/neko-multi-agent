#!/usr/bin/env bash
# auto-retrospective.sh - Emit a retrospective YAML skeleton and notify oyabun.
#
# Called by kashira when a cmd completes. Creates:
#   queue/reports/retrospective_<cmd_id>.yaml  (if not already present)
# with a pre-filled 5-minute retrospective template, then appends an event to
# queue/inbox/oyabun.queue so oyabun sees it on next prompt.
#
# This does NOT run the retrospective itself — it prepares the artifact so
# kashira + workers can fill it async. Oyabun reviews and promotes findings
# to memory/patterns.yaml.
#
# Usage:
#   scripts/auto-retrospective.sh <cmd_id> [<title>]

set -uo pipefail

CMD_ID="${1:-}"
TITLE="${2:-<title pending>}"
[ -z "$CMD_ID" ] && { echo "Usage: $0 <cmd_id> [<title>]" >&2; exit 2; }

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TARGET="${REPO_ROOT}/queue/reports/retrospective_${CMD_ID}.yaml"
INBOX="${REPO_ROOT}/queue/inbox/oyabun.queue"

mkdir -p "$(dirname "$TARGET")" "$(dirname "$INBOX")" 2>/dev/null || true

if [ -f "$TARGET" ]; then
  echo "[auto-retrospective] ${TARGET} already exists — skipping creation"
else
  cat > "$TARGET" <<EOF
# Retrospective — ${CMD_ID}
# Generated: $(date -Iseconds)
# Protocol: instructions/_rules/retrospective.md (5-minute format)

cmd_id: ${CMD_ID}
title: ${TITLE}
generated_at: $(date -Iseconds)
generated_by: auto-retrospective.sh

# What went well
kept:
  - <fill in>

# What to change / stop
problems:
  - <fill in>

# Concrete try for next cmd
try:
  - <fill in>

# Surprises / non-obvious learnings (candidates for memory promotion)
learnings:
  - <fill in>

# Promotion decision (oyabun fills)
memory_promotion:
  status: pending         # pending | approved | rejected
  target_file: <e.g. memory/project_<slug>.md>
  reviewed_by: <oyabun-on-YYYY-MM-DD>
EOF
  echo "[auto-retrospective] created ${TARGET}"
fi

# Notify oyabun via inbox
ts=$(date -Iseconds)
echo "${ts}|auto-retrospective|retrospective_ready|${CMD_ID} retrospective template at queue/reports/retrospective_${CMD_ID}.yaml" >> "$INBOX"
echo "[auto-retrospective] notified oyabun.queue"
exit 0
