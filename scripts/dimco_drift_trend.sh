#!/bin/bash
# dimco_drift_trend.sh
#
# 目的: DIMCO Top 3 violation (PT-ACCORDION / PT-MODAL-ONCLICK / PT-CHECKBOX-CUSTOM) の
#       全 file 累計件数を計測、過去実行と比較して trend を可視化
#
# 使い方:
#   ./dimco_drift_trend.sh           # 計測 + 比較表示
#   ./dimco_drift_trend.sh --reset   # baseline 記録のみ (現在件数を新 baseline 化)
#
# 想定呼び出し:
#   - kashira 自走で 5 cmd 毎に実行
#   - 結果が悪化 (件数増加) してたら oyabun inbox に通知
#   - 結果が改善 (件数減少) してたら良好レポート
#
# データ保存:
#   logs/dimco_drift_trend.log (timestamp + 各 pattern 件数)
#
# 出典: cmd_254 audit (2026-05-11)、軽量版毎 5 cmd 監視
# 詳細 audit は cmd_254 type の重 cmd を別途実行 (月 1 回程度想定)

set -uo pipefail

PROTOTYPE_DIR="/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype"
LOG="/mnt/c/tools/neko-multi-agent/logs/dimco_drift_trend.log"

if [ ! -d "$PROTOTYPE_DIR" ]; then
  echo "ERROR: prototype dir not found: $PROTOTYPE_DIR"
  exit 1
fi

# 計測
NOW=$(date "+%Y-%m-%dT%H:%M:%S")

ACCORDION_HIT=$(grep -rln 'collapsible-header' "$PROTOTYPE_DIR/001_new/" "$PROTOTYPE_DIR/002_new横/" 2>/dev/null | wc -l)
MODAL_ONCLICK_HIT=$(grep -rlE 'onclick="select[A-Z][a-zA-Z]+\(this\)"' "$PROTOTYPE_DIR/001_new/" "$PROTOTYPE_DIR/002_new横/" 2>/dev/null | wc -l)
CHECKBOX_CUSTOM_HIT=$(grep -rlE 'input\[type="checkbox"\][[:space:]]*\{[^}]*border-radius:[[:space:]]*50%' "$PROTOTYPE_DIR/001_new/" "$PROTOTYPE_DIR/002_new横/" 2>/dev/null | wc -l)
SELECT_DOUBLE_HIT=$(grep -rlE 'select[[:space:]]*\{[^}]*appearance:[[:space:]]*auto' "$PROTOTYPE_DIR/001_new/" "$PROTOTYPE_DIR/002_new横/" 2>/dev/null | wc -l)
TOTAL_FILES=$(find "$PROTOTYPE_DIR/001_new/" "$PROTOTYPE_DIR/002_new横/" -name "*.html" 2>/dev/null | wc -l)

if [ "${1:-}" = "--reset" ]; then
  echo "[$NOW] BASELINE_RESET ACCORDION=$ACCORDION_HIT MODAL_ONCLICK=$MODAL_ONCLICK_HIT CHECKBOX_CUSTOM=$CHECKBOX_CUSTOM_HIT SELECT_DOUBLE=$SELECT_DOUBLE_HIT TOTAL_FILES=$TOTAL_FILES" >> "$LOG"
  echo "Baseline reset:"
  echo "  PT-ACCORDION (collapsible-header):       $ACCORDION_HIT files"
  echo "  PT-MODAL-ONCLICK:                        $MODAL_ONCLICK_HIT files"
  echo "  PT-CHECKBOX-CUSTOM (circle):             $CHECKBOX_CUSTOM_HIT files"
  echo "  PT-SELECT-DOUBLE-ARROW (appearance:auto): $SELECT_DOUBLE_HIT files"
  echo "  Total HTML files:                        $TOTAL_FILES"
  exit 0
fi

# log 追記
echo "[$NOW] MEASURE ACCORDION=$ACCORDION_HIT MODAL_ONCLICK=$MODAL_ONCLICK_HIT CHECKBOX_CUSTOM=$CHECKBOX_CUSTOM_HIT SELECT_DOUBLE=$SELECT_DOUBLE_HIT TOTAL_FILES=$TOTAL_FILES" >> "$LOG"

# 前回計測との diff
PREV_LINE=$(grep -v "BASELINE_RESET" "$LOG" 2>/dev/null | tail -2 | head -1)
echo "========================================"
echo "DIMCO Drift Trend Report ($NOW)"
echo "========================================"
echo ""
echo "Current measurement:"
echo "  PT-ACCORDION (collapsible-header):       $ACCORDION_HIT / $TOTAL_FILES files"
echo "  PT-MODAL-ONCLICK:                        $MODAL_ONCLICK_HIT / $TOTAL_FILES files"
echo "  PT-CHECKBOX-CUSTOM (circle):             $CHECKBOX_CUSTOM_HIT / $TOTAL_FILES files"
echo "  PT-SELECT-DOUBLE-ARROW (appearance:auto): $SELECT_DOUBLE_HIT / $TOTAL_FILES files"
echo ""

if [ -n "$PREV_LINE" ]; then
  PREV_ACCORDION=$(echo "$PREV_LINE" | grep -oE 'ACCORDION=[0-9]+' | head -1 | cut -d= -f2)
  PREV_MODAL=$(echo "$PREV_LINE" | grep -oE 'MODAL_ONCLICK=[0-9]+' | head -1 | cut -d= -f2)
  PREV_CHECKBOX=$(echo "$PREV_LINE" | grep -oE 'CHECKBOX_CUSTOM=[0-9]+' | head -1 | cut -d= -f2)
  PREV_SELECT=$(echo "$PREV_LINE" | grep -oE 'SELECT_DOUBLE=[0-9]+' | head -1 | cut -d= -f2)
  PREV_TS=$(echo "$PREV_LINE" | grep -oE '^\[[^\]]+\]' | tr -d '[]')

  echo "Trend vs previous ($PREV_TS):"

  trend_line() {
    local name=$1
    local prev=$2
    local cur=$3
    local diff=$((cur - prev))
    if [ "$diff" -gt 0 ]; then
      echo "  [WORSE] $name: $prev → $cur (+$diff)"
    elif [ "$diff" -lt 0 ]; then
      echo "  [BETTER] $name: $prev → $cur ($diff)"
    else
      echo "  [SAME] $name: $cur"
    fi
  }

  trend_line "PT-ACCORDION       " "$PREV_ACCORDION" "$ACCORDION_HIT"
  trend_line "PT-MODAL-ONCLICK   " "$PREV_MODAL" "$MODAL_ONCLICK_HIT"
  trend_line "PT-CHECKBOX-CUSTOM " "$PREV_CHECKBOX" "$CHECKBOX_CUSTOM_HIT"
  trend_line "PT-SELECT-DOUBLE   " "$PREV_SELECT" "$SELECT_DOUBLE_HIT"
else
  echo "No previous measurement — this is baseline."
  echo "Run again after the next 5 cmds to see trend."
fi

echo ""
echo "Log file: $LOG"
