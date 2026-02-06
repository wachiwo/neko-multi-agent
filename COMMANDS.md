# neko-multi-agent コマンド一覧

> コピペで使えるコマンドリファレンス。Windows起動からシステム操作・終了まで。

---

## 1. PowerShellからWSLに入る

Windows起動後、PowerShellまたはWindows Terminalを開く。

```powershell
# WSLに入る
wsl
```

WSLに入ったら、プロジェクトディレクトリへ移動する。

```bash
cd ~/neko-multi-agent
```

> **ヒント**: 初回セットアップ済みなら `csm` エイリアスで移動可能（後述）。

---

## 2. 初回セットアップ（最初の1回だけ）

初めて使うときに1回だけ実行する。tmux、Node.js、Claude Code CLI のインストールとディレクトリ構造の作成を行う。

```bash
chmod +x first_setup.sh
./first_setup.sh
```

### セットアップ内容
- tmux のインストール確認・自動インストール
- Node.js（nvm経由）のインストール確認・自動インストール
- Claude Code CLI のインストール確認・自動インストール
- ディレクトリ構造の作成（queue, config, status, logs 等）
- 設定ファイルの初期化（config/settings.yaml, config/projects.yaml）
- エイリアスの登録（~/.bashrc に追加）
- Memory MCP のセットアップ

### エイリアス反映

セットアップ後、エイリアスを反映するには以下のいずれかを実行する。

```bash
# 方法1: bashrcを再読み込み
source ~/.bashrc

# 方法2: WSLを再起動（PowerShellで実行）
wsl --shutdown
# → その後ターミナルを開き直す
```

---

## 3. 毎日の起動

### 全エージェント起動（通常の使い方）

```bash
./osanpo.sh
```

これにより以下が自動で行われる:
1. 既存セッションのクリーンアップ
2. 前回記録のバックアップ（logs/backup_YYYYMMDD_HHMMSS/）
3. キューファイル・ダッシュボードの初期化
4. tmuxセッション作成（oyabun + multiagent）
5. 全ペインで Claude Code 起動
6. 各エージェントに指示書を配布

### オプション

```bash
# セットアップのみ（Claude Code は手動で起動する）
./osanpo.sh -s

# 全エージェント起動 + Windows Terminal でタブを自動展開
./osanpo.sh -t

# ヘルプ表示
./osanpo.sh -h
```

### エイリアス（first_setup.sh で登録済み）

```bash
# 起動（cd + osanpo.sh 実行）
css

# プロジェクトディレクトリへ移動のみ
csm
```

> **注意**: `osanpo.sh -h` には `csst`, `css`, `csm` が別の意味で表示されるが、
> 実際に `first_setup.sh` が登録するエイリアスは上記2つ。

---

## 4. tmuxセッション操作

### セッションにアタッチ（接続）

```bash
# 親分猫のセッション（指示を出す場所）
tmux attach-session -t oyabun

# 頭猫・作業猫(犬)のセッション（作業状況を見る場所）
tmux attach-session -t multiagent
```

### セッションからデタッチ（切断・セッションは残る）

```
Ctrl+b → d
```

### セッション一覧を確認

```bash
tmux ls
```

### ペイン切替（multiagentセッション内）

multiagentセッションには5つのペインがある。

| ペイン | 役割 |
|--------|------|
| 0 | 頭猫（kashira） |
| 1 | 1号猫（worker1） |
| 2 | 2号犬（worker2） |
| 3 | 3号猫（worker3） |
| 4 | 4号猫（worker4） |

```
# 次のペインへ移動
Ctrl+b → o

# ペイン番号を指定して移動
Ctrl+b → q → 番号キー（0〜4）

# ペイン一覧表示（番号付き）
Ctrl+b → q
```

### ペインのスクロール（出力履歴を見る）

```
# スクロールモードに入る
Ctrl+b → [

# ↑/↓ または PgUp/PgDn でスクロール

# スクロールモードを抜ける
q
```

---

## 5. 親分猫への指示方法

