---
description: Check idle state of kashira + 4 workers via deep tmux capture (30-line scrollback)
---

# /idle-check

kashira + W1-W4 の idle 状態を一括確認する。

## 実行内容

各 pane を **30 行 scrollback** で取得 (tail 5 だと pane スクロール位置で誤判定しやすい):

```bash
for pane in multiagent:0.0 multiagent:0.1 multiagent:0.2 multiagent:0.3 multiagent:0.4; do
  echo "=== $pane ==="
  tmux capture-pane -t "$pane" -p -S -30 2>/dev/null | tail -12
done
```

**判定**:
- 最後の非空白行に `❯` が単独で残っている → idle
- `●` (spinner) / `Running...` / tool 出力 / `⏵⏵` (permission prompt) → busy
- `↓ N lines below` / `/exit` など → scroll されてて判定不能 → `tmux send-keys -t <pane> q` で最下端に戻す (F004 に違反しないよう単発のみ)

## 使い方

```
/idle-check
```

## 出力例

```
=== multiagent:0.0 ===
[last 12 lines...]
❯
──────────
kashira: idle

=== multiagent:0.1 ===
[last 12 lines...]
● Running Bash (120s · ↓ 1.2k tokens · esc to interrupt)
worker1: busy (Bash tool running)
```

## 注意

- **polling 禁止 (F004)** なので単発実行のみ。loop 禁止
- idle worker に即 task 割当したい場合は kashira に指示 (直接 worker 指示は禁止)
- spinner 絵文字は実行中サイン、`❯` 単独が真の idle
- **false idle 回避**: 直前 30s 以内に send-keys をしてる場合、worker はまだ処理開始してない可能性 → そのターンは idle 判定しない

## 関連

- 実装根拠: `instructions/_rules/send_keys_protocol.md` § idle detection
- 誤判定事例: tail -5 だと長い出力の途中で `❯` 以外の記号が最下行になり busy 誤判定、逆に scroll 途中だと古い `❯` を拾って idle 誤判定
