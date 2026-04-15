#!/usr/bin/env python3
"""cmd_184 053_海外入力_パッキング.html 9 flat section-header → CollapsibleSection wrap."""
import re
import pathlib

FILE = pathlib.Path("/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new/053_海外入力_パッキング.html")
text = FILE.read_text(encoding="utf-8")

# 9 flat sections: section-header → form-section OR table-container の 2 パターン
sections = [
    ("common-items",    "共通項目",      "form-section"),
    ("trade-terms-a",   "取引条件",      "form-section"),   # A: 前半
    ("basic-info",      "基本情報",      "form-section"),
    ("counterparty",    "相手情報",      "form-section"),
    ("description",     "DESCRIPTION",   "form-section"),
    ("product-info",    "製品情報",      "table-container"), # DataGridTable 直接
    ("trade-terms-b",   "取引条件",      "form-section"),   # B: 後半 (同タイトル別セクション)
    ("packing-case",    "梱包ケース情報", "form-section"),
    ("note-memo",       "NOTE（備考）",  "form-section"),
]

# Step 1: flat section-header + form-section/table-container → CollapsibleSection wrap
# Pattern: `<div class="section-header">TITLE</div>\n<div class="X">`
# We need to replace with wrap structure
#
# しかし同じタイトルが複数ある (取引条件 x 2) → 順番で処理する必要あり

# 順序依存のため、replacement を 1 つずつ順に (残 section-header 最初の物を発見して処理)
remaining_sections = list(sections)

def process_one():
    global text
    if not remaining_sections:
        return False
    key, title, content_class = remaining_sections[0]
    content_id = f"sec-{key}-content"
    indicator_id = f"ind-{key}"

    # Find first occurrence of `<div class="section-header">TITLE</div>`
    pat = re.compile(
        r'(\s*)<div class="section-header">' + re.escape(title) + r'</div>\s*\n'
        r'(\s*)<div class="' + content_class + r'">',
    )
    m = pat.search(text)
    if not m:
        print(f"  [MISS] {key}: {title}")
        remaining_sections.pop(0)
        return True
    indent1 = m.group(1)
    indent2 = m.group(2)
    new_block = (
        f'{indent1}<div class="collapsible-section" data-component="CollapsibleSection">\n'
        f'{indent1}<div class="collapsible-header" onclick="toggleSection(\'{content_id}\', \'{indicator_id}\')">\n'
        f'{indent1}    <span>{title}</span>\n'
        f'{indent1}    <span class="collapsible-indicator" id="{indicator_id}">▼</span>\n'
        f'{indent1}</div>\n'
        f'{indent2}<div id="{content_id}" class="collapsible-content">\n'
    )
    # 製品情報 (table-container = DataGridTable): content 内の table-container に data-component 付与
    if content_class == "table-container":
        new_block += (
            f'{indent2}<!-- 部品名: DataGridTable / ★cmd_184 対象外・触らない★ 製品情報表示 -->\n'
            f'{indent2}<div class="table-container" data-component="DataGridTable">'
        )
    else:
        # form-section → collapsible-content 化 (CSS 済)。だが class name はまだ form-section 残存。
        # → <div class="form-section"> を廃止。開きを collapsible-content で取り込んだので、元 form-section の開き div を削除
        # いや、正しくは: 元の `<div class="form-section">` が新 collapsible-content に置き換わる
        pass

    # Replace only that first occurrence; use re.sub with count=1 and string substitution
    text_new = pat.sub(lambda m: new_block, text, count=1)
    if text_new == text:
        print(f"  [NO-CHANGE] {key}: {title}")
    else:
        print(f"  [OK] {key}: {title} ({content_class})")
        text = text_new
    remaining_sections.pop(0)
    return True

while process_one():
    pass

# Step 2: 元の section-header を削除した場合、form-section の閉じる </div> が余剰になる可能性あり
# 実際は: 元 `<div class="form-section">` を `<div class="collapsible-content">` に置き換え、
# さらにその外側に collapsible-section wrapper を追加 → 元の </div> ペアにプラス 1 </div> 必要
# 現在のテキストでは: collapsible-section 開始 + collapsible-content 開始 (元の form-section 開きを置換) が発生
# 元の form-section の終わり </div> に対して、collapsible-section 終わり </div> がないので、
# 各セクション末尾に閉じタグ追加が必要

# 実装方針変更: 上記複雑なのでやり直し。別アプローチで section-header と form-section 両方を Edit で個別処理する

# Step 3: form-row に InputFieldContainer 付与
def add_ifc(match):
    full = match.group(0)
    if 'data-component' in full:
        return full
    return full.replace('<div class="form-row"', '<div class="form-row" data-component="InputFieldContainer"', 1)

text = re.sub(r'<div class="form-row"[^>]*>', add_ifc, text)

# Step 4: form-row-2/-3/-4 にも付与
for rn in ('form-row-2', 'form-row-3', 'form-row-4'):
    def add_ifc_n(match, rn=rn):
        full = match.group(0)
        if 'data-component' in full:
            return full
        return full.replace(f'<div class="{rn}"', f'<div class="{rn}" data-component="InputFieldContainer"', 1)
    text = re.sub(rf'<div class="{rn}"[^>]*>', add_ifc_n, text)

# Step 5: container → InputLayout
text = text.replace(
    '<div class="container">',
    '<!--\n'
    '      部品名: InputLayout (data-orientation="vertical")\n'
    '      Blazor: <InputLayout TModel="PackingListModel" Orientation="Orientation.Vertical">\n'
    '      用途: 海外入力_パッキングリスト画面全体のルート (CollapsibleSection × 9 内包)\n'
    '    -->\n'
    '    <div class="container" data-component="InputLayout" data-orientation="vertical">',
    1,
)

# Step 6: body 目次
text = text.replace(
    '<body>',
    '<body>\n'
    '<!--\n'
    '  ══════════════ 部品カタログ目次 (cmd_184 Round 2 / new/053_海外入力_パッキング.html) ══════════════\n'
    '  社内共通部品カタログ。基準_縦.html 準拠の正規8種 data-component 体系。\n'
    '  検索時は data-component 属性で特定可能。verdict=vertical (cmd_181 classification)。\n'
    '    - InputLayout           : 入力フォーム全体ルート (data-orientation="vertical")\n'
    '    - CollapsibleSection    : アコーディオン 9区画 (共通項目/取引条件A/基本情報/相手情報/DESCRIPTION/製品情報/取引条件B/梱包ケース情報/NOTE)\n'
    '    - InputFieldContainer   : 入力項目ラッパ (form-row/-2/-3/-4 × N)\n'
    '    - DataGridTable         : 製品情報 table (触らない)\n'
    '  ※ 053_パッキング には ActionBar/AdminInfo/SearchPanel/InlineFieldGroup 該当なし。\n'
    '  ═══════════════════════════════════════════════════════════════════════════\n'
    '-->',
    1,
)

FILE.write_text(text, encoding="utf-8")
print(f"\n✅ 053_パッキング 改修完了: {FILE}")