### 基本の流れ

1. oyabunセッションにアタッチする
2. Claude Code のプロンプトに日本語で指示を入力する
3. 親分猫が頭猫→作業猫(犬)へタスクを分配する

```bash
# 1. アタッチ
tmux attach-session -t oyabun

# 2. プロンプトが表示されたら指示を入力
#    例: 「todo-appのUIをリファクタリングしてにゃ」
```

### 指示のコツ

- 何をしたいか具体的に書く
- プロジェクトのパスがあれば含める
- 親分猫が頭猫経由で作業猫(犬)に分配するので、細かい作業指示は不要

---

## 6. 進捗確認

### にゃんボード（dashboard.md）を見る

ブラウザやエディタで確認する。または:

```bash
cat ./dashboard.md
```

### にゃんボードの構成

| セクション | 内容 |
|-----------|------|
| 要対応 | ご主人様の判断が必要な事項 |
| 進行中 | 現在作業中のタスク |
| 本日の成果 | 完了したタスクの一覧 |
| スキル化候補 | 再利用可能なスキルの提案 |
| 待機中 | 待機中のタスク |
| 伺い事項 | エージェントからの質問 |

### 各エージェントの画面を直接確認

```bash
# 頭猫の画面を見る（アタッチせずに）
tmux capture-pane -t multiagent:0.0 -p | tail -20

# 作業猫1号の画面を見る
tmux capture-pane -t multiagent:0.1 -p | tail -20

# 作業猫2号（犬）の画面を見る
tmux capture-pane -t multiagent:0.2 -p | tail -20

# 作業猫3号の画面を見る
tmux capture-pane -t multiagent:0.3 -p | tail -20

# 作業猫4号の画面を見る
tmux capture-pane -t multiagent:0.4 -p | tail -20

# 親分猫の画面を見る
tmux capture-pane -t oyabun -p | tail -20
```

---

## 7. 終了・再起動

### セッションを終了する

```bash
# 全セッションを終了
tmux kill-session -t multiagent
tmux kill-session -t oyabun

# または全tmuxセッションを一括終了
tmux kill-server
```

### 再起動する

```bash
# 終了後、再度起動スクリプトを実行
./osanpo.sh
```

> 起動スクリプトは既存セッションを自動でクリーンアップするので、
> 手動で終了せずにそのまま再実行しても問題ない。

### 特定のエージェントだけ再起動

```bash
# 例: 頭猫（pane 0）だけ再起動
# 1. multiagentセッションにアタッチ
tmux attach-session -t multiagent
# 2. Ctrl+b → q → 0 でpane 0に移動
# 3. Claude Code が停止していたら再起動
claude --dangerously-skip-permissions
```

---

## 8. トラブルシューティング

### tmuxセッションが見つからない

```bash
# セッション一覧を確認
tmux ls

# セッションがなければ再起動
./osanpo.sh
```

### Claude Code が応答しない（特定のペイン）

```bash
# 対象ペインの状態を確認
tmux capture-pane -t multiagent:0.1 -p | tail -30

# 必要に応じてペインで Ctrl+C してから再起動
tmux send-keys -t multiagent:0.1 C-c
tmux send-keys -t multiagent:0.1 "claude --dangerously-skip-permissions" Enter
```

### claude コマンドが見つからない

```bash
# Node.js / npm の確認
node -v
npm -v

# Claude Code CLI をインストール
npm install -g @anthropic-ai/claude-code

# または first_setup.sh を再実行
./first_setup.sh
```

### エイリアスが効かない

```bash
# bashrc を再読み込み
source ~/.bashrc

# 登録されているか確認
grep "alias cs" ~/.bashrc
```

### ログ・バックアップの場所

```bash
# 前回セッションのバックアップ
ls ./logs/

# キューファイル（タスク・報告）
ls ./queue/tasks/
ls ./queue/reports/
```

### WSLが重い・固まった

```powershell
# PowerShellで WSL を再起動
wsl --shutdown
# → ターミナルを開き直して wsl を実行
```
