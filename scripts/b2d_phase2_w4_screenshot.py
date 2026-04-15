#!/usr/bin/env python3
"""subtask_184_b2d_phase2_verify_w4: 3viewport screenshots for 011/012/013."""
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

BASE = Path("/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new")
OUTDIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_184_b2d/phase2_w4_verify")
TARGETS = [
    ("011", BASE / "011_累計仕入先上位分析表.html"),
    ("012", BASE / "012_累計得意先上位分析表（粗利）.html"),
    ("013", BASE / "013_累計得意先上位分析表.html"),
]
ZOOMS = [1.0, 1.5, 2.0]

PROBE = """() => {
    const rows = document.querySelectorAll('.form-row');
    const fields = document.querySelectorAll('.form-field');
    const tables = document.querySelectorAll('table');
    const dataTable = document.querySelector('.data-table');
    return {
        form_row_count: rows.length,
        form_field_count: fields.length,
        table_count: tables.length,
        body_font_family: getComputedStyle(document.body).fontFamily,
        form_field_flex_direction: fields[0] ? getComputedStyle(fields[0]).flexDirection : null,
        data_table_layout: dataTable ? getComputedStyle(dataTable).tableLayout : null,
        data_table_min_width: dataTable ? getComputedStyle(dataTable).minWidth : null,
        data_table_width: dataTable ? getComputedStyle(dataTable).width : null,
        body_scrollWidth: document.body.scrollWidth,
        window_innerWidth: window.innerWidth,
        overflow_x: document.body.scrollWidth > window.innerWidth,
    };
}"""


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    report = {}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for tag, path in TARGETS:
            report[tag] = {"file": str(path), "zooms": {}}
            url = f"file://{quote(str(path))}"
            for zoom in ZOOMS:
                ctx = browser.new_context(viewport={"width": 1280, "height": 900})
                page = ctx.new_page()
                page.goto(url, wait_until="domcontentloaded")
                page.evaluate(f"document.body.style.zoom = '{zoom}'")
                page.wait_for_timeout(500)
                pct = int(zoom * 100)
                out = OUTDIR / f"{tag}_zoom{pct}.png"
                page.screenshot(path=str(out), full_page=True)
                probe = page.evaluate(PROBE)
                report[tag]["zooms"][pct] = {"screenshot": str(out), "probe": probe}
                print(f"[{tag}] zoom {pct}%: overflow={probe['overflow_x']} data_table_layout={probe['data_table_layout']} ff_flex={probe['form_field_flex_direction']}")
                ctx.close()
        browser.close()
    (OUTDIR / "w4_probe_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\nJSON report: {OUTDIR / 'w4_probe_report.json'}")


if __name__ == "__main__":
    main()
