#!/usr/bin/env python3
"""cmd_184 052 W1 上半分 v2: L2435 境界 (8 番目の ▲追加ブロック) で分割."""
import re
import pathlib

FILE = pathlib.Path("/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new/052_受注画面(受注明細).html")
text = FILE.read_text(encoding="utf-8")
lines = text.split('\n')

# 境界: 8 番目の "<!-- ▲追加ブロック -->" (L2435)
marker = "<!-- ▲追加ブロック -->"
marker_lines = [i for i, line in enumerate(lines) if line.strip() == marker]
print(f"[マーカー位置] 計 {len(marker_lines)} 件: {marker_lines[:10]}")

# W1 範囲: 先頭 〜 8 番目マーカー (index=7) を含む行まで
# W2 範囲: 9 番目マーカー以降
if len(marker_lines) < 8:
    print(f"ERROR: 8番目マーカーが見つからない (found {len(marker_lines)})")
    raise SystemExit(1)

w1_end_idx = marker_lines[7]  # 0-indexed, 8 番目は index 7、L2435 = 2434 (0-indexed)
print(f"[分割] W1: lines[0..{w1_end_idx}] ({w1_end_idx + 1} 行), W2: lines[{w1_end_idx + 1}..] ({len(lines) - w1_end_idx - 1} 行)")

w1_lines = lines[:w1_end_idx + 1]  # 8 番目マーカー行を含む
w2_lines = lines[w1_end_idx + 1:]  # それ以降
w1_text = '\n'.join(w1_lines)
w2_text = '\n'.join(w2_lines)

# ═════ W1 範囲への処理 ═════

# Step 1: section-header-bar → collapsible-header (class rename のみ、wrap なし)
w1_text = re.sub(
    r'<div class="section-header-bar"',
    '<div class="collapsible-header"',
    w1_text,
)

# Step 2: section-content → collapsible-content
w1_text = re.sub(
    r'<div class="section-content"',
    '<div class="collapsible-content"',
    w1_text,
)

# Step 3: search-form-row.single → form-row.single
w1_text = w1_text.replace('class="search-form-row single"', 'class="form-row single"')
w1_text = w1_text.replace('class="search-form-row"', 'class="form-row"')

# Step 4: search-form-field → form-field
w1_text = w1_text.replace('class="search-form-field', 'class="form-field')

# Step 5: form-row / form-row.single に data-component="InputFieldContainer"
def add_ifc(match):
    full = match.group(0)
    if 'data-component' in full:
        return full
    # form-row 直後 (single 対応済み)
    return full[:12] + ' data-component="InputFieldContainer"' + full[12:]

# form-row のみ (data-component 未付与)
w1_text = re.sub(r'<div class="form-row(?= single"| ")', r'<div data-component="InputFieldContainer" class="form-row', w1_text)

# Step 5.5: container → InputLayout (W1 側でのみ)
w1_text = w1_text.replace(
    '<div class="container">',
    '<!--\n'
    '              部品名: InputLayout (data-orientation="vertical")\n'
    '              Blazor: <InputLayout TModel="OrderModel" Orientation="Orientation.Vertical">\n'
    '              用途: 受注画面全体のルート\n'
    '              ※ W1 担当 (L1-L2435): 受注基本情報〜明細情報 8 セクション\n'
    '              ※ W2 担当 (L2436-末尾): 入金情報+仕入3セク\n'
    '            -->\n'
    '              <div class="container" data-component="InputLayout" data-orientation="vertical">',
    1,
)

# Step 6: body 目次 (W1 側で追加)
w1_text = w1_text.replace(
    '<body>',
    '<body>\n'
    '<!--\n'
    '  ══════════════ 部品カタログ目次 (cmd_184 Round 2 / new/052_受注画面(受注明細).html) ══════════════\n'
    '  社内共通部品カタログ。基準_縦.html 準拠の正規8種 data-component 体系。\n'
    '  ★W1/W2 協調分担★\n'
    '    W1 (L1-L2435): 受注基本情報/得意先/請求書送付先/直送先/エンドユーザ/取引条件/受注備考等/明細情報 の 8 セクション\n'
    '    W2 (L2436-末尾): 入金情報/仕入情報/仕入入力 + 末尾スクリプト\n'
    '  検索時は data-component 属性で特定可能。verdict=vertical (cmd_181 classification)。\n'
    '    - InputLayout           : 入力フォーム全体ルート (data-orientation="vertical")\n'
    '    - InputFieldContainer   : 入力項目ラッパ (form-row / form-row.single × N)\n'
    '    - DataGridTable         : 明細情報内の child-table はW2側で識別予定 (または触らない)\n'
    '  ※ section-header-bar は元々 onclick 無しの静的ヘッダー → class rename のみ。\n'
    '    CollapsibleSection data-component は付与しない (独自挙動追加禁止の新ルール)。\n'
    '  ※ .search-form-* / .section-content は .form-* / .collapsible-content に正規化済。\n'
    '  ═══════════════════════════════════════════════════════════════════════════\n'
    '-->',
    1,
)

