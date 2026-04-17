---
description: Template-generate new cmd dispatch to queue/oyabun_to_kashira.yaml
argument-hint: <cmd_id> <short description>
---

# /dispatch

新 cmd を定型テンプレで `queue/oyabun_to_kashira.yaml` に追記する。

## Arguments

$ARGUMENTS = cmd_id + 短い説明 (例: `cmd_198 020_発注明細 の検索ボタン紺色化`)

## 実行内容

1. `queue/oyabun_to_kashira.yaml` に以下の YAML block を append:

```yaml
  - id: <cmd_id>
    timestamp: "<YYYY-MM-DDTHH:MM:SS>"
    command: "<description>"
    project: dimco-prototype
    priority: medium
    cross_review: required
    status: approved

    goshujinsama_directive: |
      <指示引用>

    target_file: "<new/XXX.html>"

    approach:
      - "step 1: <...>"

    scope_lock:
      - "指示範囲のみ"
      - "文言変更禁止"

    autonomy:
      granted: full

    effort: <S/M/L>
    assign: "kashira 裁量"

    completion_criteria:
      - "<criteria>"
      - "cross-review: reviewer != author"

    report_protocol:
      method: "inbox + send-keys 両方"
```

2. 送信 2 件:
   - inbox pairing: `echo "<ts>|oyabun|cmd_dispatch|<cmd_id>" >> queue/inbox/kashira.queue`
   - tmux send-keys 2-call: 【親分→kashira】<cmd_id> dispatch にゃ

## 注意

- goshujinsama の指示文は必ずそのまま `goshujinsama_directive` に貼る (改変禁止)
- priority は high/medium/low から選択、scope_lock は必須
- effort 見積もりは S (<30min) / M (30-90min) / L (90min+) の目安
