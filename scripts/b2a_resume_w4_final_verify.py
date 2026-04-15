#!/usr/bin/env python3
"""subtask_184_b2a_resume_verify_w4: F1+F2 final verify screenshots.

001 (F1, W1 fix) と 002 (F2, W2 fix) を zoom 100%/150%/200% で
Playwright で描画し、overflow / layout 破綻の機械チェック + PNG 保存。
"""
from __future__ import annotations

import json
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
OUTDIR = Path(
    "/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/"
    "cmd_184_b2a_resume/w4_final_verify"
)
TARGETS = [
    ("001", BASE / "001_個人営業管理.html"),
    ("002", BASE / "002_国別累計仕入先上位分析表.html"),
]
ZOOMS = [1.0, 1.5, 2.0]


PROBE_001 = """() => {
    const row = document.querySelector('.form-row');
    const fields = document.querySelectorAll('.form-row .form-field');
    const btn = document.querySelector('.btn-search');
    const rect = row ? row.getBoundingClientRect() : null;
    return {
        form_row_width: rect ? rect.width : null,
        form_row_height: rect ? rect.height : null,
        field_count_in_row: fields.length,
        btn_exists: !!btn,
        btn_parent_tag: btn ? btn.parentElement.tagName : null,
        btn_parent_class: btn ? (btn.parentElement.className || '(inline-style-div)') : null,
        btn_inside_form_row: btn ? !!btn.closest('.form-row') : null,
        body_scrollWidth: document.body.scrollWidth,
        window_innerWidth: window.innerWidth,
        overflow_x: document.body.scrollWidth > window.innerWidth,
        body_font_family: getComputedStyle(document.body).fontFamily,
    };
}"""

PROBE_002 = """() => {
    const rows = document.querySelectorAll('.form-row');
    const fields = document.querySelectorAll('.form-row .form-field');
    const btns = document.querySelectorAll('button');
    return {
        form_row_count: rows.length,
        form_field_total: fields.length,
        button_count: btns.length,
        body_scrollWidth: document.body.scrollWidth,
        window_innerWidth: window.innerWidth,
        overflow_x: document.body.scrollWidth > window.innerWidth,
        body_font_family: getComputedStyle(document.body).fontFamily,
    };
}"""

PROBES = {"001": PROBE_001, "002": PROBE_002}


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
                probe = page.evaluate(PROBES[tag])
                report[tag]["zooms"][pct] = {"screenshot": str(out), "probe": probe}
                print(f"[{tag}] zoom {pct}%: {probe}")
                print(f"  written: {out}")
                ctx.close()
        browser.close()
    (OUTDIR / "probe_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\nJSON report: {OUTDIR / 'probe_report.json'}")


if __name__ == "__main__":
    main()
