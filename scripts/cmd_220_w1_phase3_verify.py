#!/usr/bin/env python3
"""cmd_220 Phase 3: Playwright 3vp visual verify (post-fix).

Verify:
- 左側色 表示 (--light-blue + --secondary-blue 修復後 var() fallback 解消)
- 下部デグレ 解消 (legacy .search-form 削除後の visual 確認)
- 29-row hierarchical table + 3 modals 動作維持
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
    "/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new横/053_海外取引一覧.html"
)
OUTDIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_220/w1_phase3_screenshots")

VIEWPORTS = [(1024, 768), (1280, 900), (1920, 1080)]


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    url = f"file://{quote(str(TARGET))}"
    results = {"file": TARGET.name, "viewports": {}, "expand_test": {}}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for w, h in VIEWPORTS:
            context = browser.new_context(viewport={"width": w, "height": h})
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(400)

            probe = page.evaluate(
                """() => {
                const root = getComputedStyle(document.documentElement);
                const ths = document.querySelectorAll('.excel-table th');
                const dataTableThs = document.querySelectorAll('.data-table th');
                const sectionHeader = document.querySelector('.section-header');
                const ph = document.querySelector('.page-header');
                const containerStyle = document.querySelector('.container');
                const expandIcons = document.querySelectorAll('.expand-icon-cell');
                const modals = document.querySelectorAll('.modal-overlay');
                return {
                    css_light_blue: root.getPropertyValue('--light-blue').trim(),
                    css_secondary_blue: root.getPropertyValue('--secondary-blue').trim(),
                    css_lighter_blue: root.getPropertyValue('--lighter-blue').trim(),
                    excel_table_th_bg: ths[0] ? getComputedStyle(ths[0]).backgroundColor : null,
                    excel_table_th_border_right: ths[0] ? getComputedStyle(ths[0]).borderRight : null,
                    section_header_bg: sectionHeader ? getComputedStyle(sectionHeader).backgroundColor : null,
                    page_header_pos: ph ? getComputedStyle(ph).position : null,
                    container_box_shadow: containerStyle ? getComputedStyle(containerStyle).boxShadow : null,
                    expand_icon_count: expandIcons.length,
                    modal_count: modals.length,
                };
            }"""
            )
            results["viewports"][f"{w}x{h}"] = probe
            page.screenshot(path=str(OUTDIR / f"053_torihiki_w1_{w}x{h}_post_fix.png"), full_page=True)
            context.close()

        # Functional test: expand row 1 + open 1 modal at 1280x900
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(400)

        # Click first expand-icon-cell
        page.evaluate("() => { const el = document.querySelector('.expand-icon-cell'); if (el) el.click(); }")
        page.wait_for_timeout(500)
        expand_state = page.evaluate(
            """() => {
            const firstChild = document.querySelector('.child-table-container');
            const firstIcon = document.querySelector('.expand-icon');
            return {
                child_visible: firstChild ? firstChild.classList.contains('expanded') : null,
                icon_text: firstIcon ? firstIcon.textContent.trim() : null,
            };
        }"""
        )
        page.screenshot(path=str(OUTDIR / "053_torihiki_w1_1280x900_row_expanded.png"), full_page=True)

        # Open 得意先検索 modal
        page.evaluate("() => { if (typeof openTokuisakiModal === 'function') openTokuisakiModal(); }")
        page.wait_for_timeout(500)
        modal_state = page.evaluate(
            """() => {
            const modal = document.getElementById('tokuisakiModal');
            return {
                modal_class: modal ? modal.className : null,
                modal_visible: modal ? getComputedStyle(modal).display : null,
            };
        }"""
        )
        page.screenshot(path=str(OUTDIR / "053_torihiki_w1_1280x900_modal_open.png"), full_page=True)
        context.close()
        browser.close()

        results["expand_test"] = {
            "row_expanded": expand_state,
            "modal_state": modal_state,
        }

    out_json = OUTDIR / "_verify.json"
    out_json.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