# ═════ CSS 部分の処理 (W1 側で実施、W2 は従う) ═════
# W1 の CSS 正規化 (.section-content / .section.collapsed .section-content)
w1_text = w1_text.replace(
    '.section-content {\n    display: block;\n}\n.section.collapsed .section-content {\n    display: none;\n}',
    '/* cmd_184 正規化: .section-content → .collapsible-content (display:none 単純切替) */\n'
    '.collapsible-content {\n    display: block;\n}\n'
    '.collapsible-content.collapsed {\n    display: none;\n}',
)

# CSS 内の .section-header-bar → .collapsible-header (W1 で定義変更)
w1_text = w1_text.replace(
    '.section-header-bar {\n        background: var(--primary-blue);\n        color: white;\n        padding: 12px 16px;\n        font-weight: 600;\n        margin-top: 20px;\n        margin-bottom: 0;\n        border: none;\n        border-radius: 6px 6px 0 0;\n        font-size: 14px;\n        box-shadow: var(--shadow);\n        cursor: pointer;\n    }',
    '/* cmd_184 正規化: .section-header-bar → .collapsible-header (class rename のみ、wrap 追加なし) */\n'
    '    .collapsible-header {\n        background: var(--primary-blue);\n        color: white;\n        padding: 12px 16px;\n        font-weight: 600;\n        margin-top: 20px;\n        margin-bottom: 0;\n        border: none;\n        border-radius: 6px 6px 0 0;\n        font-size: 14px;\n        box-shadow: var(--shadow);\n        cursor: pointer;\n    }',
)

# CSS 内 .search-form → .collapsible-content (名前変更、既存 collapsible-content と競合回避のため 旧 search-form ルールを置換して統合)
w1_text = w1_text.replace(
    '.search-form {\n        border: 1px solid var(--border-color);\n        border-top: none;\n        padding: 20px;\n        background: white;\n        border-radius: 0 0 8px 8px;\n        margin-bottom: 20px;\n    }',
    '/* cmd_184 正規化: .search-form → .collapsible-content */\n'
    '    .collapsible-content {\n        border: 1px solid var(--border-color);\n        border-top: none;\n        padding: 20px;\n        background: white;\n        border-radius: 0 0 8px 8px;\n        margin-bottom: 20px;\n    }',
)

# CSS 内 .search-form-row → .form-row
w1_text = w1_text.replace(
    '.search-form-row {\n        display: grid;\n        grid-template-columns: 1fr 1fr;\n        gap: 20px;\n        margin-bottom: 15px;\n    }\n    .search-form-row.single {\n        grid-template-columns: 1fr;\n    }',
    '.form-row {\n        display: grid;\n        grid-template-columns: 1fr 1fr;\n        gap: 20px;\n        margin-bottom: 15px;\n    }\n    .form-row.single {\n        grid-template-columns: 1fr;\n    }',
)

# CSS 内 .search-form-field → .form-field
w1_text = w1_text.replace(
    '.search-form-field {\n        display: flex;\n        align-items: center;\n        gap: 10px;\n    }',
    '.form-field {\n        display: flex;\n        align-items: center;\n        gap: 10px;\n    }',
)
w1_text = w1_text.replace(
    '.search-form-field label {\n        min-width: 100px;\n        font-weight: 500;\n        color: var(--text-dark);\n    }',
    '.form-field label {\n        min-width: 100px;\n        font-weight: 500;\n        color: var(--text-dark);\n    }',
)
w1_text = w1_text.replace(
    '.search-form-field input,\n    .search-form-field select {',
    '.form-field input,\n    .form-field select {',
)
w1_text = w1_text.replace(
    '.search-form-field input:focus,\n    .search-form-field select:focus {',
    '.form-field input:focus,\n    .form-field select:focus {',
)

# 統合
out = w1_text + '\n' + w2_text
FILE.write_text(out, encoding="utf-8")
print(f"\n✅ 052 W1 上半分 改修完了 (v2)")
