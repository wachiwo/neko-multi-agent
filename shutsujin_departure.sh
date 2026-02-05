#!/bin/bash
# =^._.^= neko-multi-agent おでかけスクリプト（毎日の起動用）
# Daily Deployment Script for Neko Multi-Agent Orchestration System
#
# 使用方法:
#   ./shutsujin_departure.sh           # 全エージェント起動（通常）
#   ./shutsujin_departure.sh -s        # セットアップのみ（Claude起動なし）
#   ./shutsujin_departure.sh -h        # ヘルプ表示

set -e

# スクリプトのディレクトリを取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 言語設定を読み取り（デフォルト: ja）
LANG_SETTING="ja"
if [ -f "./config/settings.yaml" ]; then
    LANG_SETTING=$(grep "^language:" ./config/settings.yaml 2>/dev/null | awk '{print $2}' || echo "ja")
fi

# 色付きログ関数（猫風）
log_info() {
    echo -e "\033[1;33m【報】\033[0m $1"
}

log_success() {
    echo -e "\033[1;32m【成】\033[0m $1"
}

log_neko() {
    echo -e "\033[1;35m【猫】\033[0m $1"
}

# ═══════════════════════════════════════════════════════════════════════════════
# オプション解析
# ═══════════════════════════════════════════════════════════════════════════════
SETUP_ONLY=false
OPEN_TERMINAL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--setup-only)
            SETUP_ONLY=true
            shift
            ;;
        -t|--terminal)
            OPEN_TERMINAL=true
            shift
            ;;
        -h|--help)
            echo ""
            echo "=^._.^= neko-multi-agent おでかけスクリプト"
            echo ""
            echo "使用方法: ./shutsujin_departure.sh [オプション]"
            echo ""
            echo "オプション:"
            echo "  -s, --setup-only  tmuxセッションのセットアップのみ（Claude起動なし）"
            echo "  -t, --terminal    Windows Terminal で新しいタブを開く"
            echo "  -h, --help        このヘルプを表示"
            echo ""
            echo "例:"
            echo "  ./shutsujin_departure.sh      # 全エージェント起動（通常のおでかけ）"
            echo "  ./shutsujin_departure.sh -s   # セットアップのみ（手動でClaude起動）"
            echo "  ./shutsujin_departure.sh -t   # 全エージェント起動 + ターミナルタブ展開"
            echo ""
            echo "エイリアス:"
            echo "  csst  → cd $(pwd) && ./shutsujin_departure.sh"
            echo "  css   → tmux attach-session -t oyabun"
            echo "  csm   → tmux attach-session -t multiagent"
            echo ""
            exit 0
            ;;
        *)
            echo "不明なオプション: $1"
            echo "./shutsujin_departure.sh -h でヘルプを表示"
            exit 1
            ;;
    esac
done

