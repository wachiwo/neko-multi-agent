---
description: Trigger retrospective synthesis for a completed cmd
argument-hint: <cmd_id>
---

# /retrospective

完遂 cmd の振り返り synthesis を発火する。

## Arguments

$ARGUMENTS = cmd_id (例: `cmd_186_phase3`)

## 実行内容

`instructions/_rules/retrospective.md` の 5 分プロトコルに従って:

1. **参加者**: kashira + 関与 worker 全員
2. **3 質問** (各 worker が short answer):
   - `went_well`: 何がうまくいったか
   - `went_poorly`: 何が難しかった / 詰まったか
   - `next_time`: 次同じタスクやるなら何を変えるか
3. **synthesis** (kashira が取りまとめ):
   - `patterns_to_save`: memory/patterns.yaml へ転写候補
   - `process_improvements`: CLAUDE.md / instructions 反映候補
   - `team_mood`: 概況
   - `handoff_to_oyabun`: 親分に伝えたい事
4. 結果を `queue/reports/retrospective_<cmd_id>.yaml` に出力
5. inbox + send-keys で oyabun に通知

## 使い方

```
/retrospective cmd_186_phase3
```

## トリガ条件

以下のいずれかで発火推奨:
- 大型 cmd (5 subtask 超) 完遂時
- 事故・修正が発生した cmd 完遂時
- 新パターン (skill 候補 / rule 候補) が浮上したとき

## 注意

- 「感想文」にしない — 具体的 pattern / process を抽出
- blame-free: 原因追及はプロセスに対して、個人に対してではない
