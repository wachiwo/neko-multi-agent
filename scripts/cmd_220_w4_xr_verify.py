#!/usr/bin/env python3
"""cmd_220 W4 cross-review — independent Playwright 3vp visual restoration verify."""
import os, sys, json
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

TARGET = Path("/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new横/053_海外取引一覧.html")
OUTDIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_220/w4_phase4_xr_screenshots")
VIEWPORTS = [(1024, 768), (1280, 900), (1920, 1080)]


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    url = f"file://{quote(str(TARGET))}"
    results = {"file": TARGET.name, "viewports": {}}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for w, h in VIEWPORTS:
            ctx = browser.new_context(viewport={"width": w, "height": h})
            page = ctx.new_page()
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(600)

            probe = page.evaluate("""() => {
                // excel-table th visual restoration check
                const th = document.querySelector('.excel-table th');
                const td = document.querySelector('.excel-table td');
                // table-container check
                const tc = document.querySelector('.table-container');
                // data-table th
                const dth = document.querySelector('.data-table th');
                // page-header / sidebar / app-container basic
                const ph = document.querySelector('.page-header');
                const sb = document.querySelector('.sidebar');
                // hierarchical table row count
                const rows = document.querySelectorAll('.data-table tbody tr').length;
                // search modal count
                const modals = document.querySelectorAll('[id*="customerSearchModal"], [id*="searchModal"], [class*="modal"]').length;
                // legacy .search-form CSS still present?
                const sfElements = document.querySelectorAll('.search-form, .search-form-row, .search-form-field').length;

                const measure = (el) => el ? {
                    bg: getComputedStyle(el).backgroundColor,
                    color: getComputedStyle(el).color,
                    border_right: getComputedStyle(el).borderRight,
                    padding: getComputedStyle(el).padding
                } : null;

                return {
                    excel_table_th_style: measure(th),
                    excel_table_td_style: measure(td),
                    data_table_th_style: measure(dth),
                    page_header_style: measure(ph),
                    sidebar_exists: !!sb,
                    hierarchical_table_rows: rows,
                    modal_elements_count: modals,
                    legacy_search_form_dom_count: sfElements
                };
            }""")
            results["viewports"][f"{w}x{h}"] = probe
            page.screenshot(path=str(OUTDIR / f"053_xr_{w}x{h}.png"), full_page=True)
            ctx.close()
        browser.close()

    out_json = OUTDIR / "_xr_verify.json"
    out_json.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
