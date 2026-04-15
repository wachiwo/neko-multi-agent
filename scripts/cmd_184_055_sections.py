#!/usr/bin/env python3
"""cmd_184 055_仕入先見積管理明細.html 4 CollapsibleSection 一括置換."""
import re
import pathlib

FILE = pathlib.Path("/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new/055_仕入先見積管理明細.html")
text = FILE.read_text(encoding="utf-8")

sections = [
    ("quote-register",  "▽見積登録情報", "見積登録情報"),
    ("supplier-info",   "▽仕入先情報",   "仕入先情報"),
    ("quote-info",      "▽見積情報",     "見積情報"),
    ("adoption-info",   "▽採用情報",     "採用情報"),
]

for key, old_title, new_title in sections:
    content_id = f"sec-{key}-content"
    indicator_id = f"ind-{key}"

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
    print(f"  [{'OK' if count else 'MISS'}] {key}: {old_title}")
    text = new_text

# section wrapper → collapsible-section (id属性対応)
text = re.sub(
    r'<div class="section"(\s+id="[^"]*")?>',
    lambda m: f'<div class="collapsible-section" data-component="CollapsibleSection"{m.group(1) or ""}>',
    text,
)

# form-row → InputFieldContainer
def add_ifc(match):
    full = match.group(0)
    if 'data-component' in full:
        return full
    return full.replace('<div class="form-row"', '<div class="form-row" data-component="InputFieldContainer"', 1)

text = re.sub(r'<div class="form-row"[^>]*>', add_ifc, text)

# container → InputLayout
text = text.replace(
    '<div class="container">',
    '<!--\n'
    '      部品名: InputLayout (data-orientation="vertical")\n'
    '      Blazor: <InputLayout TModel="SupplierQuoteDetailModel" Orientation="Orientation.Vertical">\n'
    '      用途: 仕入先見積管理明細画面全体のルート (CollapsibleSection × 4 内包)\n'
    '    -->\n'
    '    <div class="container" data-component="InputLayout" data-orientation="vertical">',
    1,
)

# toggleSection(header) DOM依存 → 2引数シンプル版
text = re.sub(
    r'function toggleSection\(header\)\s*\{(?:[^{}]*(?:\{[^}]*\})?)*?\n\s*\}',
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

# body 目次
text = text.replace(
    '<body>',
    '<body>\n'
    '<!--\n'
    '  ══════════════ 部品カタログ目次 (cmd_184 Round 2 / new/055_仕入先見積管理明細.html) ══════════════\n'
    '  社内共通部品カタログ。基準_縦.html 準拠の正規8種 data-component 体系。\n'
    '  検索時は data-component 属性で特定可能。verdict=vertical (cmd_181 classification)。\n'
    '    - InputLayout           : 入力フォーム全体ルート (data-orientation="vertical")\n'
    '    - CollapsibleSection    : アコーディオン 4区画 (見積登録情報/仕入先情報/見積情報/採用情報)\n'
    '    - InputFieldContainer   : 入力項目ラッパ (form-row × 11)\n'
    '  ※ 055 には ActionBar/AdminInfo/SearchPanel/InlineFieldGroup/DataGridTable 該当なし。\n'
    '  ═══════════════════════════════════════════════════════════════════════════\n'
    '-->',
    1,
)

FILE.write_text(text, encoding="utf-8")
print(f"\n✅ 055 改修完了: {FILE}")
