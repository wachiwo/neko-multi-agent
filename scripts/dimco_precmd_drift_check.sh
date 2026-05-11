#!/bin/bash
# dimco_precmd_drift_check.sh
#
# 目的: DIMCO cmd dispatch 前に対象 file の drift 状態を可視化、
#       kashira/worker が「現状把握→catalog literal port」の判断を最短化
#
# 使い方:
#   ./dimco_precmd_drift_check.sh <file_path> [<file_path> ...]
#
# 出力: file ごとに以下を表示
#   - drift pattern hit count (PT-ACCORDION / PT-MODAL-ONCLICK / PT-CHECKBOX-CUSTOM 等)
#   - catalog reference candidate (どの catalog file の signature と一致するか)
#   - 推奨 action (literal port / keep / 要 ご主人様 review)
#
# 想定呼び出し元: kashira (cmd dispatch 前に自走実行、結果を spec.md に貼る)
#
# 出典: cmd_254 全面 drift audit (2026-05-11)、memory/feedback_cmd_yaml_dimco_template.md
#
# cmd_255 Phase 0 tuning (2026-05-11T22:10、kashira):
# - Fix integer expression bug: removed pipefail-incompatible `| head -1 || echo 0` pattern
# - Fix PT-CHECKBOX-CUSTOM false positive (golden master 059 reported MINOR DRIFT):
#   - Changed from file-wide grep (border-radius:50% + appearance:none anywhere) to
#     rule-scoped Python check (both within same input[type=checkbox] CSS rule block)

set -uo pipefail

CATALOG_DIR="/mnt/i/仕事/001_ディムコ/001_ソース/002_部品"

if [ "$#" -eq 0 ]; then
  echo "Usage: $0 <file_path> [<file_path> ...]"
  echo ""
  echo "Drift patterns checked:"
  echo "  PT-ACCORDION         — .collapsible-header (drift) vs .collapsible-title (canonical)"
  echo "  PT-MODAL-ONCLICK     — <tr onclick=\"select...\"> (drift) vs <input type=radio> + 登録 button (canonical)"
  echo "  PT-CHECKBOX-CUSTOM   — input[type=checkbox] + appearance:none / border-radius:50% (drift) vs native (canonical)"
  echo "  PT-SELECT-DOUBLE-ARROW — select { appearance: auto } 後勝ち (drift)"
  echo "  PT-SEARCH-CONDITION  — 独自 search form structure (drift)"
  echo "  PT-DATA-GRID-CUSTOM  — 独自 table structure (drift)"
  exit 1
fi

# 色定義
RED='\033[0;31m'
YELLOW='\033[0;33m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

