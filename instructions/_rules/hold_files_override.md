# hold_files_override — hold_files 踏み越え判定 matrix

## 背景 (2026-04-17 確定、W1 提案)

- cmd_197b で hold_files 015/051 踏み越え判断を W1 が「layout 非影響=hold 意図保全」と根拠づけ
- ★この判断の境界線が明文化されていない★ = case-by-case 判断を別 worker が同じ基準でできる保証がない
- 原因: hold_files の保全目的 (layout 保持) と触って良い範囲 (色/フォント 等 layout 非影響) の区別が個人判断依存

## hold_files とは

### 定義

cmd_184 時代から「layout 属性 (width/ch/maxlength/height 等) を手動調整した file」として保全対象に指定された files。具体的には:

- `015_見積明細.html`: width 180px × 2 + 22ch × 9 (担当者列)
- `016_受注一覧.html`: canonical 全体保全 (他画面が参照する baseline)
- `048_引合一覧.html`: inquiry-content 5 props
- `051_見積明細（海外）.html`: 104ch × 148件 (商品名称複数行、intentional)
- `053_海外入力_プロフォーマ.html`: form-group=13 form-field=0 (TRUE NEGATIVE)

### 保全目的

layout 属性 (画面上の表示幅/高さ/文字数制限) を保持すること。layout 以外の変更は本来の保全意図を損なわない可能性がある。

## rule (強制): 踏み越え判定 matrix

| 変更種別 | 判定 | 根拠 |
|---------|------|------|
| **color_only** (color/background/border-color) | **allowed** | layout 非影響、sp_028 canonical 統一優先 |
| **font_family / font_size** (layout 影響小) | **kashira_approval_required** | line-height 変化で layout 影響の可能性、実測確認後 |
| **padding / margin** | **forbidden** | layout 直接影響、hold 意図違反 |
| **width / height / max-width / max-height** | **forbidden** | layout 属性そのもの、hold 対象 |
| **display / flex / grid** | **forbidden** | layout 根幹、canonical 構造変更 |
| **position / overflow / z-index** | **forbidden** | layout 副作用大、sp_028/039 破壊リスク |
| **class rename** (canonical 名義統一) | **kashira_approval_required** | 命名は hold 意図外だが CSS セレクタ変更で副作用あり |
| **form_structure** (form-row/form-field 書換) | **forbidden** | layout そのもの、hold 中核 |
| **DOM 追加/削除** (button/input 追加等) | **forbidden** | layout 根本変更 |
| **attribute 変更** (maxlength/min/max/step) | **forbidden** | hold 対象の layout 属性 |

### 判定 allowed の場合の必須要件

踏み越え commit msg に以下 4 項目を必須明記:

1. **audit 漏れ補完根拠**: なぜ当初 scope 外だったか (cmd_194 W1 audit の drift_diff_table 未登録 等)
2. **layout delta 実測**: 全 layout 属性 (width/ch/maxlength/height 等) の diff 0 を実測値で提示
3. **Playwright computed 値**: 変更後の canonical 準拠 (例: rgb(74,144,217) = #4A90D9) を実測
4. **代替案比較**: hold_files 除外案の問題 (canonical 統一の分断状態等) と踏み越え案の長期価値比較

### 判定 kashira_approval_required の場合

worker が踏み越え判断を独断せず、kashira に escalation:

```yaml
kashira_approval_request:
  task_id: subtask_XXX
  hold_file: "015_見積明細.html"
  change_type: "font_size"
  reason: "canonical drift fix (sp_029)"
  layout_impact_estimate: "line-height 変化で ±2px 可能性、実測要"
```

kashira が親分と相談 or 独断で判定。

### 判定 forbidden の場合

worker は絶対 touch せず、別 cmd として切り出し or 親分経由ご主人様判断へ escalation。

## XR reviewer 側の義務

hold_files の diff 検出時 reviewer は:

1. 変更種別を matrix で判定 (allowed / kashira_approval_required / forbidden)
2. allowed の場合、commit msg の 4 項目明記を確認
3. kashira_approval_required の場合、`kashira_approval_request` の存在を確認
4. forbidden の場合、F2 high finding (無断踏み越え、即修正要求)

## 関連

- **sp_028 DIMCO カラー統一**: color_only 踏み越えの根拠
- **sp_029 DIMCO タイポグラフィ統一**: font 踏み越えの根拠
- **sp_053 canonical_normalization**: 踏み越え内容を layout_delta_per_file で必須記録
- **sp_055 handoff_2in1**: 踏み越え判断を handoff workflow に統合

## 歴史

- cmd_194 W1 audit で #4da3d9 が drift_diff_table から漏れ (cmd_197 scope 外)
- cmd_197b で hold_files 015/051 に #4da3d9 残存発覚、踏み越え判断が必要に
- W1 が layout 4 属性 (width/ch/maxlength/file_size) 全 diff 0 で根拠作成 → 親分 GO A 案で踏み越え成立
- W1 retrospective t4 で「境界線明文化不足」指摘 → 本 matrix 明文化

## 実装メモ

- worker が hold_files 発見時、本 matrix を参照して判定
- commit msg 4 項目明記を template 化 (W1 cmd_197b 実績を雛形に)
- 新 hold_files 追加時は matrix も再評価 (project_dimco_design_system.md と連動)
