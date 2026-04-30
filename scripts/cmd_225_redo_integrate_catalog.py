#!/usr/bin/env python3
"""cmd_225_redo Phase 2 reintegration: 4 worker degawa SSOT sections → catalog (fresh).

Phase 0 audit findings:
- W1 layout (1332 lines): no doctype, body-only section. Has 4 .part-label + .part-demo-area showroom blocks.
  - Sidebar HTML: L52-71 (inside 1st part-demo-area)
  - Header HTML: L102-105 (inside 2nd part-demo-area)
  - Inline CSS: L185-1251 (W1 full = degawa style.css + zdo_drawer_menu.css + responsive-common.css + .part-label CSS)
  - Inline JS: L1258-1310 (zdo_drawer_menu.js)
- W2 modal-button (394 lines): FULL doctype + head + body. :root L37 (2 vars subset).
  - Body: L162-368
  - Inline JS: L379-391
- W3 table-variants (528 lines): FULL doctype + head + body. :root L25 (26+ vars from degawa style.css L3-52 byte-match).
  - Body: L116-509 (★has 二段ヘッダー PENDING finding visible in body★)
- W4 form-input (440 lines): FULL doctype + head + body. :root L34 (2 vars subset).
  - Body: L152-418
  - Inline JS: L431-437

Integration strategy:
- HTML5 + Bootstrap 5 CDN + jQuery CDN
- Catalog-level CSS = W1 full inline CSS (already has degawa :root + style.css + zdo + responsive-common) + W2 specific CSS + W3 specific CSS + W4 specific CSS (all minus :root duplicates)
- Outer wrapper = container-fluid > row > [W1 sidebar literal at L52-71] + [main col with header literal at L102-105 + main with TOC + 4 sections]
- 4 sections inside main:
    - Section 1: W1 layout documentation (4 .part-label entries — keep as-is)
    - Section 2: W2 body content
    - Section 3: W3 body content (★PENDING finding 二段ヘッダー visible 維持★)
    - Section 4: W4 body content
- DOMContentLoaded wrap (W1 cmd_225 経験継続)
"""
import re
from pathlib import Path

REDO = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_225_redo")
TARGET = Path("/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new/dimco-parts-catalog.html")


def read(name: str) -> list[str]:
    return (REDO / name).read_text(encoding="utf-8").splitlines()


def slice_lines(lines: list[str], start: int, end: int) -> str:
    # 1-indexed inclusive; convert to 0-indexed slice
    return "\n".join(lines[start - 1:end])


def strip_root_block(css: str) -> str:
    """Remove :root { ... } block(s) from css string."""
    return re.sub(r":root\s*\{[^}]*\}", "/* :root removed (catalog uses W1 canonical) */", css, flags=re.DOTALL)


def main():
    w1 = read("w1_layout_section.html")
    w2 = read("w2_modal_button_section.html")
    w3 = read("w3_table_variants_section.html")
    w4 = read("w4_form_input_section.html")

    # W1 components (inline boundaries verified via grep)
    w1_sidebar_html = slice_lines(w1, 51, 71)   # L51 comment + L52-71 sidebar
    w1_header_html = slice_lines(w1, 102, 105)  # L102-105 header (skip L99-101 demo-area open + col-sm wrap)
    w1_inline_css = slice_lines(w1, 186, 1250)  # L186-1250 (between <style> L185 and </style> L1251)
    w1_inline_js = slice_lines(w1, 1259, 1309)  # L1259-1309 (between <script> L1258 and </script> L1310)

    # W2 specific CSS (excluding :root)
    w2_css_full = slice_lines(w2, 37, 159)   # L37-159
    w2_css = strip_root_block(w2_css_full)
    w2_body = slice_lines(w2, 163, 368)      # L163-368 (skip L162 <body>, exclude </body>)
    w2_js = slice_lines(w2, 380, 390)        # L380-390 (between <script> L379 and </script> L391)

    # W3 specific CSS (excluding :root duplicate with W1)
    w3_css_full = slice_lines(w3, 21, 113)   # L21-113 (between <style> L21 and </style> L114, but L21 is <style> open so L22-113)
    # Actually the <style> tag itself is at L21 from grep, content starts L22
    w3_css_full = slice_lines(w3, 22, 113)
    w3_css = strip_root_block(w3_css_full)
    w3_body = slice_lines(w3, 117, 526)      # L117-526 (skip L116 <body>, exclude </body> L527)

    # W4 specific CSS (excluding :root)
    w4_css_full = slice_lines(w4, 31, 149)   # L31-149 (between <style> L30 and </style> L150)
    w4_css = strip_root_block(w4_css_full)
    w4_body = slice_lines(w4, 153, 418)      # L153-418 (skip L152 <body>, exclude </body>)
    w4_js = slice_lines(w4, 432, 436)        # L432-436 (between <script> L431 and </script> L437)

    # Build catalog
    catalog = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DIMCO パーツカタログ (degawa SSOT 起点、cmd_225_redo 完成形)</title>
