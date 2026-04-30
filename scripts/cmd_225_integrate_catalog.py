#!/usr/bin/env python3
"""cmd_225 4 section → dimco-parts-catalog.html integration.

Phase 0 audit findings:
- W1 (452 lines): no doctype, layout (sidebar+page-header+footer audit). Section comments + style/script blocks inline.
- W2 (620 lines): no doctype, 5 modal byte-identical (id: customer/enduser/hanbaiten/product/supplierSearchModal).
- W3 (481 lines): FULL doctype + head/body. :root at L8-21, base styles L22-25, body L28-480.
- W4 (563 lines): FULL doctype + head/body. :root at L17-30, head <style> L16-159 (catalog UI + checkbox/radio/button/page-header-demo CSS), body L161-562.

Strategy:
- catalog-level :root = W3 :root (literal port, identical to W4 :root by design)
- catalog-level base styles = W3 base + W4 head <style> (excluding :root duplicate)
- W1/W2 body-only sections (already no head wrapper)
- W3 body L28-480 (strip <h1>"W3 Section" L30-31 internal header → keep h2 onwards)
- W4 body L161-562 (strip <h1>"W4 Section" L163-166 internal header)
"""
import re
from pathlib import Path

CMD225_DIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_225")
TARGET = Path("/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new/dimco-parts-catalog.html")


def read_section(name: str) -> str:
    return (CMD225_DIR / f"{name}_section.html").read_text(encoding="utf-8")


def extract_w3_root_and_base() -> str:
    """W3 head <style> 内の :root + base styles を抽出 (L8-25)."""
    w3 = read_section("w3").splitlines()
    # L7 = '/* ===== W3 Section 全体 base ===== */'
    # L8-21 = :root block
    # L22-25 = body/.catalog-section/h2/.demo-area
    # L26 = </style>
    return "\n".join(w3[6:25])  # 0-indexed: L7-L25


def extract_w4_head_styles_no_root() -> str:
    """W4 head <style> から :root 以外の全 CSS を抽出 (L31-159、catalog UI + control CSS)."""
    w4 = read_section("w4").splitlines()
    # L17-30 = :root block (skip)
    # L31-158 = base body/.catalog-section + checkbox + radio + button + page-header-demo CSS
    # L159 = </style>
    return "\n".join(w4[30:158])  # 0-indexed: L31-L158


def extract_w1_full() -> str:
    """W1 section: layout (no doctype, no <h1> wrapper).

    ★Integration fix★: W1 section の sidebar toggle script (L281-292) は hamburgerBtn HTML より前に
    配置されているため、catalog 統合時に script 実行時点で hamburgerBtn が未パース → null reference error。
    016 SSOT 原典では script が body 末尾にあるため起きないが、W1 section 化で順序が変わった。
    integration step で DOMContentLoaded wrapper を追加して defer 実行に変更 (literal 改変ではなく
    実行 timing 保証のための defensive wrap、機能 contract 100% 保持)。
    """
    content = read_section("w1")
    # Wrap the sidebar open/close <script> block in DOMContentLoaded
    old_script = """<script>
/* ★sidebar JS literal copy from new横/016_受注一覧.html L2282-2342 (byte-match)★ */
// Sidebar open/close
document.getElementById('hamburgerBtn').addEventListener('click', function() {
    document.getElementById('sidebar').classList.add('open');
    document.getElementById('sidebarOverlay').classList.add('open');
});
document.getElementById('sidebarOverlay').addEventListener('click', function() {
    document.getElementById('sidebar').classList.remove('open');
    document.getElementById('sidebarOverlay').classList.remove('open');
});
</script>"""
    new_script = """<script>
/* ★sidebar JS literal copy from new横/016_受注一覧.html L2282-2342 (byte-match)★ */
/* ★cmd_225 integration fix★: catalog 統合時に script 実行順序問題回避のため DOMContentLoaded wrap 追加 (016 原典では body 末尾配置で OK だった) */
document.addEventListener('DOMContentLoaded', function() {
    // Sidebar open/close
    document.getElementById('hamburgerBtn').addEventListener('click', function() {
        document.getElementById('sidebar').classList.add('open');
        document.getElementById('sidebarOverlay').classList.add('open');
    });
    document.getElementById('sidebarOverlay').addEventListener('click', function() {
        document.getElementById('sidebar').classList.remove('open');
        document.getElementById('sidebarOverlay').classList.remove('open');
    });
});
</script>"""
    if old_script not in content:
        raise RuntimeError("W1 sidebar toggle script signature changed; integration fix needs update")
    return content.replace(old_script, new_script, 1)