# ═══════════════════════════════════════════════════════════════════════════════
# おでかけバナー表示
# ═══════════════════════════════════════════════════════════════════════════════
show_neko_banner() {
    clear

    # タイトルバナー（色付き）
    echo ""
    echo -e "\033[1;35m╔══════════════════════════════════════════════════════════════════════════════════╗\033[0m"
    echo -e "\033[1;35m║\033[0m \033[1;33m███╗   ██╗███████╗██╗  ██╗ ██████╗                                          \033[0m \033[1;35m║\033[0m"
    echo -e "\033[1;35m║\033[0m \033[1;33m████╗  ██║██╔════╝██║ ██╔╝██╔═══██╗                                         \033[0m \033[1;35m║\033[0m"
    echo -e "\033[1;35m║\033[0m \033[1;33m██╔██╗ ██║█████╗  █████╔╝ ██║   ██║                                         \033[0m \033[1;35m║\033[0m"
    echo -e "\033[1;35m║\033[0m \033[1;33m██║╚██╗██║██╔══╝  ██╔═██╗ ██║   ██║                                         \033[0m \033[1;35m║\033[0m"
    echo -e "\033[1;35m║\033[0m \033[1;33m██║ ╚████║███████╗██║  ██╗╚██████╔╝                                         \033[0m \033[1;35m║\033[0m"
    echo -e "\033[1;35m║\033[0m \033[1;33m╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝  \033[1;37mMulti-Agent System\033[0m                    \033[1;35m║\033[0m"
    echo -e "\033[1;35m╠══════════════════════════════════════════════════════════════════════════════════╣\033[0m"
    echo -e "\033[1;35m║\033[0m       \033[1;37mおでかけするにゃ〜！！！\033[0m    \033[1;33m=^._.^=\033[0m    \033[1;36mみんな集合にゃ！\033[0m                  \033[1;35m║\033[0m"
    echo -e "\033[1;35m╚══════════════════════════════════════════════════════════════════════════════════╝\033[0m"
    echo ""

    # ═══════════════════════════════════════════════════════════════════════════
    # 猫チーム紹介
    # ═══════════════════════════════════════════════════════════════════════════
    echo -e "\033[1;35m  ╔═════════════════════════════════════════════════════════════════════════════╗\033[0m"
    echo -e "\033[1;35m  ║\033[0m                    \033[1;37m【 ね こ チ ー ム ・ 集 合 】\033[0m                          \033[1;35m║\033[0m"
    echo -e "\033[1;35m  ╚═════════════════════════════════════════════════════════════════════════════╝\033[0m"

    cat << 'NEKO_EOF'

                        =^._.^=
                       /       \          「みんな〜、おでかけするにゃ！」
                      | o   o  |                 ── 親分猫
                      |  =w=   |
                       \_____/
                      /|     |\
                     (_|     |_)

       /\_/\      /\_/\      /\_/\      /\_/\
      ( o.o )    ( o.o )    ( >.< )    ( -.- )
       > ^ <      > ^ <      > ^ <      > ^ <
      /|   |\    /|   |\    /|   |\    /|   |\
     (_|   |_)  (_|   |_)  (_|   |_)  (_|   |_)
     [1号猫]    [2号犬]    [3号猫]    [4号猫]
      真面目    にゃわん    のんびり    クール

NEKO_EOF

    echo -e "                    \033[1;36m「「「 にゃ〜！！ おでかけにゃ〜！！ 」」」\033[0m"
    echo ""

    # ═══════════════════════════════════════════════════════════════════════════
    # システム情報
    # ═══════════════════════════════════════════════════════════════════════════
    echo -e "\033[1;33m  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\033[0m"
    echo -e "\033[1;33m  ┃\033[0m  \033[1;37m=^._.^= neko-multi-agent\033[0m  〜 \033[1;36mねこマルチエージェントシステム\033[0m 〜              \033[1;33m┃\033[0m"
    echo -e "\033[1;33m  ┃\033[0m                                                                           \033[1;33m┃\033[0m"
    echo -e "\033[1;33m  ┃\033[0m    \033[1;35m親分猫\033[0m: プロジェクト統括    \033[1;31m頭猫\033[0m: タスク管理    \033[1;34m作業猫(犬)\033[0m: 実働×4    \033[1;33m┃\033[0m"
    echo -e "\033[1;33m  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\033[0m"
    echo ""
}

# バナー表示実行
show_neko_banner

echo -e "  \033[1;33mにゃ〜！準備を始めるにゃ\033[0m (Setting up the playground)"
echo ""

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 1: 既存セッションクリーンアップ
# ═══════════════════════════════════════════════════════════════════════════════
log_info "お片付け中にゃ..."
tmux kill-session -t multiagent 2>/dev/null && log_info "  └─ multiagentセッション、お片付け完了" || log_info "  └─ multiagentセッションは存在せず"
tmux kill-session -t oyabun 2>/dev/null && log_info "  └─ oyabunセッション、お片付け完了" || log_info "  └─ oyabunセッションは存在せず"

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 1.5: 前回記録のバックアップ（内容がある場合のみ）
# ═══════════════════════════════════════════════════════════════════════════════
BACKUP_DIR="./logs/backup_$(date '+%Y%m%d_%H%M%S')"
NEED_BACKUP=false

if [ -f "./dashboard.md" ]; then
    if grep -q "cmd_" "./dashboard.md" 2>/dev/null; then
        NEED_BACKUP=true
    fi
fi

