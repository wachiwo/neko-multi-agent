#!/usr/bin/env python3
"""cmd_215 W1 047_請求予定一覧 collapsible port verify.

3 viewport screenshots + main page collapsible toggle + modal section toggle.
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
    "/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new横/047_請求予定一覧.html"
)
OUTDIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_215/w1_047_screenshots")

VIEWPORTS = [
    (1024, 768),
    (1280, 900),
    (1920, 1080),
]


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    url = f"file://{quote(str(TARGET))}"
    results = {"file": TARGET.name, "viewports": {}, "main_toggle": {}, "modal_toggle": {}}

    with sync_playwright() as p:
        browser = p.chromium.launch()

        for w, h in VIEWPORTS:
            context = browser.new_context(viewport={"width": w, "height": h})
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(400)

            probe = page.evaluate(
                """() => {
                const sections = document.querySelectorAll('.collapsible-section');
                const titles = document.querySelectorAll('.collapsible-title');
                const contents = document.querySelectorAll('.collapsible-content');
                const indicators = document.querySelectorAll('.collapse-indicator');
                const oldHeaders = document.querySelectorAll('.section-header');
                const ph = document.querySelector('.page-header');
                return {
                    section_count: sections.length,
                    title_count: titles.length,
                    content_count: contents.length,
                    indicator_count: indicators.length,
                    old_section_header_count: oldHeaders.length,
                    page_header_pos: ph ? getComputedStyle(ph).position : null,
                    main_section_title: titles[0] ? titles[0].textContent.trim() : null,
                    indicators_text: Array.from(indicators).map(i => i.textContent.trim()),
                };
            }"""
            )
            results["viewports"][f"{w}x{h}"] = probe
            page.screenshot(path=str(OUTDIR / f"047_w1_{w}x{h}_expanded.png"), full_page=True)
            context.close()

        # Main page collapsible toggle test (1280x900)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(400)

        before = page.evaluate(
            """() => {
            const t = document.querySelector('.collapsible-title');
            const c = document.querySelector('.collapsible-content');
            return {
                title_collapsed: t ? t.classList.contains('collapsed') : null,
                content_max_height: c ? c.style.maxHeight : null,
            };
        }"""
        )
        page.click('.collapsible-title')
        page.wait_for_timeout(500)
        page.click('.collapsible-title')  # 2nd click for actual collapse
        page.wait_for_timeout(500)
        collapsed = page.evaluate(
            """() => {
            const t = document.querySelector('.collapsible-title');
            const c = document.querySelector('.collapsible-content');
            return {
                title_collapsed: t ? t.classList.contains('collapsed') : null,
                content_max_height: c ? c.style.maxHeight : null,
            };
        }"""
        )
        page.screenshot(path=str(OUTDIR / "047_w1_1280x900_main_collapsed.png"), full_page=True)
        page.click('.collapsible-title')
        page.wait_for_timeout(500)
        re_expanded = page.evaluate(
            """() => {
            const t = document.querySelector('.collapsible-title');
            const c = document.querySelector('.collapsible-content');
            return {
                title_collapsed: t ? t.classList.contains('collapsed') : null,
                content_max_height: c ? c.style.maxHeight : null,
            };
        }"""
        )
        results["main_toggle"] = {
            "initial": before,
            "after_2nd_click_collapsed": collapsed,
            "after_3rd_click_re_expanded": re_expanded,
        }

        # Modal section toggle test (open modal, click 基本情報 collapsible)
        page.click('.btn-select')   # opens modal
        page.wait_for_timeout(500)
        # Click 基本情報 collapsible inside modal (2nd .collapsible-title overall)
        page.evaluate("() => { document.querySelectorAll('.collapsible-title')[1].click(); }")
        page.wait_for_timeout(500)
        page.evaluate("() => { document.querySelectorAll('.collapsible-title')[1].click(); }")
        page.wait_for_timeout(500)
        modal_state = page.evaluate(
            """() => {
            const titles = document.querySelectorAll('.collapsible-title');
            const contents = document.querySelectorAll('.collapsible-content');
            return {
                modal_section_count: titles.length,
                first_modal_title_text: titles[1] ? titles[1].textContent.trim() : null,
                first_modal_collapsed: titles[1] ? titles[1].classList.contains('collapsed') : null,
                first_modal_content_max_height: contents[1] ? contents[1].style.maxHeight : null,
            };
        }"""
        )
        page.screenshot(path=str(OUTDIR / "047_w1_1280x900_modal_section_toggled.png"), full_page=True)
        results["modal_toggle"] = modal_state

        context.close()
        browser.close()

    out_json = OUTDIR / "_verify.json"
    out_json.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
