#!/usr/bin/env python3
"""cmd_184 053_海外入力_パッキング.html: CSS rename + HTML class rename + wrapper追加の段階処理.

方針:
  Step1: CSS .section-header → .collapsible-header + アニメ無し CSS 追加 (display:none のみ)
  Step2: CSS .form-section → .collapsible-content (name change)
  Step3: HTML の .form-section → .collapsible-content (存在する全箇所)
  Step4: HTML の各 .section-header → 完全な CollapsibleSection wrap + collapsible-header + indicator
  Step5: form-row に data-component="InputFieldContainer"
  Step6: container に InputLayout
  Step7: body 目次
  Step8: DataGridTable 識別 (製品情報 table-container)
  Step9: 各セクション末尾の閉じ div 追加

★閉じ div の追加は、form-section (今 collapsible-content) の end 後に 1 つ追加★
  → 方針: 各セクションは <div class="section-header">TITLE</div>\n<div class="form-section">...</div>
     で構成されているので、section-header → wrap 開き に置換した後、form-section → collapsible-content
     の閉じ div 後に CollapsibleSection 閉じ div を追加する必要
  → しかし form-section の閉じ div を特定するのは DOM 構造依存で困難

★代替方針★:
  各セクションで 開きと閉じをペアで処理:
    section-header + form-section 開き → CollapsibleSection 開き + collapsible-header + collapsible-content 開き
    form-section 閉じ → collapsible-content 閉じ + CollapsibleSection 閉じ

  ただし form-section 閉じ div は section-header/form-section ペアごとに異なる位置
  → Python で構造解析が必要 → 行単位で状態管理

実装: 行単位 stateful parser で対応
"""
import re
import pathlib

FILE = pathlib.Path("/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new/053_海外入力_パッキング.html")
text = FILE.read_text(encoding="utf-8")

# Step 1+2: CSS class rename
text = text.replace(
    '.section-header { background: var(--primary-blue); color: white; padding: 12px 16px; font-weight: 600; margin-top: 20px; margin-bottom: 0; border: none; border-radius: 6px 6px 0 0; font-size: 14px; box-shadow: var(--shadow); }',
    (
        '/* cmd_184 正規化: .section-header/.form-section → collapsible-* (基準_縦.html 準拠) */\n'
        '        .collapsible-section { margin-bottom: 12px; }\n'
        '        .collapsible-header { background: var(--primary-blue); color: white; padding: 12px 16px; font-weight: 600; margin-top: 20px; margin-bottom: 0; border: none; border-radius: 6px 6px 0 0; font-size: 14px; box-shadow: var(--shadow); cursor: pointer; display: flex; justify-content: space-between; align-items: center; user-select: none; }\n'
        '        .collapsible-header:hover { background: var(--primary-blue-dark); }\n'
        '        .collapsible-indicator { font-size: 12px; transition: transform 0.3s ease; }\n'
        '        .collapsible-indicator.collapsed { transform: rotate(-90deg); }'
    ),
)

text = text.replace(
    '.form-section { border: 1px solid var(--border-color); border-top: none; padding: 20px; background: white; border-radius: 0 0 8px 8px; margin-bottom: 20px; }',
    (
        '.collapsible-content { border: 1px solid var(--border-color); border-top: none; padding: 20px; background: white; border-radius: 0 0 8px 8px; margin-bottom: 20px; }\n'
        '        .collapsible-content.collapsed { display: none; }'
    ),
)

# セクション定義 (順番通り、製品情報は table-container なので特殊扱い)
sections = [
    ("common-items",    "共通項目",      False),
    ("trade-terms-a",   "取引条件",      False),
    ("basic-info",      "基本情報",      False),
    ("counterparty",    "相手情報",      False),
    ("description",     "DESCRIPTION",   False),
    ("product-info",    "製品情報",      True),   # DataGridTable
    ("trade-terms-b",   "取引条件",      False),
    ("packing-case",    "梱包ケース情報", False),
    ("note-memo",       "NOTE（備考）",  False),
]

# HTML 行単位で parse
lines = text.split('\n')
out = []
i = 0
section_idx = 0
depth_stack = []  # stack of (depth, type) where type='cs' (collapsible-section)
wait_for_form_section_close = None  # stores {indent_depth}

# depth カウントで form-section (= collapsible-content) の終わりを検出する簡易 approach
current_open_cs_depth = None  # 現在 開いている collapsible-content の開始 div 深度

