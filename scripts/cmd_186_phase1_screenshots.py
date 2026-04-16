#!/usr/bin/env python3
"""cmd_186 Phase 1 W2: before/after screenshot capture (15 files x 3 viewports)"""
import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

NEW_DIR = Path("/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new")
OUT_DIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_186_phase1_express/screenshots_w2")

FILES = [
    "014_見積一覧", "015_見積明細", "016_受注一覧", "017_商談一覧", "018_発注一覧",
    "019_発注明細", "020_未発注一覧", "021_作業予定一覧", "022_作業予定表",
    "023_出荷", "024_出荷一覧", "025_入庫", "026_入庫一覧",
    "027_納期回答一覧", "028_納品書一覧",
]
ZOOMS = [
    ("zoom100", 1200, 900),
    ("zoom150", 800, 600),
    ("zoom200", 600, 450),
]


async def shoot(page, html_path, label, zoom_label, w, h):
    await page.set_viewport_size({"width": w, "height": h})
    await page.goto(f"file://{html_path}", wait_until="domcontentloaded", timeout=15000)
    await page.wait_for_timeout(400)
    out = OUT_DIR / f"{html_path.stem}_{label}_{zoom_label}.png"
    await page.screenshot(path=str(out), full_page=False)


async def main():
    label = sys.argv[1] if len(sys.argv) > 1 else "before"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Capturing {label} screenshots: {len(FILES)} files x {len(ZOOMS)} zooms")
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        ctx = await browser.new_context()
        page = await ctx.new_page()
        for i, name in enumerate(FILES, 1):
            html = NEW_DIR / f"{name}.html"
            if not html.exists():
                print(f"  [{i}/{len(FILES)}] MISSING: {name}")
                continue
            for zl, w, h in ZOOMS:
                await shoot(page, html, label, zl, w, h)
            print(f"  [{i}/{len(FILES)}] {name} ({label})", flush=True)
        await browser.close()
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
