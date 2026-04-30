#!/usr/bin/env python3
"""cmd_214 W1 042 cross-review + Phase 4 final verify (post W4 hotfix).

3 viewport screenshots + collapsed/expanded state verify + relocated
.collapsible-title.collapsed border-radius rule effect verify (independent
verification of W4 hotfix mathematical proof).
"""
import os
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
    "/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new横/042_請求書出力指示.html"
)
OUTDIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_214/w1_042_xr_screenshots")

VIEWPORTS = [
    (1024, 768),
    (1280, 900),
    (1920, 1080),
]


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    url = f"file://{quote(str(TARGET))}"
    results = {"file": TARGET.name, "viewports": {}, "toggle_test": {}, "collapsed_state_unique_rule": {}}

    with sync_playwright() as p:
        browser = p.chromium.launch()

        # Pass 1: 3 viewport expanded screenshots + computed style probe
        for w, h in VIEWPORTS:
            context = browser.new_context(viewport={"width": w, "height": h})
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(400)

            probe = page.evaluate(
                """() => {
                const sec = document.querySelector('.collapsible-section');
                const title = document.querySelector('.collapsible-title');
                const content = document.querySelector('.collapsible-content');
                const indicator = document.querySelector('.collapse-indicator');
                const ph = document.querySelector('.page-header');
                const oldSh = document.querySelector('.section-header');
                const get = (el) => el ? {
                    bg: getComputedStyle(el).backgroundColor,
                    color: getComputedStyle(el).color,
                    display: getComputedStyle(el).display,
                    border_radius: getComputedStyle(el).borderRadius,
                    text: el.textContent ? el.textContent.trim().slice(0, 40) : null
                } : null;
                return {
                    section_count: document.querySelectorAll('.collapsible-section').length,
                    title_count: document.querySelectorAll('.collapsible-title').length,
                    content_count: document.querySelectorAll('.collapsible-content').length,
                    indicator_count: document.querySelectorAll('.collapse-indicator').length,
                    old_section_header_count: document.querySelectorAll('.section-header').length,
                    title_style: get(title),
                    content_style: get(content),
                    page_header_pos: ph ? getComputedStyle(ph).position : null,
                    excel_table_in_content: !!document.querySelector('.collapsible-content .excel-table'),
                    indicator_text: indicator ? indicator.textContent.trim() : null,
                };
            }"""
            )
            results["viewports"][f"{w}x{h}"] = probe
            page.screenshot(path=str(OUTDIR / f"042_xr_{w}x{h}_expanded.png"), full_page=True)
            context.close()

        # Pass 2: 1280x900 collapsed-state interaction + unique rule effect verify
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(400)

        # Initial state probe
        before = page.evaluate(
            """() => {
            const t = document.querySelector('.collapsible-title');
            const c = document.querySelector('.collapsible-content');
            const s = document.querySelector('.collapsible-section');
            return {
                title_collapsed: t ? t.classList.contains('collapsed') : null,
                content_collapsed: c ? c.classList.contains('collapsed') : null,
                section_collapsed: s ? s.classList.contains('collapsed') : null,
                title_border_radius: t ? getComputedStyle(t).borderRadius : null,
                content_max_height: c ? c.style.maxHeight : null,
            };
        }"""
        )
        # Click 1: state init (canonical 016 quirk)
        page.click('.collapsible-title')
        page.wait_for_timeout(500)
        # Click 2: actual collapse
        page.click('.collapsible-title')
        page.wait_for_timeout(500)
        collapsed = page.evaluate(
            """() => {
            const t = document.querySelector('.collapsible-title');
            const c = document.querySelector('.collapsible-content');
            const s = document.querySelector('.collapsible-section');
            return {
                title_collapsed: t ? t.classList.contains('collapsed') : null,
                content_collapsed: c ? c.classList.contains('collapsed') : null,
                section_collapsed: s ? s.classList.contains('collapsed') : null,
                title_border_radius: t ? getComputedStyle(t).borderRadius : null,
                content_max_height: c ? c.style.maxHeight : null,
            };
        }"""
        )
        page.screenshot(path=str(OUTDIR / "042_xr_1280x900_collapsed.png"), full_page=True)

        # Click 3: re-expand
        page.click('.collapsible-title')
        page.wait_for_timeout(500)
        re_expanded = page.evaluate(
            """() => {
            const t = document.querySelector('.collapsible-title');
            const c = document.querySelector('.collapsible-content');
            const s = document.querySelector('.collapsible-section');
            return {
                title_collapsed: t ? t.classList.contains('collapsed') : null,
                content_collapsed: c ? c.classList.contains('collapsed') : null,
                section_collapsed: s ? s.classList.contains('collapsed') : null,
                title_border_radius: t ? getComputedStyle(t).borderRadius : null,
                content_max_height: c ? c.style.maxHeight : null,
            };
        }"""
        )
        results["toggle_test"] = {
            "initial_expanded": before,
            "after_2nd_click_collapsed": collapsed,
            "after_3rd_click_re_expanded": re_expanded,
        }
        # Verify the unique rule (.collapsible-title.collapsed { border-radius: 6px; }) is active
        results["collapsed_state_unique_rule"] = {
            "expected_collapsed_title_border_radius": "6px",
            "actual_collapsed_title_border_radius": collapsed.get("title_border_radius"),
            "match": collapsed.get("title_border_radius") == "6px",
            "expected_expanded_title_border_radius": "6px 6px 0px 0px",
            "actual_expanded_title_border_radius": before.get("title_border_radius"),
            "match_expanded": before.get("title_border_radius") in ["6px 6px 0px 0px", "6px 6px 0 0"],
        }
        context.close()
        browser.close()

    out_json = OUTDIR / "_xr_verify.json"
    out_json.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
