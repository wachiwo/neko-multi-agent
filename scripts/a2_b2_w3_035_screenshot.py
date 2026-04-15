#!/usr/bin/env python3
"""subtask_184_a2_b2_035_w3 self-verify screenshot (Phase 0 FAIL 解消確認)."""
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
    "/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new/035_入金予定表出力指示.html"
)
OUTDIR = Path(
    "/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_184_phase_a2_b2/phase1_w3"
)
ZOOMS = [1.0, 1.5, 2.0]


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    url = f"file://{quote(str(TARGET))}"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for zoom in ZOOMS:
            context = browser.new_context(viewport={"width": 1280, "height": 900})
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded")
            page.evaluate(f"document.body.style.zoom = '{zoom}'")
            page.wait_for_timeout(500)
            pct = int(zoom * 100)
            out = OUTDIR / f"035_zoom{pct}.png"
            page.screenshot(path=str(out), full_page=True)
            probe = page.evaluate(
                """() => {
                    const fields = document.querySelectorAll('.form-field');
                    const fieldData = [];
                    fields.forEach((f, i) => {
                        const s = window.getComputedStyle(f);
                        fieldData.push({
                            idx: i,
                            flex_direction: s.flexDirection,
                            align_items: s.alignItems
                        });
                    });
                    const inline = document.querySelector('.form-field-inline');
                    const sp = document.querySelector('[data-component="SearchPanel"]');
                    return {
                        form_field_count: fields.length,
                        form_field_styles: fieldData,
                        all_column: fields.length > 0 && Array.from(fields).every(f => window.getComputedStyle(f).flexDirection === 'column'),
                        form_field_inline_exists: !!inline,
                        search_panel_exists: !!sp,
                        body_scrollWidth: document.body.scrollWidth,
                        window_innerWidth: window.innerWidth,
                        overflow_x: document.body.scrollWidth > window.innerWidth,
                    };
                }"""
            )
            print(f"zoom {pct}%: form-field count={probe['form_field_count']}, all_column={probe['all_column']}, form-field-inline={probe['form_field_inline_exists']}, SearchPanel={probe['search_panel_exists']}, overflow_x={probe['overflow_x']}")
            print(f"  written: {out}")
            context.close()
        browser.close()


if __name__ == "__main__":
    main()