if [ "$NEED_BACKUP" = true ]; then
    mkdir -p "$BACKUP_DIR" || true
    cp "./dashboard.md" "$BACKUP_DIR/" 2>/dev/null || true
    cp -r "./queue/reports" "$BACKUP_DIR/" 2>/dev/null || true
    cp -r "./queue/tasks" "$BACKUP_DIR/" 2>/dev/null || true
    cp "./queue/oyabun_to_kashira.yaml" "$BACKUP_DIR/" 2>/dev/null || true
    log_info "前回の記録をバックアップしたにゃ: $BACKUP_DIR"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 2: 報告ファイルリセット
# ═══════════════════════════════════════════════════════════════════════════════
log_info "前回の記録をお片付け中にゃ..."

# queue ディレクトリが存在しない場合は作成
[ -d ./queue/reports ] || mkdir -p ./queue/reports
[ -d ./queue/tasks ] || mkdir -p ./queue/tasks
[ -d ./queue/inbox ] || mkdir -p ./queue/inbox

# inbox ファイル初期化（各エージェント用）
for agent in kashira worker1 worker2 worker3 worker4; do
    : > "./queue/inbox/${agent}.queue"
done
log_info "  └─ inbox 初期化完了にゃ"

# 作業猫(犬)タスクファイルリセット
WORKER_NAMES=("1号猫" "2号犬" "3号猫" "4号猫")
for i in {1..4}; do
    cat > ./queue/tasks/worker${i}.yaml << EOF
# ${WORKER_NAMES[$((i-1))]}専用タスクファイル
task:
  task_id: null
  parent_cmd: null
  description: null
  target_path: null
  status: idle
  timestamp: ""
EOF
done

# 作業猫(犬)レポートファイルリセット
for i in {1..4}; do
    cat > ./queue/reports/worker${i}_report.yaml << EOF
worker_id: worker${i}
task_id: null
timestamp: ""
status: idle
result: null
EOF
done

# キューファイルリセット
cat > ./queue/oyabun_to_kashira.yaml << 'EOF'
queue: []
EOF

log_success "お片付け完了にゃ！"

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 3: ダッシュボード初期化
# ═══════════════════════════════════════════════════════════════════════════════
log_info "にゃんボードを初期化中にゃ..."
TIMESTAMP=$(date "+%Y-%m-%d %H:%M")

if [ "$LANG_SETTING" = "ja" ]; then
    # 日本語のみ
    cat > ./dashboard.md << EOF
# =^._.^= にゃんボード
最終更新: ${TIMESTAMP}

## 要対応 - ご主人様のご判断をお待ちしておりますにゃ
なし

## 進行中 - お仕事中にゃ
なし

## 本日の成果
| 時刻 | プロジェクト | お仕事 | 結果 |
|------|-------------|--------|------|

## スキル化候補 - 承認待ち
なし

## 生成されたスキル
なし

## 待機中
なし

## 伺い事項
なし
EOF
else
    # 日本語 + 翻訳併記
    cat > ./dashboard.md << EOF
# =^._.^= にゃんボード (Nyan Board)
最終更新 (Last Updated): ${TIMESTAMP}

## 要対応 - ご主人様のご判断をお待ちしておりますにゃ (Action Required - Awaiting Master's Decision)
なし (None)

## 進行中 - お仕事中にゃ (In Progress - Working)
なし (None)

## 本日の成果 (Today's Achievements)
| 時刻 (Time) | プロジェクト (Project) | お仕事 (Task) | 結果 (Result) |
|------|------|------|------|

## スキル化候補 - 承認待ち (Skill Candidates - Pending Approval)
なし (None)

## 生成されたスキル (Generated Skills)
なし (None)

## 待機中 (On Standby)
なし (None)

## 伺い事項 (Questions for Master)
なし (None)
EOF
fi

log_success "  └─ にゃんボード初期化完了 (言語: $LANG_SETTING)"
echo ""

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 4: multiagentセッション作成（5ペイン：kashira + worker1-4）
# ═══════════════════════════════════════════════════════════════════════════════
# tmux の存在確認
if ! command -v tmux &> /dev/null; then
    echo ""
    echo "  ╔════════════════════════════════════════════════════════╗"
    echo "  ║  [ERROR] tmux not found!                              ║"
    echo "  ║  tmux が見つかりません                                 ║"
    echo "  ╠════════════════════════════════════════════════════════╣"
    echo "  ║  Run first_setup.sh first:                            ║"
    echo "  ║  まず first_setup.sh を実行してください:               ║"
    echo "  ║     ./first_setup.sh                                  ║"
    echo "  ╚════════════════════════════════════════════════════════╝"
    echo ""
    exit 1
