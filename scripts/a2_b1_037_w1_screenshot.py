#!/usr/bin/env python3
"""subtask_184_a2_b1_037_w1 self-verify screenshot."""
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
    "/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new/037_仕掛在庫一覧表出力指示.html"
)
OUTDIR = Path(
    "/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_184_phase_a2_b1_pilot/phase1_w1"
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
            out = OUTDIR / f"037_zoom{pct}.png"
            page.screenshot(path=str(out), full_page=True)
            probe = page.evaluate(
                """() => {
                    const row = document.querySelector('.form-row');
                    const fields = document.querySelectorAll('.form-field');
                    const inlineG = document.querySelector('.form-field-inline');
                    const dateInputs = document.querySelectorAll('.form-field-inline input[type="date"]');
                    const dc = {
                        InputLayout: !!document.querySelector('[data-component="InputLayout"]'),
                        SearchPanel: !!document.querySelector('[data-component="SearchPanel"]'),
                        CollapsibleSection: !!document.querySelector('[data-component="CollapsibleSection"]'),
                        InputFieldContainer: !!document.querySelector('[data-component="InputFieldContainer"]'),
                        InlineFieldGroup: !!document.querySelector('[data-component="InlineFieldGroup"]'),
                    };
                    return {
                        form_row_display: row ? getComputedStyle(row).display : null,
                        form_row_grid_template: row ? getComputedStyle(row).gridTemplateColumns : null,
                        form_field_count: fields.length,
                        form_field_flex_dir: fields[0] ? getComputedStyle(fields[0]).flexDirection : null,
                        form_field_align_items: fields[0] ? getComputedStyle(fields[0]).alignItems : null,
                        form_field_inline_exists: !!inlineG,
                        form_field_inline_display: inlineG ? getComputedStyle(inlineG).display : null,
                        date_input_count: dateInputs.length,
                        date_input_width: dateInputs[0] ? getComputedStyle(dateInputs[0]).width : null,
                        data_components: dc,
                        body_scrollWidth: document.body.scrollWidth,
                        window_innerWidth: window.innerWidth,
                        overflow_x_main: document.body.scrollWidth > window.innerWidth,
                    };
                }"""
            )
            print(f"--- zoom {pct}% ---")
            for k, v in probe.items():
                print(f"  {k}: {v}")
            print(f"  written: {out}")
            context.close()
        browser.close()


if __name__ == "__main__":
    main()
