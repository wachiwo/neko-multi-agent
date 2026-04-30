"""
cmd_214 subtask_214_021_w2_036_xr_real
W2 independent Playwright 3viewport verify for new横/036_入金予定一覧.html
- Verifies W3 self-fix (CSS dup removal at L395-439)
- Independent reproduction of W3 verify results
- 1024x768 / 1280x900 / 1920x1080
- collapsible expand/collapse ON/OFF screenshots
"""
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

TARGET = "/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new横/036_入金予定一覧.html"
OUT = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_214/w2_036_xr_screenshots")
OUT.mkdir(parents=True, exist_ok=True)

VIEWPORTS = [
    ("1024x768",  1024, 768),
    ("1280x900",  1280, 900),
    ("1920x1080", 1920, 1080),
]

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        results = []
        for label, w, h in VIEWPORTS:
            ctx = await browser.new_context(viewport={"width": w, "height": h})
            page = await ctx.new_page()
            url = "file://" + TARGET
            await page.goto(url)
            await page.wait_for_load_state("networkidle")

            # initial expanded screenshot
            png_open = OUT / f"036_xr_{label}_expanded.png"
            await page.screenshot(path=str(png_open), full_page=True)

            # initial state
            initial_max_h = await page.locator(".collapsible-content").first.evaluate(
                "el => el.style.maxHeight"
            )
            initial_collapsed = await page.locator(".collapsible-section").first.evaluate(
                "el => el.classList.contains('collapsed')"
            )
            title_count = await page.locator(".collapsible-title").count()
            indicator_text = await page.locator(".collapse-indicator").first.text_content()

            # 1st click (no-op visually, maxHeight '' -> 'none' via setTimeout)
            await page.locator(".collapsible-title").first.click()
            await page.wait_for_timeout(400)
            after_1st_max_h = await page.locator(".collapsible-content").first.evaluate(
                "el => el.style.maxHeight"
            )

            # 2nd click (actual collapse)
            await page.locator(".collapsible-title").first.click()
            await page.wait_for_timeout(600)
            png_collapsed = OUT / f"036_xr_{label}_collapsed.png"
            await page.screenshot(path=str(png_collapsed), full_page=True)
            collapsed_h = await page.locator(".collapsible-content").first.evaluate(
                "el => getComputedStyle(el).maxHeight"
            )
            section_collapsed = await page.locator(".collapsible-section").first.evaluate(
                "el => el.classList.contains('collapsed')"
            )
            indicator_rotation = await page.locator(".collapse-indicator").first.evaluate(
                "el => getComputedStyle(el).transform"
            )

            # 3rd click (re-expand)
            await page.locator(".collapsible-title").first.click()
            await page.wait_for_timeout(600)
            re_expanded_h = await page.locator(".collapsible-content").first.evaluate(
                "el => getComputedStyle(el).maxHeight"
            )
            section_re_expanded = await page.locator(".collapsible-section").first.evaluate(
                "el => el.classList.contains('collapsed')"
            )

            results.append({
                "viewport": label,
                "title_count": title_count,
                "indicator_text": (indicator_text or "").strip(),
                "initial_max_height": initial_max_h,
                "initial_collapsed_class": initial_collapsed,
                "after_1st_click_max_height": after_1st_max_h,
                "collapsed_max_height": collapsed_h,
                "section_collapsed_class": section_collapsed,
                "indicator_rotation_when_collapsed": indicator_rotation,
                "re_expanded_max_height": re_expanded_h,
                "section_re_expanded_class": section_re_expanded,
                "png_expanded": str(png_open),
                "png_collapsed": str(png_collapsed),
            })
            await ctx.close()
        await browser.close()
        return results

if __name__ == "__main__":
    res = asyncio.run(run())
    out_json = OUT / "_xr_verify.json"
    with out_json.open("w") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)
    for r in res:
        print(f"--- {r['viewport']} ---")
        for k, v in r.items():
            print(f"  {k}: {v}")
    print(f"\nResults JSON: {out_json}")
