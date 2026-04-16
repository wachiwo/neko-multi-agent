#!/usr/bin/env python3
"""cmd_186 Phase 1 Addendum W1: before/after screenshot for 2 company files.
Usage: python3 cmd_186_phase1_addendum_w1_screenshot.py [before|after]
"""
from __future__ import annotations

import os
import sys
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

NEW_DIR = Path("/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new")
OUTDIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_186_phase1_express/screenshots_addendum")
ZOOMS = [1.0, 1.5, 2.0]

FILES = [
    "company-dashboard.html",
    "company-search.html",
]


def slug(name):
    return name.replace(".html", "").replace(" ", "_")


def main():
    phase = sys.argv[1] if len(sys.argv) > 1 else "before"
    assert phase in ("before", "after")
    OUTDIR.mkdir(parents=True, exist_ok=True)

    summary = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for filename in FILES:
            target = NEW_DIR / filename
            url = f"file://{quote(str(target))}"
            for zoom in ZOOMS:
                context = browser.new_context(viewport={"width": 1280, "height": 900})
                page = context.new_page()
                page.goto(url, wait_until="domcontentloaded")
                page.evaluate(f"document.body.style.zoom = '{zoom}'")
                page.wait_for_timeout(300)
                pct = int(zoom * 100)
                out = OUTDIR / f"{slug(filename)}_zoom{pct}_{phase}.png"
                page.screenshot(path=str(out), full_page=True)

                probe = page.evaluate(
                    """() => {
                        const rootStyle = getComputedStyle(document.documentElement);
                        const bodyStyle = getComputedStyle(document.body);
                        const menu_active = document.querySelector('.menu-item.active');
                        const ch = document.querySelector('.collapsible-header, .card-header, .section-header');
                        return {
                            root_border: rootStyle.getPropertyValue('--border').trim(),
                            root_border_color: rootStyle.getPropertyValue('--border-color').trim(),
                            body_font: bodyStyle.fontFamily,
                            menu_active_border_left_color: menu_active ? getComputedStyle(menu_active).borderLeftColor : null,
                            container_bg: ch ? getComputedStyle(ch).backgroundColor : null,
                        };
                    }"""
                )
                summary.append({
                    "file": filename,
                    "zoom": pct,
                    "phase": phase,
                    "probe": probe,
                })
                if zoom == 1.0:
                    print(f"--- {filename} zoom {pct}% ({phase}) ---")
                    for k, v in probe.items():
                        print(f"  {k}: {v}")
                context.close()
        browser.close()

    import json
    json_path = OUTDIR / f"summary_{phase}.json"
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nOK: {json_path}")


if __name__ == "__main__":
    main()
