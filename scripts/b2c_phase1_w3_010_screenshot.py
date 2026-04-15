#!/usr/bin/env python3
"""subtask_184_b2c_010_w3 self-verify screenshot.

010_売上予測表.html の B2c Phase 1 改修後、zoom 100/150/200% で
form-row/form-field canonical 準拠 + sp_041 table-layout:fixed + overflow を確認。
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
    "/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new/010_売上予測表.html"
)
OUTDIR = Path(
    "/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_184_b2c/phase1_w3"
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
            out = OUTDIR / f"010_zoom{pct}.png"
            page.screenshot(path=str(out), full_page=True)
            probe = page.evaluate(
                """() => {
                    const row = document.querySelector('.form-row');
                    const fields = document.querySelectorAll('.form-row .form-field');
                    const inline = document.querySelector('.form-field-inline');
                    const btn = document.querySelector('.btn');
                    const dgt = document.querySelectorAll('[data-component="DataGridTable"]');
                    const layout = document.querySelector('[data-component="InputLayout"]');
                    const collapsible = document.querySelectorAll('[data-component="CollapsibleSection"]');
                    const dataTable = document.querySelector('.data-table');
                    const summaryTable = document.querySelector('.summary-table');
                    const fieldStyle = fields[0] ? window.getComputedStyle(fields[0]) : null;
                    return {
                        form_row_exists: !!row,
                        form_row_display: row ? window.getComputedStyle(row).display : null,
                        field_count_in_row: fields.length,
                        form_field_flex_direction: fieldStyle ? fieldStyle.flexDirection : null,
                        form_field_align_items: fieldStyle ? fieldStyle.alignItems : null,
                        form_field_inline_exists: !!inline,
                        btn_exists: !!btn,
                        btn_parent_class: btn ? btn.parentElement.className : null,
                        input_layout_orientation: layout ? layout.getAttribute('data-orientation') : null,
                        collapsible_count: collapsible.length,
                        data_grid_table_count: dgt.length,
                        data_table_layout: dataTable ? window.getComputedStyle(dataTable).tableLayout : null,
                        summary_table_layout: summaryTable ? window.getComputedStyle(summaryTable).tableLayout : null,
                        data_table_min_width: dataTable ? window.getComputedStyle(dataTable).minWidth : null,
                        body_scrollWidth: document.body.scrollWidth,
                        window_innerWidth: window.innerWidth,
                        overflow_x: document.body.scrollWidth > window.innerWidth,
                    };
                }"""
            )
            print(f"zoom {pct}%: {probe}")
            print(f"  written: {out}")
            context.close()
        browser.close()


if __name__ == "__main__":
    main()
