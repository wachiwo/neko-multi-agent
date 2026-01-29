# neko-multi-agent

<div align="center">

**Claude Code マルチエージェント統率システム**

*コマンド1つで、6体のAI猫エージェントが並列稼働*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code](https://img.shields.io/badge/Claude-Code-blueviolet)](https://claude.ai)
[![tmux](https://img.shields.io/badge/tmux-required-green)](https://github.com/tmux/tmux)

[English](README.md) | [日本語](README_ja.md)

</div>

---

## これは何？

**neko-multi-agent** は、複数の Claude Code インスタンスを同時に実行し、猫チームとして統率するシステムです（1匹だけ自分を猫だと思っている犬がいます）。

**なぜ使うのか？**
- 1つの命令で、4体のAIワーカーが並列で実行
- 待ち時間なし - タスクがバックグラウンドで実行中も次の命令を出せる
- AIがセッションを跨いであなたの好みを記憶（Memory MCP）
- ダッシュボードでリアルタイム進捗確認

```
      あなた（ご主人様）
           │
           ▼ 命令を出す
    ┌─────────────┐
    │   OYABUN     │  ← 親分猫：命令を受け取り、番頭猫に委譲
    │  (親分猫)    │
    └──────┬──────┘
           │ YAMLファイル + tmux
    ┌──────▼──────┐
    │   BANTOU     │  ← 番頭猫：タスクを作業猫(犬)に分配
    │  (番頭猫)    │
    └──────┬──────┘
           │
    ┌──┬──┼──┬──┐
    │1 │2 │3 │4 │  ← 4体の作業猫(犬)が並列実行
    └──┴──┴──┴──┘
```

### 作業猫(犬)の個性

| 名前 | ID | 口調 | 特徴 |
|------|-----|------|------|
| 1号猫 | worker1 | 真面目・丁寧「かしこまりましたにゃ」 | 礼儀正しくお仕事 |
| 2号犬 | worker2 | 「にゃわん！」混在 | 猫だと思ってる犬 |
| 3号猫 | worker3 | のんびり「にゃ〜ん」 | マイペースだけど確実 |
| 4号猫 | worker4 | クール「…了解にゃ」 | 無口だけど優秀 |

---

## クイックスタート

### Windowsユーザー（最も一般的）

<table>
<tr>
<td width="60">

**Step 1**

</td>
<td>

**リポジトリをダウンロード**

[ZIPダウンロード](https://github.com/wachiwo/neko-multi-agent/archive/refs/heads/main.zip) して `C:\tools\neko-multi-agent` に展開

*または git を使用:* `git clone https://github.com/wachiwo/neko-multi-agent.git C:\tools\neko-multi-agent`

</td>
</tr>
<tr>
<td>

**Step 2**

</td>
<td>

**`install.bat` を実行**

右クリック→「管理者として実行」（WSL2が未インストールの場合）。WSL2 + Ubuntu をセットアップします。

</td>
</tr>
<tr>
<td>

**Step 3**

</td>
<td>

**Ubuntu を開いて以下を実行**（初回のみ）

```bash
cd /mnt/c/tools/neko-multi-agent
./first_setup.sh
```

</td>
</tr>
<tr>
<td>

**Step 4**

</td>
<td>

**出陣！**

```bash
./shutsujin_departure.sh
```

</td>
</tr>
</table>

#### 毎日の起動（初回セットアップ後）

**Ubuntuターミナル**（WSL）を開いて実行：

```bash
cd /mnt/c/tools/neko-multi-agent
./shutsujin_departure.sh
```

---

<details>
<summary><b>Linux / Mac ユーザー</b>（クリックで展開）</summary>

### 初回セットアップ

```bash
# 1. リポジトリをクローン
git clone https://github.com/wachiwo/neko-multi-agent.git ~/neko-multi-agent
cd ~/neko-multi-agent

# 2. スクリプトに実行権限を付与
chmod +x *.sh

# 3. 初回セットアップを実行
./first_setup.sh
```

### 毎日の起動

```bash
cd ~/neko-multi-agent
./shutsujin_departure.sh
```

</details>

---

<details>
<summary><b>WSL2とは？なぜ必要？</b>（クリックで展開）</summary>

### WSL2について

**WSL2（Windows Subsystem for Linux）** は、Windows内でLinuxを実行できる機能です。このシステムは `tmux`（Linuxツール）を使って複数のAIエージェントを管理するため、WindowsではWSL2が必要です。

### WSL2がまだない場合

問題ありません！`install.bat` を実行すると：
1. WSL2がインストールされているかチェック（なければ自動インストール）
2. Ubuntuがインストールされているかチェック（なければ自動インストール）
3. 次のステップ（`first_setup.sh` の実行方法）を案内

**クイックインストールコマンド**（PowerShellを管理者として実行）：
```powershell
wsl --install
```

その後、コンピュータを再起動して `install.bat` を再実行してください。

</details>

---

<details>
<summary><b>スクリプトリファレンス</b>（クリックで展開）</summary>

| スクリプト | 用途 | 実行タイミング |
|-----------|------|---------------|
| `install.bat` | Windows: WSL2 + Ubuntu のセットアップ | 初回のみ |
| `first_setup.sh` | tmux、Node.js、Claude Code CLI をインストール + Memory MCP設定 | 初回のみ |
| `shutsujin_departure.sh` | tmuxセッション作成 + Claude Code起動 + 指示書読み込み | 毎日 |

### `install.bat` が自動で行うこと：
- WSL2がインストールされているかチェック（未インストールなら案内）
- Ubuntuがインストールされているかチェック（未インストールなら案内）
- 次のステップ（`first_setup.sh` の実行方法）を案内

### `shutsujin_departure.sh` が行うこと：
- tmuxセッションを作成（oyabun + multiagent）
- 全エージェントでClaude Codeを起動
- 各エージェントに指示書を自動読み込み
- キューファイルをリセットして新しい状態に

**実行後、全エージェントが即座にコマンドを受け付ける準備完了！**

</details>

---

<details>
<summary><b>必要環境（手動セットアップの場合）</b>（クリックで展開）</summary>

依存関係を手動でインストールする場合：

| 要件 | インストール方法 | 備考 |
|------|-----------------|------|
| WSL2 + Ubuntu | PowerShellで `wsl --install` | Windowsのみ |
| tmux | `sudo apt install tmux` | ターミナルマルチプレクサ |
| Node.js v20+ | `nvm install 20` | Claude Code CLIに必要 |
| Claude Code CLI | `npm install -g @anthropic-ai/claude-code` | Anthropic公式CLI |

</details>

---

### セットアップ後の状態

起動スクリプトを実行すると、**6体のAIエージェント**が自動起動します：

| エージェント | 役割 | 数 |
|-------------|------|-----|
| 親分猫（Oyabun） | 総大将 - ご主人様の命令を受ける | 1 |
| 番頭猫（Bantou） | 管理者 - タスクを分配・コードレビュー | 1 |
| 作業猫(犬) | ワーカー - 並列でタスク実行 | 4 |

tmuxセッションが作成されます：
- `oyabun` - ここに接続してコマンドを出す
- `multiagent` - 番頭猫 + 作業猫(犬)4体が稼働（5ペイン）

---

## 基本的な使い方

### Step 1: 親分猫に接続

`shutsujin_departure.sh` 実行後、全エージェントが自動的に指示書を読み込み、作業準備完了となります。

新しいターミナルを開いて親分猫に接続：

```bash
tmux attach-session -t oyabun
```

### Step 2: 最初の命令を出す

親分猫は既に初期化済み！そのまま命令を出せます：

```
JavaScriptフレームワーク上位5つを調査して比較表を作成してにゃ
```

親分猫は：
1. タスクをYAMLファイルに書き込む
2. 番頭猫に通知
3. 即座にあなたに制御を返す（待つ必要なし！）

その間、番頭猫はタスクを作業猫(犬)に分配し、並列実行します。

### Step 3: 進捗を確認

エディタで `dashboard.md` を開いてリアルタイム状況を確認：

```markdown
## 進行中
| ワーカー | タスク | 状態 |
|----------|--------|------|
| 1号猫 | React調査 | 実行中 |
| 2号犬 | Vue調査 | 実行中 |
| 3号猫 | Angular調査 | 完了 |
```

---

## 主な特徴

### 1. 並列実行

1つの命令で最大4つの並列タスクを生成：

```
あなた: 「4つのMCPサーバを調査してにゃ」
  -> 4体の作業猫(犬)が同時に調査開始
  -> 数時間ではなく数分で結果が出る
```

### 2. ノンブロッキングワークフロー

親分猫は即座に委譲して、あなたに制御を返します：

```
あなた: 命令 -> 親分猫: 委譲 -> あなた: 次の命令をすぐ出せる
                                    |
                    ワーカー: バックグラウンドで実行
                                    |
                    ダッシュボード: 結果を表示
```

### 3. セッション間記憶（Memory MCP）

AIがあなたの好みを記憶します：

```
セッション1: 「シンプルな方法が好き」と伝える
            -> Memory MCPに保存

セッション2: 起動時にAIがメモリを読み込む
            -> 複雑な方法を提案しなくなる
```

### 4. イベント駆動（ポーリングなし）

エージェントはYAMLファイルで通信し、tmux send-keysで互いを起こします。
**ポーリングループでAPIコールを浪費しません。**

### 5. スクリーンショット連携

```
# config/settings.yaml でスクショフォルダを設定
screenshot:
  path: "/mnt/c/Users/あなたの名前/Pictures/Screenshots"

# 親分猫に伝えるだけ:
あなた: 「最新のスクショを見てにゃ」
-> AIが即座にスクリーンショットを読み取って分析
```

**Windowsのコツ:** `Win + Shift + S` でスクショが撮れます。

### 6. エラー自動リトライ

作業猫(犬)はエラー時に最大3回自動リトライ（毎回アプローチを変える）。3回失敗したら番頭猫が別のワーカーに再割当。

### 7. コードレビュー

番頭猫がコード成果物をレビュー（構文・セキュリティ・パフォーマンス・可読性）。問題があればフィードバック付きで修正指示。

### 8. 学習機能

成功/失敗パターンを `memory/patterns.yaml` に蓄積。作業猫(犬)はタスク開始前にパターンを参照して過去の失敗を回避。

---

### モデル設定

| エージェント | モデル | 思考モード | 理由 |
|-------------|--------|----------|------|
| 親分猫 | Opus | 無効 | 委譲とダッシュボード更新に深い推論は不要 |
| 番頭猫 | デフォルト | 有効 | タスク分配には慎重な判断が必要 |
| 作業猫(犬) | デフォルト | 有効 | 実装作業にはフル機能が必要 |

---

## 設計思想

### なぜ階層構造（親分猫→番頭猫→作業猫）なのか

1. **即時応答**: 親分猫は即座に委譲してご主人様に制御を返す
2. **並列実行**: 番頭猫が複数の作業猫(犬)に同時にタスクを分配
3. **関心の分離**: 親分猫が「何を」、番頭猫が「誰に」を決める
4. **割り込み防止**: 作業猫(犬)はdashboard.md更新のみで報告（send-keys禁止）。ご主人様の入力中に割り込まない

### なぜ YAML + send-keys なのか

1. **ポーリング不要**: イベント駆動でAPIコストを削減
2. **状態の永続化**: YAMLファイルでタスク状態を追跡可能
3. **デバッグ容易**: 人間がYAMLを直接読んで状況把握できる
4. **競合回避**: 各作業猫(犬)に専用ファイルを割り当て

### なぜ dashboard.md は番頭猫のみが更新するのか

1. **単一更新者**: 競合を防ぐため、更新責任者を1人に限定
2. **情報集約**: 番頭猫は全作業猫(犬)の報告を受ける立場なので全体像を把握
3. **割り込み防止**: 親分猫が更新すると、ご主人様の入力中に割り込む恐れあり

---

## スキル

初期状態ではスキルはありません。
運用中にダッシュボード（dashboard.md）の「スキル化候補」から承認して増やしていきます。

### スキルの思想

**1. スキルはコミット対象外**

`.claude/commands/` 配下のスキルはリポジトリにコミットしない設計。理由：
- 各ユーザの業務・ワークフローは異なる
- 汎用的なスキルを押し付けるのではなく、ユーザが自分に必要なスキルを育てていく

**2. スキル取得の手順**

```
作業猫(犬)が作業中にパターンを発見
    |
dashboard.md の「スキル化候補」に上がる
    |
ご主人様が内容を確認
    |
承認すれば番頭猫に指示してスキルを作成
```

---

## MCPセットアップガイド

MCP（Model Context Protocol）サーバはClaudeの機能を拡張します：

```bash
# 1. Notion - Notionワークスペースに接続
claude mcp add notion -e NOTION_TOKEN=your_token_here -- npx -y @notionhq/notion-mcp-server

# 2. Playwright - ブラウザ自動化
claude mcp add playwright -- npx @playwright/mcp@latest

# 3. GitHub - リポジトリ操作
claude mcp add github -e GITHUB_PERSONAL_ACCESS_TOKEN=your_pat_here -- npx -y @modelcontextprotocol/server-github

# 4. Sequential Thinking - 複雑な問題を段階的に思考
claude mcp add sequential-thinking -- npx -y @modelcontextprotocol/server-sequential-thinking

# 5. Memory - セッション間の長期記憶（first_setup.sh で自動設定済み）
claude mcp add memory -e MEMORY_FILE_PATH="$PWD/memory/neko_memory.jsonl" -- npx -y @modelcontextprotocol/server-memory
```

`claude mcp list` で確認できます。

---

## 実用例

### 例1: 調査タスク

```
あなた: 「AIコーディングアシスタント上位4つを調査して比較してにゃ」

実行される処理:
1. 親分猫が番頭猫に委譲
2. 番頭猫が割り当て:
   - 1号猫: GitHub Copilotを調査
   - 2号犬: Cursorを調査
   - 3号猫: Claude Codeを調査
   - 4号猫: Codeiumを調査
3. 4体が同時に調査
4. 結果がdashboard.mdに集約
```

### 例2: Webアプリ開発

```
あなた: 「Flaskでユーザー認証付きWebアプリを作ってにゃ」

実行される処理:
1. 番頭猫がサブタスクに分割:
   - 1号猫: DBスキーマ + モデル
   - 2号犬: APIルート + 認証
   - 3号猫: フロントエンドテンプレート + CSS
   - 4号猫: テスト + ドキュメント
2. 番頭猫が各ワーカーの成果物をレビュー
3. 結果を集約して報告
```

---

## 設定

### 言語設定

`config/settings.yaml` を編集：

```yaml
language: ja   # 日本語のみ（猫語）
language: en   # 猫語 + 英訳併記
```

---

## 上級者向け

<details>
<summary><b>スクリプトアーキテクチャ</b>（クリックで展開）</summary>

```
+---------------------------------------------------------------------+
|                      初回セットアップ（1回だけ実行）                   |
+---------------------------------------------------------------------+
|                                                                     |
|  install.bat (Windows)                                              |
|      |                                                              |
|      +-- WSL2のチェック/インストール案内                              |
|      +-- Ubuntuのチェック/インストール案内                            |
|                                                                     |
|  first_setup.sh (Ubuntu/WSLで手動実行)                               |
|      |                                                              |
|      +-- tmuxのチェック/インストール                                  |
|      +-- Node.js v20+のチェック/インストール (nvm経由)                |
|      +-- Claude Code CLIのチェック/インストール                      |
|      +-- Memory MCPサーバの設定                                      |
|                                                                     |
+---------------------------------------------------------------------+
|                      毎日の起動（毎日実行）                           |
+---------------------------------------------------------------------+
|                                                                     |
|  shutsujin_departure.sh                                             |
|      |                                                              |
|      +-> tmuxセッションを作成                                       |
|      |         - "oyabun"セッション（1ペイン）                       |
|      |         - "multiagent"セッション（5ペイン）                   |
|      |                                                              |
|      +-> キューファイルとダッシュボードをリセット                     |
|      |                                                              |
|      +-> 全エージェントでClaude Codeを起動                          |
|                                                                     |
+---------------------------------------------------------------------+
```

</details>

<details>
<summary><b>shutsujin_departure.sh オプション</b>（クリックで展開）</summary>

```bash
# デフォルト: フル起動（tmuxセッション + Claude Code起動）
./shutsujin_departure.sh

# セッションセットアップのみ（Claude Code起動なし）
./shutsujin_departure.sh -s

# フル起動 + Windows Terminalタブを開く
./shutsujin_departure.sh -t

# ヘルプを表示
./shutsujin_departure.sh -h
```

</details>

<details>
<summary><b>よく使うワークフロー</b>（クリックで展開）</summary>

**通常の毎日の使用：**
```bash
./shutsujin_departure.sh          # 全て起動
tmux attach-session -t oyabun     # 接続してコマンドを出す
```

**デバッグモード（手動制御）：**
```bash
./shutsujin_departure.sh -s       # セッションのみ作成

# 特定のエージェントでClaude Codeを手動起動
tmux send-keys -t oyabun:0 'claude --dangerously-skip-permissions' Enter
tmux send-keys -t multiagent:0.0 'claude --dangerously-skip-permissions' Enter
```

**クラッシュ後の再起動：**
```bash
# 既存セッションを終了
tmux kill-session -t oyabun
tmux kill-session -t multiagent

# 新しく起動
./shutsujin_departure.sh
```

</details>

<details>
<summary><b>便利なエイリアス</b>（クリックで展開）</summary>

`first_setup.sh` を実行すると、以下のエイリアスが `~/.bashrc` に自動追加されます：

```bash
alias css='cd ~/neko-multi-agent && ./shutsujin_departure.sh'  # 移動+出陣
alias csm='cd ~/neko-multi-agent'                              # ディレクトリ移動のみ
```

※ エイリアスを反映するには `source ~/.bashrc` を実行するか、PowerShellで `wsl --shutdown` してからターミナルを開き直してください。

</details>

---

## ファイル構成

<details>
<summary><b>クリックでファイル構成を展開</b></summary>

```
neko-multi-agent/
|
|  +------------------- セットアップスクリプト -------------------+
+-- install.bat               # Windows: 初回セットアップ
+-- first_setup.sh            # Ubuntu/Mac: 初回セットアップ
+-- shutsujin_departure.sh    # 毎日の起動（指示書自動読み込み）
|  +-------------------------------------------------------------+
|
+-- instructions/             # エージェント指示書
|   +-- oyabun.md             # 親分猫の指示書
|   +-- bantou.md             # 番頭猫の指示書
|   +-- 1gou-neko.md          # 1号猫の指示書
|   +-- 2gou-inu.md           # 2号犬の指示書
|   +-- 3gou-neko.md          # 3号猫の指示書
|   +-- 4gou-neko.md          # 4号猫の指示書
|
+-- config/
|   +-- settings.yaml         # 言語その他の設定
|
+-- queue/                    # 通信ファイル
|   +-- oyabun_to_bantou.yaml # 親分猫から番頭猫へのコマンド
|   +-- tasks/                # 各ワーカーのタスクファイル
|   +-- reports/              # ワーカーレポート
|
+-- memory/                   # Memory MCP + 学習パターン
+-- dashboard.md              # リアルタイム状況一覧（にゃんボード）
+-- CLAUDE.md                 # Claude用プロジェクトコンテキスト
```

</details>

---

## トラブルシューティング

<details>
<summary><b>MCPツールが動作しない？</b></summary>

MCPツールは「遅延ロード」方式で、最初にロードが必要です：

```
# 間違い - ツールがロードされていない
mcp__memory__read_graph()  <- エラー！

# 正しい - 先にロード
ToolSearch("select:mcp__memory__read_graph")
mcp__memory__read_graph()  <- 動作！
```

</details>

<details>
<summary><b>エージェントが権限を求めてくる？</b></summary>

`--dangerously-skip-permissions` 付きで起動していることを確認：

```bash
claude --dangerously-skip-permissions
```

</details>

<details>
<summary><b>ワーカーが停止している？</b></summary>

ワーカーのペインを確認：
```bash
tmux attach-session -t multiagent
# Ctrl+B の後 q でペイン番号表示、番号を押して移動
```

</details>

---

## tmux クイックリファレンス

| コマンド | 説明 |
|----------|------|
| `tmux attach -t oyabun` | 親分猫に接続 |
| `tmux attach -t multiagent` | ワーカーに接続 |
| `Ctrl+B` の後 `q` → `0-4` | ペイン間を切り替え |
| `Ctrl+B` の後 `d` | デタッチ（実行継続） |
| `tmux kill-session -t oyabun` | 親分猫セッションを停止 |
| `tmux kill-session -t multiagent` | ワーカーセッションを停止 |

---

## クレジット

[Claude-Code-Communication](https://github.com/Akira-Papa/Claude-Code-Communication) by Akira-Papa をベースに開発。

---

## ライセンス

MIT License - 詳細は [LICENSE](LICENSE) を参照。

---

<div align="center">

**猫チームを統率せよ。より速く構築せよ。**

</div>
