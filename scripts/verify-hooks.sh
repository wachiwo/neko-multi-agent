#!/usr/bin/env bash
# verify-hooks.sh - SessionStart hook
#
# Purpose: Integrity check for the hook scripts themselves. If an attacker (or
# a runaway agent) modifies a hook script, this prints a stderr warning at
# session start so the operator notices.
#
# How it works:
#   - scripts/hook-checksums.txt stores the expected sha256 for each hook.
#   - This script recomputes sha256 for the listed hooks and diffs.
#   - Missing baseline file → first-run bootstrap (emit the current checksums
#     to stderr so the operator can commit them).
#
# Non-blocking. Output on stderr only.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASELINE="${REPO_ROOT}/scripts/hook-checksums.txt"

HOOKS=(
  "scripts/detect-persona.sh"
  "scripts/check-polling.sh"
  "scripts/check-notification.sh"
  "scripts/check-secrets.sh"
  "scripts/check-package-install.sh"
  "scripts/log-skill-usage.sh"
  "scripts/hook-userpromptsubmit.sh"
  "scripts/hook-precompact.sh"
  "scripts/hook-postcompact.sh"
  "scripts/verify-hooks.sh"
)

compute_line() {
  local rel="$1"
  local abs="${REPO_ROOT}/${rel}"
  if [ -f "$abs" ]; then
    local sum
    sum=$(sha256sum "$abs" | awk '{print $1}')
    echo "${sum}  ${rel}"
  else
    echo "MISSING  ${rel}"
  fi
}

# --seed mode: emit current checksums to stdout and exit (no compare)
if [ "${1:-}" = "--seed" ]; then
  for h in "${HOOKS[@]}"; do
    compute_line "$h"
  done
  exit 0
fi

# Bootstrap mode: no baseline yet
if [ ! -f "$BASELINE" ]; then
  {
    echo "[verify-hooks] BOOTSTRAP: no baseline at scripts/hook-checksums.txt"
    echo "  To seed it (after reviewing hooks), run:"
    echo
    for h in "${HOOKS[@]}"; do
      compute_line "$h"
    done
    echo
    echo "  …and commit scripts/hook-checksums.txt"
  } >&2
  exit 0
fi

# Compare mode
MISMATCH=0
MISMATCH_DETAIL=""

for h in "${HOOKS[@]}"; do
  expected=$(awk -v f="$h" '$2==f {print $1}' "$BASELINE")
  actual_line=$(compute_line "$h")
  actual=$(echo "$actual_line" | awk '{print $1}')

  if [ -z "$expected" ]; then
    MISMATCH=1
    MISMATCH_DETAIL+="  + untracked hook: ${h} (${actual})\n"
    continue
  fi
  if [ "$expected" != "$actual" ]; then
    MISMATCH=1
    MISMATCH_DETAIL+="  ! changed: ${h}\n      expected: ${expected}\n      actual:   ${actual}\n"
  fi
done

if [ "$MISMATCH" -ne 0 ]; then
  {
    echo "[verify-hooks] WARNING: hook script integrity mismatch"
    printf "%b" "$MISMATCH_DETAIL"
    echo
    echo "If the change is intentional, regenerate the baseline:"
    echo "  bash scripts/verify-hooks.sh --seed > scripts/hook-checksums.txt"
    echo "(review the diff before committing.)"
  } >&2
fi

exit 0
