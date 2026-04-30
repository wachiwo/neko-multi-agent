#!/usr/bin/env python3
"""cmd_214 W4 042 hotfix verify — capture screenshots + computed style probe.

Mode 'before' captures pre-edit baseline.
Mode 'after' captures post-edit and is compared with before.
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
    "/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new横/042_請求書出力指示.html"
)
OUTBASE = Path(
    "/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_214/w4_042_hotfix_screenshots"
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
                const title = document.querySelector('.collapsible-title');
                const indicator = document.querySelector('.collapse-indicator');
                const content = document.querySelector('.collapsible-content');
                const section = document.querySelector('.collapsible-section');
                const get = (el) => el ? {
                    bg: getComputedStyle(el).backgroundColor,
                    color: getComputedStyle(el).color,
                    padding: getComputedStyle(el).padding,
                    fontSize: getComputedStyle(el).fontSize,
                    fontWeight: getComputedStyle(el).fontWeight,
                    borderRadius: getComputedStyle(el).borderRadius,
                    marginTop: getComputedStyle(el).marginTop,
                    cursor: getComputedStyle(el).cursor,
                    display: getComputedStyle(el).display,
                    transition: getComputedStyle(el).transition
                } : null;
                return {
                    title_style: get(title),
                    indicator_style: get(indicator),
                    content_style: get(content),
                    section_style: get(section),
                    title_bbox: title ? {
                        w: Math.round(title.getBoundingClientRect().width),
                        h: Math.round(title.getBoundingClientRect().height)
                    } : null,
                };
            }"""
            )
            results["viewports"][f"{w}x{h}"] = probe
            screenshot_path = outdir / f"042_{mode}_{w}x{h}.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            context.close()
        browser.close()

    out_json = outdir / f"_{mode}.json"
    out_json.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "before"
    main(mode)
