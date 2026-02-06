# neko-multi-agent セットアップガイド

Windows PCに猫エージェントシステムをゼロから導入する手順です。

## 前提条件

- Windows 10/11 のPC
- Claudeのアカウント（Max $200プラン推奨。Pro $20プランでも動きますがトークン制限に注意）
- インターネット接続

## セットアップ手順

### Step 1: WSLインストール

PowerShellを **管理者として実行** し、以下を入力：

```powershell
wsl --install
```

完了後、**PCを再起動**してください。

再起動後、Ubuntuが自動で開きます。Linuxのユーザー名とパスワードを設定してください。
（パスワードは入力しても画面に表示されません。そのまま打ってEnterでOKです）

### Step 2: Node.jsインストール

Ubuntuのターミナルで以下を順番に実行：

```bash
sudo apt-get update && sudo apt-get install -y curl
```

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
```

**ターミナルを一度閉じて開き直してから**、以下を実行：

```bash
nvm install 22
```

確認：

```bash
node --version
```

`v22.x.x` と表示されればOKです。

### Step 3: tmux・gitインストール

```bash
sudo apt-get install -y tmux git
```

### Step 4: Claude Codeインストール

```bash
npm install -g @anthropic-ai/claude-code
```

### Step 5: Claude Codeにログイン

```bash
claude
```

初回起動で認証画面が出ます：
1. 表示されるURLをコピーしてブラウザで開く
2. Claudeアカウントでログイン
3. ブラウザに表示される認証コードをコピー
4. ターミナルの `paste code here` に貼り付けてEnter

ログインできたら `/exit` で一旦終了します。

### Step 6: リポジトリをクローン

```bash
cd ~ && git clone https://github.com/wachiwo/neko-multi-agent.git
```

### Step 7: gitのユーザー設定

```bash
git config --global user.name "あなたの名前"
git config --global user.email "あなたのメールアドレス"
```

### Step 8: 初回セットアップスクリプト実行

```bash
cd ~/neko-multi-agent
bash first_setup.sh
```

ディレクトリ構造の作成やMemory MCPの設定を自動で行います。

### Step 9: おさんぽ！（猫チーム起動）

```bash
bash osanpo.sh
```

猫チーム全員が自動で起動します。

### Step 10: 親分猫に接続

```bash
tmux attach-session -t oyabun
```

これで親分猫に命令を出せる状態になります。

---

## 毎日の起動手順（2回目以降）

1. Windowsのスタートメニューから **「Ubuntu」** を開く
2. 以下を実行：

```bash
cd ~/neko-multi-agent && bash osanpo.sh
```

3. 親分猫に接続：

```bash
tmux attach-session -t oyabun
```

これだけです。

---

## よく使う操作

| やりたいこと | コマンド |
|---|---|
| 親分猫に接続 | `tmux attach-session -t oyabun` |
| 頭猫・作業猫を確認 | `tmux attach-session -t multiagent` |
| tmuxから抜ける（猫は動いたまま） | `Ctrl+B` を押した後 `D` |
| ペインを切り替える | `Ctrl+B` を押した後 `Q` → 数字キー |
| 猫チーム全員停止 | `tmux kill-server` |

**ポイント**: tmuxから抜けても猫たちはバックグラウンドで動き続けます。再接続はいつでもできます。

---

## 使い方

親分猫に接続したら、日本語で命令を出すだけです：

```
JavaScriptフレームワーク上位5つを調査して比較表を作成して
```

親分猫が頭猫に指示を出し、作業猫たちが並列で実行します。
進捗は `dashboard.md` で確認できます。

---

## 注意事項

- **$20プラン** の場合、API利用量に制限があります。全6エージェント同時稼働は消費が大きいので、軽いタスクから試してください。**$200 Maxプラン推奨**。
- 個人データ（作業履歴、メモリ、設定など）はgitに含まれないため、他の人と共有されることはありません。

---

## トラブルシューティング

### `claude` コマンドが見つからない

ターミナルを開き直してから再実行してください：

```bash
source ~/.bashrc
claude --version
```

### tmuxセッションがおかしくなった

全セッションを終了して再起動：

```bash
tmux kill-server
cd ~/neko-multi-agent && bash osanpo.sh
```

### Claude Codeの認証が切れた

```bash
claude
```

で再ログインしてから `/exit` で抜け、起動スクリプトを実行し直してください。
