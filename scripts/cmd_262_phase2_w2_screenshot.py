#!/usr/bin/env python3
"""cmd_262 Phase 2 W2 — 011 對象/地域 width 縮小 verify screenshot (3 viewport)."""
from __future__ import annotations

import os
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
    "/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/002_new横/011_累計仕入先上位分析表.html"
)
OUTDIR = Path("/mnt/c/tools/neko-multi-agent/outputs/cmd_262/phase2_w2_screenshots")
VIEWPORTS = [
    ("375", 375, 800),
    ("960", 960, 800),
    ("1920", 1920, 1080),
]


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    url = f"file://{quote(str(TARGET))}"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for tag, w, h in VIEWPORTS:
            context = browser.new_context(viewport={"width": w, "height": h})
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(500)
            out = OUTDIR / f"011_vw{tag}.png"
            page.screenshot(path=str(out), full_page=True)
            probe = page.evaluate(
                """() => {
                    const ts = document.getElementById('target-select');
                    const rs = document.getElementById('region-select');
                    const periodInput = document.getElementById('period-input');
                    const topInput = document.getElementById('top-input');
                    return {
                        target_select_width: ts ? getComputedStyle(ts).width : null,
                        target_select_inline_style: ts ? ts.getAttribute('style') : null,
                        target_select_type: ts ? ts.tagName : null,
                        region_select_width: rs ? getComputedStyle(rs).width : null,
                        region_select_inline_style: rs ? rs.getAttribute('style') : null,
                        period_input_type: periodInput ? periodInput.getAttribute('type') : null,
                        period_input_width: periodInput ? getComputedStyle(periodInput).width : null,
                        top_input_width: topInput ? getComputedStyle(topInput).width : null,
                        body_scrollWidth: document.body.scrollWidth,
                        window_innerWidth: window.innerWidth,
                        overflow_x: document.body.scrollWidth > window.innerWidth,
                    };
                }"""
            )
            print(f"--- viewport {tag} ({w}x{h}) ---")
            for k, v in probe.items():
                print(f"  {k}: {v}")
            print(f"  written: {out}")
            context.close()
        browser.close()


if __name__ == "__main__":
    main()