def extract_w2_full() -> str:
    """W2 section: 5 modal (no doctype)."""
    return read_section("w2")


def extract_w3_body() -> str:
    """W3 body L28-480 から W3-internal <h1>+<p> を除外 (L30-31)、<h2> 以降を抽出."""
    w3 = read_section("w3").splitlines()
    # L28 = <body>
    # L29 = (空行)
    # L30 = <h1>DIMCO Parts Catalog — W3 Section</h1>
    # L31 = <p style="...">Collapsible + フォーム部品 SSOT ...</p>
    # L32-479 = section content
    # L480 = </body>
    # L481 = </html>
    return "\n".join(w3[31:479])  # 0-indexed: L32-L479 (skip <body> + W3 header, keep section comment+content)


def extract_w4_body() -> str:
    """W4 body L161-562 から W4-internal <h1> wrapper を除外 (L163-166)、section content 抽出."""
    w4 = read_section("w4").splitlines()
    # L161 = <body>
    # L162 = (空行)
    # L163-166 = <h1 ...>DIMCO Parts Catalog — W4 Section <small>...</small></h1>
    # L167-561 = section content
    # L562 = </body>
    # L563 = </html>
    return "\n".join(w4[166:561])  # 0-indexed: L167-L561


def build_catalog() -> str:
    w3_root_and_base = extract_w3_root_and_base()
    w4_head_styles = extract_w4_head_styles_no_root()
    w1_section = extract_w1_full()
    w2_section = extract_w2_full()
    w3_section_body = extract_w3_body()
    w4_section_body = extract_w4_body()

    catalog = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DIMCO パーツカタログ (PERMANENT rule SSOT、cmd_225 完成形)</title>
<!--
============================================================
  DIMCO パーツカタログ — cmd_225 完成形
  作成日: 2026-04-30
  作成者: 4 worker 共同 (W1=layout / W2=modals / W3=collapsible+forms / W4=controls+drift)
  統合: kashira から W1 (1号猫) に delegate、subtask_225_005_w1_integration
  spec: outputs/dimco-prototype/cmd_225/spec.md
  PERMANENT rule: memory/project_dimco_permanent_rule_component_reuse.md
  方針: 016 SSOT (cmd_217 真 SSOT 揃え達成済) を baseline として全部品 literal port、
        編集時はここから コピペ → データ差替方式 (個別 file fix 集合体方式から脱却)
  self-contained: ✓ 外部 file ref 0、browser 単体動作
============================================================
-->
<style>
/* ====================================================================== */
/* ★ catalog-level :root + base styles (W3 section L7-25 から literal port) ★ */
/* W4 :root (L17-30) と byte-identical 確認済、duplicate 排除 */
/* ====================================================================== */
{w3_root_and_base}

/* ====================================================================== */
/* ★ catalog-level UI styles (W4 section L31-158 から literal port) ★ */
/* checkbox + radio + button + .page-header-demo + .catalog-section + .drift-warning + .usage-guide */
/* :root duplicate は除外、base styles は W3 と一部重複あるが W4 値を優先 (より詳細) */
/* ====================================================================== */
{w4_head_styles}

/* ====================================================================== */
/* ★ catalog-level navigation TOC + section header styles (W1 統合担当追加) ★ */
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
    font-size: 1.875em;
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
    margin-bottom: 32px;
    box-shadow: var(--shadow);
    border-left: 4px solid var(--secondary-blue);
}}
.toc h3 {{
    color: var(--primary-blue-dark);
    margin: 0 0 12px 0;
    font-size: 1.1em;
}}
.toc ul {{
    list-style: none;
    padding: 0;
    margin: 0;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 8px 24px;
}}
.toc li {{
    padding: 4px 0;
}}
.toc a {{
    color: var(--primary-blue);
    text-decoration: none;
    font-weight: 500;
    transition: color 0.2s;
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
    font-size: 1.625em;
}}
</style>
</head>
<body>