fi

log_neko "頭猫・作業猫(犬)のお部屋を準備中にゃ（5名配備）..."

# 最初のペイン作成
if ! tmux new-session -d -s multiagent -n "agents" 2>/dev/null; then
    echo ""
    echo "  ╔════════════════════════════════════════════════════════════╗"
    echo "  ║  [ERROR] Failed to create tmux session 'multiagent'      ║"
    echo "  ║  tmux セッション 'multiagent' の作成に失敗しました       ║"
    echo "  ╠════════════════════════════════════════════════════════════╣"
    echo "  ║  An existing session may be running.                     ║"
    echo "  ║  既存セッションが残っている可能性があります              ║"
    echo "  ║                                                          ║"
    echo "  ║  Check: tmux ls                                          ║"
    echo "  ║  Kill:  tmux kill-session -t multiagent                  ║"
    echo "  ╚════════════════════════════════════════════════════════════╝"
    echo ""
    exit 1
fi

# 1x5グリッド作成（横一列に5ペイン: kashira + worker1-4）
# 注意: split-window はフォーカスを新ペインに移すため、分割元ペインを明示指定する
# new-session で Pane 0 が作成済み。以降は最後のペインを分割して右に追加。
tmux split-window -h -t "multiagent:0.0"
tmux select-layout -t "multiagent:0" even-horizontal
tmux split-window -h -t "multiagent:0.1"
tmux select-layout -t "multiagent:0" even-horizontal
tmux split-window -h -t "multiagent:0.2"
tmux select-layout -t "multiagent:0" even-horizontal
tmux split-window -h -t "multiagent:0.3"
tmux select-layout -t "multiagent:0" even-horizontal

# ペインタイトル設定（0: kashira, 1-4: worker1-4）
PANE_TITLES=("kashira" "worker1" "worker2" "worker3" "worker4")
PANE_COLORS=("1;31" "1;34" "1;33" "1;32" "1;36")  # kashira: 赤, worker1: 青, worker2: 黄, worker3: 緑, worker4: シアン

for i in {0..4}; do
    tmux select-pane -t "multiagent:0.$i" -T "${PANE_TITLES[$i]}"
    tmux send-keys -t "multiagent:0.$i" "cd \"$(pwd)\" && export PS1='(\[\033[${PANE_COLORS[$i]}m\]${PANE_TITLES[$i]}\[\033[0m\]) \[\033[1;32m\]\w\[\033[0m\]\$ ' && clear" Enter
done

log_success "  └─ 頭猫・作業猫(犬)のお部屋、準備完了にゃ"
echo ""

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 5: oyabunセッション作成（1ペイン）
# ═══════════════════════════════════════════════════════════════════════════════
log_neko "親分猫のお部屋を準備中にゃ..."
if ! tmux new-session -d -s oyabun 2>/dev/null; then
    echo ""
    echo "  ╔════════════════════════════════════════════════════════════╗"
    echo "  ║  [ERROR] Failed to create tmux session 'oyabun'          ║"
    echo "  ║  tmux セッション 'oyabun' の作成に失敗しました           ║"
    echo "  ╠════════════════════════════════════════════════════════════╣"
    echo "  ║  An existing session may be running.                     ║"
    echo "  ║  既存セッションが残っている可能性があります              ║"
    echo "  ║                                                          ║"
    echo "  ║  Check: tmux ls                                          ║"
    echo "  ║  Kill:  tmux kill-session -t oyabun                      ║"
    echo "  ╚════════════════════════════════════════════════════════════╝"
    echo ""
    exit 1
fi
tmux send-keys -t oyabun "cd \"$(pwd)\" && export PS1='(\[\033[1;35m\]親分猫\[\033[0m\]) \[\033[1;32m\]\w\[\033[0m\]\$ ' && clear" Enter
tmux select-pane -t oyabun:0.0 -P 'bg=#002b36'  # 親分猫の Solarized Dark

