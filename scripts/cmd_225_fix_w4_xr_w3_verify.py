#!/usr/bin/env python3
"""cmd_225_fix W4 XR of W3 collapsible+form: source grep + Playwright runtime verify."""
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

F = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_225_fix/w3_collapsible_form_refactored.html")
OUT = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_225_fix/w4_xr_w3_screenshots")


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    src = F.read_text(encoding="utf-8")
    src_results = {}
    src_results["table_tag_count"] = len(re.findall(r"<table\b", src))
    body_match = re.search(r'<body[^>]*>(.*?)</body>', src, re.DOTALL)
    body = body_match.group(1) if body_match else ""
    body_no_html_comments = re.sub(r'<!--.*?-->', '', body, flags=re.DOTALL)
    src_results["visible_drift_keyword"] = body_no_html_comments.count("drift")
    src_results["visible_warning_marker"] = body_no_html_comments.count("⚠")
    # Note: <script> content remains in body_no_html_comments since it's not HTML comment
    # Strip script tags too
    body_no_script = re.sub(r'<script[^>]*>.*?</script>', '', body_no_html_comments, flags=re.DOTALL)
    src_results["visible_canonical_no_script"] = body_no_script.count("canonical")
    src_results["visible_drift_no_script"] = body_no_script.count("drift")
    src_results["visible_cmd_no_script"] = body_no_script.count("cmd_")
    src_results["visible_lineref_no_script"] = len(re.findall(r'L\d+-\d+', body_no_script))

    # Count expected 4 values (049 byte-match) per select
    options_4 = re.findall(r'<option value="(高い|やや高い|やや低い|低い)">', src)
    src_results["expected_4_values_total"] = len(options_4)

    # toggleSection 1-arg confirm
    src_results["toggleSection_1arg_def"] = len(re.findall(r"function toggleSection\(header\)", src))
    src_results["toggleSection_2arg_def"] = len(re.findall(r"function toggleSection\(\w+,\s*\w+\)", src))
    src_results["toggleSection_this_calls"] = len(re.findall(r"onclick=\"toggleSection\(this\)\"", src))

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        page.goto(f"file://{quote(str(F))}", wait_until="domcontentloaded")
        page.wait_for_timeout(500)

        runtime = page.evaluate("""() => {
            const sections = document.querySelectorAll('.catalog-section');
            const collapsibleSections = document.querySelectorAll('.collapsible-section');
            const collapsibleHeaders = document.querySelectorAll('.collapsible-header');
            const formRows = document.querySelectorAll('.form-row');
            const formFields = document.querySelectorAll('.form-field');
            const tables = document.querySelectorAll('table');
            const orderProb = document.getElementById('order-probability');
            const currentProb = document.getElementById('current-probability');
            const orderProbOpts = orderProb ? Array.from(orderProb.options).map(o => o.value) : null;
            const currentProbOpts = currentProb ? Array.from(currentProb.options).map(o => o.value) : null;
            const textareas = document.querySelectorAll('textarea');
            const visibleText = document.body.innerText || '';
            const driftMatches = (visibleText.match(/drift/gi) || []).length;
            const cmdMatches = (visibleText.match(/cmd_\\d+/g) || []).length;
            const lineRefMatches = (visibleText.match(/L\\d+-\\d+/g) || []).length;
            const firstHeader = collapsibleHeaders[0];
            return {
                catalog_section_count: sections.length,
                collapsible_section_count: collapsibleSections.length,
                collapsible_header_count: collapsibleHeaders.length,
                form_row_count: formRows.length,
                form_field_count: formFields.length,
                table_count: tables.length,
                order_probability_options: orderProbOpts,
                current_probability_options: currentProbOpts,
                textarea_count: textareas.length,
                visible_drift_text_count: driftMatches,
                visible_cmd_ref_count: cmdMatches,
                visible_line_ref_count: lineRefMatches,
                first_header_tag: firstHeader ? firstHeader.tagName : null,
                first_header_bg: firstHeader ? getComputedStyle(firstHeader).backgroundColor : null,
            };
        }""")

        # Toggle test
        page.evaluate("""() => {
            const header = document.querySelector('.collapsible-header');
            if (header) header.click();
        }""")
        page.wait_for_timeout(500)
        after_first = page.evaluate("""() => {
            const header = document.querySelector('.collapsible-header');
            const section = header.parentElement;
            const content = section.querySelector('.collapsible-content');
            return {
                header_collapsed: header.classList.contains('collapsed'),
                content_max_height: content ? content.style.maxHeight : null,
            };
        }""")
        page.evaluate("""() => {
            const header = document.querySelector('.collapsible-header');
            if (header) header.click();
        }""")
        page.wait_for_timeout(500)
        after_second = page.evaluate("""() => {
            const header = document.querySelector('.collapsible-header');
            const content = header.parentElement.querySelector('.collapsible-content');
            return {
                header_collapsed: header.classList.contains('collapsed'),
                content_max_height: content ? content.style.maxHeight : null,
            };
        }""")

        page.screenshot(path=str(OUT / "w3_section_view.png"), full_page=True)
        ctx.close()
        browser.close()

    out = OUT / "_verify.json"
    out.write_text(json.dumps({
        "src_results": src_results,
        "runtime": runtime,
        "after_first_click": after_first,
        "after_second_click": after_second,
        "console_errors": errs,
    }, ensure_ascii=False, indent=2))
    print(json.dumps({
        "src_results": src_results,
        "runtime": runtime,
        "after_first_click": after_first,
        "after_second_click": after_second,
        "console_errors": errs,
    }, ensure_ascii=False, indent=2))

    issues = []
    expected_4 = ["", "高い", "やや高い", "やや低い", "低い"]
    if runtime["order_probability_options"] != expected_4:
        issues.append(f"order options drift: {runtime['order_probability_options']}")
    if runtime["current_probability_options"] != expected_4:
        issues.append(f"current options drift: {runtime['current_probability_options']}")
    if runtime["table_count"] != 0:
        issues.append(f"runtime table count = {runtime['table_count']}, expected 0 (W3 scope_lock)")
    if src_results["table_tag_count"] != 0:
        issues.append(f"source table count = {src_results['table_tag_count']}, expected 0")
    if runtime["visible_drift_text_count"] != 0:
        issues.append(f"runtime visible drift text = {runtime['visible_drift_text_count']}, expected 0")
    if runtime["visible_cmd_ref_count"] != 0:
        issues.append(f"runtime visible cmd ref = {runtime['visible_cmd_ref_count']}, expected 0 (showroom)")
    if runtime["visible_line_ref_count"] != 0:
        issues.append(f"runtime visible line ref = {runtime['visible_line_ref_count']}, expected 0 (showroom)")
    if src_results["toggleSection_1arg_def"] != 1:
        issues.append(f"toggleSection 1-arg def count = {src_results['toggleSection_1arg_def']}, expected 1")
    if src_results["toggleSection_2arg_def"] != 0:
        issues.append(f"toggleSection 2-arg def count = {src_results['toggleSection_2arg_def']}, expected 0")
    if runtime["first_header_tag"] != "DIV":
        issues.append(f"first_header tag = {runtime['first_header_tag']}, expected DIV")
    # Toggle reversibility
    if after_first["header_collapsed"] == after_second["header_collapsed"]:
        issues.append("toggle not reversible")
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
        print("VERDICT: ALL_PASS — showroom 型 + 049 byte-match + table 0 + toggleSection 1-arg + reversible")


if __name__ == "__main__":
    main()
