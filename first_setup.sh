#!/bin/bash
# ============================================================
# first_setup.sh - multi-agent-shogun 初回セットアップスクリプト
# Ubuntu / WSL / Mac 用環境構築ツール
# ============================================================
# 実行方法:
#   chmod +x first_setup.sh
#   ./first_setup.sh
# ============================================================

set -e

# 色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# アイコン付きログ関数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "\n${CYAN}${BOLD}━━━ $1 ━━━${NC}\n"
}

# スクリプトのディレクトリを取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 結果追跡用変数
RESULTS=()
HAS_ERROR=false

echo ""
echo "  ╔══════════════════════════════════════════════════════════════╗"
echo "  ║  =^._.^= neko-multi-agent インストーラー                       ║"
echo "  ║     Initial Setup Script for Ubuntu / WSL                    ║"
echo "  ╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "  このスクリプトは初回セットアップ用です。"
echo "  依存関係の確認とディレクトリ構造の作成を行います。"
echo ""
echo "  インストール先: $SCRIPT_DIR"
echo ""

# ============================================================
# STEP 1: OS チェック
# ============================================================
log_step "STEP 1: システム環境チェック"

# OS情報を取得
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS_NAME=$NAME
    OS_VERSION=$VERSION_ID
    log_info "OS: $OS_NAME $OS_VERSION"
else
    OS_NAME="Unknown"
    log_warn "OS情報を取得できませんでした"
fi

# WSL チェック
if grep -qi microsoft /proc/version 2>/dev/null; then
    log_info "環境: WSL (Windows Subsystem for Linux)"
    IS_WSL=true
else
    log_info "環境: Native Linux"
    IS_WSL=false
fi

RESULTS+=("システム環境: OK")

# ============================================================
# STEP 2: tmux チェック・インストール
# ============================================================
log_step "STEP 2: tmux チェック"

if command -v tmux &> /dev/null; then
    TMUX_VERSION=$(tmux -V | awk '{print $2}')
    log_success "tmux がインストール済みです (v$TMUX_VERSION)"
    RESULTS+=("tmux: OK (v$TMUX_VERSION)")
else
    log_warn "tmux がインストールされていません"
    echo ""

    # Ubuntu/Debian系かチェック
    if command -v apt-get &> /dev/null; then
        if [ ! -t 0 ]; then
            REPLY="Y"
        else
            read -p "  tmux をインストールしますか? [Y/n]: " REPLY
        fi
        REPLY=${REPLY:-Y}
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "tmux をインストール中..."
            if ! sudo -n apt-get update -qq 2>/dev/null; then
                if ! sudo apt-get update -qq 2>/dev/null; then
                    log_error "sudo の実行に失敗しました。ターミナルから直接実行してください"
                    RESULTS+=("tmux: インストール失敗 (sudo失敗)")
                    HAS_ERROR=true
                fi
            fi

            if [ "$HAS_ERROR" != true ]; then
                if ! sudo -n apt-get install -y tmux 2>/dev/null; then
                    if ! sudo apt-get install -y tmux 2>/dev/null; then
                        log_error "tmux のインストールに失敗しました"
                        RESULTS+=("tmux: インストール失敗")
                        HAS_ERROR=true
                    fi
                fi
            fi

            if command -v tmux &> /dev/null; then
                TMUX_VERSION=$(tmux -V | awk '{print $2}')
                log_success "tmux インストール完了 (v$TMUX_VERSION)"
                RESULTS+=("tmux: インストール完了 (v$TMUX_VERSION)")
            else
                log_error "tmux のインストールに失敗しました"
                RESULTS+=("tmux: インストール失敗")
                HAS_ERROR=true
            fi
        else
            log_warn "tmux のインストールをスキップしました"
            RESULTS+=("tmux: 未インストール (スキップ)")
            HAS_ERROR=true
        fi
    else
        log_error "apt-get が見つかりません。手動で tmux をインストールしてください"
        echo ""
        echo "  インストール方法:"
        echo "    Ubuntu/Debian: sudo apt-get install tmux"
        echo "    Fedora:        sudo dnf install tmux"
        echo "    macOS:         brew install tmux"
        RESULTS+=("tmux: 未インストール (手動インストール必要)")
        HAS_ERROR=true
    fi
