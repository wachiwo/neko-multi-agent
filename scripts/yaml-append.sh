#!/usr/bin/env bash
# yaml-append.sh - Atomic append to queue/*.yaml files with flock.
#
# Purpose: Prevent merge corruption when multiple agents (kashira + workers) write
# to queue/oyabun_to_kashira.yaml, queue/tasks/workerN.yaml, queue/reports/*.yaml
# simultaneously. Uses POSIX flock(1) for advisory exclusive locking per target file.
#
# Usage:
#   scripts/yaml-append.sh <target_yaml> <<'EOF'
#     - id: cmd_199
#       status: approved
#       ...
#   EOF
#
# Exits non-zero if target is outside queue/ (safety guard) or if append fails.
#
# NOTE: This is a NEW safety wrapper, not a replacement. Existing Edit/Write to
# queue/ still works; agents can migrate to this incrementally.

set -uo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <target_yaml>" >&2
  echo "       content is read from stdin and appended atomically" >&2
  exit 2
fi

TARGET="$1"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Resolve to absolute path
case "$TARGET" in
  /*) ABS="$TARGET" ;;
  *)  ABS="${REPO_ROOT}/${TARGET}" ;;
esac

# Safety: target must be inside REPO_ROOT/queue/
case "$ABS" in
  "${REPO_ROOT}/queue/"*) : ;;
  *)
    echo "[yaml-append] REFUSED: target '${TARGET}' is not under queue/" >&2
    exit 3
    ;;
esac

# Ensure parent exists
mkdir -p "$(dirname "$ABS")"

# Lock file (per-target)
LOCK="${ABS}.lock"

# Acquire exclusive lock with 5s timeout (prevents indefinite block if something dies)
exec 9>"$LOCK"
if ! flock -x -w 5 9; then
  echo "[yaml-append] FAILED to acquire lock on ${LOCK} within 5s" >&2
  exit 4
fi

# Append stdin content
cat >> "$ABS"
rc=$?

# Release lock (implicit on fd close)
exec 9>&-

# Optional: remove stale lock file if no other holder (best-effort, ignore errors)
rm -f "$LOCK" 2>/dev/null || true

exit $rc
