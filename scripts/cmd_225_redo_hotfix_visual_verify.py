#!/usr/bin/env python3
"""cmd_225_redo emergency hotfix 実描画 visual verify.

★feedback_phase_gate_actual_render 厳守: computed style 単体 PASS 禁止、画面全体 render 目視 MUST★
前回 subtask_225_redo_005 で probe-based check を 'ALL PASS' 報告したが実際は layout 崩壊で何も表示されていなかった。
本 verify は ★full-page screenshot + visual content 確認★ で同じ過ち繰り返さない。
"""
import os
import json
from pathlib import Path
from urllib.parse import quote

LIBASOUND_PATHS = ["/tmp/libasound/usr/lib/x86_64-linux-gnu/libasound.so.2", "/tmp/libasound_extract/usr/lib/x86_64-linux-gnu/libasound.so.2"]
if not os.environ.get("LD_PRELOAD"):
    for p in LIBASOUND_PATHS:
        if os.path.exists(p):
            os.environ["LD_PRELOAD"] = p
            break
from playwright.sync_api import sync_playwright

TARGET = Path("/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new/dimco-parts-catalog.html")
OUTDIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_225_redo/hotfix_verify")


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    url = f"file://{quote(str(TARGET))}"
    results = {"file": TARGET.name}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        console_errors = []
        page_errors = []
        page.on("console", lambda msg: console_errors.append({"type": msg.type, "text": msg.text}) if msg.type == "error" else None)
        page.on("pageerror", lambda exc: page_errors.append(str(exc)))

        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(1000)

        # 1. Section bounding rect 確認 (★nesting bug 解消★)
        section_check = page.evaluate("""() => {
            const ids = ['section-layout', 'section-modal-button', 'section-table', 'section-form-input'];
            const result = {};
            for (const id of ids) {
                const el = document.getElementById(id);
                if (el) {
                    const rect = el.getBoundingClientRect();
                    result[id] = {
                        top: Math.round(rect.top),
                        height: Math.round(rect.height),
                        width: Math.round(rect.width),
                        visible: rect.width > 100 && rect.height > 100
                    };
                }
            }
            // Check section-table is NOT nested inside section-modal-button
            const s2 = document.getElementById('section-modal-button');
            const s3 = document.getElementById('section-table');
            result['nesting_fixed'] = s2 && s3 ? !s2.contains(s3) : null;
            return result;
        }""")
        results["1_sections"] = section_check

        # 2. h1 + h2 visible (★ご主人様目視確認 trigger★)
        headings = page.evaluate("""() => {
            const h1s = document.querySelectorAll('h1');
            const h2s = document.querySelectorAll('h2');
            return {
                h1_count: h1s.length,
                h1_texts: Array.from(h1s).map(h => h.textContent.trim()).slice(0, 5),
                h2_count: h2s.length,
                h2_texts_in_main: Array.from(document.querySelectorAll('main h2')).map(h => h.textContent.trim()).slice(0, 10),
            };
        }""")
        results["2_headings"] = headings

        # 3. Layout structure: outer header → main → sections (NOT nested)
        layout_check = page.evaluate("""() => {
            const outerHeader = document.querySelector('div.col-sm.bg-maincolor > header');
            const main = document.querySelector('main.p-3');
            const mainInsideHeader = outerHeader && main ? outerHeader.contains(main) : null;
            return {
                outer_header_exists: !!outerHeader,
                outer_header_h3_text: outerHeader ? outerHeader.querySelector('h3')?.textContent.trim() : null,
                main_exists: !!main,
                main_inside_outer_header: mainInsideHeader,  // ★false = fix OK★
                main_parent_tag: main ? main.parentElement.tagName : null,
            };
        }""")
        results["3_layout_structure"] = layout_check

        # 4. Visible text content (catalog 全体が render されているか)
        body_text = page.evaluate("() => document.body.innerText")
        results["4_visible_text"] = {
            "total_length": len(body_text),
            "first_500": body_text[:500],
            "contains_DIMCO_catalog_title": "DIMCO パーツカタログ" in body_text,
            "contains_TOC_label": "目次 (Table of Contents)" in body_text,
            "contains_section_1": "1. 共通レイアウト" in body_text,
            "contains_section_2": "2. モーダル + ボタン" in body_text,
            "contains_section_3": "3. 表 (table) variants" in body_text,
            "contains_section_4": "4. フォーム + input + バリデーション" in body_text,
            "contains_PENDING_finding": "PENDING: 二段ヘッダー" in body_text,
        }

        # 5. errors
        results["5_errors"] = {
            "console_errors_count": len(console_errors),
            "page_errors_count": len(page_errors),
            "console_errors": console_errors[:5],
            "page_errors": page_errors[:5],
        }

        # 6. ★full-page screenshot 撮影 (kashira 独立確認用)★
        page.screenshot(path=str(OUTDIR / "01_top.png"), full_page=False)

        page.evaluate("document.getElementById('section-layout').scrollIntoView()")
        page.wait_for_timeout(300)
        page.screenshot(path=str(OUTDIR / "02_section1_layout.png"), full_page=False)

        page.evaluate("document.getElementById('section-modal-button').scrollIntoView()")
        page.wait_for_timeout(300)
        page.screenshot(path=str(OUTDIR / "03_section2_modal_button.png"), full_page=False)

        page.evaluate("document.getElementById('section-table').scrollIntoView()")
        page.wait_for_timeout(300)
        page.screenshot(path=str(OUTDIR / "04_section3_table.png"), full_page=False)

        page.evaluate("document.getElementById('section-form-input').scrollIntoView()")
        page.wait_for_timeout(300)
        page.screenshot(path=str(OUTDIR / "05_section4_form.png"), full_page=False)

        # full page
        page.screenshot(path=str(OUTDIR / "06_full_page.png"), full_page=True)

        context.close()
        browser.close()

    out_json = OUTDIR / "_verify.json"
    out_json.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