fi

# ============================================================
# STEP 3: Node.js チェック
# ============================================================
log_step "STEP 3: Node.js チェック"

if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v)
    log_success "Node.js がインストール済みです ($NODE_VERSION)"

    # バージョンチェック（18以上推奨）
    NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1 | tr -d 'v')
    if [ "$NODE_MAJOR" -lt 18 ]; then
        log_warn "Node.js 18以上を推奨します（現在: $NODE_VERSION）"
        RESULTS+=("Node.js: OK (v$NODE_MAJOR - 要アップグレード推奨)")
    else
        RESULTS+=("Node.js: OK ($NODE_VERSION)")
    fi
else
    log_warn "Node.js がインストールされていません"
    echo ""

    # nvm が既にインストール済みか確認
    export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
    if [ -s "$NVM_DIR/nvm.sh" ]; then
        log_info "nvm が既にインストール済みです。Node.js をセットアップ中..."
        \. "$NVM_DIR/nvm.sh"
    else
        # nvm 自動インストール
        if [ ! -t 0 ]; then
            REPLY="Y"
        else
            read -p "  Node.js (nvm経由) をインストールしますか? [Y/n]: " REPLY
        fi
        REPLY=${REPLY:-Y}
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "nvm をインストール中..."
            curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
            export NVM_DIR="$HOME/.nvm"
            [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
        else
            log_warn "Node.js のインストールをスキップしました"
            echo ""
            echo "  手動でインストールする場合:"
            echo "    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash"
            echo "    source ~/.bashrc"
            echo "    nvm install 20"
            echo ""
            RESULTS+=("Node.js: 未インストール (スキップ)")
            HAS_ERROR=true
        fi
    fi

    # nvm が利用可能なら Node.js をインストール
    if command -v nvm &> /dev/null; then
        log_info "Node.js 20 をインストール中..."
        nvm install 20 || true
        nvm use 20 || true

        if command -v node &> /dev/null; then
            NODE_VERSION=$(node -v)
            log_success "Node.js インストール完了 ($NODE_VERSION)"
            RESULTS+=("Node.js: インストール完了 ($NODE_VERSION)")
        else
            log_error "Node.js のインストールに失敗しました"
            RESULTS+=("Node.js: インストール失敗")
            HAS_ERROR=true
        fi
    elif [ "$HAS_ERROR" != true ]; then
        log_error "nvm のインストールに失敗しました"
        echo ""
        echo "  手動でインストールしてください:"
        echo "    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash"
        echo "    source ~/.bashrc"
        echo "    nvm install 20"
        echo ""
        RESULTS+=("Node.js: 未インストール (nvm失敗)")
        HAS_ERROR=true
    fi
fi

# npm チェック
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm -v)
    log_success "npm がインストール済みです (v$NPM_VERSION)"
else
    if command -v node &> /dev/null; then
        log_warn "npm が見つかりません（Node.js と一緒にインストールされるはずです）"
    fi
fi

# ============================================================
# STEP 4: Claude Code CLI チェック
# ============================================================
log_step "STEP 4: Claude Code CLI チェック"

if command -v claude &> /dev/null; then
    # バージョン取得を試みる
    CLAUDE_VERSION=$(claude --version 2>/dev/null || echo "unknown")
    log_success "Claude Code CLI がインストール済みです"
    log_info "バージョン: $CLAUDE_VERSION"
    RESULTS+=("Claude Code CLI: OK")
