#!/usr/bin/env python3
"""cmd_215 W4 052 signature fix verify — before/after capture."""
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
    "/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new横/052_受注画面(受注明細).html"
)
OUTBASE = Path(
    "/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_215/w4_052_screenshots"
)

VIEWPORTS = [(1024, 768), (1280, 900), (1920, 1080)]


def main(mode):
    if mode not in ("before", "after"):
        print("usage: script <before|after>", file=sys.stderr)
        sys.exit(1)
    outdir = OUTBASE / mode
    outdir.mkdir(parents=True, exist_ok=True)

    url = f"file://{quote(str(TARGET))}"
    results = {"file": TARGET.name, "mode": mode, "viewports": {}}

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
                    first_title_style: sampleStyle,
                    first_title_text: sample ? sample.textContent.trim().slice(0, 50) : null,
                };
            }"""
            )
            results["viewports"][f"{w}x{h}"] = probe
            screenshot_path = outdir / f"052_{mode}_{w}x{h}.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            context.close()

        # Toggle test only in 'after' mode
        if mode == "after":
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
            collapse_state = page.evaluate(
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
            page.screenshot(path=str(outdir / "052_after_1280x900_collapsed.png"), full_page=True)
            results["toggle_test"] = collapse_state
            context.close()
        browser.close()

    out_json = outdir / f"_{mode}.json"
    out_json.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "before"
    main(mode)