# Simpler: 行ごとにパターン検出
while i < len(lines):
    line = lines[i]

    # Case A: section-header 発見
    m_hdr = re.match(r'^(\s*)<div class="section-header">([^<]+)</div>\s*$', line)
    if m_hdr and section_idx < len(sections):
        indent = m_hdr.group(1)
        title_in_file = m_hdr.group(2)
        key, expected_title, is_datagrid = sections[section_idx]
        if title_in_file != expected_title:
            # タイトル不一致 → そのまま出力してスキップ (fallback)
            print(f"  [WARN] expected '{expected_title}' but found '{title_in_file}' at line {i+1}")
            out.append(line)
            i += 1
            continue

        content_id = f"sec-{key}-content"
        indicator_id = f"ind-{key}"

        # 次行が <div class="form-section"> または <div class="table-container"> であるか確認
        if i + 1 < len(lines):
            next_line = lines[i + 1]
            m_form = re.match(r'^(\s*)<div class="form-section">\s*$', next_line)
            m_tbl = re.match(r'^(\s*)<div class="table-container">\s*$', next_line)

            if is_datagrid and m_tbl:
                tbl_indent = m_tbl.group(1)
                # CollapsibleSection wrap + collapsible-content + DataGridTable
                out.append(f'{indent}<div class="collapsible-section" data-component="CollapsibleSection">')
                out.append(f'{indent}<div class="collapsible-header" onclick="toggleSection(\'{content_id}\', \'{indicator_id}\')">')
                out.append(f'{indent}    <span>{expected_title}</span>')
                out.append(f'{indent}    <span class="collapsible-indicator" id="{indicator_id}">▼</span>')
                out.append(f'{indent}</div>')
                out.append(f'{tbl_indent}<div id="{content_id}" class="collapsible-content">')
                out.append(f'{tbl_indent}<!-- 部品名: DataGridTable / ★cmd_184 対象外・触らない★ -->')
                out.append(f'{tbl_indent}<div class="table-container" data-component="DataGridTable">')
                # Mark we need to add extra </div> after the table-container closes
                depth_stack.append((tbl_indent, 'dg'))  # datagrid: 2 closing div required
                print(f"  [DG] {key}: {expected_title}")
                section_idx += 1
                i += 2  # skip next line (form-section or table-container)
                continue

            if not is_datagrid and m_form:
                form_indent = m_form.group(1)
                # CollapsibleSection wrap + collapsible-header + collapsible-content
                out.append(f'{indent}<div class="collapsible-section" data-component="CollapsibleSection">')
                out.append(f'{indent}<div class="collapsible-header" onclick="toggleSection(\'{content_id}\', \'{indicator_id}\')">')
                out.append(f'{indent}    <span>{expected_title}</span>')
                out.append(f'{indent}    <span class="collapsible-indicator" id="{indicator_id}">▼</span>')
                out.append(f'{indent}</div>')
                out.append(f'{form_indent}<div id="{content_id}" class="collapsible-content">')
                depth_stack.append((form_indent, 'cs'))
                print(f"  [OK] {key}: {expected_title}")
                section_idx += 1
                i += 2
                continue

        # Fallback: そのまま出力
        out.append(line)
        i += 1
        continue

    # Case B: depth_stack 最新の form-section/table-container の閉じ div を検出
    # 閉じ div の indent が stack top の indent と同じで "</div>" 行
    if depth_stack:
        top_indent, top_type = depth_stack[-1]
        m_close = re.match(r'^(\s*)</div>\s*$', line)
        if m_close and m_close.group(1) == top_indent:
            if top_type == 'dg':
                # datagrid: table-container の </div> + collapsible-content の </div> + section の </div>
                out.append(line)  # table-container close
                out.append(f'{top_indent}</div><!-- /collapsible-content -->')
                out.append(f'{top_indent}</div><!-- /CollapsibleSection -->')
                depth_stack.pop()
                i += 1
                continue
            elif top_type == 'cs':
                # form-section (= collapsible-content) の閉じ + CollapsibleSection wrap 閉じ
                out.append(line)  # collapsible-content close
                out.append(f'{top_indent}</div><!-- /CollapsibleSection -->')
                depth_stack.pop()
                i += 1
                continue

    out.append(line)
    i += 1

text = '\n'.join(out)

# Step 5: form-row/form-row-2/-3/-4 に InputFieldContainer
for rn in ('form-row', 'form-row-2', 'form-row-3', 'form-row-4'):
    def add_ifc_n(match, rn=rn):
        full = match.group(0)
        if 'data-component' in full:
            return full
        return full.replace(f'<div class="{rn}"', f'<div class="{rn}" data-component="InputFieldContainer"', 1)
    text = re.sub(rf'<div class="{rn}"[^>]*>', add_ifc_n, text)

# Step 6: container → InputLayout
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

# Step 7: body 目次
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

# Step 8: toggleSection 関数追加 (2引数シンプル版)
# 既存 toggleSection があれば置換、無ければ </body> 直前に挿入
if 'function toggleSection' in text:
    text = re.sub(
        r'function toggleSection\([^)]*\)\s*\{[^}]*\}',
        (
            'function toggleSection(contentId, indicatorId) {\n'
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
else:
    # </body> 直前に script タグで挿入
    text = text.replace(
        '</body>',
        '<script>\n'
        '// cmd_184: アコーディオン開閉 2引数化 (基準_縦.html 準拠、display:none 単純切替)\n'
        'function toggleSection(contentId, indicatorId) {\n'
        '    var c = document.getElementById(contentId);\n'
        '    if (c) c.classList.toggle(\'collapsed\');\n'
        '    if (indicatorId) {\n'
        '        var i = document.getElementById(indicatorId);\n'
        '        if (i) i.classList.toggle(\'collapsed\');\n'
        '    }\n'
        '}\n'
        '</script>\n'
        '</body>',
        1,
    )

FILE.write_text(text, encoding="utf-8")
print(f"\n✅ 053_パッキング 改修完了")
