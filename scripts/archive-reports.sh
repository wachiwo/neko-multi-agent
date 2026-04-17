#!/usr/bin/env bash
# archive-reports.sh - Move completed cmd reports to queue/reports/_archive/
#
# Heuristic: if a cmd's corresponding entry in queue/oyabun_to_kashira.yaml
# has status: completed|done|closed (or no longer appears at all), move all
# matching queue/reports/*_cmd_XXX*.yaml files into queue/reports/_archive/YYYY-MM/.
#
# Conservative: keeps the most recent 7 days of reports regardless (debug window).
#
# Usage:
#   scripts/archive-reports.sh           # dry-run
#   scripts/archive-reports.sh --apply   # actually move

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPORTS="${REPO_ROOT}/queue/reports"
ARCHIVE="${REPORTS}/_archive"
RECENT_DAYS="${RECENT_DAYS:-7}"

APPLY=0
[ "${1:-}" = "--apply" ] && APPLY=1

say() {
  if [ "$APPLY" -eq 1 ]; then echo "[archive-reports] $*"
  else echo "[archive-reports] DRY-RUN: $*"
  fi
}

[ ! -d "$REPORTS" ] && { echo "[archive-reports] no queue/reports, nothing to do"; exit 0; }

mkdir -p "$ARCHIVE" 2>/dev/null || true

# Active cmd ids — anything still in oyabun_to_kashira.yaml with non-terminal status
OYABUN_FILE="${REPO_ROOT}/queue/oyabun_to_kashira.yaml"
active_cmds=""
if [ -f "$OYABUN_FILE" ]; then
  # Extract cmd ids with status NOT in completed/done/closed/archived
  active_cmds=$(awk '
    /^- id:/    { id=$3 }
    /status:/   { st=$2; if (id != "" && st != "completed" && st != "done" && st != "closed" && st != "archived") print id; id=""; st="" }
  ' "$OYABUN_FILE" 2>/dev/null | sort -u)
fi

NOW_EPOCH=$(date +%s)
CUTOFF=$(( NOW_EPOCH - RECENT_DAYS * 86400 ))

moved=0
kept_recent=0
kept_active=0
while IFS= read -r -d '' f; do
  base=$(basename "$f")
  # Extract cmd id (best-effort): look for cmd_NNN in filename
  cmd_id=$(echo "$base" | grep -oE 'cmd_[0-9]+[a-z]*' | head -1)

  mtime=$(stat -c %Y "$f" 2>/dev/null || echo 0)
  if [ "$mtime" -gt "$CUTOFF" ]; then
    kept_recent=$(( kept_recent + 1 ))
    continue
  fi

  # Skip if its cmd is still active
  if [ -n "$cmd_id" ] && echo "$active_cmds" | grep -qx "$cmd_id"; then
    kept_active=$(( kept_active + 1 ))
    continue
  fi

  bucket=$(date -d "@$mtime" +%Y-%m 2>/dev/null || echo "unknown")
  target_dir="${ARCHIVE}/${bucket}"
  say "archive ${base} → _archive/${bucket}/"
  if [ "$APPLY" -eq 1 ]; then
    mkdir -p "$target_dir"
    mv "$f" "${target_dir}/"
  fi
  moved=$(( moved + 1 ))
done < <(find "$REPORTS" -maxdepth 1 -type f -name '*.yaml' -print0 2>/dev/null)

echo
echo "[archive-reports] moved=${moved} kept_recent=${kept_recent} kept_active=${kept_active}"
[ "$APPLY" -eq 0 ] && echo "[archive-reports] (dry-run — re-run with --apply to execute)"
exit 0