<!--
============================================================
  DIMCO パーツカタログ — cmd_225_redo degawa SSOT 起点 完成形
  作成日: 2026-04-30
  作成者: 4 worker 共同 (W1=layout / W2=modal+button / W3=table variants / W4=form+input)
  統合: kashira から W1 (1号猫) に delegate、subtask_225_redo_005_w1_reintegration
  spec: ご主人様 18:30 真意確定『worker 推測 SSOT (016/049/027) 採用禁止、degawa SSOT 起点 fresh build』
  方針: degawa /mnt/g/共有ドライブ/[PJ]ディムコ/01_再構築プロジェクト/90_personal/degawa/007_部品一覧/ literal copy
  cmd_225/cmd_225_fix → cmd_225_redo evolution:
    - 既存 catalog (e3c4e93) 全破棄、推測 SSOT (016/049/027) 採用 0 件
    - 全 source = degawa 4 sample HTML + assets/ CSS + JS + PNG 由来
    - W1 layout outer wrapper (Bootstrap container-fluid + row 2 col)
    - 4 sections: layout / modal+button / table / form+input
  CDN deps:
    - Bootstrap 5.3.x CSS + Bundle JS
    - Bootstrap Icons CSS
    - jQuery 3.7.x (zdo_drawer_menu.js が jQuery binding 優先)
  self-contained:
    - ローカル CSS 全 inline (degawa style.css + zdo_drawer_menu.css + responsive-common.css + 4 worker 個別 CSS)
    - ローカル JS inline (zdo_drawer_menu.js + 4 worker 個別 JS)
    - 8 PNG icons base64 inline (W1 sidebar/header)
    - 外部 file ref 0 (CDN 除く)
  ★PENDING finding (W3 critical)★:
    - 二段ヘッダー table = degawa 一覧テーブル.html literal 不在
    - W3 Section 8 で visible に明示記載、ご主人様目視時に確認 trigger
============================================================
-->
<!-- Bootstrap 5 CDN -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">
<!-- jQuery CDN (zdo_drawer_menu.js が jQuery binding 優先) -->
<script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>

<style>
/* ====================================================================== */
/* ★1. W1 layout 全 inline CSS (degawa style.css + zdo_drawer_menu.css + responsive-common.css + .part-label/.part-demo-area)★ */
/* canonical :root (33 vars) は本ブロック内、W2/W3/W4 :root は除外 (duplicate 排除) */
/* ====================================================================== */
{w1_inline_css}

/* ====================================================================== */
/* ★2. W2 modal + button specific CSS (:root 除外、W1 canonical 使用)★ */
/* ====================================================================== */
{w2_css}

/* ====================================================================== */
/* ★3. W3 table variants specific CSS (:root 除外、W1 canonical = degawa style.css 由来 と byte-match)★ */
/* ====================================================================== */
{w3_css}

/* ====================================================================== */
/* ★4. W4 form + input specific CSS (:root 除外、W1 canonical 使用)★ */
/* ====================================================================== */
{w4_css}

