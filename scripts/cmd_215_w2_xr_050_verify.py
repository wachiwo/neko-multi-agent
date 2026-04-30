"""
cmd_215 subtask_215_011_w2_050_xr_real
W2 independent Playwright 3viewport verify for new横/050_海外引合.html (post-W3 port)
- 12 sections × canonical migration verify
- 016 byte-match toggleSection logic 確認
- 初期 全 collapsed state 維持 (file 固有 design intent)
"""
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

TARGET = "/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new横/050_海外引合.html"
OUT = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_215/w2_050_xr_screenshots")
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

            section_count = await page.locator(".collapsible-section").count()
            title_count = await page.locator(".collapsible-title").count()
            content_count = await page.locator(".collapsible-content").count()
            indicator_texts = await page.locator(".collapse-indicator").all_text_contents()
            distinct_indicators = sorted(set(t.strip() for t in indicator_texts if t.strip()))

            png_initial = OUT / f"050_xr_{label}_initial_collapsed.png"
            await page.screenshot(path=str(png_initial), full_page=True)

            initial_max_heights = await page.evaluate(
                """() => Array.from(document.querySelectorAll('.collapsible-content'))
                    .map(el => getComputedStyle(el).maxHeight)"""
            )

            await page.locator(".collapsible-title").nth(0).click()
            await page.wait_for_timeout(500)
            after_first_click_max_height = await page.locator(".collapsible-content").nth(0).evaluate(
                "el => getComputedStyle(el).maxHeight"
            )
            section_class_after_open = await page.locator(".collapsible-section").nth(0).evaluate(
                "el => el.classList.contains('collapsed')"
            )
            indicator_rotation_open = await page.locator(".collapse-indicator").nth(0).evaluate(
                "el => getComputedStyle(el).transform"
            )

            await page.locator(".collapsible-title").nth(1).click()
            await page.wait_for_timeout(500)

            png_two_open = OUT / f"050_xr_{label}_2_sections_open.png"
            await page.screenshot(path=str(png_two_open), full_page=True)

            await page.locator(".collapsible-title").nth(0).click()
            await page.wait_for_timeout(500)
            after_close_max_height = await page.locator(".collapsible-content").nth(0).evaluate(
                "el => getComputedStyle(el).maxHeight"
            )
            indicator_rotation_close = await page.locator(".collapse-indicator").nth(0).evaluate(
                "el => getComputedStyle(el).transform"
            )

            results.append({
                "viewport": label,
                "section_count": section_count,
                "title_count": title_count,
                "content_count": content_count,
                "distinct_indicators": distinct_indicators,
                "initial_all_max_heights": initial_max_heights,
                "after_open_first_max_height": after_first_click_max_height,
                "section_collapsed_class_after_open": section_class_after_open,
                "indicator_rotation_open": indicator_rotation_open,
                "after_close_first_max_height": after_close_max_height,
                "indicator_rotation_close": indicator_rotation_close,
                "png_initial": str(png_initial),
                "png_two_open": str(png_two_open),
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