else
    log_warn "Claude Code CLI がインストールされていません"
    echo ""

    if command -v npm &> /dev/null; then
        echo "  インストールコマンド:"
        echo "     npm install -g @anthropic-ai/claude-code"
        echo ""
        if [ ! -t 0 ]; then
            REPLY="Y"
        else
            read -p "  今すぐインストールしますか? [Y/n]: " REPLY
        fi
        REPLY=${REPLY:-Y}
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "Claude Code CLI をインストール中..."
            npm install -g @anthropic-ai/claude-code

            if command -v claude &> /dev/null; then
                log_success "Claude Code CLI インストール完了"
                RESULTS+=("Claude Code CLI: インストール完了")
            else
                log_error "インストールに失敗しました。パスを確認してください"
                RESULTS+=("Claude Code CLI: インストール失敗")
                HAS_ERROR=true
            fi
        else
            log_warn "インストールをスキップしました"
            RESULTS+=("Claude Code CLI: 未インストール (スキップ)")
            HAS_ERROR=true
        fi
    else
        echo "  npm がインストールされていないため、先に Node.js をインストールしてください"
        RESULTS+=("Claude Code CLI: 未インストール (npm必要)")
        HAS_ERROR=true
    fi
fi

# ============================================================
# STEP 5: ディレクトリ構造作成
# ============================================================
log_step "STEP 5: ディレクトリ構造作成"

# 必要なディレクトリ一覧
DIRECTORIES=(
    "queue/tasks"
    "queue/reports"
    "queue/inbox"
    "queue/plans"
    "config"
    "status"
    "instructions"
    "logs"
    "outputs"
    "skills"
    "memory"
)

CREATED_COUNT=0
EXISTED_COUNT=0

for dir in "${DIRECTORIES[@]}"; do
    if [ ! -d "$SCRIPT_DIR/$dir" ]; then
        mkdir -p "$SCRIPT_DIR/$dir"
        log_info "作成: $dir/"
        CREATED_COUNT=$((CREATED_COUNT + 1))
    else
        EXISTED_COUNT=$((EXISTED_COUNT + 1))
    fi
done

if [ $CREATED_COUNT -gt 0 ]; then
    log_success "$CREATED_COUNT 個のディレクトリを作成しました"
fi
if [ $EXISTED_COUNT -gt 0 ]; then
    log_info "$EXISTED_COUNT 個のディレクトリは既に存在します"
fi

RESULTS+=("ディレクトリ構造: OK (作成:$CREATED_COUNT, 既存:$EXISTED_COUNT)")

# ============================================================
# STEP 6: 設定ファイル初期化
# ============================================================
log_step "STEP 6: 設定ファイル確認"

# config/settings.yaml
if [ ! -f "$SCRIPT_DIR/config/settings.yaml" ]; then
    log_info "config/settings.yaml を作成中..."
    cat > "$SCRIPT_DIR/config/settings.yaml" << EOF
# neko-multi-agent settings

# Language setting
# ja: Cat-style Japanese only (no bilingual)
# en/es/zh/ko/fr/de etc.: Cat-style Japanese + translation
language: ja

# Skill settings
skill:
  save_path: "~/.claude/skills/"
  local_path: "$SCRIPT_DIR/skills/"

# Logging
logging:
  level: info  # debug | info | warn | error
  path: "$SCRIPT_DIR/logs/"
EOF
    log_success "settings.yaml を作成しました"
else
    log_info "config/settings.yaml は既に存在します"
fi

# config/projects.yaml
if [ ! -f "$SCRIPT_DIR/config/projects.yaml" ]; then
    log_info "config/projects.yaml を作成中..."
    cat > "$SCRIPT_DIR/config/projects.yaml" << 'EOF'
projects:
  - id: sample_project
    name: "Sample Project"
    path: "/path/to/your/project"
    priority: high
    status: active

current_project: sample_project
EOF
    log_success "projects.yaml を作成しました"
else
    log_info "config/projects.yaml は既に存在します"
