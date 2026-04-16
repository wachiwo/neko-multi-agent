#!/usr/bin/env python3
"""cmd_186 Phase 1 Express W1: before/after screenshot for 15 files.
Usage: python3 cmd_186_phase1_express_w1_screenshot.py [before|after]
Captures 3 zoom viewports + computed styles for color/font verification.
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
OUTDIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_186_phase1_express/screenshots_w1")
ZOOMS = [1.0, 1.5, 2.0]

FILES = [
    "001_個人営業管理.html",
    "002_国別累計仕入先上位分析表.html",
    "003_国別累計得意先上位分析表 (粗利).html",
    "004_国別累計得意先上位分析表.html",
    "005_受注区分別実績表.html",
    "006_受注売上入金管理.html",
    "007_製品区分別累計上位分析表.html",
    "008_売上実績表.html",
    "009_売上粗利表.html",
    "010_売上予測表.html",
    "011_累計仕入先上位分析表.html",
    "012_累計得意先上位分析表（粗利）.html",
    "013_累計得意先上位分析表.html",
    "company-dashboard.html",
    "company-search.html",
]


def slug(name):
    """Convert filename to safe slug."""
    return name.replace(".html", "").replace(" ", "_").replace("(", "").replace(")", "").replace("（", "_").replace("）", "")


def main():
    phase = sys.argv[1] if len(sys.argv) > 1 else "before"
    assert phase in ("before", "after")
    OUTDIR.mkdir(parents=True, exist_ok=True)

    summary = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for filename in FILES:
            target = NEW_DIR / filename
            if not target.exists():
                print(f"SKIP {filename}: not found", file=sys.stderr)
                continue
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
                        // Capture root computed style + body font-family + sample elements
                        const rootStyle = getComputedStyle(document.documentElement);
                        const bodyStyle = getComputedStyle(document.body);
                        const ch = document.querySelector('.collapsible-header');
                        const btn = document.querySelector('.btn');
                        const th = document.querySelector('.data-table th, table th');
                        return {
                            root_primary_blue: rootStyle.getPropertyValue('--primary-blue').trim(),
                            root_primary_blue_dark: rootStyle.getPropertyValue('--primary-blue-dark').trim(),
                            root_primary_blue_light: rootStyle.getPropertyValue('--primary-blue-light').trim(),
                            root_border_color: rootStyle.getPropertyValue('--border-color').trim(),
                            body_font: bodyStyle.fontFamily,
                            collapsible_header_bg: ch ? getComputedStyle(ch).backgroundColor : null,
                            btn_bg: btn ? getComputedStyle(btn).backgroundColor : null,
                            th_bg: th ? getComputedStyle(th).backgroundColor : null,
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
                    # Log only for zoom 100%
                    print(f"--- {filename} zoom {pct}% ({phase}) ---")
                    for k, v in probe.items():
                        print(f"  {k}: {v}")
                print(f"  screenshot: {out.name}")
                context.close()
        browser.close()

    # Write JSON summary
    import json
    json_path = OUTDIR / f"summary_{phase}.json"
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nOK: summary written to {json_path}")


if __name__ == "__main__":
    main()
