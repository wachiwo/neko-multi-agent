#!/usr/bin/env bash
# check-package-install.sh - PreToolUse hook (Bash matcher)
#
# Purpose: When `npm install`, `pip install`, `cargo add`, `gem install`, or
# similar package-install commands fire, warn (non-blocking) that SLOP-001
# (slopsquatting) requires name verification before install.
#
# Context: LLMs hallucinate plausible package names. Installing a made-up name
# can pull a squatted malicious package. See CLAUDE.md slopsquatting_defense.
#
# This hook does NOT fetch from registries (no net call in a hook); it nudges
# the operator to verify with the built-in step before proceeding.

set -uo pipefail

INPUT=$(cat 2>/dev/null || true)

COMMAND=$(echo "$INPUT" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    if d.get('tool_name') == 'Bash':
        print(d.get('tool_input', {}).get('command', ''))
except Exception:
    pass
" 2>/dev/null)

[ -z "$COMMAND" ] && exit 0

# Match install-intent patterns
MGR=""
case "$COMMAND" in
  *"npm install "*|*"npm i "*|*"npm add "*)            MGR="npm" ;;
  *"yarn add "*|*"yarn install "*)                      MGR="yarn" ;;
  *"pnpm add "*|*"pnpm install "*)                      MGR="pnpm" ;;
  *"pip install "*|*"pip3 install "*|*"pipx install "*) MGR="pip" ;;
  *"uv add "*|*"uv pip install "*)                      MGR="uv" ;;
  *"cargo add "*|*"cargo install "*)                    MGR="cargo" ;;
  *"gem install "*)                                     MGR="gem" ;;
  *"go get "*|*"go install "*)                          MGR="go" ;;
  *"brew install "*)                                    MGR="brew" ;;
  *"apt-get install "*|*"apt install "*)                MGR="apt" ;;
esac

[ -z "$MGR" ] && exit 0

# Ignore pure upgrade/reinstall of already-declared deps (heuristic)
case "$COMMAND" in
  *"npm install"|*"npm i"|*"yarn install"|*"pnpm install"|*"pip install -r "*|*"pip install --upgrade pip"*)
    exit 0
    ;;
esac

cat >&2 <<EOF
[check-package-install] ${MGR} install detected. SLOP-001 reminder:

  command: ${COMMAND}

Before proceeding:
  1. Verify each NEW package name exists on its official registry.
     - npm:   https://www.npmjs.com/package/<name>
     - pypi:  https://pypi.org/project/<name>/
     - crates: https://crates.io/crates/<name>
  2. Check publisher, first-published date, download counts.
  3. If the name looks like two real packages merged, treat as hallucinated.
  4. If uncertain → ABORT and ask goshujinsama.

(CLAUDE.md § slopsquatting_defense)
EOF

# Non-blocking
exit 0
