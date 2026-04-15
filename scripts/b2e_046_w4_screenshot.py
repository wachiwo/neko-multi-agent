#!/usr/bin/env python3
"""subtask_184_b2e_046_w4 self-verify screenshot: 046 @ 100/150/200%."""
from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.parse import quote

for p in ("/tmp/libasound/usr/lib/x86_64-linux-gnu/libasound.so.2",
          "/tmp/libasound_extract/usr/lib/x86_64-linux-gnu/libasound.so.2"):
    if os.path.exists(p) and not os.environ.get("LD_PRELOAD"):
        os.environ["LD_PRELOAD"] = p
        break

from playwright.sync_api import sync_playwright

TARGET = Path("/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new/046_支払予定一覧.html")
OUTDIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_184_b2e/phase1_w4")
ZOOMS = [1.0, 1.5, 2.0]

PROBE = """() => {
    const rows = document.querySelectorAll('.form-row');
    const fields = document.querySelectorAll('.form-field');
    const finlines = document.querySelectorAll('.form-field-inline');
    const collapsibleSections = document.querySelectorAll('.collapsible-section');
    const collapsibleHeaders = document.querySelectorAll('.collapsible-header');
    const dataTable = document.querySelector('.data-table');
    const detailTable = document.querySelector('.detail-table');
    return {
        form_row_count: rows.length,
        form_field_count: fields.length,
        form_field_inline_count: finlines.length,
        collapsible_section_count: collapsibleSections.length,
        collapsible_header_count: collapsibleHeaders.length,
        body_font_family: getComputedStyle(document.body).fontFamily,
        form_field_flex_direction: fields[0] ? getComputedStyle(fields[0]).flexDirection : null,
        data_table_layout: dataTable ? getComputedStyle(dataTable).tableLayout : null,
        detail_table_layout: detailTable ? getComputedStyle(detailTable).tableLayout : null,
        body_scrollWidth: document.body.scrollWidth,
        window_innerWidth: window.innerWidth,
        overflow_x: document.body.scrollWidth > window.innerWidth,
    };
}"""


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    report = {"file": str(TARGET), "zooms": {}}
    url = f"file://{quote(str(TARGET))}"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for zoom in ZOOMS:
            ctx = browser.new_context(viewport={"width": 1280, "height": 900})
            page = ctx.new_page()
            page.goto(url, wait_until="domcontentloaded")
            page.evaluate(f"document.body.style.zoom = '{zoom}'")
            page.wait_for_timeout(500)
            pct = int(zoom * 100)
            out = OUTDIR / f"046_zoom{pct}.png"
            page.screenshot(path=str(out), full_page=True)
            probe = page.evaluate(PROBE)
            report["zooms"][pct] = {"screenshot": str(out), "probe": probe}
            print(f"zoom {pct}%: overflow={probe['overflow_x']} data_table={probe['data_table_layout']} detail_table={probe['detail_table_layout']} ff_flex={probe['form_field_flex_direction']} form_row={probe['form_row_count']} form_field={probe['form_field_count']} form_field_inline={probe['form_field_inline_count']} collapsible={probe['collapsible_section_count']}")
            ctx.close()
        browser.close()
    (OUTDIR / "w4_046_probe_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\nJSON: {OUTDIR / 'w4_046_probe_report.json'}")


if __name__ == "__main__":
    main()
