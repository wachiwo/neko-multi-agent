#!/usr/bin/env python3
"""subtask_184_a2_b2_023_w1 self-verify screenshot (extreme case verify)."""
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

TARGET = Path("/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new/023_出荷.html")
OUTDIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_184_phase_a2_b2/phase1_w1")
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
            out = OUTDIR / f"023_zoom{pct}.png"
            page.screenshot(path=str(out), full_page=True)
            probe = page.evaluate(
                """() => {
                    const formRows = document.querySelectorAll('.form-row');
                    const formFields = document.querySelectorAll('.form-field');
                    const dataTable = document.querySelector('.data-table');
                    const docTable = document.querySelector('.doc-table');
                    const dc_summary = {};
                    ['InputLayout','SearchPanel','CollapsibleSection','InputFieldContainer','DataGridTable'].forEach(t => {
                        dc_summary[t] = document.querySelectorAll(`[data-component="${t}"]`).length;
                    });
                    // probe 1: form-field flex-direction
                    const ff_column_count = Array.from(formFields).filter(el => getComputedStyle(el).flexDirection === 'column').length;
                    return {
                        form_row_count: formRows.length,
                        form_field_count: formFields.length,
                        form_field_column_count: ff_column_count,
                        data_table_layout: dataTable ? getComputedStyle(dataTable).tableLayout : null,
                        doc_table_layout: docTable ? getComputedStyle(docTable).tableLayout : null,
                        data_components: dc_summary,
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
