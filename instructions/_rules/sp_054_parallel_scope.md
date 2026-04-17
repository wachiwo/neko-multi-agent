# sp_054: parallel_scope — 並列 task の scope 明示 3 層統合

## 背景 (2026-04-17 確定、W2+W3+W4 3 層統合案 + W1 補完)

- cmd_196 (W3 横展開 table fix) + cmd_197 (W2 色 drift) が 019/029/008 で並列合流
- W4 cmd_196 XR で F1/F2 を W3 scope creep と medium 報告 → kashira 独断で F1/F2 closed (実は W2 cmd_197 の正規変更との合流)
- 症状: file に複数 worker mtime が重なる時、reviewer の origin 特定工数が爆発
- 原因: author-side の scope 明示不足、reviewer-side の並列 task 全 scope 照合プロセス欠如

## rule (強制): 3 層統合で scope 追跡

### 層 1: kashira dispatch 時に `concurrent_touching_workers` 明記 (W2 提案)

task yaml に並列 task の存在を明示:

```yaml
task:
  task_id: subtask_XXX
  concurrent_touching_workers:
    - worker: W3
      task_id: subtask_YYY
      files: ["new/019.html", "new/029.html"]
      merge_strategy: sequential  # or exclude, kashira_arbitrate
  scope_lock:
    do_not_change:
      - "W3 作業中の files (053_海外取引一覧.html 等)"
```

`merge_strategy`:
- `sequential`: 片方完了待ち (競合回避)
- `exclude`: 明示的に touch 禁止
- `kashira_arbitrate`: 合流発生時 kashira が per-file 仲裁

### 層 2: worker report に `my_scope_files` 明記 (W3 提案)

worker が自分の責任範囲を明示:

```yaml
worker_report:
  task_id: subtask_XXX
  my_scope_files:
    - "new/019.html (target: #333→#1e293b, 2 occurrences)"
    - "new/029.html (target: same)"
  out_of_scope_touched: []  # 予期せず touch した file (通常は空)
```

XR 時は `git diff --numstat HEAD -- <my_scope_files>` で単独抽出規約。

### 層 3: per-file に `authors` / `cmd_origins` 明示 (W4 提案)

複数 worker が touch した file では worker report で per-file 内訳を明示:

```yaml
worker_report:
  per_file_diff:
    "new/019.html":
      authors: [W2, W3]      # この file の diff に含まれる author
      cmd_origins:            # 各 diff block の由来 cmd
        - cmd_196_min_width: "line 87: table-layout min-width 追加"
        - cmd_197_color: "line 142: #333→#1e293b"
      my_contribution_lines: [142]   # この worker の担当行
      others_contribution_lines: [87]
```

### 層 4: W1 補完 — 統一 template

上記 3 層を `instructions/_rules/sp_054_sp_055_unified.md` 風に統合した template を kashira が task dispatch 時に strict check。

## XR reviewer 側の義務

reviewer (W4 等) は並列合流が疑われる file (mtime が複数 worker 近接) で:

1. `concurrent_touching_workers` を task yaml から抽出
2. 各並列 task の scope を cross-reference
3. per-file diff を `authors` / `cmd_origins` で origin 分離
4. 合流 diff の算数確認 (例: W2 +2/-0 + W3 +2/-2 = +4/-2 独立計算)

乖離検出 → F1 finding。

## 関連

- **sp_041_strict**: per-file numstat 貼付、本 rule と相補的
- **sp_053 canonical_normalization**: 各 worker の scope 透明化、本 rule の基礎
- **sp_055 handoff_2in1** (後続): 同系統 handoff workflow
- **hold_files_override**: hold_files 踏み越え時の scope 明示

## 歴史

- cmd_196 F1/F2 (W4 cmd_196 XR で W3 scope creep 誤認): 1 回目
- 2026-04-17T16:30 kashira 独断 closed (W2 cmd_197 との合流と判明)
- W4 cmd_197 XR で合流 diff 算数独立裏付け (019: W3 +2/-0 + W2 +2/-2 = +4/-2 EXACT)
- 2026-04-17 retrospective 2 回目で W2+W3+W4 3 層統合案 + W1 補完 → 本 rule 明文化

## 実装メモ

- kashira が並列 dispatch 時に `concurrent_touching_workers` 自動計算 (task queue scan)
- worker は report 書き時に `my_scope_files` 必須、テンプレで空不可
- reviewer は独立 Playwright + `--numstat HEAD -- <files>` で合流 diff 算数検証
