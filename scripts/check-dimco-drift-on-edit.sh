#!/bin/bash
# check-dimco-drift-on-edit.sh — PreToolUse hook: DIMCO HTML drift blocker
#
# Claude Code invokes this hook before Edit/Write tool calls.
# Input: JSON on stdin with tool_name and tool_input (file_path + content/old_string/new_string).
# Output:
#   exit 0 → allow
#   exit 2 → block (Claude sees stderr as feedback and retries differently)
#
# Scope:
#   - Tool calls: Edit | Write (others fast-exit 0)
#   - File path: must contain "dimco-prototype" AND end with ".html"
#
# Behavior (cmd_255 Phase 3、規律より仕組み):
#   - Compute new_content (Write: content / Edit: current.replace(old, new))
#   - Count forbidden drift patterns in current_content (before) vs new_content (after)
#   - If after > before for ANY pattern → BLOCK (newly introduced drift)
#   - If after == before → ALLOW (pre-existing drift is grandfathered, not our scope)
#   - If file does not exist (new file via Write) → BLOCK any drift > 0
#
# Drift patterns:
#   PT-ACCORDION         class="collapsible-header"
#   PT-MODAL-ONCLICK     onclick="select<Capital><alpha>(this)"
#   PT-CHECKBOX-CUSTOM   input[type=checkbox] { ... border-radius:50% ... appearance:none ... } (rule-scoped)
#   PT-SELECT-DOUBLE-ARROW   select { ... appearance: auto ... }
#
# Reference:
#   - cmd_255 spec (queue/oyabun_to_kashira.yaml line 192-228)
#   - scripts/dimco_precmd_drift_check.sh (Phase 0 tuned drift detector)
#   - memory/project_html_drift_defense_status.md

set -uo pipefail

INPUT=$(cat)

# Pass JSON to python via env var to avoid quote-escaping bugs with arbitrary JSON content.
export DIMCO_HOOK_INPUT="$INPUT"

python3 <<'PYEOF'
import json, sys, re, os

try:
    data = json.loads(os.environ.get('DIMCO_HOOK_INPUT', '{}'))
except Exception:
    sys.exit(0)

tool_name = data.get('tool_name', '')
if tool_name not in ('Edit', 'Write'):
    sys.exit(0)

tool_input = data.get('tool_input', {}) or {}
file_path = tool_input.get('file_path', '') or ''

# Scope: dimco-prototype paths only, HTML only
if 'dimco-prototype' not in file_path:
    sys.exit(0)
if not file_path.endswith('.html'):
    sys.exit(0)

# --- compute current_content (before) and new_content (after) ---
current_content = ''
if os.path.exists(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            current_content = f.read()
    except Exception:
        current_content = ''

if tool_name == 'Write':
    new_content = tool_input.get('content', '') or ''
else:  # Edit
    old_string = tool_input.get('old_string', '') or ''
    new_string = tool_input.get('new_string', '') or ''
    replace_all = bool(tool_input.get('replace_all', False))
    if current_content == '':
        # Edit on missing file is unusual; treat new_string as the entire new content
        new_content = new_string
    elif replace_all:
        new_content = current_content.replace(old_string, new_string)
    else:
        new_content = current_content.replace(old_string, new_string, 1)

# --- pattern counters ---
def count_accordion(content):
    return len(re.findall(r'class="collapsible-header"', content))

def count_modal_onclick(content):
    return len(re.findall(r'onclick="select[A-Z][a-zA-Z]+\(this\)"', content))

def count_checkbox_custom(content):
    # Rule-scoped: input[type=checkbox] CSS rule containing BOTH border-radius:50% AND appearance:none
    # (avoids false positive when those properties live in unrelated rules across the file)
    # Leading boundary uses \W (any non-word char) so the rule matches whether preceded by
    # whitespace/comma (indented CSS) or by `>`/`}`/etc (compressed/inline CSS).
    pattern = r'(?:^|\W)input\[type\s*=\s*[\"\']?checkbox[\"\']?\][^{]*\{([^}]*)\}'
    n = 0
    for block in re.findall(pattern, content):
        if re.search(r'border-radius\s*:\s*50%', block) and re.search(r'appearance\s*:\s*none', block):
            n += 1
    return n

def count_select_double_arrow(content):
    return len(re.findall(r'select\s*\{[^}]*appearance\s*:\s*auto', content))

CHECKS = [
    ('PT-ACCORDION',
     'class="collapsible-header" (drift accordion class)',
     count_accordion,
     'Catalog: .collapsible-title (canonical accordion class)',
     'Recommended: use class="collapsible-title" paired with .collapsible-content'),
    ('PT-MODAL-ONCLICK',
     'onclick="select*(this)" row-click modal pattern',
     count_modal_onclick,
     'Catalog: 詳細入力フォーム_横.html line 1068-1102',
     'Recommended: <input type="radio" name="*Select"> + 登録 button (cmd_253 canonical)'),
    ('PT-CHECKBOX-CUSTOM',
     'input[type=checkbox] custom circle (border-radius:50% + appearance:none in same rule)',
     count_checkbox_custom,
     'Catalog: browser native checkbox',
     'Recommended: delete custom rule, use browser native'),
    ('PT-SELECT-DOUBLE-ARROW',
     'select { appearance: auto } double-arrow bug',
     count_select_double_arrow,
     'Catalog: native single arrow (delete appearance:auto)',
     'Recommended: remove appearance:auto override (custom SVG ▽ + native ▽ double render)'),
]

violations = []
for pt_id, label, counter, catalog_ref, recommendation in CHECKS:
    before = counter(current_content)
    after = counter(new_content)
    if after > before:
        violations.append({
            'pt_id': pt_id, 'label': label,
            'before': before, 'after': after, 'delta': after - before,
            'catalog_ref': catalog_ref, 'recommendation': recommendation,
        })

if not violations:
    sys.exit(0)

# Block with detailed feedback
print(f'DIMCO DRIFT BLOCKED: {len(violations)} new drift introduction(s) in:', file=sys.stderr)
print(f'  {file_path}', file=sys.stderr)
print('', file=sys.stderr)
for v in violations:
    print(f"[{v['pt_id']}] {v['label']}", file=sys.stderr)
    print(f"   Count before edit: {v['before']}", file=sys.stderr)
    print(f"   Count after edit:  {v['after']}  (+{v['delta']} NEW)", file=sys.stderr)
    print(f"   {v['catalog_ref']}", file=sys.stderr)
    print(f"   → {v['recommendation']}", file=sys.stderr)
    print('', file=sys.stderr)
print('Pre-existing drift is allowed (grandfathered); only NEWLY introduced drift is blocked.', file=sys.stderr)
print('If this is an intentional structural fix, discuss with kashira/oyabun first.', file=sys.stderr)
print('Reference: memory/project_html_drift_defense_status.md (HTML 期間 drift 防御策 5 策)', file=sys.stderr)
sys.exit(2)
PYEOF
