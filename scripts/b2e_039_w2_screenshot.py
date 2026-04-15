#!/usr/bin/env python3
"""subtask_184_b2e_039_w2 self-verify screenshot.

039_支払予定表出力指示.html の B2e 本格改修後、
zoom 100%/150%/200% の3段階で grid 崩壊/overflow を確認。
sp_042 date-range canonical + 2 CollapsibleSection (抽出条件/集計方法) の適用結果を visual + probe で検証。
"""
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
    "/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new/039_支払予定表出力指示.html"
)
OUTDIR = Path(
    "/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/"
    "cmd_184_b2e/phase1_w2"
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
            out = OUTDIR / f"039_zoom{pct}.png"
            page.screenshot(path=str(out), full_page=True)
            probe = page.evaluate(
                """() => {
                    const rows = document.querySelectorAll('.form-row');
                    const fields = document.querySelectorAll('.form-field');
                    const inlines = document.querySelectorAll('.form-field-inline');
                    const dateInputs = document.querySelectorAll('.form-field-inline input[type="date"]');
                    const collapsibles = document.querySelectorAll('.collapsible-header');
                    const dc = {
                        InputLayout: !!document.querySelector('[data-component="InputLayout"]'),
                        SearchPanel: !!document.querySelector('[data-component="SearchPanel"]'),
                        CollapsibleSection: document.querySelectorAll('[data-component="CollapsibleSection"]').length,
                        InputFieldContainer: document.querySelectorAll('[data-component="InputFieldContainer"]').length,
                        DataGridTable: document.querySelectorAll('[data-component="DataGridTable"]').length,
                    };
                    return {
                        form_row_count: rows.length,
                        form_row_displays: Array.from(rows).map(r => getComputedStyle(r).display),
                        form_row_grid_templates: Array.from(rows).map(r => getComputedStyle(r).gridTemplateColumns),
                        form_field_count: fields.length,
                        field_flex_dir: fields[0] ? getComputedStyle(fields[0]).flexDirection : null,
                        field_align_items: fields[0] ? getComputedStyle(fields[0]).alignItems : null,
                        form_field_inline_count: inlines.length,
                        date_input_count: dateInputs.length,
                        date_input_widths: Array.from(dateInputs).map(d => getComputedStyle(d).width),
                        collapsible_count: collapsibles.length,
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