log_success "  └─ 親分猫のお部屋、準備完了にゃ"
echo ""

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 6: Claude Code 起動（--setup-only でスキップ）
# ═══════════════════════════════════════════════════════════════════════════════
if [ "$SETUP_ONLY" = false ]; then
    # Claude Code CLI の存在チェック
    if ! command -v claude &> /dev/null; then
        log_info "claude コマンドが見つからないにゃ"
        echo "  first_setup.sh を再実行してください:"
        echo "    ./first_setup.sh"
        exit 1
    fi

    log_neko "全員に Claude Code を召喚中にゃ..."

    # ═══════════════════════════════════════════════════════════════════════════
    # 起動方式: CLIの引数にプロンプトを直接渡す
    # ═══════════════════════════════════════════════════════════════════════════
    # SessionStart hook (detect-persona.sh) が additionalContext として指示書を注入。
    # CLI引数の prompt で最初の指示を同時に渡すことで、
    # プロンプト（❯）検出のポーリングが不要になる。

    # ═══════════════════════════════════════════════════════════════════════════
    # 全エージェント一括起動（並列起動）
    # ═══════════════════════════════════════════════════════════════════════════
    # 各ペインは独立しているため、sleep なしで一括起動する。

    # 親分猫（Opusモデル指定）
    OYABUN_PROMPT="Read instructions/oyabun.md and understand your role. You are oyabun."
    tmux send-keys -t oyabun "MAX_THINKING_TOKENS=0 claude --model opus --dangerously-skip-permissions \"${OYABUN_PROMPT}\""
    tmux send-keys -t oyabun Enter
    log_info "  └─ 親分猫、召喚完了にゃ"

    # 頭猫
    KASHIRA_PROMPT="IMPORTANT: You are in pane multiagent:0.0. This means you are kashira (head cat). Read ONLY instructions/kashira.md - that is YOUR instruction file. Display idle cat art after understanding."
    tmux send-keys -t "multiagent:0.0" "claude --dangerously-skip-permissions \"${KASHIRA_PROMPT}\""
    tmux send-keys -t "multiagent:0.0" Enter
    log_info "  └─ 頭猫、召喚完了にゃ"

    # 作業猫(犬)（1-4、それぞれ個別の指示書 — 一括起動）
    WORKER_INSTRUCTIONS=("instructions/1gou-neko.md" "instructions/2gou-inu.md" "instructions/3gou-neko.md" "instructions/4gou-neko.md")
    WORKER_LABELS=("1号猫" "2号犬" "3号猫" "4号猫")

    for i in {1..4}; do
        WORKER_PROMPT="IMPORTANT: You are in pane multiagent:0.$i. This means you are worker$i (${WORKER_LABELS[$((i-1))]}). Read ONLY ${WORKER_INSTRUCTIONS[$((i-1))]} - that is YOUR instruction file. Ignore any other worker identity from CLAUDE.md. Display idle cat art after understanding."
        tmux send-keys -t "multiagent:0.$i" "claude --dangerously-skip-permissions \"${WORKER_PROMPT}\""
        tmux send-keys -t "multiagent:0.$i" Enter
    done
    log_info "  └─ 作業猫(犬)、召喚完了にゃ"

    # 全エージェントの起動待ち（一括）
    sleep 3

    log_success "全員 Claude Code 起動完了にゃ！"
    echo ""

    # ═══════════════════════════════════════════════════════════════════════════
    # 猫チーム出発！
    # ═══════════════════════════════════════════════════════════════════════════
    echo -e "\033[1;35m  ┌────────────────────────────────────────────────────────────────────────────┐\033[0m"
    echo -e "\033[1;35m  │\033[0m                        \033[1;37m【 ね こ チ ー ム 出 発 ！ 】\033[0m                        \033[1;35m│\033[0m"
    echo -e "\033[1;35m  └────────────────────────────────────────────────────────────────────────────┘\033[0m"

    cat << 'NEKO_DEPART_EOF'

          /\_/\   「みんな準備はいいかにゃ〜？」
         ( o.o )
          > ^ <         /\_/\  /\_/\  /\_/\  /\_/\
         /|   |\       ( o.o )( o.o )( >.< )( -.- )
        (_|   |_)       > ^ <  > ^ <  > ^ <  > ^ <
        [親分猫]       [1号猫][2号犬][3号猫][4号猫]

NEKO_DEPART_EOF

    echo -e "                         \033[1;35m「 おでかけにゃ〜！がんばるにゃ！ 」\033[0m"
    echo ""
