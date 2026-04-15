#!/usr/bin/env python3
"""subtask_184_b2a_resume_F1_w1 self-verify screenshot.

001_個人営業管理.html の form-field[1] 構造修正後、
zoom 100%/150%/200% の3段階で grid 崩壊/overflow を確認。
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
    "/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new/001_個人営業管理.html"
)
OUTDIR = Path(
    "/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/"
    "cmd_184_b2a_resume/f1_w1_self_verify"
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
            out = OUTDIR / f"001_zoom{pct}.png"
            page.screenshot(path=str(out), full_page=True)
            overflow = page.evaluate(
                """() => {
                    const row = document.querySelector('.form-row');
                    if (!row) return {error: 'no form-row'};
                    const rect = row.getBoundingClientRect();
                    const fields = document.querySelectorAll('.form-row .form-field');
                    const btn = document.querySelector('.btn-search');
                    return {
                        form_row_width: rect.width,
                        form_row_height: rect.height,
                        field_count_in_row: fields.length,
                        btn_exists: !!btn,
                        btn_parent_class: btn ? btn.parentElement.className : null,
                        body_scrollWidth: document.body.scrollWidth,
                        window_innerWidth: window.innerWidth,
                        overflow_x: document.body.scrollWidth > window.innerWidth,
                    };
                }"""
            )
            print(f"zoom {pct}%: {overflow}")
            print(f"  written: {out}")
            context.close()
        browser.close()


if __name__ == "__main__":
    main()