check_file() {
  local file="$1"

  if [ ! -f "$file" ]; then
    echo -e "${RED}[ERROR]${NC} file not found: $file"
    return 1
  fi

  echo ""
  echo "========================================"
  echo "File: $file"
  echo "========================================"

  local total_drift=0
  local hit=0

  # helper: safe grep -c (returns 0 on no match, avoids pipefail "0\n0" bug)
  count_grep() {
    local pat="$1"; local f="$2"
    local n
    n=$(grep -cE "$pat" "$f" 2>/dev/null) || n=0
    echo "$n"
  }

  # PT-ACCORDION drift
  hit=$(count_grep 'collapsible-header' "$file")
  if [ "$hit" -gt 0 ]; then
    echo -e "${RED}[DRIFT]${NC} PT-ACCORDION: collapsible-header found ($hit times)"
    echo "   → Recommendation: literal port to .collapsible-title (CSS + class)"
    total_drift=$((total_drift + hit))
  fi

  # PT-MODAL-ONCLICK drift
  hit=$(count_grep 'onclick="select[A-Z][a-zA-Z]+\(this\)"' "$file")
  if [ "$hit" -gt 0 ]; then
    echo -e "${RED}[DRIFT]${NC} PT-MODAL-ONCLICK: row-onclick modal pattern found ($hit times)"
    echo "   → Recommendation: port to catalog left-radio + 登録 button pattern"
    echo "     Catalog ref: $CATALOG_DIR/詳細入力フォーム_横.html (line ~1068-1102)"
    total_drift=$((total_drift + hit))
  fi

  # PT-CHECKBOX-CUSTOM drift (rule-scoped: BOTH border-radius:50% AND appearance:none MUST be within same input[type=checkbox] CSS rule block)
  # cmd_255 Phase 0 fix: previously file-wide check caused false positive on 059 横 (golden master had border-radius:50% on avatar + appearance:none on select elsewhere)
  local checkbox_drift
  checkbox_drift=$(python3 -c '
import re, sys
try:
    content = open(sys.argv[1], "r", encoding="utf-8").read()
except Exception:
    print(0); sys.exit(0)
# Match input[type=checkbox]... {...} or combined selectors containing input[type=checkbox]
pattern = r"(?:^|[,\s])input\[type\s*=\s*[\"\x27]?checkbox[\"\x27]?\][^{]*\{([^}]*)\}"
count = 0
for block in re.findall(pattern, content):
    if re.search(r"border-radius\s*:\s*50%", block) and re.search(r"appearance\s*:\s*none", block):
        count += 1
print(count)
' "$file" 2>/dev/null) || checkbox_drift=0
  if [ "$checkbox_drift" -gt 0 ]; then
    echo -e "${RED}[DRIFT]${NC} PT-CHECKBOX-CUSTOM: circle checkbox CSS rule detected (rule-scoped: border-radius:50% + appearance:none in same input[type=checkbox] block, $checkbox_drift rules)"
    echo "   → Recommendation: delete custom rule, use browser native"
    total_drift=$((total_drift + checkbox_drift))
  fi

  # PT-SELECT-DOUBLE-ARROW drift
  if grep -qE 'select[[:space:]]*\{[^}]*appearance:[[:space:]]*auto' "$file" 2>/dev/null; then
    echo -e "${RED}[DRIFT]${NC} PT-SELECT-DOUBLE-ARROW: select { appearance: auto } found"
    echo "   → Recommendation: delete (custom SVG ▽ + native ▽ double-render)"
    total_drift=$((total_drift + 1))
  fi

  # PT-SEARCH-CONDITION-PANEL drift heuristic
  hit=$(count_grep 'class="search-form-field"|class="search-section-header"' "$file")
  if [ "$hit" -gt 0 ]; then
    echo -e "${YELLOW}[CHECK]${NC} PT-SEARCH-CONDITION: custom search-form-field structure ($hit times)"
    echo "   → Recommendation: compare with catalog 検索条件 pattern, port if drift"
  fi

  # 部品 catalog 参照存在チェック
  if grep -qE 'collapsible-title|excel-table|btn-search-trigger' "$file" 2>/dev/null; then
    echo -e "${GREEN}[OK]${NC} Catalog signature found (collapsible-title or excel-table or btn-search-trigger)"
  else
    echo -e "${YELLOW}[WARN]${NC} No canonical catalog signature found — file may be all custom"
  fi

  echo ""
  if [ "$total_drift" -eq 0 ]; then
    echo -e "Summary: ${GREEN}NO MAJOR DRIFT${NC} ✓"
  elif [ "$total_drift" -le 3 ]; then
    echo -e "Summary: ${YELLOW}MINOR DRIFT${NC} (${total_drift} hits) — port recommended in current cmd"
  else
    echo -e "Summary: ${RED}HEAVY DRIFT${NC} (${total_drift} hits) — escalate to separate cmd"
  fi
}

echo -e "${CYAN}DIMCO Pre-cmd Drift Check${NC}"
echo "Catalog: $CATALOG_DIR"
echo "Target file count: $#"

for file in "$@"; do
  check_file "$file"
done

echo ""
echo "========================================"
echo "Reference memory rules:"
echo "  - project_dimco_permanent_rule_component_reuse.md"
echo "  - feedback_component_reuse_principle.md"
echo "  - feedback_new_section_visual_parity.md"
echo "  - feedback_cmd_yaml_dimco_template.md"
echo "========================================"
