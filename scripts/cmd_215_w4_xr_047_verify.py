#!/usr/bin/env python3
"""cmd_215 W4 cross-review of 047 — independent Playwright verify (3 viewport + main + modal toggle)."""
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
    "/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new横/047_請求予定一覧.html"
)
OUTDIR = Path(
    "/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_215/w4_047_xr_screenshots"
)

VIEWPORTS = [(1024, 768), (1280, 900), (1920, 1080)]


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    url = f"file://{quote(str(TARGET))}"
    results = {"file": TARGET.name, "viewports": {}, "main_toggle_test": {}, "modal_test": {}}

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
                const titles = document.querySelectorAll('.collapsible-title');
                const contents = document.querySelectorAll('.collapsible-content');
                const indicators = document.querySelectorAll('.collapse-indicator');
                const sectionHeadersOld = document.querySelectorAll('.section-header');
                const ph = document.querySelector('.page-header');
                const sample = titles[0];
                const sampleStyle = sample ? {
                    bg: getComputedStyle(sample).backgroundColor,
                    color: getComputedStyle(sample).color,
                    cursor: getComputedStyle(sample).cursor,
                    padding: getComputedStyle(sample).padding,
                    fontSize: getComputedStyle(sample).fontSize,
                    fontWeight: getComputedStyle(sample).fontWeight,
                } : null;
                return {
                    section_count: sections.length,
                    title_count: titles.length,
                    content_count: contents.length,
                    indicator_count: indicators.length,
                    section_header_old_count: sectionHeadersOld.length,
                    indicators_unique_text: Array.from(new Set(Array.from(indicators).map(el => el.textContent.trim()))),
                    page_header_position: ph ? getComputedStyle(ph).position : null,
                    first_title_style: sampleStyle,
                    first_title_text: sample ? sample.textContent.trim().slice(0, 50) : null,
                };
            }"""
            )
            results["viewports"][f"{w}x{h}"] = probe
            screenshot_path = OUTDIR / f"047_xr_{w}x{h}_expanded.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            context.close()

        # Main page toggle test (1280×900)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(500)

        # 1st click (no-op)
        page.click('.collapsible-title')
        page.wait_for_timeout(500)
        # 2nd click (collapse)
        page.click('.collapsible-title')
        page.wait_for_timeout(500)
        main_collapse = page.evaluate(
            """() => {
            const t = document.querySelector('.collapsible-title');
            const c = document.querySelector('.collapsible-content');
            const s = document.querySelector('.collapsible-section');
            return {
                title_collapsed: t ? t.classList.contains('collapsed') : null,
                content_collapsed: c ? c.classList.contains('collapsed') : null,
                section_collapsed: s ? s.classList.contains('collapsed') : null,
                content_max_height: c ? c.style.maxHeight : null
            };
        }"""
        )
        page.screenshot(path=str(OUTDIR / "047_xr_1280x900_main_collapsed.png"), full_page=True)
        results["main_toggle_test"] = main_collapse

        # Try modal section toggle if modal exists
        modal_exists = page.evaluate("() => !!document.querySelector('.modal') || !!document.getElementById('modalOverlay')")
        if modal_exists:
            results["modal_test"]["modal_exists"] = True
            # Try opening modal — find an expand button
            try:
                page.evaluate("() => { const m = document.getElementById('modalOverlay'); if (m) m.style.display = 'flex'; const mc = document.querySelector('.modal'); if (mc) mc.style.display = 'block'; }")
                page.wait_for_timeout(500)
                # try click first modal collapsible-title
                modal_titles = page.evaluate("""() => {
                    const titles = document.querySelectorAll('.modal .collapsible-title, [class*=modal] .collapsible-title');
                    return titles.length;
                }""")
                results["modal_test"]["modal_collapsible_titles"] = modal_titles
            except Exception as e:
                results["modal_test"]["error"] = str(e)
        else:
            results["modal_test"]["modal_exists"] = False
        context.close()
        browser.close()

    out_json = OUTDIR / "_xr_verify.json"
    out_json.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
