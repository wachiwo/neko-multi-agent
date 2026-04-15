#!/usr/bin/env python3
"""subtask_184_a2_b1_027_041_042_w2 self-verify screenshots.

3 files (027/041/042) の A2 b1 retrofit 後、zoom 100%/150%/200% 確認。
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

BASE = Path("/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new")
TARGETS = ["027_納期回答一覧.html", "041_売掛一覧表出力指示.html", "042_請求書出力指示.html"]
OUTDIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_184_phase_a2_b1_pilot/phase1_w2")
ZOOMS = [1.0, 1.5, 2.0]


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for target_name in TARGETS:
            target = BASE / target_name
            url = f"file://{quote(str(target))}"
            stem = target_name.split('_')[0]
            for zoom in ZOOMS:
                context = browser.new_context(viewport={"width": 1280, "height": 900})
                page = context.new_page()
                page.goto(url, wait_until="domcontentloaded")
                page.evaluate(f"document.body.style.zoom = '{zoom}'")
                page.wait_for_timeout(500)
                pct = int(zoom * 100)
                out = OUTDIR / f"{stem}_zoom{pct}.png"
                page.screenshot(path=str(out), full_page=True)
                probe = page.evaluate(
                    """() => {
                        const rows = document.querySelectorAll('.form-row');
                        const fields = document.querySelectorAll('.form-field');
                        const inlines = document.querySelectorAll('.form-field-inline');
                        const dateInputs = document.querySelectorAll('.form-field-inline input[type="date"]');
                        const collapsibles = document.querySelectorAll('.collapsible-header');
                        const table = document.querySelector('.data-table, table');
                        const dc = {
                            InputLayout: document.querySelectorAll('[data-component="InputLayout"]').length,
                            SearchPanel: document.querySelectorAll('[data-component="SearchPanel"]').length,
                            CollapsibleSection: document.querySelectorAll('[data-component="CollapsibleSection"]').length,
                            InputFieldContainer: document.querySelectorAll('[data-component="InputFieldContainer"]').length,
                            DataGridTable: document.querySelectorAll('[data-component="DataGridTable"]').length,
                            InlineFieldGroup: document.querySelectorAll('[data-component="InlineFieldGroup"]').length,
                        };
                        return {
                            form_row_count: rows.length,
                            form_field_count: fields.length,
                            field_flex_dir: fields[0] ? getComputedStyle(fields[0]).flexDirection : null,
                            field_align_items: fields[0] ? getComputedStyle(fields[0]).alignItems : null,
                            form_field_inline_count: inlines.length,
                            date_input_count: dateInputs.length,
                            collapsible_count: collapsibles.length,
                            table_layout: table ? getComputedStyle(table).tableLayout : null,
                            data_components: dc,
                            body_scrollWidth: document.body.scrollWidth,
                            window_innerWidth: window.innerWidth,
                            overflow_x_main: document.body.scrollWidth > window.innerWidth,
                        };
                    }"""
                )
                print(f"=== {stem} zoom {pct}% ===")
                for k, v in probe.items():
                    print(f"  {k}: {v}")
                context.close()
        browser.close()


if __name__ == "__main__":
    main()
