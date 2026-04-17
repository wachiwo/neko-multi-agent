# sp_041 strict: diff-based XR per-file numstat 直接貼付必須

## 背景 (2026-04-17 確定)

- W2 で **3 回連続再発** (cmd_188 / cmd_195efg / cmd_197)
- 症状: report の `diff_stat` に per-file の ins/del を breakdown で記載しているが、`git diff --numstat` の raw 出力と乖離
  - 例: 申告 `"012_.html": { changes: minor }` vs 実際 `012_.html: 3 insertions, 8 deletions`
  - 例: 申告 `total_net: +192 -59` vs numstat raw `189 -57` (算数一致 false)
- 原因: worker が内部集計値を書いているが、機械確認しにくく、XR reviewer の精度検証コストが高い

## rule (強制)

### 1. per-file numstat を★生データで★貼付必須

worker report の `diff_stat` には必ず以下形式で **`git diff --numstat` の raw 出力** をそのまま貼付する:

```yaml
diff_stat:
  numstat_raw: |
    4	2	new/012_累計得意先上位分析表（粗利）.html
    3	1	new/010_売上予測表.html
    3	1	new/006_受注売上入金管理.html
  total_ins: 10
  total_del: 4
  net: "+6"
  file_count: 3
  anomaly_threshold: 40
  anomaly_triggered: false
```

### 2. 要素

- `numstat_raw`: `git diff --numstat` の出力を **コピペ貼付** (集計値を手書きしない)
- `total_ins` / `total_del` / `net`: numstat_raw から機械算出した集計値 (worker が電卓不要、`awk '{s+=$1} END {print s}'` 等で集計)
- `file_count`: 変更 file 数 (numstat_raw の行数)
- `anomaly_threshold`: 単 file で超過したら anomaly flag を立てる閾値 (デフォルト 40 行 ins+del)
- `anomaly_triggered`: 1 file でも閾値超えたら true

### 3. XR reviewer 側の義務

reviewer (W4 等) は worker report の `numstat_raw` を信じず、独立で `git diff --numstat` を実行して差分 0 確認:

```bash
cd /mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype
git diff --numstat HEAD -- new/ | ...  # target file だけに絞る
```

raw 値が worker 申告と 1 行でも異なる → F1 medium finding (sp_041 違反、報告精度乖離)。

## batch task の場合

複数 file を 1 task で扱う場合、**全 file の numstat を 1 block で貼付**:

```yaml
diff_stat:
  numstat_raw: |
    3	1	new/006_受注売上入金管理.html
    4	2	new/010_売上予測表.html
    2	1	new/012_累計得意先上位分析表（粗利）.html
    5	3	new/024_出荷一覧.html
  per_file_summary:
    - file: "006_受注売上入金管理.html"
      ins: 3
      del: 1
      net: "+2"
      note: "header-button 1 つ移動"
  total_ins: 14
  total_del: 7
  net: "+7"
  file_count: 4
```

`per_file_summary` は任意 (人間が読みやすくするため)、ただし `numstat_raw` は必須。

## auto-inject 条件

- `inject_rules` に `sp_041_strict` が含まれる task
- `type: fix_task` / `type: batch_task` / diff が発生するすべての task

## 違反時の処理

- XR reviewer が numstat 乖離検出 → F1 medium finding
- 2 回目以降: 再発扱い、worker voice feedback で自己反省要求
- 3 回目以降: kashira が task YAML hints に強制 reminder 注入

## 歴史

- 初回 cmd_188 W2 company 縦化 (2026-04-17、W4 XR F2 low)
- 2 回目 cmd_195efg W2 batch (2026-04-17、W4 XR F1 low)
- 3 回目 cmd_197 W2 color drift batch (2026-04-17、W4 XR F2 low)
- 親分 GO で本 rule 明文化 (2026-04-17、retrospective を待たず即適用)
