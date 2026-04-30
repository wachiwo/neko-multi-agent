#!/usr/bin/env python3
"""cmd_225_fix Phase 2 reintegration: 5 sections → dimco-parts-catalog.html (商品ショールーム型).

Phase 0 audit findings:
- W1 cmd_225_fix tables (283 lines): no doctype, body-only. Section 1 .excel-table + Section 2 input width canonical showroom.
- W1 cmd_225 original layout (452 lines): no doctype, body-only. sidebar + page-header + footer audit.
- W2 cmd_225_fix modals (629 lines): FULL doctype + head + body. :root at L42 (8 vars, lowercase hex).
- W3 cmd_225_fix collapsible-form (368 lines): FULL doctype + head + body. :root at L18 (12 vars, capitalized, ★canonical SSOT★).
- W4 cmd_225_fix controls (404 lines): FULL doctype + head + body. :root at L28 (12 vars, byte-identical W3).

Integration strategy:
- catalog-level :root = W3 (literal port, 12 canonical vars per cmd_217 真 SSOT)
- W3 + W4 head <style> minus :root → catalog-level inline CSS (W3 base + W4 base, deduped where needed)
- W2 head <style> minus :root → catalog-level inline CSS (modal CSS)
- 5 sections: layout (W1 original) + collapsible-form (W3 fix) + tables (W1 fix) + modals (W2 fix) + controls-drift (W4 fix)
- DOMContentLoaded fix for sidebar script (cmd_225 教訓継続)
- TOC = 5 sections
"""
import re
from pathlib import Path

CMD225_DIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_225")
CMD225_FIX_DIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_225_fix")
TARGET = Path("/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new/dimco-parts-catalog.html")