<header class="catalog-header">
<h1>DIMCO パーツカタログ</h1>
<p class="subtitle">★PERMANENT rule SSOT、cmd_225 完成形 (2026-04-30)★ — 編集時はここから コピペ → データ差替方式。全部品 016 横版/縦版 SSOT (cmd_217 真 SSOT 揃え達成済) から literal port。</p>
</header>

<nav class="toc">
<h3>目次 (Table of Contents)</h3>
<ul>
<li><a href="#section-layout">1. 共通レイアウト (W1: sidebar + page-header sticky + footer audit)</a></li>
<li><a href="#section-collapsible-form">2. Collapsible + フォーム部品 (W3: アコーディオン / excel-table / form-row / input / 期待度 4 値)</a></li>
<li><a href="#section-modal">3. モーダル 5 種 (W2: 仕入先 / 商品 / 得意先 / 販売店 / エンドユーザ、018 byte-identical)</a></li>
<li><a href="#section-controls-drift">4. コントロール + 過去 drift 警告 (W4: checkbox / radio / button / .export-section + 17 drift warning)</a></li>
</ul>
</nav>

<!-- ====================================================================== -->
<!-- ★SECTION 1: 共通レイアウト (W1)★ -->
<!-- ====================================================================== -->
<section id="section-layout" class="catalog-section-wrapper">
<h2>1. 共通レイアウト (W1)</h2>

{w1_section}

</section>

<!-- ====================================================================== -->
<!-- ★SECTION 2: Collapsible + フォーム部品 (W3)★ -->
<!-- ====================================================================== -->
<section id="section-collapsible-form" class="catalog-section-wrapper">
<h2>2. Collapsible + フォーム部品 (W3)</h2>

{w3_section_body}

</section>

<!-- ====================================================================== -->
<!-- ★SECTION 3: モーダル 5 種 (W2)★ -->
<!-- ====================================================================== -->
<section id="section-modal" class="catalog-section-wrapper">
<h2>3. モーダル 5 種 (W2)</h2>

{w2_section}

</section>

<!-- ====================================================================== -->
<!-- ★SECTION 4: コントロール + 過去 drift 警告 (W4)★ -->
<!-- ====================================================================== -->
<section id="section-controls-drift" class="catalog-section-wrapper">
<h2>4. コントロール + 過去 drift 警告 (W4)</h2>

{w4_section_body}

</section>

</body>
</html>
"""
    return catalog


def main():
    # Verify W3/W4 :root byte-identical (sanity check)
    w3 = read_section("w3").splitlines()
    w4 = read_section("w4").splitlines()
    w3_root = "\n".join(w3[7:21])  # L8-21
    w4_root = "\n".join(w4[16:30])  # L17-30
    if w3_root.strip() != w4_root.strip():
        print("[WARN] W3 and W4 :root NOT byte-identical, manual reconcile may be needed:")
        print(f"  W3 (lines 8-21):\n{w3_root}")
        print(f"  W4 (lines 17-30):\n{w4_root}")
    else:
        print("[OK] W3 and W4 :root byte-identical (W3 used as catalog :root canonical)")

    # Verify modal id uniqueness (W2)
    w2 = read_section("w2")
    modal_ids = re.findall(r'id="(\w+SearchModal)"', w2)
    if len(modal_ids) != len(set(modal_ids)):
        print(f"[ERROR] W2 modal id duplicates detected: {modal_ids}")
    else:
        print(f"[OK] W2 modal ids unique: {sorted(set(modal_ids))}")

    # Build catalog
    catalog = build_catalog()
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(catalog, encoding="utf-8")

    line_count = catalog.count("\n") + 1
    byte_count = len(catalog.encode("utf-8"))
    print(f"[OK] Wrote {TARGET} ({line_count} lines, {byte_count:,} bytes)")


if __name__ == "__main__":
    main()
