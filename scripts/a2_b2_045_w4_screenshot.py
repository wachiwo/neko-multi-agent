#!/usr/bin/env python3
"""subtask_184_a2_b2_045_w4: 3viewport screenshots for 045."""
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

TARGET = Path("/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new/045_買掛一覧表出力指示.html")
OUTDIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_184_phase_a2_b2/phase1_w4")
ZOOMS = [1.0, 1.5, 2.0]

PROBE = """() => {
    const fields = document.querySelectorAll('.form-field');
    const rows = document.querySelectorAll('.form-row');
    const finlines = document.querySelectorAll('.form-field-inline');
    return {
        form_row_count: rows.length,
        form_field_count: fields.length,
        form_field_inline_count: finlines.length,
        form_field_flex_direction_element_0: fields[0] ? getComputedStyle(fields[0]).flexDirection : null,
        form_field_flex_direction_element_1: fields[1] ? getComputedStyle(fields[1]).flexDirection : null,
        body_font_family: getComputedStyle(document.body).fontFamily,
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
            out = OUTDIR / f"045_zoom{pct}.png"
            page.screenshot(path=str(out), full_page=True)
            probe = page.evaluate(PROBE)
            report["zooms"][pct] = {"screenshot": str(out), "probe": probe}
            print(f"zoom {pct}%: overflow={probe['overflow_x']} ff[0]={probe['form_field_flex_direction_element_0']} ff[1]={probe['form_field_flex_direction_element_1']} form_row={probe['form_row_count']} form_field={probe['form_field_count']} form_field_inline={probe['form_field_inline_count']}")
            ctx.close()
        browser.close()
    (OUTDIR / "w4_045_probe_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