fi

# memory/global_context.md
if [ ! -f "$SCRIPT_DIR/memory/global_context.md" ]; then
    log_info "memory/global_context.md を作成中..."
    cat > "$SCRIPT_DIR/memory/global_context.md" << 'EOF'
# Global Context
Last updated: -

## Master's Preferences
- Prefer simple, minimal solutions. No over-engineering.
- No unnecessary comments or docstrings in code.
- Internal communication in English (token optimization).
- dashboard.md and user-facing output in Japanese.

## Quality Standards
- Code must be production-quality regardless of cat persona.
- Never mix cat-speak ("nya") into code, documents, or output files.
- Cross-review is REQUIRED by default.
- Language-specific review checklists are in config/review_criteria.yaml.

## Project Conventions
- All output files go to outputs/ directory.
- Each worker writes to its own files only (RACE-001).
- Timestamps always retrieved via date command, never guessed.
- Reports must always include skill_candidate field.

## System Notes
- 6 agents: oyabun (Opus), kashira + 4 workers (default model).
- Token optimization: instructions and internal YAML in English.
- dashboard.md is the single source of truth for the master.
EOF
    log_success "global_context.md を作成しました"
else
    log_info "memory/global_context.md は既に存在します"
fi

# memory/patterns.yaml
if [ ! -f "$SCRIPT_DIR/memory/patterns.yaml" ]; then
    echo "patterns: []" > "$SCRIPT_DIR/memory/patterns.yaml"
    log_success "patterns.yaml を作成しました"
fi

# status/agent_status.yaml
if [ ! -f "$SCRIPT_DIR/status/agent_status.yaml" ]; then
    log_info "status/agent_status.yaml を作成中..."
    cat > "$SCRIPT_DIR/status/agent_status.yaml" << 'EOF'
agents:
  kashira:
    status: idle
    current_task: null
    completed_today: 0
    errors: 0
  worker1:
    status: idle
    current_task: null
    completed_today: 0
    errors: 0
  worker2:
    status: idle
    current_task: null
    completed_today: 0
    errors: 0
  worker3:
    status: idle
    current_task: null
    completed_today: 0
    errors: 0
  worker4:
    status: idle
    current_task: null
    completed_today: 0
    errors: 0
EOF
    log_success "agent_status.yaml を作成しました"
else
    log_info "status/agent_status.yaml は既に存在します"
fi

RESULTS+=("設定ファイル: OK")

# ============================================================
# STEP 7: 足軽用タスク・レポートファイル初期化
# ============================================================
log_step "STEP 7: キューファイル初期化"

# ワーカー用タスクファイル作成
WORKER_NAMES=("1号猫" "2号犬" "3号猫" "4号猫")
for i in {1..4}; do
    TASK_FILE="$SCRIPT_DIR/queue/tasks/worker${i}.yaml"
    if [ ! -f "$TASK_FILE" ]; then
        cat > "$TASK_FILE" << EOF
# ${WORKER_NAMES[$((i-1))]}専用タスクファイル
task:
  task_id: null
  parent_cmd: null
  description: null
  target_path: null
  status: idle
  timestamp: ""
EOF
    fi
done
log_info "ワーカータスクファイル (1-4) を確認/作成しました"

# ワーカー用レポートファイル作成
for i in {1..4}; do
    REPORT_FILE="$SCRIPT_DIR/queue/reports/worker${i}_report.yaml"
    if [ ! -f "$REPORT_FILE" ]; then
        cat > "$REPORT_FILE" << EOF
worker_id: worker${i}
task_id: null
timestamp: ""
status: idle
result: null
EOF
    fi
done
log_info "ワーカーレポートファイル (1-4) を確認/作成しました"

# inbox ファイル作成
mkdir -p "$SCRIPT_DIR/queue/inbox"
for agent in kashira worker1 worker2 worker3 worker4; do
    INBOX_FILE="$SCRIPT_DIR/queue/inbox/${agent}.queue"
    if [ ! -f "$INBOX_FILE" ]; then
        touch "$INBOX_FILE"
    fi