def read_file(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def extract_w3_root_and_base() -> str:
    """W3 cmd_225_fix の head <style> 中身 (L17-127) を 1 個の str として返す。
    :root + base body/.section-title/.catalog-section/.demo-area/.demo-row/.demo-label/.demo-cell + collapsible CSS + form-row CSS。
    """
    w3 = read_file(CMD225_FIX_DIR / "w3_collapsible_form_refactored.html").splitlines()
    # L16 = <style>
    # L17-127 = CSS rules (incl. :root L18-31)
    # L128 = </style>
    return "\n".join(w3[16:127])  # 0-indexed L17-L127


def extract_w4_head_styles_no_root() -> str:
    """W4 cmd_225_fix の head <style> 中身から :root 以外を抽出 (L42-174)."""
    w4 = read_file(CMD225_FIX_DIR / "w4_controls_refactored.html").splitlines()
    # L27 = <style>
    # L28-41 = :root block (skip)
    # L42-174 = base body + checkbox/radio/button/page-header-demo/.drift-warning/.usage-guide CSS
    # L175 = </style>
    return "\n".join(w4[41:174])  # 0-indexed L42-L174


def extract_w2_head_styles_no_root() -> str:
    """W2 cmd_225_fix の head <style> 中身から :root 以外を抽出 (L51-95).
    W2 :root は 8 vars/lowercase で W3 12 vars/capitalized より少ないため除外、modal CSS のみ port。
    """
    w2 = read_file(CMD225_FIX_DIR / "w2_modals_refactored.html").splitlines()
    # L40 = <style>
    # L42-50 = :root (skip)
    # L51-95 = modal CSS + demo-row CSS
    # L96 = </style>
    return "\n".join(w2[50:95])  # 0-indexed L51-L95


def extract_w1_layout_full() -> str:
    """W1 cmd_225 original layout (refactor なし、そのまま keep) + DOMContentLoaded fix."""
    content = read_file(CMD225_DIR / "w1_section.html")
    # cmd_225 統合経験 (W1 自身) で適用した DOMContentLoaded fix を再適用
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
/* ★cmd_225 integration fix (W1 自身経験) ★: catalog 統合時 script 実行順序問題回避のため DOMContentLoaded wrap */
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
        raise RuntimeError("W1 cmd_225 sidebar toggle script signature changed; integration fix needs update")
    return content.replace(old_script, new_script, 1)


def extract_w1_tables() -> str:
    """W1 cmd_225_fix tables refactored (全 content、no doctype)."""
    return read_file(CMD225_FIX_DIR / "w1_tables_refactored.html")


def extract_w3_body() -> str:
    """W3 cmd_225_fix body 抽出 (L130-366、<body>+<h1>+<p> 除外)."""
    w3 = read_file(CMD225_FIX_DIR / "w3_collapsible_form_refactored.html").splitlines()
    # L130 = <body>
    # L131 = (空)
    # L132 = <h1>...</h1> (W3 internal title)
    # L133 = <p class="subtitle">...</p> (W3 internal subtitle)
    # L134-366 = section content
    # L367 = </body>
    # 注: W3 fix では table 部品が削除済 (W1 fix へ移管)
    return "\n".join(w3[133:366])  # 0-indexed L134-L366


def extract_w4_body() -> str:
    """W4 cmd_225_fix body 抽出 (L177-402、<body>+<h1>+intro 除外)."""
    w4 = read_file(CMD225_FIX_DIR / "w4_controls_refactored.html").splitlines()
    # L177 = <body>
    # 内部の W4 internal h1 + intro を除外、section content 抽出
    # 行範囲は実際のファイル内容で調整必要、ここでは body 内 first heading 後から </body> 直前まで
    content_start = None
    content_end = None
    for i, line in enumerate(w4):
        if i >= 177 and content_start is None:
            # Skip empty lines and W4 internal h1/intro
            stripped = line.strip()
            if stripped and not stripped.startswith("<h1") and not stripped.startswith("<p") and not stripped.startswith("<!--"):
                content_start = i
                break
    # body content end = "</body>" line index - 1
    for i, line in enumerate(w4):
        if line.strip() == "</body>":
            content_end = i
            break
    # If content_start detection failed, just use everything between body tags except first heading
    if content_start is None:
        content_start = 178  # fallback: line after <body>
    return "\n".join(w4[content_start:content_end]) if content_end else "\n".join(w4[content_start:])


def extract_w2_body() -> str:
    """W2 cmd_225_fix body 抽出 (L98-627、<body>+<h1>+subtitle 除外)."""
    w2 = read_file(CMD225_FIX_DIR / "w2_modals_refactored.html").splitlines()
    # L98 = <body>
    # 後続: W2 internal h1 + subtitle、その後 demo-row 群 + 5 modal
    content_start = None
    content_end = None
    for i, line in enumerate(w2):
        if i >= 98 and content_start is None:
            stripped = line.strip()
            if stripped and not stripped.startswith("<h1") and not stripped.startswith("<p") and not stripped.startswith("<!--"):
                content_start = i
                break
    for i, line in enumerate(w2):
        if line.strip() == "</body>":
            content_end = i
            break
    if content_start is None:
        content_start = 99
    return "\n".join(w2[content_start:content_end]) if content_end else "\n".join(w2[content_start:])


def build_catalog() -> str:
    w3_root_base = extract_w3_root_and_base()
    w4_head_styles = extract_w4_head_styles_no_root()
    w2_head_styles = extract_w2_head_styles_no_root()
    w1_layout = extract_w1_layout_full()
    w1_tables = extract_w1_tables()
    w3_body = extract_w3_body()
    w4_body = extract_w4_body()
    w2_body = extract_w2_body()

    catalog = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DIMCO パーツカタログ (商品ショールーム型、cmd_225_fix 完成形)</title>
<!--
============================================================
  DIMCO パーツカタログ — cmd_225_fix 商品ショールーム型完成形
  作成日: 2026-04-30
  作成者: 4 worker 共同 (W1=layout+tables / W2=modals / W3=collapsible+forms / W4=controls+drift)
  統合: kashira から W1 (1号猫) に delegate、subtask_225_fix_005_w1_reintegration
  spec: ご主人様 17:42 直接指摘『表にソースが来たり、縦幅小さいのに間違った部品が来たり』
  方針: 商品ショールーム型 = 説明 minimum、実物 maximum、画面 source 表示 0
  cmd_225 → cmd_225_fix 進化:
    - W1 layout: そのまま keep (cmd_225 オリジナル、refactor 不要)
    - W1 tables: ★NEW★ 表 (table) section 分離、showroom-card grid + audit metadata HTML コメント化
    - W2 modals: refactored (subtitle 等の不要 explanatory text 削除)
    - W3 collapsible-form: refactored (table 部品 W1 fix へ移管、内部 explanatory minimum 化)
    - W4 controls + drift: refactored (drift 17 件 HTML コメント化、画面表示 0)
  TOC: 4 sections → 5 sections (新 section-tables 追加)
  self-contained: ✓ 外部 file ref 0、browser 単体動作
============================================================
-->
<style>
/* ====================================================================== */
/* ★ catalog-level :root + base styles (W3 cmd_225_fix L17-127 から literal port) ★ */
/* W4 :root (L28-41) と byte-identical 確認済 (cmd_225 統合時の検証継続) */
/* W2 :root (8 vars, lowercase) は subset、W3 12 vars canonical で完全 cover */
/* ====================================================================== */
{w3_root_base}

/* ====================================================================== */
/* ★ catalog-level UI styles (W4 cmd_225_fix L42-174 から literal port、:root 除外)★ */
/* checkbox + radio + button + .page-header-demo + .drift-warning + .usage-guide + (W4 catalog-section override) */
/* ====================================================================== */
{w4_head_styles}

/* ====================================================================== */
/* ★ modal styles (W2 cmd_225_fix L51-95 から literal port、:root 除外)★ */
/* .modal-overlay + .modal-header + .modal-body + .modal-footer + .modal-btn + .modal-result-table */
/* ====================================================================== */
{w2_head_styles}

/* ====================================================================== */
/* ★ catalog-level header / TOC / section-wrapper (W1 統合担当追加) ★ */
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
<h1>DIMCO パーツカタログ (商品ショールーム型)</h1>
<p class="subtitle">★cmd_225_fix 完成形 (2026-04-30)、説明 minimum・実物 maximum★ — 編集時はここから コピペ → データ差替方式。全部品 016 横版/縦版 SSOT (cmd_217 真 SSOT 揃え達成済) から literal port、画面 source 表示 0。</p>
</header>

<nav class="toc">
<h3>目次 (Table of Contents)</h3>
<ul>
<li><a href="#section-layout">1. 共通レイアウト (sidebar + page-header sticky + footer audit)</a></li>
<li><a href="#section-collapsible-form">2. Collapsible + フォーム部品 (アコーディオン / form-row / input / textarea / 期待度 4 値)</a></li>
<li><a href="#section-tables">3. 表 (table) 部品 (excel-table + input width canonical 7 variant showroom)</a></li>
<li><a href="#section-modal">4. モーダル 5 種 (仕入先 / 商品 / 得意先 / 販売店 / エンドユーザ、018 byte-identical)</a></li>
<li><a href="#section-controls-drift">5. コントロール + 過去 drift 警告 (checkbox / radio / button / .export-section + 17 drift HTML コメント化)</a></li>
</ul>
</nav>

<!-- ====================================================================== -->
<!-- ★SECTION 1: 共通レイアウト (W1 cmd_225 original、refactor なし keep)★ -->
<!-- ====================================================================== -->
<section id="section-layout" class="catalog-section-wrapper">
<h2>1. 共通レイアウト</h2>

{w1_layout}

</section>

<!-- ====================================================================== -->
<!-- ★SECTION 2: Collapsible + フォーム部品 (W3 cmd_225_fix refactored、table 除外済)★ -->
<!-- ====================================================================== -->
<section id="section-collapsible-form" class="catalog-section-wrapper">
<h2>2. Collapsible + フォーム部品</h2>

{w3_body}

</section>

<!-- ====================================================================== -->
<!-- ★SECTION 3: 表 (table) 部品 (★NEW★ W1 cmd_225_fix 商品ショールーム型)★ -->
<!-- ====================================================================== -->
<section id="section-tables" class="catalog-section-wrapper">
<h2>3. 表 (table) 部品</h2>

{w1_tables}

</section>

<!-- ====================================================================== -->
<!-- ★SECTION 4: モーダル 5 種 (W2 cmd_225_fix refactored)★ -->
<!-- ====================================================================== -->
<section id="section-modal" class="catalog-section-wrapper">
<h2>4. モーダル 5 種</h2>

{w2_body}

</section>

<!-- ====================================================================== -->
<!-- ★SECTION 5: コントロール + 過去 drift 警告 (W4 cmd_225_fix refactored、drift 17 件 HTML コメント化済)★ -->
<!-- ====================================================================== -->
<section id="section-controls-drift" class="catalog-section-wrapper">
<h2>5. コントロール + 過去 drift 警告</h2>

{w4_body}

</section>

</body>
</html>
"""
    return catalog


def main():
    # Sanity: verify W3 == W4 :root byte-identical
    w3 = read_file(CMD225_FIX_DIR / "w3_collapsible_form_refactored.html").splitlines()
    w4 = read_file(CMD225_FIX_DIR / "w4_controls_refactored.html").splitlines()
    w3_root = "\n".join(w3[17:31])
    w4_root = "\n".join(w4[27:41])
    if w3_root.strip() != w4_root.strip():
        print("[WARN] W3 and W4 :root NOT byte-identical:")
        print(f"  W3:\n{w3_root}")
        print(f"  W4:\n{w4_root}")
    else:
        print("[OK] W3 ↔ W4 :root byte-identical (W3 used as catalog :root canonical)")

    # Modal id uniqueness (W2)
    w2 = read_file(CMD225_FIX_DIR / "w2_modals_refactored.html")
    modal_ids = re.findall(r'id="(\w+SearchModal)"', w2)
    if len(modal_ids) != len(set(modal_ids)):
        print(f"[ERROR] W2 modal id duplicates: {modal_ids}")
    else:
        print(f"[OK] W2 modal ids unique: {sorted(set(modal_ids))}")

    catalog = build_catalog()

    # Backup current catalog
    if TARGET.exists():
        backup = TARGET.with_suffix(".html.cmd_225_pre_fix_backup")
        backup.write_text(TARGET.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"[OK] Backup current catalog → {backup.name}")

    TARGET.write_text(catalog, encoding="utf-8")
    line_count = catalog.count("\n") + 1
    byte_count = len(catalog.encode("utf-8"))
    print(f"[OK] Wrote {TARGET} ({line_count} lines, {byte_count:,} bytes)")


if __name__ == "__main__":
    main()
