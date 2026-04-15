#!/usr/bin/env python3
"""subtask_184_b2c_009_w2 self-verify screenshot.

009_売上粗利表.html の B2c 本格改修後、
zoom 100%/150%/200% の3段階で grid 崩壊/overflow を確認。
sp_041 table-layout:fixed + sp_042 date-range canonical の適用結果を visual + probe で検証。
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
    "/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new/009_売上粗利表.html"
)
OUTDIR = Path(
    "/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/"
    "cmd_184_b2c/phase1_w2"
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
            page.wait_for_timeout(600)
            pct = int(zoom * 100)
            out = OUTDIR / f"009_zoom{pct}.png"
            page.screenshot(path=str(out), full_page=True)
            probe = page.evaluate(
                """() => {
                    const row = document.querySelector('.form-row');
                    const fields = document.querySelectorAll('.form-row .form-field');
                    const inline = document.querySelector('.form-field-inline');
                    const btn = document.querySelector('.container .btn');
                    const collapsible = document.querySelector('.collapsible-header');
                    const table = document.querySelector('.data-table');
                    const dc = {
                        InputLayout: !!document.querySelector('[data-component="InputLayout"]'),
                        SearchPanel: !!document.querySelector('[data-component="SearchPanel"]'),
                        CollapsibleSection: !!document.querySelector('[data-component="CollapsibleSection"]'),
                        InputFieldContainer: !!document.querySelector('[data-component="InputFieldContainer"]'),
                        DataGridTable: document.querySelectorAll('[data-component="DataGridTable"]').length,
                    };
                    return {
                        form_row_exists: !!row,
                        form_row_display: row ? getComputedStyle(row).display : null,
                        form_row_grid_template: row ? getComputedStyle(row).gridTemplateColumns : null,
                        field_count_in_row: fields.length,
                        field_flex_dir: fields[0] ? getComputedStyle(fields[0]).flexDirection : null,
                        field_align_items: fields[0] ? getComputedStyle(fields[0]).alignItems : null,
                        form_field_inline_exists: !!inline,
                        form_field_inline_display: inline ? getComputedStyle(inline).display : null,
                        date_input_count_in_inline: inline ? inline.querySelectorAll('input[type="date"]').length : 0,
                        btn_exists: !!btn,
                        btn_parent_style: btn ? btn.parentElement.getAttribute('style') : null,
                        collapsible_header_exists: !!collapsible,
                        table_layout: table ? getComputedStyle(table).tableLayout : null,
                        table_width: table ? table.getBoundingClientRect().width : null,
                        table_column_count: table ? table.querySelectorAll('thead tr:last-child th').length : 0,
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
