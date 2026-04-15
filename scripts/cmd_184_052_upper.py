#!/usr/bin/env python3
"""cmd_184 052_受注画面(受注明細).html W1 上半分 (L1-L2435): class rename のみ。

方針:
  - section-header-bar は元々 onclick 無し → CollapsibleSection data-component 付与せず、
    class name を .collapsible-header にだけ rename (cursor:pointer はCSSで継続)
  - search-form-row → .form-row + data-component="InputFieldContainer"
  - search-form-row.single → .form-row.single (class rename)
  - search-form-field → .form-field
  - .section-content → .collapsible-content (HTML class)
  - container → data-component="InputLayout" data-orientation="vertical"
  - body 目次

★独自装飾/アニメ追加禁止★ を厳守: wrap 追加なし、toggle 機能追加なし。
W1 範囲: L1-L2435 (▲追加ブロック コメント直前まで)
W2 範囲: L2436+ → W2 担当、触らない
"""
import re
import pathlib

FILE = pathlib.Path("/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new/052_受注画面(受注明細).html")
text = FILE.read_text(encoding="utf-8")

# W1/W2 境界: L2435 の "<!-- ▲追加ブロック -->" コメント
# Python text-level 分割: "<!-- ▲追加ブロック -->" で split
marker = "<!-- ▲追加ブロック -->"
if marker in text:
    parts = text.split(marker, 1)
    head, tail = parts[0], marker + parts[1]
    # head = W1 範囲 (L1-L2434), tail = W2 範囲 (L2435-end)
else:
    print("WARN: marker not found, treating whole file as W1")
    head = text
    tail = ""

print(f"[分割] W1 範囲: {len(head.splitlines())} 行, W2 範囲: {len(tail.splitlines())} 行")

# ─── W1 (head) への処理 ───

# Step 1: section-header-bar → collapsible-header (class rename のみ)
head = re.sub(
    r'<div class="section-header-bar"',
    '<div class="collapsible-header"',
    head,
)

# Step 2: section-content (HTML class) → collapsible-content
head = re.sub(
    r'<div class="section-content"',
    '<div class="collapsible-content"',
    head,
)

# Step 3: search-form-row.single / search-form-row (class rename) + InputFieldContainer
# single 優先 (two-level class "search-form-row single")
def add_ifc(match):
    full = match.group(0)
    if 'data-component' in full:
        return full
    return full.replace('class="form-row single"', 'class="form-row single" data-component="InputFieldContainer"').replace('class="form-row"', 'class="form-row" data-component="InputFieldContainer"', 1)

head = head.replace('class="search-form-row single"', 'class="form-row single"')
head = head.replace('class="search-form-row"', 'class="form-row"')
# InputFieldContainer 付与
head = re.sub(r'<div class="form-row( single)?"[^>]*>', add_ifc, head)

# Step 4: search-form-field → form-field
head = head.replace('class="search-form-field', 'class="form-field')

# Step 5: container → InputLayout (最初の 1 回のみ)
head = head.replace(
    '<div class="container">',
    '<!--\n'
    '              部品名: InputLayout (data-orientation="vertical")\n'
    '              Blazor: <InputLayout TModel="OrderModel" Orientation="Orientation.Vertical">\n'
    '              用途: 受注画面全体のルート (受注基本情報〜受注備考等〜明細情報〜入金情報〜仕入情報〜仕入入力)\n'
    '              ※ W1 担当は L1-L2435 (受注基本情報〜明細情報 8 セクション)、W2 担当は L2436-末尾\n'
    '            -->\n'
    '              <div class="container" data-component="InputLayout" data-orientation="vertical">',
    1,
)

# Step 6: body 目次追加
head = head.replace(
    '<body>',
    '<body>\n'
    '<!--\n'
    '  ══════════════ 部品カタログ目次 (cmd_184 Round 2 / new/052_受注画面(受注明細).html) ══════════════\n'
    '  社内共通部品カタログ。基準_縦.html 準拠の正規8種 data-component 体系。\n'
    '  ★W1/W2 協調分担★ W1=L1-L2435 (受注基本情報〜明細情報 8セク), W2=L2436-末尾 (入金+仕入3セク)\n'
    '  検索時は data-component 属性で特定可能。verdict=vertical (cmd_181 classification)。\n'
    '    - InputLayout           : 入力フォーム全体ルート (data-orientation="vertical")\n'
    '    - InputFieldContainer   : 入力項目ラッパ (form-row × N、form-row.single 含)\n'
    '    - DataGridTable         : 明細情報内の child-table (W2 側で識別)\n'
    '  ※ section-header-bar は onclick 元々なしの静的ヘッダー → class rename のみで CollapsibleSection\n'
    '    data-component は付与しない (独自挙動追加禁止の新ルール遵守)。\n'
    '  ※ .search-form-* 方言は .form-* に正規化済。.section-content も .collapsible-content に rename。\n'
    '  ═══════════════════════════════════════════════════════════════════════════\n'
    '-->',
    1,
)

# 統合して書き込み
out = head + tail
FILE.write_text(out, encoding="utf-8")
print(f"\n✅ 052 W1 上半分 改修完了")
