#!/usr/bin/env python3
"""cmd_214 W4 043_得意先売上一覧表 collapsible port verify.

3 viewport screenshots + toggle interaction test.
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
    "/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new横/043_得意先売上一覧表.html"
)
OUTDIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_214/w4_043_screenshots")

VIEWPORTS = [
    (1024, 768),
    (1280, 900),
    (1920, 1080),
]


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
            page.wait_for_timeout(400)

            probe = page.evaluate(
                """() => {
                const sec = document.querySelector('.collapsible-section');
                const title = document.querySelector('.collapsible-title');
                const content = document.querySelector('.collapsible-content');
                const indicator = document.querySelector('.collapse-indicator');
                const ph = document.querySelector('.page-header');
                const exp = document.querySelector('.export-section');
                const get = (el) => el ? {
                    bg: getComputedStyle(el).backgroundColor,
                    color: getComputedStyle(el).color,
                    display: getComputedStyle(el).display,
                    text: el.textContent ? el.textContent.trim().slice(0, 40) : null
                } : null;
                return {
                    section_exists: !!sec,
                    title_style: get(title),
                    content_style: get(content),
                    indicator_text: indicator ? indicator.textContent.trim() : null,
                    page_header_pos: ph ? getComputedStyle(ph).position : null,
                    export_section_exists: !!exp,
                    excel_table_in_content: !!document.querySelector('.collapsible-content .excel-table'),
                    th_count: document.querySelectorAll('.collapsible-content .excel-table th').length,
                };
            }"""
            )
            results["viewports"][f"{w}x{h}"] = probe
            screenshot_path = OUTDIR / f"043_w4_{w}x{h}_expanded.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            context.close()

        # Toggle interaction test (use 1280x900)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(400)

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
        # 1st click: 016 baseline behavior — initial maxHeight=="" takes EXPAND path (no-op)
        page.click('.collapsible-title')
        page.wait_for_timeout(500)
        after_first_click = page.evaluate(
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
        # 2nd click: actually collapses
        page.click('.collapsible-title')
        page.wait_for_timeout(500)
        after_collapse = page.evaluate(
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
            path=str(OUTDIR / "043_w4_1280x900_collapsed.png"), full_page=True
        )
        # 3rd click: re-expand
        page.click('.collapsible-title')
        page.wait_for_timeout(500)
        after_expand = page.evaluate(
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
            "after_1st_click_noop": after_first_click,
            "after_2nd_click_collapse": after_collapse,
            "after_3rd_click_expand": after_expand,
        }
        context.close()
        browser.close()

    out_json = OUTDIR / "_verify.json"
    out_json.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
