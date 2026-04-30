#!/usr/bin/env python3
"""cmd_214 W1 015_見積明細 collapsible port verify.

3 viewport screenshots + toggle interaction test + hold-list render probe
(担当者 width 180px ×2 + 22ch ×9 桁数 保持必須リスト visual evidence).
"""
import os
import json
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
    "/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new横/015_見積明細.html"
)
OUTDIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_214/w1_015_screenshots")

VIEWPORTS = [
    (1024, 768),
    (1280, 900),
    (1920, 1080),
]


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    url = f"file://{quote(str(TARGET))}"
    results = {"file": TARGET.name, "viewports": {}, "toggle_test": {}, "hold_list_probe": {}}

    with sync_playwright() as p:
        browser = p.chromium.launch()

        for w, h in VIEWPORTS:
            context = browser.new_context(viewport={"width": w, "height": h})
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(400)

            probe = page.evaluate(
                """() => {
                const secs = document.querySelectorAll('.collapsible-section');
                const titles = document.querySelectorAll('.collapsible-title');
                const contents = document.querySelectorAll('.collapsible-content');
                const indicators = document.querySelectorAll('.collapse-indicator');
                const ph = document.querySelector('.page-header');
                const get = (el) => el ? {
                    bg: getComputedStyle(el).backgroundColor,
                    color: getComputedStyle(el).color,
                    display: getComputedStyle(el).display,
                    text: el.textContent ? el.textContent.trim().slice(0, 40) : null
                } : null;
                return {
                    section_count: secs.length,
                    title_count: titles.length,
                    content_count: contents.length,
                    indicator_count: indicators.length,
                    first_title_style: get(titles[0]),
                    first_content_style: get(contents[0]),
                    first_indicator: indicators[0] ? indicators[0].textContent.trim() : null,
                    page_header_pos: ph ? getComputedStyle(ph).position : null,
                    excel_table_in_content: !!document.querySelector('.collapsible-content .excel-table'),
                };
            }"""
            )
            # Hold-list probe: 180px selects (営業担当者 + 見積作成者) + first 22ch input
            hold_probe = page.evaluate(
                """() => {
                // 営業担当者 + 見積作成者 selects (180px hold list)
                const allSelects = Array.from(document.querySelectorAll('select'));
                const sel180 = allSelects.filter(s => s.style && s.style.width === '180px');
                const sel180Widths = sel180.map(s => s.getBoundingClientRect().width);
                // 22ch inputs (9 hold list)
                const allInputs = Array.from(document.querySelectorAll('input'));
                const inp22 = allInputs.filter(i => i.style && i.style.width === '22ch');
                const inp22Widths = inp22.map(i => i.getBoundingClientRect().width);
                // 担当者 (label + input pairs)
                const ths = Array.from(document.querySelectorAll('.excel-table th'));
                const tantoTh = ths.filter(t => t.textContent.trim() === '担当者');
                return {
                    selects_180px_count: sel180.length,
                    selects_180px_widths: sel180Widths,
                    inputs_22ch_count: inp22.length,
                    inputs_22ch_widths_first3: inp22Widths.slice(0, 3),
                    tanto_th_count: tantoTh.length
                };
            }"""
            )
            results["viewports"][f"{w}x{h}"] = probe
            results["hold_list_probe"][f"{w}x{h}"] = hold_probe

            screenshot_path = OUTDIR / f"015_w1_{w}x{h}_expanded.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            context.close()

        # Toggle interaction test (use 1280×900, first section = 得意先情報)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(400)

        before = page.evaluate(
            """() => {
            const c = document.querySelector('.collapsible-content');
            const s = document.querySelector('.collapsible-section');
            return {
                content_collapsed: c ? c.classList.contains('collapsed') : null,
                section_collapsed: s ? s.classList.contains('collapsed') : null,
                content_max_height: c ? c.style.maxHeight : null
            };
        }"""
        )
        page.click('.collapsible-title')
        page.wait_for_timeout(500)
        after_collapse = page.evaluate(
            """() => {
            const c = document.querySelector('.collapsible-content');
            const s = document.querySelector('.collapsible-section');
            return {
                content_collapsed: c ? c.classList.contains('collapsed') : null,
                section_collapsed: s ? s.classList.contains('collapsed') : null,
                content_max_height: c ? c.style.maxHeight : null
            };
        }"""
        )
        page.screenshot(
            path=str(OUTDIR / "015_w1_1280x900_first_collapsed.png"), full_page=True
        )
        page.click('.collapsible-title')
        page.wait_for_timeout(500)
        after_expand = page.evaluate(
            """() => {
            const c = document.querySelector('.collapsible-content');
            const s = document.querySelector('.collapsible-section');
            return {
                content_collapsed: c ? c.classList.contains('collapsed') : null,
                section_collapsed: s ? s.classList.contains('collapsed') : null,
                content_max_height: c ? c.style.maxHeight : null
            };
        }"""
        )
        results["toggle_test"] = {
            "initial": before,
            "after_collapse_click": after_collapse,
            "after_expand_click": after_expand,
        }
        context.close()
        browser.close()

    out_json = OUTDIR / "_verify.json"
    out_json.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
