#!/usr/bin/env bash
# check-report-schema.sh — PreToolUse hook (Write|Edit matcher)
#
# Purpose: reject worker report writes that violate scripts/report-schema.yaml.
# Origin: cmd_199 P0-a (2026-04-20). Closes the sp_041_strict escape hatch by
# blocking placeholder tokens (minor / N/A / ? / TBD / TODO / placeholder / "...")
# and non-numeric insertions/deletions BEFORE the yaml reaches disk.
#
# Input  (stdin JSON): {"tool_name": "Write|Edit", "tool_input": {...}}
# Output exit codes:
#   0 — allow (non-report path, unparseable legacy yaml, or content passes)
#   2 — block (schema violation; stderr carries the fix, Claude sees it)
#
# Non-blocking semantics chosen for: missing yaml module, unparseable content,
# unreadable current file during Edit simulation. Rationale: the hook must
# never break legitimate writes on infrastructure glitches — it only blocks
# when it has POSITIVE evidence of a schema violation.
#
# Coexists with check-secrets.sh in the PreToolUse Write|Edit matcher chain.
# Does not touch: check-secrets.sh / check-polling.sh / check-notification.sh /
# check-package-install.sh / detect-persona.sh / verify-hooks.sh.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCHEMA="${REPO_ROOT}/scripts/report-schema.yaml"
LOG="${REPO_ROOT}/logs/hook_check_report_schema.log"

mkdir -p "$(dirname "$LOG")"

INPUT=$(cat 2>/dev/null || true)
[ -z "$INPUT" ] && exit 0

PY_CODE=$(cat <<'PY'
import sys, json, os, re

SCHEMA_PATH = sys.argv[1]
REPO_ROOT = sys.argv[2]
LOG_PATH = sys.argv[3]

def iso_now():
    import datetime
    return datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()

def log(tool, path, verdict, reason):
    # Single-line log: newlines/pipes in reason (e.g. yaml parse errors) would
    # break the ISO8601|tool|path|verdict|reason format when consumers grep it.
    clean = str(reason).replace("\n", " / ").replace("\r", " ").replace("|", "/")
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"{iso_now()}|{tool}|{path}|{verdict}|{clean}\n")
    except Exception:
        pass  # never let logging failure break the hook

def allow(tool, path, reason):
    log(tool, path, "PASS", reason)
    sys.exit(0)

def block(tool, path, violations):
    msgs = []
    for v in violations:
        field, val, reason, fix = v
        msgs.append(
            f"  field:  {field}\n"
            f"  value:  {val!r}\n"
            f"  reason: {reason}\n"
            f"  fix:    {fix}"
        )
    sep = "\n  --\n"
    sys.stderr.write(
        f"[check-report-schema] REJECTED: {path}\n"
        + sep.join(msgs)
        + "\n\n"
        + "(see instructions/_rules/sp_041_strict.md; schema: scripts/report-schema.yaml)\n"
    )
    log(tool, path, "REJECT", f"{len(violations)} violation(s)")
    sys.exit(2)

try:
    import yaml
except ImportError:
    log("?", "?", "SKIP", "pyyaml missing")
    sys.exit(0)

try:
    data = json.loads(sys.stdin.read())
except Exception as e:
    log("?", "?", "SKIP", f"stdin not JSON: {e}")
    sys.exit(0)

tool = data.get("tool_name", "")
inp = data.get("tool_input", {}) or {}
fp = inp.get("file_path", "") or ""

if tool not in ("Write", "Edit"):
    # MultiEdit / NotebookEdit / others — out of scope for this hook.
    sys.exit(0)

if not fp:
    allow(tool, fp, "no file_path")

# --- Target filter: queue/reports/**/*.yaml only -----------------------------
# Match both absolute paths rooted at REPO_ROOT and relative paths.
abs_fp = os.path.abspath(fp)
reports_dir = os.path.abspath(os.path.join(REPO_ROOT, "queue", "reports"))
if not abs_fp.startswith(reports_dir + os.sep):
    sys.exit(0)  # non-report write: completely transparent
if not fp.endswith(".yaml"):
    allow(tool, fp, "not a yaml")

# --- Reconstruct the post-write content --------------------------------------
if tool == "Write":
    content = inp.get("content", "")
elif tool == "Edit":
    old = inp.get("old_string", "")
    new = inp.get("new_string", "")
    replace_all = bool(inp.get("replace_all", False))
    if not os.path.exists(abs_fp):
        allow(tool, fp, "edit target missing")
    try:
        with open(abs_fp, "r", encoding="utf-8") as f:
            cur = f.read()
    except Exception as e:
        allow(tool, fp, f"read fail: {e}")
    if old and old not in cur:
        allow(tool, fp, "old_string not present (Edit will fail)")
    if replace_all:
        content = cur.replace(old, new) if old else cur
    else:
        content = cur.replace(old, new, 1) if old else cur
else:
    sys.exit(0)

# --- Load schema --------------------------------------------------------------
try:
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = yaml.safe_load(f) or {}
except Exception as e:
    log(tool, fp, "SKIP", f"schema load fail: {e}")
    sys.exit(0)

forbidden = set(schema.get("forbidden_placeholder_values", []) or [])
num_fields = set(schema.get("numeric_fields", []) or [])
scopes = set(schema.get("sp_041_scoped_sections", []) or [])

# --- Parse content ------------------------------------------------------------
try:
    doc = yaml.safe_load(content)
except Exception as e:
    # Pre-existing invalid yaml (legacy reports use [PJ]-bracketed paths etc).
    # Don't block — we have no positive evidence of a schema violation.
    log(tool, fp, "SKIP", f"content parse fail: {e}")
    sys.exit(0)

if doc is None:
    allow(tool, fp, "empty yaml")

# --- Walk & validate ----------------------------------------------------------
violations = []

def walk(node, path, in_scope):
    if isinstance(node, dict):
        for k, v in node.items():
            ks = str(k)
            child_path = f"{path}.{ks}" if path else ks
            child_in_scope = in_scope or ks in scopes
            if child_in_scope and ks in num_fields and v is not None:
                if not isinstance(v, (int, float)) or isinstance(v, bool):
                    violations.append((
                        child_path,
                        v,
                        "numeric field holds non-numeric value (sp_041_strict)",
                        "replace with integer line count from `git diff --numstat HEAD -- <file>`",
                    ))
            walk(v, child_path, child_in_scope)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            walk(item, f"{path}[{i}]", in_scope)
    else:
        if in_scope and isinstance(node, str):
            if node.strip() in forbidden:
                violations.append((
                    path,
                    node,
                    f"placeholder value inside sp_041-scoped section (forbidden: {sorted(forbidden)})",
                    "paste raw `git diff --numstat HEAD -- <file>` output instead of a placeholder token",
                ))

walk(doc, "", False)

if violations:
    block(tool, fp, violations)

allow(tool, fp, "schema ok")
PY
)

python3 -c "$PY_CODE" "$SCHEMA" "$REPO_ROOT" "$LOG" <<<"$INPUT"