fi

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 7: 環境確認・完了メッセージ
# ═══════════════════════════════════════════════════════════════════════════════
log_info "お部屋を確認中にゃ..."
echo ""
echo "  ┌──────────────────────────────────────────────────────────┐"
echo "  │  Tmuxセッション (Sessions)                                │"
echo "  └──────────────────────────────────────────────────────────┘"
tmux list-sessions | sed 's/^/     /'
echo ""
echo "  ┌──────────────────────────────────────────────────────────┐"
echo "  │  お部屋配置図 (Formation)                                 │"
echo "  └──────────────────────────────────────────────────────────┘"
echo ""
echo "     【oyabunセッション】親分猫のお部屋"
echo "     ┌─────────────────────────────┐"
echo "     │  Pane 0: 親分猫 (OYABUN)   │  ← 統括・プロジェクト管理"
echo "     └─────────────────────────────┘"
echo ""
echo "     【multiagentセッション】頭猫・作業猫(犬)のお部屋（1x5 = 5ペイン）"
echo "     ┌─────────┬─────────┬─────────┬─────────┬─────────┐"
echo "     │ kashira  │ worker1 │ worker2 │ worker3 │ worker4 │"
echo "     │(頭猫) │(1号猫)  │(2号犬)  │(3号猫)  │(4号猫)  │"
echo "     └─────────┴─────────┴─────────┴─────────┴─────────┘"
echo ""

echo ""
echo "  ╔══════════════════════════════════════════════════════════╗"
echo "  ║  =^._.^= おでかけ準備完了にゃ！がんばるにゃ〜！          ║"
echo "  ╚══════════════════════════════════════════════════════════╝"
echo ""

if [ "$SETUP_ONLY" = true ]; then
    echo "  セットアップのみモード: Claude Codeは未起動です"
    echo ""
    echo "  手動でClaude Codeを起動するには:"
    echo "  ┌──────────────────────────────────────────────────────────┐"
    echo "  │  # 親分猫を召喚                                          │"
    echo "  │  tmux send-keys -t oyabun 'claude --dangerously-skip-permissions' Enter │"
    echo "  │                                                          │"
    echo "  │  # 頭猫・作業猫(犬)を一斉召喚                          │"
    echo "  │  for i in {0..4}; do \\                                   │"
    echo "  │    tmux send-keys -t multiagent:0.\$i \\                   │"
    echo "  │      'claude --dangerously-skip-permissions' Enter       │"
    echo "  │  done                                                    │"
    echo "  └──────────────────────────────────────────────────────────┘"
    echo ""
fi

echo "  次のステップ:"
echo "  ┌──────────────────────────────────────────────────────────┐"
echo "  │  親分猫のお部屋にアタッチして命令開始:                    │"
echo "  │     tmux attach-session -t oyabun   (または: css)        │"
echo "  │                                                          │"
echo "  │  頭猫・作業猫(犬)のお部屋を確認:                       │"
echo "  │     tmux attach-session -t multiagent   (または: csm)    │"
echo "  │                                                          │"
echo "  │  ※ 各エージェントは指示書を読み込み済み。                 │"
echo "  │    すぐに命令を開始できます。                             │"
echo "  └──────────────────────────────────────────────────────────┘"
echo ""
echo "  ════════════════════════════════════════════════════════════"
echo "   =^._.^= おでかけにゃ〜！みんながんばるにゃ！"
echo "  ════════════════════════════════════════════════════════════"
echo ""

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 8: Windows Terminal でタブを開く（-t オプション時のみ）
# ═══════════════════════════════════════════════════════════════════════════════
if [ "$OPEN_TERMINAL" = true ]; then
    log_info "Windows Terminal でタブを展開中にゃ..."

    # Windows Terminal が利用可能か確認
    if command -v wt.exe &> /dev/null; then
        wt.exe -w 0 new-tab wsl.exe -e bash -c "tmux attach-session -t oyabun" \; new-tab wsl.exe -e bash -c "tmux attach-session -t multiagent"
        log_success "  └─ ターミナルタブ展開完了にゃ"
    else
        log_info "  └─ wt.exe が見つかりません。手動でアタッチしてください。"
    fi
    echo ""
fi
