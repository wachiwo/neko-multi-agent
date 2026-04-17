---
description: Check idle state of kashira + 4 workers via tmux capture-pane
---

# /idle-check

kashira + W1-W4 の idle 状態を一括確認する。

## 実行内容

以下を順に tmux capture-pane で取得、最終 5 行を確認:

- multiagent:0.0 (kashira)
- multiagent:0.1 (worker1)
- multiagent:0.2 (worker2)
- multiagent:0.3 (worker3)
- multiagent:0.4 (worker4)

各 pane の最終行が `❯` なら idle、それ以外は busy。

## 使い方

```
/idle-check
```

## 出力例

```
kashira: idle (❯ detected)
worker1: busy (running tool)
worker2: idle
worker3: idle
worker4: idle
```

## 注意

- polling 禁止 (F004) なので**単発実行のみ**。繰り返し呼ぶのは禁止
- idle worker に即 task 割当したい場合は kashira に指示 (直接 worker 指示は禁止)
