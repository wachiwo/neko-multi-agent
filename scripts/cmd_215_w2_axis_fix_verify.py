"""
cmd_215 subtask_215_002_w2_axis2_axis3_fix
W2 Playwright 3viewport visual verify for 4 files (post axis 2 + axis 3 fix)
- 015 / 036 / 042 / 043
- 1024x768 / 1280x900 / 1920x1080 expanded only (visual unchanged confirm)
- 043 expanded + collapsed (axis 2 fix verify)
"""
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

BASE = "/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new横/"
OUT = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_215/w2_axis_fix_screenshots")
OUT.mkdir(parents=True, exist_ok=True)

FILES = [
    ("015", "015_見積明細.html"),
    ("036", "036_入金予定一覧.html"),
    ("042", "042_請求書出力指示.html"),
    ("043", "043_得意先売上一覧表.html"),
]
VIEWPORTS = [
    ("1024x768",  1024, 768),
    ("1280x900",  1280, 900),
    ("1920x1080", 1920, 1080),
]

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        all_results = {}
        for fid, fname in FILES:
            file_results = []
            for label, w, h in VIEWPORTS:
                ctx = await browser.new_context(viewport={"width": w, "height": h})
                page = await ctx.new_page()
                url = "file://" + BASE + fname
                await page.goto(url)
                await page.wait_for_load_state("networkidle")

                png = OUT / f"{fid}_{label}_expanded.png"
                await page.screenshot(path=str(png), full_page=True)

                # 043 only: collapsed test (axis 2 fix verify)
                collapsed_data = None
                if fid == "043":
                    title_count = await page.locator(".collapsible-title").count()
                    if title_count > 0:
                        await page.locator(".collapsible-title").first.click()
                        await page.wait_for_timeout(400)
                        await page.locator(".collapsible-title").first.click()
                        await page.wait_for_timeout(600)
                        png_c = OUT / f"{fid}_{label}_collapsed.png"
                        await page.screenshot(path=str(png_c), full_page=True)
                        collapsed_h = await page.locator(".collapsible-content").first.evaluate(
                            "el => getComputedStyle(el).maxHeight"
                        )
                        section_collapsed = await page.locator(".collapsible-section").first.evaluate(
                            "el => el.classList.contains('collapsed')"
                        )
                        collapsed_data = {
                            "collapsed_max_height": collapsed_h,
                            "section_collapsed_class": section_collapsed,
                            "png_collapsed": str(png_c),
                        }

                file_results.append({
                    "viewport": label,
                    "png_expanded": str(png),
                    "collapsed": collapsed_data,
                })
                await ctx.close()
            all_results[fid] = file_results
        await browser.close()
        return all_results

if __name__ == "__main__":
    res = asyncio.run(run())
    out_json = OUT / "_axis_fix_verify.json"
    with out_json.open("w") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)
    for fid, file_results in res.items():
        print(f"=== {fid} ===")
        for r in file_results:
            print(f"  {r['viewport']}: expanded={Path(r['png_expanded']).name}")
            if r.get('collapsed'):
                print(f"    collapsed: max_h={r['collapsed']['collapsed_max_height']}, section_collapsed={r['collapsed']['section_collapsed_class']}")
    print(f"\nResults JSON: {out_json}")
