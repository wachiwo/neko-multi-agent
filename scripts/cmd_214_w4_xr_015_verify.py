#!/usr/bin/env python3
"""cmd_214 W4 cross-review of 015 — independent Playwright verify.

Validates W1's claims:
- Hold-list widths: 担当者 select 180px×2 + 担当者/電話/FAX input 22ch×9 (= 176px @ 8px/ch)
- 016 canonical collapsible structure rendered correctly
- Toggle ON/OFF interaction works
- 3 viewport rendering (1024×768 / 1280×900 / 1920×1080)
"""
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
    "/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new横/015_見積明細.html"
)
OUTDIR = Path(
    "/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_214/w4_015_xr_screenshots"
)

VIEWPORTS = [(1024, 768), (1280, 900), (1920, 1080)]


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    url = f"file://{quote(str(TARGET))}"
    results = {"file": TARGET.name, "viewports": {}, "toggle_test": {}}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for w, h in VIEWPORTS:
            context = browser.new_context(viewport={"width": w, "height": h})
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            probe = page.evaluate(
                """() => {
                // 担当者 select 180px width audit
                const selects180 = Array.from(document.querySelectorAll('select')).filter(s => {
                    const inline = s.getAttribute('style') || '';
                    return inline.includes('180px') && !inline.includes('max-width');
                }).map(s => ({
                    width_render: Math.round(s.getBoundingClientRect().width),
                    inline_style: s.getAttribute('style')
                }));

                // 22ch input width audit (担当者/電話/FAX)
                const inputs22ch = Array.from(document.querySelectorAll('input')).filter(i => {
                    const inline = i.getAttribute('style') || '';
                    return inline.includes('22ch');
                }).map(i => ({
                    width_render: Math.round(i.getBoundingClientRect().width),
                    inline_style: i.getAttribute('style')
                }));

                // collapsible structure audit
                const sections = document.querySelectorAll('.collapsible-section');
                const titles = document.querySelectorAll('.collapsible-title');
                const contents = document.querySelectorAll('.collapsible-content');
                const indicators = document.querySelectorAll('.collapse-indicator');
                const indicators_text = Array.from(indicators).map(el => el.textContent.trim());

                // page-header check
                const ph = document.querySelector('.page-header');

                // Sample collapsible-title computed style (first one)
                const firstTitle = titles[0];
                const titleStyle = firstTitle ? {
                    bg: getComputedStyle(firstTitle).backgroundColor,
                    color: getComputedStyle(firstTitle).color,
                    cursor: getComputedStyle(firstTitle).cursor
                } : null;

                return {
                    selects_180_count: selects180.length,
                    selects_180_widths: selects180.map(s => s.width_render),
                    inputs_22ch_count: inputs22ch.length,
                    inputs_22ch_widths: inputs22ch.map(i => i.width_render),
                    collapsible_section_count: sections.length,
                    collapsible_title_count: titles.length,
                    collapsible_content_count: contents.length,
                    collapse_indicator_count: indicators.length,
                    indicators_unique_text: Array.from(new Set(indicators_text)),
                    page_header_position: ph ? getComputedStyle(ph).position : null,
                    first_title_style: titleStyle,
                };
            }"""
            )
            results["viewports"][f"{w}x{h}"] = probe
            screenshot_path = OUTDIR / f"015_xr_{w}x{h}_expanded.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            context.close()

        # Toggle interaction test (1280×900)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(500)

        before = page.evaluate(
            """() => {
            const c = document.querySelector('.collapsible-content');
            const s = document.querySelector('.collapsible-section');
            return {
                content_collapsed: c ? c.classList.contains('collapsed') : null,
                section_collapsed: s ? s.classList.contains('collapsed') : null,
                content_max_height: c ? c.style.maxHeight : null
            };
        }"""
        )
        # 1st click (016 baseline: no-op for fresh page)
        page.click('.collapsible-title')
        page.wait_for_timeout(500)
        after_1st = page.evaluate(
            """() => {
            const c = document.querySelector('.collapsible-content');
            const s = document.querySelector('.collapsible-section');
            return {
                content_collapsed: c ? c.classList.contains('collapsed') : null,
                section_collapsed: s ? s.classList.contains('collapsed') : null,
                content_max_height: c ? c.style.maxHeight : null
            };
        }"""
        )
        # 2nd click (actual collapse)
        page.click('.collapsible-title')
        page.wait_for_timeout(500)
        after_2nd = page.evaluate(
            """() => {
            const c = document.querySelector('.collapsible-content');
            const s = document.querySelector('.collapsible-section');
            return {
                content_collapsed: c ? c.classList.contains('collapsed') : null,
                section_collapsed: s ? s.classList.contains('collapsed') : null,
                content_max_height: c ? c.style.maxHeight : null
            };
        }"""
        )
        page.screenshot(
            path=str(OUTDIR / "015_xr_1280x900_collapsed.png"), full_page=True
        )
        # 3rd click (re-expand)
        page.click('.collapsible-title')
        page.wait_for_timeout(500)
        after_3rd = page.evaluate(
            """() => {
            const c = document.querySelector('.collapsible-content');
            const s = document.querySelector('.collapsible-section');
            return {
                content_collapsed: c ? c.classList.contains('collapsed') : null,
                section_collapsed: s ? s.classList.contains('collapsed') : null,
                content_max_height: c ? c.style.maxHeight : null
            };
        }"""
        )
        results["toggle_test"] = {
            "initial": before,
            "after_1st_click_noop": after_1st,
            "after_2nd_click_collapse": after_2nd,
            "after_3rd_click_expand": after_3rd,
        }
        context.close()
        browser.close()

    out_json = OUTDIR / "_xr_verify.json"
    out_json.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
