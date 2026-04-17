#!/usr/bin/env bash
# check-secrets.sh - PreToolUse hook (Read/Write/Edit matcher)
#
# Purpose: Warn (non-blocking) when Read/Write/Edit targets a path that looks like
# a secret, credential, or token file. Complements the deny list in settings.json
# by catching patterns the schema glob can't express (e.g. content-based hints).
#
# Rationale: deny list blocks exact glob matches. This hook catches the long tail:
#   - non-standard names like "prod_secrets.txt", "backup.env.bak"
#   - untracked files outside the usual paths
# Output-only — does not block. Escalate via visible stderr warning.

set -uo pipefail

INPUT=$(cat 2>/dev/null || true)

read -r TOOL PATH_ARG <<<"$(echo "$INPUT" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    t = d.get('tool_name', '')
    inp = d.get('tool_input', {})
    p = inp.get('file_path') or inp.get('path') or ''
    print(t, p)
except Exception:
    print('', '')
" 2>/dev/null)"

# Only inspect file-access tools
case "$TOOL" in
  Read|Write|Edit|NotebookEdit) : ;;
  *) exit 0 ;;
esac

[ -z "$PATH_ARG" ] && exit 0

# Heuristic patterns — case-insensitive basename/path hints
BASENAME=$(basename "$PATH_ARG")
LOWER=$(echo "$PATH_ARG" | tr '[:upper:]' '[:lower:]')
LBASE=$(echo "$BASENAME" | tr '[:upper:]' '[:lower:]')

MATCH=""

case "$LBASE" in
  *secret*|*credential*|*password*|*passwd*|*apikey*|*api_key*|*token*) MATCH="filename hint" ;;
  id_rsa|id_ed25519|id_ecdsa|id_dsa|*.pem|*.key|*.pfx|*.p12) MATCH="private key extension" ;;
  .env|.env.*|*.env|*.env.local|*.env.production) MATCH="env file" ;;
esac

case "$LOWER" in
  *"/.ssh/"*|*"/.aws/"*|*"/.gnupg/"*|*"/.config/gcloud/"*) MATCH="${MATCH:+$MATCH + }sensitive directory" ;;
  *"service-account"*|*"serviceaccount"*) MATCH="${MATCH:+$MATCH + }service account" ;;
esac

[ -z "$MATCH" ] && exit 0

cat >&2 <<EOF
[check-secrets] WARNING: ${TOOL} target looks like a secret/credential file.
  path:  ${PATH_ARG}
  hint:  ${MATCH}

If this is intentional (e.g. reading a template, auditing a leak), ignore.
If not, cancel this call. Never commit secrets to the repo.

(See .claude/settings.json permissions.deny for hard-blocked patterns.)
EOF

# Non-blocking
exit 0