/* ====================================================================== */
/* ★5. catalog UI styles (W1 統合担当追加: catalog-header / .toc / .catalog-section-wrapper)★ */
/* ====================================================================== */
.catalog-header {{
    background: white;
    padding: 24px 32px;
    border-radius: 12px;
    margin-bottom: 24px;
    box-shadow: var(--shadow);
    border-top: 4px solid var(--primary-blue);
}}
.catalog-header h1 {{
    color: var(--primary-blue);
    margin: 0 0 8px 0;
    font-size: 1.75em;
}}
.catalog-header .subtitle {{
    color: var(--text-gray);
    font-size: 0.95em;
    margin: 0;
}}
.toc {{
    background: white;
    padding: 20px 32px;
    border-radius: 12px;
    margin-bottom: 24px;
    box-shadow: var(--shadow);
    border-left: 4px solid var(--accent-blue);
}}
.toc h3 {{
    color: var(--primary-blue-dark);
    margin: 0 0 12px 0;
    font-size: 1.05em;
}}
.toc ul {{
    list-style: none;
    padding: 0;
    margin: 0;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 8px 24px;
}}
.toc li {{ padding: 4px 0; }}
.toc a {{
    color: var(--primary-blue);
    text-decoration: none;
    font-weight: 500;
}}
.toc a:hover {{
    color: var(--primary-blue-dark);
    text-decoration: underline;
}}
.catalog-section-wrapper {{
    background: white;
    padding: 24px 32px;
    border-radius: 12px;
    margin-bottom: 24px;
    box-shadow: var(--shadow);
    scroll-margin-top: 16px;
}}
.catalog-section-wrapper > h2 {{
    color: var(--primary-blue);
    border-bottom: 3px solid var(--primary-blue);
    padding-bottom: 8px;
    margin: 0 0 16px 0;
    font-size: 1.5em;
}}
.pending-finding-badge {{
    background: #ea580c;
    color: white;
    font-size: 11px;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 4px;
    display: inline-block;
    margin-left: 12px;
    vertical-align: middle;
}}
</style>
</head>
<body>

<div class="container-fluid">
<div class="row">

<!-- ============================================================ -->
<!-- ★OUTER LEFT: W1 Sidebar (degawa zdo_drawer_menu literal、L52-71 from w1_layout_section.html)★ -->
<!-- ============================================================ -->
{w1_sidebar_html}

<!-- ============================================================ -->
<!-- ★OUTER RIGHT: main col (header sticky + main with catalog content)★ -->
<!-- ============================================================ -->
<div class="col-sm p-0 min-vh-100 bg-maincolor">

<!-- ★W1 Header literal (degawa sample_登録.html L419-435 byte-match)★ -->
{w1_header_html}

<main class="p-3">

<header class="catalog-header">
<h1>DIMCO パーツカタログ (degawa SSOT 起点)</h1>
<p class="subtitle">★cmd_225_redo 完成形 (2026-04-30)、degawa /mnt/g/.../degawa/007_部品一覧/ literal port★ — 編集時はここから コピペ → データ差替方式。worker 推測 SSOT (016/049/027) 採用 0 件。</p>
</header>

<nav class="toc">
<h3>目次 (Table of Contents)</h3>
<ul>
<li><a href="#section-layout">1. 共通レイアウト (sidebar + header sticky + footer absent finding + app-container)</a></li>
<li><a href="#section-modal-button">2. モーダル + ボタン (degawa .modal-card + button variants)</a></li>
<li><a href="#section-table">3. 表 (table) variants (10 patterns degawa 一覧テーブル.html literal) <span class="pending-finding-badge">PENDING: 二段ヘッダー</span></a></li>
<li><a href="#section-form-input">4. フォーム + input + バリデーション (degawa form-row + form-group)</a></li>
</ul>
</nav>

<!-- ====================================================================== -->
<!-- ★SECTION 1: 共通レイアウト (W1 documentation)★ -->
<!-- ====================================================================== -->
<section id="section-layout" class="catalog-section-wrapper">
<h2>1. 共通レイアウト (W1)</h2>
<p style="color: var(--text-gray); font-size: 0.9em; margin: 0 0 16px 0;">★本 catalog の outer wrapper (container-fluid + row > sidebar + main col) は本セクションで documented するレイアウト部品の literal 適用★。下記の .part-label entry はデモ参照、実物はページ全体に既に rendered されています。</p>

<div class="part-label">サイドバー (zdo_drawer_menu) — degawa SSOT (本ページ全体で functional 動作中)</div>
<div class="part-demo-area">
<p style="color: var(--text-gray); margin: 0;">★左カラムの zdo_drawer_menu が functional sidebar (本ページ全体で動作中)★、ハンバーガー click で drawer 開閉、960px breakpoint でアイコンナビ ↔ ハンバーガー 切替。canonical: degawa 007_部品一覧/sample_登録.html L382-413 + assets/zdo_drawer_menu.css 全 145 行 + zdo_drawer_menu.js 全 49 行。</p>
</div>

