#!/usr/bin/env python3
"""cmd_225 W4 section catalog verify."""
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

F = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_225/w4_section.html")
OUT = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_225/w4_screenshots")


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
            const sections = document.querySelectorAll('section.catalog-section');
            const checkboxes = document.querySelectorAll('input[type="checkbox"]');
            const radios = document.querySelectorAll('input[type="radio"]');
            const btns = document.querySelectorAll('.btn');
            const btnSearchTriggers = document.querySelectorAll('.btn-search-trigger');
            const exportSections = document.querySelectorAll('.export-section');
            const driftWarnings = document.querySelectorAll('.drift-warning');
            const usageGuides = document.querySelectorAll('.usage-guide');
            const checkboxStyle = checkboxes[0] ? getComputedStyle(checkboxes[0]) : null;
            return {
                section_count: sections.length,
                checkbox_count: checkboxes.length,
                radio_count: radios.length,
                btn_count: btns.length,
                btn_search_trigger_count: btnSearchTriggers.length,
                export_section_count: exportSections.length,
                drift_warning_count: driftWarnings.length,
                usage_guide_count: usageGuides.length,
                first_checkbox_borderRadius: checkboxStyle ? checkboxStyle.borderRadius : null,
                first_checkbox_appearance: checkboxStyle ? checkboxStyle.appearance : null,
            };
        }""")

        # Toggle radio test
        page.evaluate("""() => {
            const sel = document.querySelector('input[name="transaction-method-demo"][value="select"]');
            sel.checked = true;
            sel.dispatchEvent(new Event('change'));
        }""")
        page.wait_for_timeout(200)
        after_radio = page.evaluate("""() => {
            const free = document.querySelector('.transaction-input-demo-free');
            const sel = document.querySelector('.transaction-input-demo-select');
            return {
                free_display: free ? getComputedStyle(free).display : null,
                select_display: sel ? getComputedStyle(sel).display : null,
            };
        }""")

        page.screenshot(path=str(OUT / "w4_section_full.png"), full_page=True)
        ctx.close()
        browser.close()

    out = OUT / "_verify.json"
    out.write_text(json.dumps({"probe": probe, "after_radio": after_radio, "console_errors": errs}, ensure_ascii=False, indent=2))
    print(json.dumps({"probe": probe, "after_radio": after_radio, "console_errors": errs}, ensure_ascii=False, indent=2))

    issues = []
    if probe["section_count"] != 5:
        issues.append(f"section_count = {probe['section_count']}, expected 5")
    if probe["radio_count"] != 2:
        issues.append(f"radio_count = {probe['radio_count']}, expected 2 (demo radio pair)")
    if probe["btn_count"] < 8:
        issues.append(f"btn_count = {probe['btn_count']}, expected >= 8")
    if probe["btn_search_trigger_count"] < 2:
        issues.append(f"btn_search_trigger_count = {probe['btn_search_trigger_count']}")
    if probe["first_checkbox_borderRadius"] != "50%":
        issues.append(f"checkbox borderRadius drift: {probe['first_checkbox_borderRadius']}")
    if probe["drift_warning_count"] < 8:
        issues.append(f"drift_warning_count = {probe['drift_warning_count']}, expected >= 8")
    if after_radio["free_display"] != "none":
        issues.append(f"radio toggle: free_display = {after_radio['free_display']!r}, expected none")
    if after_radio["select_display"] != "flex":
        issues.append(f"radio toggle: select_display = {after_radio['select_display']!r}, expected flex")
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
        print("VERDICT: ALL_PASS — catalog section self-contained 動作 + radio toggle + drift warnings >= 8")


if __name__ == "__main__":
    main()