done
log_info "inbox ファイルを確認/作成しました"

# oyabun_to_kashira.yaml 作成
if [ ! -f "$SCRIPT_DIR/queue/oyabun_to_kashira.yaml" ]; then
    echo "queue: []" > "$SCRIPT_DIR/queue/oyabun_to_kashira.yaml"
fi
log_info "コマンドキューを確認/作成しました"

RESULTS+=("キューファイル: OK")

# ============================================================
# STEP 8: スクリプト実行権限付与
# ============================================================
log_step "STEP 8: 実行権限設定"

SCRIPTS=(
    "setup.sh"
    "osanpo.sh"
    "first_setup.sh"
)

for script in "${SCRIPTS[@]}"; do
    if [ -f "$SCRIPT_DIR/$script" ]; then
        chmod +x "$SCRIPT_DIR/$script"
        log_info "$script に実行権限を付与しました"
    fi
done

RESULTS+=("実行権限: OK")

# ============================================================
# STEP 9: bashrc alias設定
# ============================================================
log_step "STEP 9: alias設定"

# alias追加対象ファイル
BASHRC_FILE="$HOME/.bashrc"

# aliasが既に存在するかチェックし、なければ追加
ALIAS_ADDED=false

# css alias (おさんぽコマンド)
if [ -f "$BASHRC_FILE" ]; then
    EXPECTED_CSS="alias css='cd \"$SCRIPT_DIR\" && ./osanpo.sh'"
    if ! grep -q "alias css=" "$BASHRC_FILE" 2>/dev/null; then
        # alias が存在しない → 新規追加
        echo "" >> "$BASHRC_FILE"
        echo "# neko-multi-agent aliases (added by first_setup.sh)" >> "$BASHRC_FILE"
        echo "$EXPECTED_CSS" >> "$BASHRC_FILE"
        log_info "alias css を追加しました（おさんぽコマンド）"
        ALIAS_ADDED=true
    elif ! grep -qF "$EXPECTED_CSS" "$BASHRC_FILE" 2>/dev/null; then
        # alias は存在するがパスが異なる → 更新
        if sed -i "s|alias css=.*|$EXPECTED_CSS|" "$BASHRC_FILE" 2>/dev/null; then
            log_info "alias css を更新しました（パス変更検出）"
        else
            log_warn "alias css の更新に失敗しました"
        fi
        ALIAS_ADDED=true
    else
        log_info "alias css は既に正しく設定されています"
    fi

    # csm alias (ディレクトリ移動)
    EXPECTED_CSM="alias csm='cd \"$SCRIPT_DIR\"'"
    if ! grep -q "alias csm=" "$BASHRC_FILE" 2>/dev/null; then
        if [ "$ALIAS_ADDED" = false ]; then
            echo "" >> "$BASHRC_FILE"
            echo "# neko-multi-agent aliases (added by first_setup.sh)" >> "$BASHRC_FILE"
        fi
        echo "$EXPECTED_CSM" >> "$BASHRC_FILE"
        log_info "alias csm を追加しました（ディレクトリ移動）"
        ALIAS_ADDED=true
    elif ! grep -qF "$EXPECTED_CSM" "$BASHRC_FILE" 2>/dev/null; then
        if sed -i "s|alias csm=.*|$EXPECTED_CSM|" "$BASHRC_FILE" 2>/dev/null; then
            log_info "alias csm を更新しました（パス変更検出）"
        else
            log_warn "alias csm の更新に失敗しました"
        fi
        ALIAS_ADDED=true
    else
        log_info "alias csm は既に正しく設定されています"
    fi
else
    log_warn "$BASHRC_FILE が見つかりません"
fi