<div class="part-label">ヘッダー (sticky、ロゴ + dropdown) — degawa SSOT (本ページ最上段で functional 動作中)</div>
<div class="part-demo-area">
<p style="color: var(--text-gray); margin: 0;">★最上段の header が functional sticky header (本ページで動作中)★、background var(--primary-blue) #005DA8、左 logo + 右 user dropdown。canonical: degawa sample_登録.html L419-435 + style.css L714-767 (sticky + 960px responsive)。</p>
</div>

<div class="part-label">フッター — degawa 不在 (audit finding)</div>
<div class="part-demo-area">
<p style="color: var(--text-gray); font-style: italic; margin: 0;">degawa SSOT で page-level footer 不在 (DIMCO 既存 file も同様)。catalog では本 finding を documentation 化、独自 footer 追加禁止。</p>
</div>

<div class="part-label">app-container 構造 (Bootstrap container-fluid + row 2 col layout) — degawa SSOT</div>
<div class="part-demo-area">
<pre style="background: #f8f9fa; padding: 12px; border-radius: 6px; overflow-x: auto; font-size: 12px; margin: 0;"><code>&lt;body&gt;
  &lt;div class="container-fluid"&gt;
    &lt;div class="row"&gt;
      &lt;!-- 左サイドバー --&gt;
      &lt;div class="col-sm-auto bg-navy sticky-top"&gt;
        &lt;!-- zdo_drawer_menu HTML --&gt;
      &lt;/div&gt;
      &lt;!-- 右メインカラム --&gt;
      &lt;div class="col-sm p-0 min-vh-100 bg-maincolor"&gt;
        &lt;header&gt;...&lt;/header&gt;  &lt;!-- sticky header --&gt;
        &lt;main class="p-3"&gt;...&lt;/main&gt;  &lt;!-- page content (TOC + 4 sections) --&gt;
      &lt;/div&gt;
    &lt;/div&gt;
  &lt;/div&gt;
&lt;/body&gt;</code></pre>
</div>
</section>

<!-- ====================================================================== -->
<!-- ★SECTION 2: モーダル + ボタン (W2 degawa SSOT)★ -->
<!-- ====================================================================== -->
<section id="section-modal-button" class="catalog-section-wrapper">
<h2>2. モーダル + ボタン (degawa .modal-card)</h2>

{w2_body}

</section>

<!-- ====================================================================== -->
<!-- ★SECTION 3: 表 (table) variants (W3 degawa SSOT、★PENDING finding 二段ヘッダー★)★ -->
<!-- ====================================================================== -->
<section id="section-table" class="catalog-section-wrapper">
<h2>3. 表 (table) variants <span class="pending-finding-badge">PENDING: 二段ヘッダー finding</span></h2>
<p style="color: var(--text-gray); font-size: 0.9em; margin: 0 0 16px 0;">★ご主人様明示懸念「二段ヘッダー table」 = degawa 一覧テーブル.html で literal 不在 finding★。詳細は本セクション末尾の Finding ブロックを参照、ご主人様確認 待機中。</p>

{w3_body}

</section>

<!-- ====================================================================== -->
<!-- ★SECTION 4: フォーム + input + バリデーション (W4 degawa SSOT)★ -->
<!-- ====================================================================== -->
<section id="section-form-input" class="catalog-section-wrapper">
<h2>4. フォーム + input + バリデーション</h2>

{w4_body}

</section>

</main>

</div>

</div>
</div>

<!-- Bootstrap Bundle JS (Bootstrap dropdown + drawer 動作用) -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>

<script>
/* ====================================================================== */
/* ★W1 zdo_drawer_menu.js (degawa assets/zdo_drawer_menu.js 全 49 行 literal)★ */
/* ====================================================================== */
{w1_inline_js}
</script>

<script>
/* ====================================================================== */
/* ★W2 modal + button JS★ */
/* ====================================================================== */
{w2_js}
</script>

<script>
/* ====================================================================== */
/* ★W4 form + input JS★ */
/* ====================================================================== */
{w4_js}
</script>

</body>
</html>
"""

    # Write
    TARGET.write_text(catalog, encoding="utf-8")
    line_count = catalog.count("\n") + 1
    byte_count = len(catalog.encode("utf-8"))
    print(f"[OK] Wrote {TARGET} ({line_count} lines, {byte_count:,} bytes)")


if __name__ == "__main__":
    main()
