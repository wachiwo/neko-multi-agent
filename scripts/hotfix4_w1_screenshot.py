#!/usr/bin/env python3
"""subtask_184_hotfix4_002_w1 step_9 self-verify screenshot.

031 (仕入先 input 拡大確認) + 032 (色統一確認) を 1200/800/600 viewport で撮影、計6枚。
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

PROJECT_ROOT = Path(
    "/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype"
)
TARGETS = [
    "new/031_発送一覧.html",
    "new/032_在庫一覧.html",
]
OUTDIR = Path(
    "/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/"
    "cmd_184_hotfix4_field_width_tuning/w1_self_verify"
)
VIEWPORTS = [1200, 800, 600]


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for rel in TARGETS:
            abs_path = PROJECT_ROOT / rel
            url = f"file://{quote(str(abs_path))}"
            tag = abs_path.stem.split("_")[0]
            for vp in VIEWPORTS:
                context = browser.new_context(viewport={"width": vp, "height": 900})
                page = context.new_page()
                page.goto(url, wait_until="domcontentloaded")
                page.wait_for_timeout(600)
                out = OUTDIR / f"{tag}_{vp}w.png"
                page.screenshot(path=str(out), full_page=True)
                print(f"written: {out}")
                context.close()
        browser.close()


if __name__ == "__main__":
    main()
