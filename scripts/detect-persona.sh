#!/bin/bash
# ペルソナ自動検出・注入スクリプト
# Claude Code の SessionStart hook から呼ばれ、
# tmux のセッション名・ペインインデックスからエージェントを特定し、
# 対応する instruction ファイルを stdout に出力する。
# stdout は additionalContext として会話に注入される。
#
# Worker agents: _worker_base.md (共通テンプレート) + 個別差分ファイルを連結出力。
# プレースホルダー ({{WORKER_ID}} 等) を sed で置換する。

SESSION_NAME=$(tmux display-message -p '#S' 2>/dev/null)
PANE_INDEX=$(tmux display-message -p '#P' 2>/dev/null)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
INSTRUCTIONS_DIR="$PROJECT_DIR/instructions"

# エージェント判定ロジック
AGENT=""
case "$SESSION_NAME" in
  oyabun)
    AGENT="oyabun"
    ;;
  multiagent)
    case "$PANE_INDEX" in
      0) AGENT="kashira" ;;
      1) AGENT="1gou-neko" ;;
      2) AGENT="2gou-inu" ;;
      3) AGENT="3gou-neko" ;;
      4) AGENT="4gou-neko" ;;
    esac
    ;;
esac

# instruction ファイル読み込み → stdout
if [ -n "$AGENT" ]; then
  echo "=== ペルソナ自動注入 ==="
  echo "あなたは【${AGENT}】として起動されています。"
  echo "以下の指示書に従って行動してください。"
  echo ""

  case "$AGENT" in
    oyabun)
      cat "$INSTRUCTIONS_DIR/oyabun.md"
      ;;
    kashira)
      cat "$INSTRUCTIONS_DIR/kashira.md"
      ;;
    1gou-neko|2gou-inu|3gou-neko|4gou-neko)
      # Worker: 個別差分ファイル + 共通テンプレートを連結
      WORKER_FILE=""
      WORKER_ID=""
      WORKER_NUM=""
      WORKER_NAME_CAP=""
      case "$AGENT" in
        1gou-neko) WORKER_FILE="1gou-neko.md"; WORKER_ID="worker1"; WORKER_NUM="1"; WORKER_NAME_CAP="Worker1" ;;
        2gou-inu)  WORKER_FILE="2gou-inu.md";  WORKER_ID="worker2"; WORKER_NUM="2"; WORKER_NAME_CAP="Worker2" ;;
        3gou-neko) WORKER_FILE="3gou-neko.md"; WORKER_ID="worker3"; WORKER_NUM="3"; WORKER_NAME_CAP="Worker3" ;;
        4gou-neko) WORKER_FILE="4gou-neko.md"; WORKER_ID="worker4"; WORKER_NUM="4"; WORKER_NAME_CAP="Worker4" ;;
      esac

      # 個別差分ファイル（YAML front matter + 個性セクション）
      if [ -f "$INSTRUCTIONS_DIR/$WORKER_FILE" ]; then
        cat "$INSTRUCTIONS_DIR/$WORKER_FILE"
      fi

      # 共通テンプレート（プレースホルダー置換）
      BASE_FILE="$INSTRUCTIONS_DIR/_worker_base.md"
      if [ -f "$BASE_FILE" ]; then
        echo ""
        echo "# Common Worker Instructions"
        echo ""
        sed \
          -e "s/{{WORKER_ID}}/$WORKER_ID/g" \
          -e "s/{{WORKER_NUM}}/$WORKER_NUM/g" \
          -e "s/{{WORKER_NAME_CAP}}/$WORKER_NAME_CAP/g" \
          "$BASE_FILE"
      fi
      ;;
  esac
fi
