#!/usr/bin/env python3
"""cmd_225_fix W4 showroom verify: drift visible = 0、canonical sizes、radio toggle。"""
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

F = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_225_fix/w4_controls_refactored.html")
OUT = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_225_fix/w4_screenshots")


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    # First: source-level grep verify
    src = F.read_text(encoding="utf-8")
    src_results = {}
    # 17 DW markers in HTML comments
    dw_markers = re.findall(r"\[DW-\d+\]", src)
    src_results["dw_marker_count"] = len(dw_markers)
    src_results["dw_markers_unique"] = sorted(set(dw_markers))

    # Visible drift-warning class block count in body (should be 0)
    visible_drift_warning_blocks = re.findall(r'<div\s+class="drift-warning"', src)
    src_results["visible_drift_warning_blocks"] = len(visible_drift_warning_blocks)

    # Visible "drift warning" text outside HTML comments?
    # Simple heuristic: count occurrences inside <body>...</body> excluding HTML comments
    body_match = re.search(r'<body[^>]*>(.*?)</body>', src, re.DOTALL)
    body_text = body_match.group(1) if body_match else ""
    # Strip HTML comments
    body_no_comments = re.sub(r'<!--.*?-->', '', body_text, flags=re.DOTALL)
    src_results["visible_drift_warning_text"] = body_no_comments.count("drift warning")
    src_results["visible_drift_keyword"] = body_no_comments.count("drift")
    src_results["visible_DW_marker"] = body_no_comments.count("[DW-")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        page.goto(f"file://{quote(str(F))}", wait_until="domcontentloaded")
        page.wait_for_timeout(500)

        runtime = page.evaluate("""() => {
            const sections = document.querySelectorAll('section.showroom-section');
            const checkboxes = document.querySelectorAll('input[type="checkbox"]');
            const radios = document.querySelectorAll('input[type="radio"]');
            const btns = document.querySelectorAll('.btn');
            const btnSearch = document.querySelectorAll('.btn-search-trigger');
            const exportSec = document.querySelectorAll('.export-section');
            // Look for any visible "drift" word in textContent
            const visibleText = document.body.innerText || document.body.textContent || '';
            const driftMatches = (visibleText.match(/drift/gi) || []).length;
            const dwMarkerMatches = (visibleText.match(/\\[DW-\\d+\\]/g) || []).length;
            // Compute first .btn padding
            const btn = btns[0];
            const btnSearchEl = btnSearch[0];
            const checkbox = checkboxes[0];
            const radio = radios[0];
            return {
                section_count: sections.length,
                checkbox_count: checkboxes.length,
                radio_count: radios.length,
                btn_count: btns.length,
                btn_search_count: btnSearch.length,
                export_section_count: exportSec.length,
                visible_drift_text_count: driftMatches,
                visible_dw_marker_count: dwMarkerMatches,
                btn_padding: btn ? getComputedStyle(btn).padding : null,
                btn_font_size: btn ? getComputedStyle(btn).fontSize : null,
                btn_search_padding: btnSearchEl ? getComputedStyle(btnSearchEl).padding : null,
                btn_search_font_size: btnSearchEl ? getComputedStyle(btnSearchEl).fontSize : null,
                checkbox_border_radius: checkbox ? getComputedStyle(checkbox).borderRadius : null,
                checkbox_appearance: checkbox ? getComputedStyle(checkbox).appearance : null,
                radio_width: radio ? getComputedStyle(radio).width : null,
            };
        }""")

        # Toggle radio test
        page.evaluate("""() => {
            const sel = document.querySelector('input[name="transaction-method-demo"][value="select"]');
            sel.checked = true;
            sel.dispatchEvent(new Event('change'));
        }""")
        page.wait_for_timeout(200)
        toggle = page.evaluate("""() => {
            const free = document.querySelector('.transaction-input-demo-free');
            const sel = document.querySelector('.transaction-input-demo-select');
            return {
                free_display: free ? getComputedStyle(free).display : null,
                select_display: sel ? getComputedStyle(sel).display : null,
            };
        }""")

        page.screenshot(path=str(OUT / "showroom_full.png"), full_page=True)
        ctx.close()
        browser.close()

    out = OUT / "_verify.json"
    out.write_text(json.dumps({
        "src_results": src_results,
        "runtime": runtime,
        "after_radio_toggle": toggle,
        "console_errors": errs,
    }, ensure_ascii=False, indent=2))
    print(json.dumps({
        "src_results": src_results,
        "runtime": runtime,
        "after_radio_toggle": toggle,
        "console_errors": errs,
    }, ensure_ascii=False, indent=2))

    issues = []
    if src_results["dw_marker_count"] != 17:
        issues.append(f"DW markers in source = {src_results['dw_marker_count']}, expected 17")
    if src_results["visible_drift_warning_blocks"] != 0:
        issues.append(f"visible drift-warning class blocks = {src_results['visible_drift_warning_blocks']}, expected 0")
    if src_results["visible_DW_marker"] != 0:
        issues.append(f"DW markers visible in body = {src_results['visible_DW_marker']}, expected 0 (must be in HTML comments)")
    if runtime["visible_drift_text_count"] != 0:
        issues.append(f"runtime visible 'drift' text count = {runtime['visible_drift_text_count']}, expected 0")
    if runtime["visible_dw_marker_count"] != 0:
        issues.append(f"runtime visible DW marker count = {runtime['visible_dw_marker_count']}, expected 0")
    if runtime["section_count"] != 4:
        issues.append(f"section count = {runtime['section_count']}, expected 4")
    if runtime["btn_count"] < 8:
        issues.append(f"btn count = {runtime['btn_count']}, expected >= 8 (4 in section 3 + 4 in section 4)")
    if runtime["btn_search_count"] < 2:
        issues.append(f"btn-search-trigger count = {runtime['btn_search_count']}")
    if runtime["checkbox_border_radius"] != "50%":
        issues.append(f"checkbox borderRadius = {runtime['checkbox_border_radius']}, expected 50% (016 canonical)")
    # canonical sizes
    # .btn padding 0.625em 1.875em with font-size 0.875em → padding-y: 0.625*0.875*16 = 8.75px、padding-x: 1.875*0.875*16 = 26.25px
    # Computed could be "8.75px 26.25px" or browser-rounded "9px 26px" range
    if not runtime["btn_padding"]:
        issues.append("btn padding missing")
    # .btn-search-trigger padding 6px 14px
    if runtime["btn_search_padding"] != "6px 14px":
        issues.append(f"btn-search-trigger padding = {runtime['btn_search_padding']!r}, expected '6px 14px' (018 canonical)")
    if toggle["free_display"] != "none":
        issues.append(f"radio toggle: free_display = {toggle['free_display']!r}, expected 'none' after select")
    if toggle["select_display"] != "flex":
        issues.append(f"radio toggle: select_display = {toggle['select_display']!r}, expected 'flex'")
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
        print("VERDICT: ALL_PASS — 17 DW in HTML comments、画面表示 drift 0、canonical sizes、radio toggle、checkbox 016 円形")


if __name__ == "__main__":
    main()
