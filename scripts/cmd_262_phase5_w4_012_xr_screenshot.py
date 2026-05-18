#!/usr/bin/env python3
"""cmd_262 Phase 5 W4 mutual XR — 012 累計得意先上位分析表（粗利）fresh verify."""
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
    "/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/002_new横/012_累計得意先上位分析表（粗利）.html"
)
OUTDIR = Path("/mnt/c/tools/neko-multi-agent/outputs/cmd_262/phase5_w4_012_xr_screenshots")
VIEWPORTS = [
    ("375", 375, 800),
    ("960", 960, 800),
    ("1920", 1920, 1080),
]


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    url = f"file://{quote(str(TARGET))}"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for tag, w, h in VIEWPORTS:
            context = browser.new_context(viewport={"width": w, "height": h})
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(500)
            out = OUTDIR / f"012_vw{tag}.png"
            page.screenshot(path=str(out), full_page=True)
            probe = page.evaluate(
                """() => {
                    const ts = document.getElementById('target-select');
                    const rs = document.getElementById('region-select');
                    const ds = document.getElementById('department-select');
                    const periodInput = document.getElementById('period-input');
                    const topInput = document.getElementById('top-input');
                    const ct = document.querySelector('.collapsible-title');
                    const fc = document.getElementById('filter-content');
                    const searchBtn = document.querySelector('.page-header .export-section .search-btn');
                    const outputBtn = document.querySelector('.page-header .export-section .output-button');
                    const clearBtn = document.querySelector('.page-header .export-section .clear-btn');
                    const phLeft = document.querySelector('.page-header > .page-header-left');
                    const phExport = document.querySelector('.page-header > .export-section');
                    const grossProfitTh = Array.from(document.querySelectorAll('th')).find(th => th.textContent.trim() === '粗利');
                    const dataTab = document.querySelector('.tab-container, .tab-button, .tab-content');
                    return {
                        target_select_width: ts ? getComputedStyle(ts).width : null,
                        target_select_inline_style: ts ? ts.getAttribute('style') : null,
                        department_select_width: ds ? getComputedStyle(ds).width : null,
                        department_select_classlist: ds ? ds.className : null,
                        region_select_width: rs ? getComputedStyle(rs).width : null,
                        period_input_type: periodInput ? periodInput.getAttribute('type') : null,
                        period_input_width: periodInput ? getComputedStyle(periodInput).width : null,
                        top_input_type: topInput ? topInput.getAttribute('type') : null,
                        top_input_width: topInput ? getComputedStyle(topInput).width : null,
                        collapsible_title_text: ct ? ct.innerText.replace(/\\s+/g, ' ').trim() : null,
                        filter_content_exists: !!fc,
                        search_btn_in_page_header: !!searchBtn,
                        search_btn_onclick: searchBtn ? searchBtn.getAttribute('onclick') : null,
                        output_btn_in_page_header: !!outputBtn,
                        output_btn_onclick: outputBtn ? outputBtn.getAttribute('onclick') : null,
                        clear_btn_in_page_header: !!clearBtn,
                        page_header_canonical: !!(phLeft && phExport),
                        grossprofit_th_exists: !!grossProfitTh,
                        tab_container_exists: !!dataTab,
                        body_scrollWidth: document.body.scrollWidth,
                        window_innerWidth: window.innerWidth,
                        overflow_x: document.body.scrollWidth > window.innerWidth,
                    };
                }"""
            )
            print(f"--- viewport {tag} ({w}x{h}) ---")
            for k, v in probe.items():
                print(f"  {k}: {v}")
            print(f"  written: {out}")
            context.close()
        browser.close()


if __name__ == "__main__":
    main()
