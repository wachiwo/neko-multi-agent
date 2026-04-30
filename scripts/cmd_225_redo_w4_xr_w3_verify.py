#!/usr/bin/env python3
"""cmd_225_redo W4 XR of W3 table variants: section + 二段ヘッダー finding independent verify."""
from __future__ import annotations
import os
import sys
import json
import re
from pathlib import Path
from urllib.parse import quote

LIBASOUND_PATHS = [
    "/tmp/libasound/usr/lib/x86_64-linux-gnu/libasound.so.2",
    "/tmp/libasound_extract/usr/lib/x86_64-linux-gnu/libasound.so.2",
]
if not os.environ.get("LD_PRELOAD"):
    for p in LIBASOUND_PATHS:
        if os.path.exists(p):
            os.environ["LD_PRELOAD"] = p
            break

from playwright.sync_api import sync_playwright

CATALOG = Path("/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new/dimco-parts-catalog.html")
W3_SOURCE = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_225_redo/w3_table_variants_section.html")
DEGAWA = Path("/mnt/g/共有ドライブ/[PJ]ディムコ/01_再構築プロジェクト/90_personal/degawa/007_部品一覧/一覧テーブル.html")
OUT = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_225_redo/w4_xr_w3_screenshots")


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    # ===== Source-level audit =====
    degawa_src = DEGAWA.read_text(encoding="utf-8")
    w3_src = W3_SOURCE.read_text(encoding="utf-8")
    catalog_src = CATALOG.read_text(encoding="utf-8")

    src_results = {}

    # 1. 二段ヘッダー pattern in degawa
    src_results["degawa_rowspan_2_count"] = len(re.findall(r'rowspan=["\']?2', degawa_src))
    src_results["degawa_rowspan_3_count"] = len(re.findall(r'rowspan=["\']?3', degawa_src))
    # thead with 2+ <tr> rows
    multi_tr_thead = 0
    for m in re.finditer(r'<thead[^>]*>(.*?)</thead>', degawa_src, re.DOTALL):
        tr_count = len(re.findall(r'<tr', m.group(1)))
        if tr_count >= 2:
            multi_tr_thead += 1
    src_results["degawa_multi_tr_thead_count"] = multi_tr_thead
    src_results["degawa_total_thead_count"] = len(re.findall(r'<thead', degawa_src))
    src_results["degawa_total_lines"] = len(degawa_src.splitlines())

    # 2. W3 source: 10 part-label + table count
    src_results["w3_part_label_count"] = len(re.findall(r'class="part-label"', w3_src))
    src_results["w3_table_count"] = len(re.findall(r'<table', w3_src))
    src_results["w3_canonical_lineref_count"] = len(re.findall(r'degawa.*L\d+', w3_src))
    # W3 二段ヘッダー finding section presence
    src_results["w3_finding_section_present"] = bool(re.search(r'二段ヘッダー.*literal 不在', w3_src))

    # 3. catalog: PENDING 3-layer trigger
    src_results["catalog_toc_pending_badge"] = len(re.findall(r'PENDING.*二段ヘッダー', catalog_src))
    src_results["catalog_section_h2_pending"] = bool(re.search(r'<h2>3\. 表 \(table\) variants <span class="pending-finding-badge">PENDING', catalog_src))
    src_results["catalog_finding_block_present"] = bool(re.search(r'finding A.*degawa.*不在', catalog_src, re.DOTALL))

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        page.goto(f"file://{quote(str(CATALOG))}", wait_until="domcontentloaded")
        page.wait_for_timeout(800)

        runtime = page.evaluate("""() => {
            const sec = document.getElementById('section-table');
            if (!sec) return null;
            const partLabels = sec.querySelectorAll('.part-label');
            const tables = sec.querySelectorAll('table');
            const orderTables = sec.querySelectorAll('table.order-table');
            const childTables = sec.querySelectorAll('table.child-table');
            const grandchildTables = sec.querySelectorAll('table.grandchild-table');
            const statusBadges = sec.querySelectorAll('.status-badge');
            const approvalStatuses = sec.querySelectorAll('.approval-status');
            const linkButtons = sec.querySelectorAll('.link-button');
            const tableCustomBg = sec.querySelectorAll('.table-custom-bg');
            const visuallyHidden = sec.querySelectorAll('.visually-hidden');
            const stickyTheads = sec.querySelectorAll('thead');
            // Check: any thead has multi <tr> rows?
            let multiTrTheadCount = 0;
            stickyTheads.forEach(t => {
                if (t.querySelectorAll('tr').length >= 2) multiTrTheadCount++;
            });
            // Pending finding badge in section
            const pendingBadges = sec.querySelectorAll('.pending-finding-badge');
            return {
                section_present: sec !== null,
                part_label_count: partLabels.length,
                table_count: tables.length,
                order_table_count: orderTables.length,
                child_table_count: childTables.length,
                grandchild_table_count: grandchildTables.length,
                status_badge_count: statusBadges.length,
                approval_status_count: approvalStatuses.length,
                link_button_count: linkButtons.length,
                table_custom_bg_count: tableCustomBg.length,
                visually_hidden_count: visuallyHidden.length,
                thead_count: stickyTheads.length,
                multi_tr_thead_count_in_catalog: multiTrTheadCount,
                pending_badge_count_in_section: pendingBadges.length,
            };
        }""")

        page.screenshot(path=str(OUT / "section_table_view.png"), full_page=False)
        ctx.close()
        browser.close()

    out = OUT / "_verify.json"
    out.write_text(json.dumps({
        "src_results": src_results,
        "runtime": runtime,
        "console_errors": errs,
    }, ensure_ascii=False, indent=2))
    print(json.dumps({
        "src_results": src_results,
        "runtime": runtime,
        "console_errors": errs,
    }, ensure_ascii=False, indent=2))

    issues = []
    # CRITICAL: W3 finding factually correct
    if src_results["degawa_rowspan_2_count"] != 0:
        issues.append(f"★W3 finding 反証★: degawa rowspan=2 count = {src_results['degawa_rowspan_2_count']}")
    if src_results["degawa_rowspan_3_count"] != 0:
        issues.append(f"★W3 finding 反証★: degawa rowspan=3 count = {src_results['degawa_rowspan_3_count']}")
    if src_results["degawa_multi_tr_thead_count"] != 0:
        issues.append(f"★W3 finding 反証★: degawa multi-tr thead count = {src_results['degawa_multi_tr_thead_count']}")
    # 10 part-label
    if src_results["w3_part_label_count"] < 10:
        issues.append(f"W3 part-label count = {src_results['w3_part_label_count']}, expected >= 10")
    # 10 line refs
    if src_results["w3_canonical_lineref_count"] < 10:
        issues.append(f"W3 canonical line ref count = {src_results['w3_canonical_lineref_count']}, expected >= 10")
    # PENDING 3-layer trigger
    if src_results["catalog_toc_pending_badge"] < 1:
        issues.append("catalog TOC PENDING badge missing")
    if not src_results["catalog_section_h2_pending"]:
        issues.append("catalog Section h2 PENDING badge missing")
    if not src_results["catalog_finding_block_present"]:
        issues.append("catalog finding A/B/C block missing")
    # Runtime in catalog
    if runtime is None:
        issues.append("section-table not found in catalog")
    else:
        if runtime["multi_tr_thead_count_in_catalog"] != 0:
            issues.append(f"catalog runtime multi-tr thead = {runtime['multi_tr_thead_count_in_catalog']}, expected 0")
        if runtime["pending_badge_count_in_section"] < 1:
            issues.append(f"section pending badge = {runtime['pending_badge_count_in_section']}")
        if runtime["part_label_count"] < 10:
            issues.append(f"section part-label = {runtime['part_label_count']}, expected >= 10")
    if errs:
        issues.append(f"console errors: {errs}")

    print()
    print("=" * 60)
    if issues:
        print("VERDICT: ISSUES FOUND")
        for i in issues:
            print(f"  - {i}")
        sys.exit(1)
    else:
        print("VERDICT: ALL_PASS — 二段ヘッダー finding factually correct + 10 variants line ref + PENDING 3-layer trigger 完備")


if __name__ == "__main__":
    main()