if [ "$ALIAS_ADDED" = true ]; then
    log_success "alias設定を追加しました"
    log_warn "alias を反映するには、以下のいずれかを実行してください："
    log_info "  1. source ~/.bashrc"
    log_info "  2. PowerShell で 'wsl --shutdown' してからターミナルを開き直す"
    log_info "  ※ ウィンドウを閉じるだけでは WSL が終了しないため反映されません"
fi

RESULTS+=("alias設定: OK")

# ============================================================
# STEP 10: Memory MCP セットアップ
# ============================================================
log_step "STEP 10: Memory MCP セットアップ"

if command -v claude &> /dev/null; then
    # Memory MCP が既に設定済みか確認
    if claude mcp list 2>/dev/null | grep -q "memory"; then
        log_info "Memory MCP は既に設定済みです"
        RESULTS+=("Memory MCP: OK (設定済み)")
    else
        log_info "Memory MCP を設定中..."
        if claude mcp add memory \
            -e MEMORY_FILE_PATH="$SCRIPT_DIR/memory/oyabun_memory.jsonl" \
            -- npx -y @modelcontextprotocol/server-memory 2>/dev/null; then
            log_success "Memory MCP 設定完了"
            RESULTS+=("Memory MCP: 設定完了")
        else
            log_warn "Memory MCP の設定に失敗しました（手動で設定可能）"
            RESULTS+=("Memory MCP: 設定失敗 (手動設定可能)")
        fi
    fi
else
    log_warn "claude コマンドが見つからないため Memory MCP 設定をスキップ"
    RESULTS+=("Memory MCP: スキップ (claude未インストール)")
fi

# ============================================================
# 結果サマリー
# ============================================================
echo ""
echo "  ╔══════════════════════════════════════════════════════════════╗"
echo "  ║  📋 セットアップ結果サマリー                                  ║"
echo "  ╚══════════════════════════════════════════════════════════════╝"
echo ""

for result in "${RESULTS[@]}"; do
    if [[ $result == *"未インストール"* ]] || [[ $result == *"失敗"* ]]; then
        echo -e "  ${RED}✗${NC} $result"
    elif [[ $result == *"アップグレード"* ]] || [[ $result == *"スキップ"* ]]; then
        echo -e "  ${YELLOW}!${NC} $result"
    else
        echo -e "  ${GREEN}✓${NC} $result"
    fi
done

echo ""

if [ "$HAS_ERROR" = true ]; then
    echo "  ╔══════════════════════════════════════════════════════════════╗"
    echo "  ║  ⚠️  一部の依存関係が不足しています                           ║"
    echo "  ╚══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "  上記の警告を確認し、不足しているものをインストールしてください。"
    echo "  すべての依存関係が揃ったら、再度このスクリプトを実行して確認できます。"
else
    echo "  ╔══════════════════════════════════════════════════════════════╗"
    echo "  ║  ✅ セットアップ完了にゃ！準備万端にゃ！                      ║"
    echo "  ╚══════════════════════════════════════════════════════════════╝"
fi

echo ""
echo "  ┌──────────────────────────────────────────────────────────────┐"
echo "  │  📜 次のステップ                                             │"
echo "  └──────────────────────────────────────────────────────────────┘"
echo ""
echo "  おさんぽ（全エージェント起動）:"
echo "     ./osanpo.sh"
echo ""
echo "  オプション:"
echo "     ./osanpo.sh -s   # セットアップのみ（Claude手動起動）"
echo "     ./osanpo.sh -t   # Windows Terminalタブ展開"
echo ""
echo "  詳細は README.md を参照してください。"
echo ""
echo "  ════════════════════════════════════════════════════════════════"
echo "   =^._.^= にゃ〜！準備完了にゃ！"
echo "  ════════════════════════════════════════════════════════════════"
echo ""

# 依存関係不足の場合は exit 1 を返す（install.bat が検知できるように）
if [ "$HAS_ERROR" = true ]; then
    exit 1
fi
