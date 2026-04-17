# sp_053: canonical_normalization — 報告 template 必須化

## 背景 (2026-04-17 確定、W3 発見者責任で草案)

- W3 cmd_195h F2 + cmd_196 F3 で **2 回連続再発**
- 症状: worker report の scope_lock 申告で「touch した / 触らない」の 2 値で済ませる癖、実態は CSS drift fix や class rename が紛れ込んで申告と乖離
- 原因: 個人意識では防げない構造問題 (W3 当事者明言)、voice→次 task の feedback loop latency が長すぎて、運用組込み前に次 task で再発

## rule (強制)

### 報告 template に canonical_normalization field 必須

すべての code 修正 task の worker report に以下を**空でも必須記載**:

```yaml
canonical_normalization:
  class_renames:
    - from: "old-class"
      to: "new-class"
      files: ["001.html", "003.html"]
      reason: "canonical 016 と命名統一"
  value_changes_matching_canonical:
    - property: "color"
      from: "#333"
      to: "#1e293b"
      files: ["040.html"]
      reason: "canonical drift fix (sp_028)"
  layout_delta_per_file:
    - file: "015.html"
      width_attr: "unchanged"
      ch_attr: "unchanged"
      maxlength_attr: "unchanged"
      note: "色のみ fix、layout 意図保全"
  inline_style_changes:
    - file: "053.html"
      from: "max-height:400px"
      to: "removed"
      reason: "cmd_189 B fix で canonical 準拠"
```

### 「空でも必須」とは

- 該当変更が無い場合でも以下のいずれかを明記:
  ```yaml
  canonical_normalization:
    class_renames: []
    value_changes_matching_canonical: []
    layout_delta_per_file: []
    inline_style_changes: []
  ```
- field 丸ごと省略禁止 = 漏れを物理的に不可能化

## XR reviewer 側の義務

reviewer は worker の `canonical_normalization` を信じず、独立で diff を走査:

```bash
git diff HEAD -- <target files> | grep -E "class=|class:" # rename 検出
git diff HEAD -- <target files> | grep -E "^\+.*#[0-9a-fA-F]{3,6}" # color 変更
```

worker 申告と実態が 1 件でも乖離 → F1 medium finding (sp_053 違反)。

### 再発時のエスカレーション

- 2 回目まで: XR finding として開示 + voice feedback で自己反省要求
- 3 回目以降: kashira が task YAML の hints に強制 reminder 注入 + retrospective に常設項目化

## auto-inject 条件

- `inject_rules` に `sp_053` を含める対象:
  - `type: fix_task` (バグ修正系)
  - `type: batch_task` (複数 file 同系統変更)
  - `canonical_*` 系 task (audit / color / typography / layout 正規化)
- 疑わしい時は inject を優先 (over-injection はコスト低、漏れはコスト高)

## 関連

- **sp_028 DIMCO カラー統一**: canonical 色の定義元
- **sp_029 DIMCO タイポグラフィ統一**: canonical font の定義元
- **sp_041_strict**: diff 報告精度、本 rule と 2 層で申告整合性を担保
- **sp_054 parallel_scope** (後続): 並列合流時の scope 明示と相互作用
- **canonical_audit.md** (後続): audit 段階の lateral scan 網羅性

## 歴史

- cmd_195h F2 (W3 author / W4 reviewer、scope_lock 申告 vs 実態乖離): 1 回目
- cmd_196 F3 (W3 author / W4 reviewer、同パターン): 2 回目
- 2026-04-17 retrospective 2 回目で W3 発見者責任明言 + 全 worker 賛同 → 本 rule 明文化

## 実装メモ

- _worker_base.md の「report 作成」節に本 template を hard-wire
- 既存 task YAML template にも field sample を追加検討
- 次 retrospective で再発件数を計測、rule 効果検証
