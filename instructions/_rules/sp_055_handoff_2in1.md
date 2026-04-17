# sp_055: handoff_2in1 — handoff protocol 体系化

## 背景 (2026-04-17 確定、全 worker 統合提案)

- cmd_195c → 195d: W2 が 008 作業中に 001/004 同種 bug 発見 → handoff report → kashira が cmd_195d で 2-in-1 指示 (3-step handoff 成立)
- cmd_197b: W4 cmd_197 XR で #4da3d9 発見 → 親分 A 案 GO → W1 (cmd_194 audit 当人=責任意識) に dispatch → 踏み越え根拠 commit msg 草案 (4-step 逆指名 handoff)
- cmd_189: W3 pre-investigation → W1 exec → W3 XR の 3 フェーズ跨ぎ、各フェーズで scope 変化 (A/B/C → A+B 採用 → child/grandchild 追加)
- 症状: scope_delta の machine-readable 記録欠如、reviewer が pre report との差分明示する protocol 未整備、hold_files 踏み越え境界線の個人判断依存

## rule (強制): handoff workflow 体系化

### ① handoff_from で scope_delta machine-readable 記録 (W3 提案)

後続 task の yaml に先行 task との差分を明示:

```yaml
task:
  task_id: subtask_189_exec_w1
  handoff_from:
    pre_task_id: subtask_189_investigation_w3
    scope_delta:
      added:
        - "child-table padding-left 0 fix"
        - "grandchild-table padding-left 0 fix"
      removed:
        - "C (form-row 横並び復元) — 親分却下で scope 外"
      unchanged:
        - "A (collapsible-content padding 0)"
        - "B (max-height:400px 削除)"
      reason: "親分独断判断 2026-04-17T16:22、C 却下 + child-table scope 内"
```

### ② audit 段階で lateral scan mandatory (W2 提案)

handoff 発生する可能性がある task (audit 系、canonical 系) で lateral scan を必須化:

- 類似 pattern の全候補を grep で列挙 (後出し禁止)
- `canonical_audit.md` の exhaustive lateral scan と連携
- audit 漏れが後続 task で発覚 → 遡及 fix コスト = sp_055 運用で防止

### ③ per-file authors / cmd_origins 明示 (W4 提案)

handoff 2-in-1 で複数 cmd 由来の変更が 1 file に入る場合、sp_054 の per-file diff 形式で明示:

```yaml
per_file_diff:
  "new/001.html":
    authors: [W2]
    cmd_origins:
      - cmd_195c: "handoff 発見: 008/001 同種 bug"
      - cmd_195d_2in1: "W2 2-in-1 fix: .btn background 追加 + header 移動"
    handoff_reason: "cmd_195c lateral scan で発見、cmd_195d 実施時にまとめて修正"
```

### ④ hold_files 踏み越え判定 matrix (W1 提案、hold_files_override.md に独立化)

別 file `hold_files_override.md` を参照。

## 3-step / 4-step handoff パターン

### 3-step (W2 確立、cmd_195c → 195d)
```
発見 (author A が task X 中に別 bug を見つける)
  → report に handoff 記載 (handoff_to: [cmd_Y])
  → kashira が cmd_Y で 2-in-1 指示 (1 task で 2 目的)
```

### 4-step (W4 実証、cmd_197 XR → cmd_197b)
```
reviewer 発見 (W4 が XR で新 drift #4da3d9 発見)
  → kashira escalation (親分判断要請)
  → 親分 GO で責任者逆指名 (cmd_194 audit 当人 W1)
  → W1 dispatch + 踏み越え根拠 commit msg 草案
```

「責任者逆指名」= audit 漏れを audit 当人が清掃する閉ループ、retrospective 学習サイクルとして優秀。

## XR reviewer 側の義務

reviewer は `handoff_from.scope_delta` を元に:

1. pre report と exec report の差分を明示 (added/removed/unchanged 各節を検証)
2. scope 拡張/縮小が kashira or 親分承認済か確認
3. hold_files 踏み越えがあれば `hold_files_override.md` の matrix で妥当性判定

承認なき scope 拡張 → F2 high finding (無断拡張)。

## 関連

- **sp_053 canonical_normalization**: handoff で変更した正規化の記録基盤
- **sp_054 parallel_scope**: 並列 task との scope 分離、本 rule と補完
- **hold_files_override.md**: 踏み越え判定 matrix
- **canonical_audit.md**: audit 段階の lateral scan mandatory

## 歴史

- cmd_195c → 195d: 3-step handoff 成立 (W2 確立、2026-04-17)
- cmd_189: W3 pre + W1 exec + W3 XR、scope 変化を task yaml で追跡できず混乱 (W3 t4 発見)
- cmd_197b: 4-step 逆指名 handoff (W4→親分→W1、2026-04-17)
- retrospective 2 回目で全 worker 統合案 → 本 rule 明文化

## 実装メモ

- `handoff_from` field を task yaml template に標準組込
- kashira が scope 拡張時に `scope_delta.added/removed` を明示的に記録
- reviewer は pre report との diff を per-file で XR report に含める
