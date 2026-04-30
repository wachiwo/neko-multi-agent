#!/usr/bin/env python3
"""cmd_225 W4 XR W3 collapsible+form section verify."""
from __future__ import annotations
import os
import sys
import json
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

F = Path("/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new/dimco-parts-catalog.html")
OUT = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_225/w4_xr_w3_screenshots")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        page.goto(f"file://{quote(str(F))}", wait_until="domcontentloaded")
        page.wait_for_timeout(500)

        probe = page.evaluate("""() => {
            const sec = document.getElementById('section-collapsible-form');
            if (!sec) return null;
            const collapsibleSections = sec.querySelectorAll('.collapsible-section');
            const collapsibleHeaders = sec.querySelectorAll('.collapsible-header');
            const collapsibleIndicators = sec.querySelectorAll('.collapsible-indicator');
            const excelTables = sec.querySelectorAll('table.excel-table');
            const formRows = sec.querySelectorAll('.form-row');
            const formFields = sec.querySelectorAll('.form-field');
            const orderProbSel = sec.querySelector('select#order-probability');
            const currentProbSel = sec.querySelector('select#current-probability');
            const orderProbOpts = orderProbSel ? Array.from(orderProbSel.options).map(o => o.value) : null;
            const currentProbOpts = currentProbSel ? Array.from(currentProbSel.options).map(o => o.value) : null;
            const textareas = sec.querySelectorAll('textarea');

            // Compute first .collapsible-header style
            const firstHeader = collapsibleHeaders[0];
            const headerStyle = firstHeader ? {
                bg: getComputedStyle(firstHeader).backgroundColor,
                cursor: getComputedStyle(firstHeader).cursor,
                fontSize: getComputedStyle(firstHeader).fontSize,
                tagName: firstHeader.tagName,
            } : null;

            return {
                section_present: sec !== null,
                collapsible_section_count: collapsibleSections.length,
                collapsible_header_count: collapsibleHeaders.length,
                collapsible_indicator_count: collapsibleIndicators.length,
                excel_table_count: excelTables.length,
                form_row_count: formRows.length,
                form_field_count: formFields.length,
                order_probability_options: orderProbOpts,
                current_probability_options: currentProbOpts,
                textarea_count: textareas.length,
                first_header_style: headerStyle,
            };
        }""")

        # Toggle test on first .collapsible-header in section
        page.evaluate("""() => {
            const sec = document.getElementById('section-collapsible-form');
            const header = sec.querySelector('.collapsible-header');
            if (header) header.click();
        }""")
        page.wait_for_timeout(500)
        after_first_click = page.evaluate("""() => {
            const sec = document.getElementById('section-collapsible-form');
            const header = sec.querySelector('.collapsible-header');
            const section = header.parentElement;
            const content = section.querySelector('.collapsible-content');
            return {
                header_collapsed: header.classList.contains('collapsed'),
                section_collapsed: section.classList.contains('collapsed'),
                content_collapsed: content ? content.classList.contains('collapsed') : null,
                content_max_height: content ? content.style.maxHeight : null,
            };
        }""")

        # Click again to toggle back
        page.evaluate("""() => {
            const sec = document.getElementById('section-collapsible-form');
            const header = sec.querySelector('.collapsible-header');
            if (header) header.click();
        }""")
        page.wait_for_timeout(500)
        after_second_click = page.evaluate("""() => {
            const sec = document.getElementById('section-collapsible-form');
            const header = sec.querySelector('.collapsible-header');
            const section = header.parentElement;
            const content = section.querySelector('.collapsible-content');
            return {
                header_collapsed: header.classList.contains('collapsed'),
                content_max_height: content ? content.style.maxHeight : null,
            };
        }""")

        page.screenshot(path=str(OUT / "w3_section_view.png"), full_page=False)
        ctx.close()
        browser.close()

    out = OUT / "_verify.json"
    out.write_text(json.dumps({
        "probe": probe,
        "after_first_click": after_first_click,
        "after_second_click": after_second_click,
        "console_errors": errs,
    }, ensure_ascii=False, indent=2))
    print(json.dumps({
        "probe": probe,
        "after_first_click": after_first_click,
        "after_second_click": after_second_click,
        "console_errors": errs,
    }, ensure_ascii=False, indent=2))

    issues = []
    expected_4_values = ["", "高い", "やや高い", "やや低い", "低い"]
    if probe["order_probability_options"] != expected_4_values:
        issues.append(f"order options drift: {probe['order_probability_options']}")
    if probe["current_probability_options"] != expected_4_values:
        issues.append(f"current options drift: {probe['current_probability_options']}")
    if probe["collapsible_section_count"] < 1:
        issues.append("no .collapsible-section in W3 section")
    if probe["excel_table_count"] < 1:
        issues.append("no .excel-table in W3 section")
    if probe["form_row_count"] < 1:
        issues.append("no .form-row in W3 section")
    if probe["textarea_count"] < 1:
        issues.append("no textarea in W3 section")
    # Toggle reversibility
    af = after_first_click
    as_ = after_second_click
    if af["header_collapsed"] == as_["header_collapsed"]:
        issues.append("toggle not reversible")
    if errs:
        issues.append(f"console errors: {errs}")

    print()
    print("=" * 50)
    if issues:
        print("VERDICT: ISSUES FOUND")
        for i in issues:
            print(f"  - {i}")
        sys.exit(1)
    else:
        print("VERDICT: ALL_PASS — W3 section self-contained 動作 + 4値完備 + toggle reversible")


if __name__ == "__main__":
    main()
