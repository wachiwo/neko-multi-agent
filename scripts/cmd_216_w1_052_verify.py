#!/usr/bin/env python3
"""cmd_216 W1 052_受注画面 4 categories cleanup verify.

3 viewport (375/960/1920) section toggle behavior + :root canonical + structure migration.
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
    "/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new横/052_受注画面(受注明細).html"
)
OUTDIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_216/w1_052_screenshots")

VIEWPORTS = [
    (375, 812),
    (960, 720),
    (1920, 1080),
]


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    url = f"file://{quote(str(TARGET))}"
    results = {"file": TARGET.name, "viewports": {}, "migration_toggle": {}}

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
                const headers = document.querySelectorAll('.collapsible-header');  // new from #3 migration
                const titles = document.querySelectorAll('.collapsible-title');     // pre-existing
                const contents = document.querySelectorAll('.collapsible-content');
                const sectionHeaderBars = document.querySelectorAll('.section-header-bar');
                const rs = getComputedStyle(document.documentElement);
                // Check first NEW collapsible-header (from #3 migration)
                const newHeaders = Array.from(headers);
                return {
                    section_count: sections.length,
                    pre_existing_title_count: titles.length,
                    new_header_count: headers.length,
                    content_count: contents.length,
                    section_header_bar_count: sectionHeaderBars.length,  // expect 1 (L2152 入金情報 only)
                    section_header_bar_text: Array.from(sectionHeaderBars).map(el => el.textContent.trim()),
                    var_lighter_blue: rs.getPropertyValue('--lighter-blue').trim(),
                    var_accent_blue: rs.getPropertyValue('--accent-blue').trim(),
                    new_header_first_text: newHeaders[0] ? newHeaders[0].textContent.trim() : null,
                };
            }"""
            )
            results["viewports"][f"{w}x{h}"] = probe
            page.screenshot(path=str(OUTDIR / f"052_w1_{w}x{h}_initial.png"), full_page=True)
            context.close()

        # Toggle test on first new collapsible-header (明細情報 from migration)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(500)

        before = page.evaluate(
            """() => {
            const h = document.querySelector('.collapsible-header');
            const s = h ? h.parentElement : null;
            const c = s ? s.querySelector('.collapsible-content') : null;
            return {
                exists: !!h,
                header_collapsed: h ? h.classList.contains('collapsed') : null,
                content_max_height: c ? c.style.maxHeight : null,
            };
        }"""
        )
        page.click('.collapsible-header')
        page.wait_for_timeout(500)
        after_collapse = page.evaluate(
            """() => {
            const h = document.querySelector('.collapsible-header');
            const s = h ? h.parentElement : null;
            const c = s ? s.querySelector('.collapsible-content') : null;
            return {
                header_collapsed: h ? h.classList.contains('collapsed') : null,
                content_max_height: c ? c.style.maxHeight : null,
            };
        }"""
        )
        page.click('.collapsible-header')
        page.wait_for_timeout(500)
        after_reexpand = page.evaluate(
            """() => {
            const h = document.querySelector('.collapsible-header');
            const s = h ? h.parentElement : null;
            const c = s ? s.querySelector('.collapsible-content') : null;
            return {
                header_collapsed: h ? h.classList.contains('collapsed') : null,
                content_max_height: c ? c.style.maxHeight : null,
            };
        }"""
        )
        results["migration_toggle"] = {
            "initial": before,
            "after_1st_click": after_collapse,
            "after_2nd_click": after_reexpand,
        }

        context.close()
        browser.close()

    out_json = OUTDIR / "_verify.json"
    out_json.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
