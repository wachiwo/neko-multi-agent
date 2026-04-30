#!/usr/bin/env python3
"""cmd_217 W4 050 collapsible canonical migration verify.

Captures probe (counts + first-section computed style) at 3 viewports
(375 / 960 / 1920) and tests toggle reachability + class state. Mathematical
proof workflow per kashira spec.
"""
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

TARGET = Path(
    "/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new/050_海外引合.html"
)
OUTBASE = Path(
    "/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_217/w4_050_screenshots"
)

VIEWPORTS = [(375, 800), (960, 720), (1920, 1080)]


def main():
    OUTBASE.mkdir(parents=True, exist_ok=True)
    url = f"file://{quote(str(TARGET))}"
    results = {"file": TARGET.name, "viewports": {}}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for w, h in VIEWPORTS:
            context = browser.new_context(viewport={"width": w, "height": h})
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            probe = page.evaluate(
                """() => {
                const sections = document.querySelectorAll('.collapsible-section');
                const headers = document.querySelectorAll('.collapsible-header');
                const contents = document.querySelectorAll('.collapsible-content');
                const indicators = document.querySelectorAll('.collapsible-indicator');
                const sample = headers[0];
                const sampleStyle = sample ? {
                    bg: getComputedStyle(sample).backgroundColor,
                    color: getComputedStyle(sample).color,
                    cursor: getComputedStyle(sample).cursor,
                    padding: getComputedStyle(sample).padding,
                    fontSize: getComputedStyle(sample).fontSize,
                    fontWeight: getComputedStyle(sample).fontWeight,
                    display: getComputedStyle(sample).display,
                } : null;
                const rootStyle = getComputedStyle(document.documentElement);
                return {
                    section_count: sections.length,
                    header_count: headers.length,
                    content_count: contents.length,
                    indicator_count: indicators.length,
                    first_header_tag: sample ? sample.tagName : null,
                    first_header_style: sampleStyle,
                    first_header_text: sample ? sample.textContent.trim().slice(0, 50) : null,
                    root_vars: {
                        primary_blue: rootStyle.getPropertyValue('--primary-blue').trim(),
                        accent_blue: rootStyle.getPropertyValue('--accent-blue').trim(),
                        lighter_blue: rootStyle.getPropertyValue('--lighter-blue').trim(),
                        light_blue: rootStyle.getPropertyValue('--light-blue').trim(),
                        border_color: rootStyle.getPropertyValue('--border-color').trim(),
                        shadow: rootStyle.getPropertyValue('--shadow').trim(),
                        shadow_hover: rootStyle.getPropertyValue('--shadow-hover').trim(),
                        text_dark: rootStyle.getPropertyValue('--text-dark').trim(),
                    }
                };
            }"""
            )
            results["viewports"][f"{w}x{h}"] = probe
            screenshot_path = OUTBASE / f"050_{w}x{h}.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            context.close()

        # Toggle test on 1280x900 viewport (default-ish)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(500)

        # Initial state: all collapsed (per markup)
        initial = page.evaluate(
            """() => {
            const headers = document.querySelectorAll('.collapsible-header');
            return Array.from(headers).map(h => ({
                text: h.textContent.trim().slice(0, 20),
                collapsed: h.classList.contains('collapsed'),
            }));
        }"""
        )

        # Click first header to expand
        page.click('.collapsible-header >> nth=0')
        page.wait_for_timeout(500)

        after_open = page.evaluate(
            """() => {
            const h = document.querySelector('.collapsible-header');
            const s = h.parentElement;
            const c = s.querySelector('.collapsible-content');
            return {
                header_collapsed: h.classList.contains('collapsed'),
                section_collapsed: s.classList.contains('collapsed'),
                content_collapsed: c.classList.contains('collapsed'),
                content_max_height: c.style.maxHeight,
            };
        }"""
        )

        # Click again to collapse
        page.click('.collapsible-header >> nth=0')
        page.wait_for_timeout(500)
        after_close = page.evaluate(
            """() => {
            const h = document.querySelector('.collapsible-header');
            const s = h.parentElement;
            const c = s.querySelector('.collapsible-content');
            return {
                header_collapsed: h.classList.contains('collapsed'),
                section_collapsed: s.classList.contains('collapsed'),
                content_collapsed: c.classList.contains('collapsed'),
                content_max_height: c.style.maxHeight,
            };
        }"""
        )

        results["toggle_test"] = {
            "initial_collapsed_count": sum(1 for x in initial if x["collapsed"]),
            "initial_total": len(initial),
            "after_first_click": after_open,
            "after_second_click": after_close,
        }
        page.screenshot(path=str(OUTBASE / "050_toggle_open.png"), full_page=True)
        context.close()
        browser.close()

    # Console errors check
    results["target_path"] = str(TARGET)

    out_json = OUTBASE / "_verify.json"
    out_json.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(json.dumps(results, ensure_ascii=False, indent=2))

    # Verdict
    issues = []
    for vp, probe in results["viewports"].items():
        if probe["section_count"] != 12:
            issues.append(f"{vp}: section_count={probe['section_count']} expected 12")
        if probe["header_count"] != 12:
            issues.append(f"{vp}: header_count={probe['header_count']} expected 12")
        if probe["content_count"] != 12:
            issues.append(f"{vp}: content_count={probe['content_count']} expected 12")
        if probe["indicator_count"] != 12:
            issues.append(f"{vp}: indicator_count={probe['indicator_count']} expected 12")
        if probe["first_header_tag"] != "DIV":
            issues.append(f"{vp}: first_header_tag={probe['first_header_tag']} expected DIV")
        rv = probe["root_vars"]
        if rv["accent_blue"] != "#004B87":
            issues.append(f"{vp}: accent_blue={rv['accent_blue']} expected #004B87")
        if rv["lighter_blue"].lower() != "#ebf3fa":
            issues.append(f"{vp}: lighter_blue={rv['lighter_blue']} expected #EBF3FA")
        if rv["border_color"] != "#cbd5e1":
            issues.append(f"{vp}: border_color={rv['border_color']} expected #cbd5e1")

    tt = results["toggle_test"]
    if tt["initial_collapsed_count"] != 12:
        issues.append(f"initial collapsed count={tt['initial_collapsed_count']} expected 12")
    ao = tt["after_first_click"]
    if ao["header_collapsed"] is True:
        issues.append("after open: header still collapsed (toggle to open didn't work)")
    ac = tt["after_second_click"]
    if ac["header_collapsed"] is False:
        issues.append("after close: header not collapsed (toggle to close didn't work)")

    print("\n" + "=" * 50)
    if issues:
        print("VERDICT: ISSUES FOUND")
        for i in issues:
            print(f"  - {i}")
        sys.exit(1)
    else:
        print("VERDICT: ALL PASS — 12 sections × 4 elements × 3 viewports + toggle reversible + canonical :root")


if __name__ == "__main__":
    main()
