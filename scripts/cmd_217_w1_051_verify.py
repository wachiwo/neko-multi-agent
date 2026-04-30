#!/usr/bin/env python3
"""cmd_217 W1 051_見積明細(海外) HIGH 6 items verify.

3 viewport screenshots (375/960/1920) + collapsible toggle round-trip
(canonical 1-arg toggleSection(this) port verification).
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
    "/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new/051_見積明細（海外）.html"
)
OUTDIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_217/w1_051_screenshots")

VIEWPORTS = [
    (375, 812),
    (960, 720),
    (1920, 1080),
]


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    url = f"file://{quote(str(TARGET))}"
    results = {"file": TARGET.name, "viewports": {}, "toggle_roundtrip": {}}

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
                const exportSec = document.querySelector('.export-section');
                const exportBtns = exportSec ? exportSec.querySelectorAll('button').length : 0;
                const rs = getComputedStyle(document.documentElement);
                return {
                    section_count: sections.length,
                    header_count: headers.length,
                    content_count: contents.length,
                    export_section_present: !!exportSec,
                    export_section_btn_count: exportBtns,
                    var_lighter_blue: rs.getPropertyValue('--lighter-blue').trim(),
                    var_accent_blue: rs.getPropertyValue('--accent-blue').trim(),
                    var_pink_dark: rs.getPropertyValue('--pink-dark').trim(),
                    var_text_dark: rs.getPropertyValue('--text-dark').trim(),
                };
            }"""
            )
            results["viewports"][f"{w}x{h}"] = probe
            page.screenshot(path=str(OUTDIR / f"051_w1_{w}x{h}_initial.png"), full_page=True)
            context.close()

        # Toggle round-trip test on first .collapsible-header (1920 viewport)
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
                header_collapsed: h ? h.classList.contains('collapsed') : null,
                section_collapsed: s ? s.classList.contains('collapsed') : null,
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
                section_collapsed: s ? s.classList.contains('collapsed') : null,
                content_max_height: c ? c.style.maxHeight : null,
            };
        }"""
        )
        page.screenshot(path=str(OUTDIR / "051_w1_1920x1080_collapsed.png"), full_page=True)
        page.click('.collapsible-header')
        page.wait_for_timeout(500)
        after_reexpand = page.evaluate(
            """() => {
            const h = document.querySelector('.collapsible-header');
            const s = h ? h.parentElement : null;
            const c = s ? s.querySelector('.collapsible-content') : null;
            return {
                header_collapsed: h ? h.classList.contains('collapsed') : null,
                section_collapsed: s ? s.classList.contains('collapsed') : null,
                content_max_height: c ? c.style.maxHeight : null,
            };
        }"""
        )
        results["toggle_roundtrip"] = {
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
