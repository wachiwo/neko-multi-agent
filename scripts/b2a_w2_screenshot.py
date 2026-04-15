#!/usr/bin/env python3
"""subtask_184_pap_b2a_002_w2 step_6 self-verify screenshot.

001_個人営業管理.html を 1200/800/600 の3 viewport で撮影、
form-row/form-field + data-component 適用後の視覚確認。
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
    "cmd_184_phase_a_pivot/b2a_w2_self_verify"
)
VIEWPORTS = [1200, 800, 600]


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    url = f"file://{quote(str(TARGET))}"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for vp in VIEWPORTS:
            context = browser.new_context(viewport={"width": vp, "height": 900})
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(600)
            out = OUTDIR / f"001_{vp}w.png"
            page.screenshot(path=str(out), full_page=True)
            print(f"written: {out}")
            context.close()
        browser.close()


if __name__ == "__main__":
    main()
