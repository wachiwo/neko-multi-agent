#!/usr/bin/env python3
"""cmd_184 015_見積明細.html の 10 CollapsibleSection 一括置換.
   section/section-header/section-content → collapsible-* に変換し、
   toggleSection(this) → 2引数 contentId/indicatorId 化、
   ▽ 接頭辞 → collapsible-indicator span 化、
   form-row に data-component="InputFieldContainer" 付与、
   container に data-component="InputLayout" 付与。"""
import re
import pathlib

FILE = pathlib.Path("/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new/015_見積明細.html")
text = FILE.read_text(encoding="utf-8")

# 10 sections with their IDs/titles (line numbers are approximate, used to identify)
sections = [
    ("customer-info",         "▽得意先情報",         "得意先情報"),
    ("customer-addr",         "▽得意先住所情報",     "得意先住所情報"),
    ("seller-info",           "▽販売店情報",         "販売店情報"),
    ("seller-addr",           "▽販売店住所情報",     "販売店住所情報"),
    ("enduser-info",          "▽エンドユーザ情報",   "エンドユーザ情報"),
    ("enduser-addr",          "▽エンドユーザ住所情報", "エンドユーザ住所情報"),
    ("mitsumori-info",        "▽見積情報",           "見積情報"),
    ("mitsumori-internal",    "▽見積社内情報",       "見積社内情報"),
    ("mitsumori-detail",      "▽見積明細",           "見積明細"),
    ("update-history",        "▽更新履歴",           "更新履歴"),
]

# Step 1: 各 section block を個別に書換
for key, old_title, new_title in sections:
    content_id = f"sec-{key}-content"
    indicator_id = f"ind-{key}"

    # Pattern: `<div class="section-header" onclick="toggleSection(this)">\n...▽TITLE\n...</div>\n<div class="section-content">`
    # We preserve indentation
    old_pat = re.compile(
        r'<div class="section-header" onclick="toggleSection\(this\)">\s*\n'
        r'(\s*)' + re.escape(old_title) + r'\s*\n'
        r'(\s*)</div>\s*\n'
        r'(\s*)<div class="section-content">',
        re.MULTILINE,
    )

    def replace_block(match):
        indent1 = match.group(1)
        indent2 = match.group(2)
        indent3 = match.group(3)
        return (
            f'<div class="collapsible-header" onclick="toggleSection(\'{content_id}\', \'{indicator_id}\')">\n'
            f'{indent1}<span>{new_title}</span>\n'
            f'{indent1}<span class="collapsible-indicator" id="{indicator_id}">▼</span>\n'
            f'{indent2}</div>\n'
            f'{indent3}<div id="{content_id}" class="collapsible-content">'
        )

    new_text, count = old_pat.subn(replace_block, text, count=1)
    if count == 0:
        # 代替パターン (inline 1行形式かもしれない)
        alt_pat = re.compile(
            r'<div class="section-header" onclick="toggleSection\(this\)">' + re.escape(old_title) + r'</div>',
        )
        new_text = alt_pat.sub(
            f'<div class="collapsible-header" onclick="toggleSection(\'{content_id}\', \'{indicator_id}\')">'
            f'<span>{new_title}</span>'
            f'<span class="collapsible-indicator" id="{indicator_id}">▼</span>'
            f'</div>',
            text,
        )
        print(f"  [FALLBACK] {key}: {old_title}")
    else:
        print(f"  [OK] {key}: {old_title}")
    text = new_text

# Step 2: 残った <div class="section"> を collapsible-section に (id="mitsumori-info-section" 等 属性付きも対応)
text = re.sub(
    r'<div class="section"(\s+id="[^"]*")?>',
    lambda m: f'<div class="collapsible-section" data-component="CollapsibleSection"{m.group(1) or ""}>',
    text,
)

# Step 3: form-row に data-component="InputFieldContainer" 付与 (ただし既にあるものは除外)
# Pattern: `<div class="form-row"` ただし直後に data-component がないもの
def add_input_field_container(match):
    full = match.group(0)
    if 'data-component' in full:
        return full
    return full.replace('<div class="form-row"', '<div class="form-row" data-component="InputFieldContainer"', 1)

text = re.sub(r'<div class="form-row"[^>]*>', add_input_field_container, text)

# Step 4: container に InputLayout 付与 (最初の 1 回だけ)
text = text.replace(
    '<div class="container">',
    '<!--\n'
    '      部品名: InputLayout (data-orientation="vertical")\n'
    '      Blazor: <InputLayout TModel="QuoteDetailModel" Orientation="Orientation.Vertical">\n'
    '      用途: 見積明細画面全体のルート (10 CollapsibleSection 内包)\n'
    '    -->\n'
    '    <div class="container" data-component="InputLayout" data-orientation="vertical">',
    1,
)

# Step 5: toggleSection(header) DOM依存実装を 2引数シンプル版に置換
text = re.sub(
    r'function toggleSection\(header\)\s*\{[^}]*\n[^}]*\n[^}]*\n[^}]*\n[^}]*\n[^}]*\n[^}]*\n[^}]*\n[^}]*\n\s*\}',
    (
        '// cmd_184: アコーディオン開閉 2引数化 (基準_縦.html 準拠、display:none 単純切替)\n'
        '        function toggleSection(contentId, indicatorId) {\n'
        '            var c = document.getElementById(contentId);\n'
        '            if (c) c.classList.toggle(\'collapsed\');\n'
        '            if (indicatorId) {\n'
        '                var i = document.getElementById(indicatorId);\n'
        '                if (i) i.classList.toggle(\'collapsed\');\n'
        '            }\n'
        '        }'
    ),
    text,
    count=1,
    flags=re.DOTALL,
)

# Step 6: body目次コメント追加
text = text.replace(
    '<body>',
    '<body>\n'
    '<!--\n'
    '  ══════════════ 部品カタログ目次 (cmd_184 Round 1 / new/015_見積明細.html) ══════════════\n'
    '  社内共通部品カタログ。基準_縦.html 準拠の正規8種 data-component 体系。\n'
    '  検索時は data-component 属性で特定可能。verdict=vertical (cmd_181 classification)。\n'
    '    - InputLayout           : 入力フォーム全体ルート (data-orientation="vertical")\n'
    '    - CollapsibleSection    : アコーディオン 10区画 (得意先/得意先住所/販売店/販売店住所/エンドユーザ/エンドユーザ住所/見積/見積社内/見積明細/更新履歴)\n'
    '    - InputFieldContainer   : 入力項目ラッパ (form-row × 70)\n'
    '  ※ 015 には ActionBar/AdminInfo/SearchPanel/InlineFieldGroup/DataGridTable 該当なし (明細画面)。\n'
    '  ※ 開閉は display:none 単純切替 (オリジナル016方式、アニメなし)。\n'
    '  ═══════════════════════════════════════════════════════════════════════════\n'
    '-->',
    1,
)

FILE.write_text(text, encoding="utf-8")
print(f"\n✅ 015 改修完了: {FILE}")
