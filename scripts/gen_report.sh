#!/usr/bin/env bash
# gen_report.sh — Report YAML skeleton generator
# Usage: scripts/gen_report.sh <worker_id> <task_id> <status> [mode]
# Output: YAML to stdout. Redirect to file: scripts/gen_report.sh w2 task1 done > report.yaml
set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "Usage: $0 <worker_id> <task_id> <status> [mode]" >&2
  echo "  mode: normal (default) | lightweight" >&2
  exit 1
fi

WORKER_ID="$1"
TASK_ID="$2"
STATUS="$3"
MODE="${4:-normal}"
TIMESTAMP="$(date '+%Y-%m-%dT%H:%M:%S')"

cat <<EOF
worker_id: ${WORKER_ID}
task_id: ${TASK_ID}
timestamp: "${TIMESTAMP}"
status: ${STATUS}
result:
  summary: ""
  files_modified: []
  notes: ""
one_line_summary: ""
unverified_risks: []
EOF

if [[ "$MODE" == "normal" ]]; then
  cat <<'EOF'
not_fixed: []
verification_coverage:
  tested: []
  not_tested: []
verification_evidence:
  type: command_result
  content: ""
EOF
fi

echo "skill_candidate: none"
