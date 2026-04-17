#!/usr/bin/env bash
# rotate-logs.sh - Compress aged logs/ files and consolidate backup_* dirs.
#
# Purpose: logs/ currently sits at ~170MB and slows grep/audit. This rotates:
#   1. Regular files under logs/ older than RETENTION_DAYS (default 30) →
#      logs/_archive/YYYY-MM.tar.gz (monthly buckets), then removed.
#   2. backup_YYYYMMDD_* dirs: keep newest KEEP_BACKUPS (default 3), archive rest
#      into logs/_archive/backups/.
#
# Usage:
#   scripts/rotate-logs.sh              # dry-run (prints what would happen)
#   scripts/rotate-logs.sh --apply      # actually rotate
#
# Safe by default: never touches logs/skill_usage.log (live append target) or
# logs/oyabun_session.md (active session log). Never deletes _archive contents.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOGS_DIR="${REPO_ROOT}/logs"
ARCHIVE_DIR="${LOGS_DIR}/_archive"
BACKUP_ARCHIVE="${ARCHIVE_DIR}/backups"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
KEEP_BACKUPS="${KEEP_BACKUPS:-3}"

APPLY=0
[ "${1:-}" = "--apply" ] && APPLY=1

# Files we never rotate (live targets)
PROTECTED=(
  "skill_usage.log"
  "oyabun_session.md"
  "routing_log.queue"
  "bridge_watcher.log"
)

is_protected() {
  local name="$1"
  for p in "${PROTECTED[@]}"; do
    [ "$name" = "$p" ] && return 0
  done
  return 1
}

say() {
  if [ "$APPLY" -eq 1 ]; then
    echo "[rotate-logs] $*"
  else
    echo "[rotate-logs] DRY-RUN: $*"
  fi
}

[ ! -d "$LOGS_DIR" ] && { echo "[rotate-logs] no logs/ dir, nothing to do"; exit 0; }

mkdir -p "$ARCHIVE_DIR" "$BACKUP_ARCHIVE" 2>/dev/null || true

# ---- Phase 1: archive aged regular files ----
# Find top-level files only (not recursing _archive)
CUTOFF_SEC=$(( RETENTION_DAYS * 86400 ))
NOW_EPOCH=$(date +%s)

declare -A BUCKETS=()
while IFS= read -r -d '' f; do
  base=$(basename "$f")
  is_protected "$base" && continue
  mtime=$(stat -c %Y "$f" 2>/dev/null || echo 0)
  [ "$mtime" -eq 0 ] && continue
  age=$(( NOW_EPOCH - mtime ))
  [ "$age" -lt "$CUTOFF_SEC" ] && continue

  bucket=$(date -d "@$mtime" +%Y-%m 2>/dev/null || echo "unknown")
  BUCKETS[$bucket]+="$f"$'\n'
done < <(find "$LOGS_DIR" -maxdepth 1 -type f -print0 2>/dev/null)

total_files=0
for bucket in "${!BUCKETS[@]}"; do
  count=$(echo -n "${BUCKETS[$bucket]}" | grep -c '^' || true)
  total_files=$(( total_files + count ))
  tarball="${ARCHIVE_DIR}/${bucket}.tar.gz"
  say "archive ${count} files → ${tarball}"
  if [ "$APPLY" -eq 1 ]; then
    # Append to existing tarball by re-creating with union
    tmpdir=$(mktemp -d)
    if [ -f "$tarball" ]; then
      tar -xzf "$tarball" -C "$tmpdir" 2>/dev/null || true
    fi
    # Copy new files into tmpdir
    while IFS= read -r newf; do
      [ -z "$newf" ] && continue
      cp -p "$newf" "$tmpdir/" 2>/dev/null || true
    done <<<"${BUCKETS[$bucket]}"
    # Re-tar
    ( cd "$tmpdir" && tar -czf "$tarball.new" . ) && mv "$tarball.new" "$tarball"
    # Delete originals only on success
    while IFS= read -r newf; do
      [ -z "$newf" ] && continue
      rm -f "$newf"
    done <<<"${BUCKETS[$bucket]}"
    rm -rf "$tmpdir"
  fi
done

# ---- Phase 2: backup dir generational ----
# List backup_* dirs newest-first, skip newest KEEP_BACKUPS, archive the rest
mapfile -t BDIRS < <(find "$LOGS_DIR" -maxdepth 1 -type d -name 'backup_*' -printf '%T@ %p\n' 2>/dev/null | sort -rn | awk '{ $1=""; sub(/^ /,""); print }')

bdir_idx=0
for d in "${BDIRS[@]}"; do
  bdir_idx=$(( bdir_idx + 1 ))
  if [ "$bdir_idx" -le "$KEEP_BACKUPS" ]; then
    say "keep backup: $(basename "$d")"
    continue
  fi
  bname=$(basename "$d")
  tarball="${BACKUP_ARCHIVE}/${bname}.tar.gz"
  say "archive backup dir → ${tarball}"
  if [ "$APPLY" -eq 1 ]; then
    ( cd "$LOGS_DIR" && tar -czf "$tarball.new" "$bname" ) && mv "$tarball.new" "$tarball" && rm -rf "$d"
  fi
done

echo
echo "[rotate-logs] summary: ${total_files} regular files, $(( ${#BDIRS[@]} - KEEP_BACKUPS >= 0 ? ${#BDIRS[@]} - KEEP_BACKUPS : 0 )) backup dirs rotated"
if [ "$APPLY" -eq 0 ]; then
  echo "[rotate-logs] (dry-run — re-run with --apply to execute)"
fi

exit 0
