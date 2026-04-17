#!/usr/bin/env bash
# split-taskmd.sh - Split task.md into recent + archive
#
# task.md is kashira's handover ledger. When it exceeds RECENT_LINES (default
# 800), tail is kept in task.md and the older portion is appended to
# task_archive_YYYY.md.
#
# Format assumption: task.md uses `## cmd_NNN` as section delimiters. The split
# point is the last `## ` header whose cumulative line count keeps task.md
# under RECENT_LINES.
#
# Usage:
#   scripts/split-taskmd.sh          # dry-run
#   scripts/split-taskmd.sh --apply  # actually split

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TASKMD="${REPO_ROOT}/task.md"
RECENT_LINES="${RECENT_LINES:-800}"

APPLY=0
[ "${1:-}" = "--apply" ] && APPLY=1

[ ! -f "$TASKMD" ] && { echo "[split-taskmd] no task.md"; exit 0; }

total=$(wc -l < "$TASKMD")
if [ "$total" -le "$RECENT_LINES" ]; then
  echo "[split-taskmd] task.md is ${total} lines (<= ${RECENT_LINES}), no split needed"
  exit 0
fi

# Find the last ## header line such that lines_from_there_to_end <= RECENT_LINES
# We want split_line such that (total - split_line + 1) <= RECENT_LINES and line is `## `
split_line=$(awk -v total="$total" -v keep="$RECENT_LINES" '
  /^## / { if ((total - NR + 1) <= keep) { print NR; exit } }
' "$TASKMD")

if [ -z "$split_line" ]; then
  echo "[split-taskmd] no ## header within last ${RECENT_LINES} lines — cannot split safely"
  exit 2
fi

year=$(date +%Y)
archive="${REPO_ROOT}/task_archive_${year}.md"

echo "[split-taskmd] total=${total}, split at line ${split_line}"
echo "[split-taskmd] lines 1..$(( split_line - 1 )) → append to ${archive}"
echo "[split-taskmd] lines ${split_line}..${total} → keep in task.md"

if [ "$APPLY" -eq 1 ]; then
  # Append older part to archive (with header if new file)
  if [ ! -f "$archive" ]; then
    {
      echo "# Task Archive ${year}"
      echo ""
      echo "> Split from task.md on $(date -Iseconds)."
      echo ""
    } > "$archive"
  fi
  sed -n "1,$(( split_line - 1 ))p" "$TASKMD" >> "$archive"

  # Rewrite task.md with only the recent portion, plus a pointer header
  tmp=$(mktemp)
  {
    echo "<!-- archive pointer: older entries moved to task_archive_${year}.md on $(date -Iseconds) -->"
    echo ""
    sed -n "${split_line},\$p" "$TASKMD"
  } > "$tmp"
  mv "$tmp" "$TASKMD"

  echo "[split-taskmd] done. task.md is now $(wc -l < "$TASKMD") lines."
else
  echo "[split-taskmd] (dry-run — re-run with --apply to execute)"
fi
exit 0
