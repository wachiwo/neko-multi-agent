#!/usr/bin/env python3
"""cmd_225_fix dimco-parts-catalog.html 商品ショールーム型 verify.

8 mandatory checks (per task spec):
1. console errors / page errors = 0
2. 5 sections visible
3. TOC anchor click works
4. modal click animation works (W2)
5. collapsible toggle works (W3)
6. radio toggle works (W4)
7. ★source code 画面表示 0 (style="...", <code>, line ref)★ — 商品ショールーム型核心
8. drift 警告画面表示 0 (HTML コメント内のみ)
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

TARGET = Path("/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new/dimco-parts-catalog.html")
OUTDIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_225_fix/integration_verify")


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

        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(800)

        # 1. errors
        results["1_console_errors"] = {"count": len(console_errors), "errors": console_errors}
        results["1_page_errors"] = {"count": len(page_errors), "errors": page_errors}

        # 2. 5 sections visibility
        section_ids = ["section-layout", "section-collapsible-form", "section-tables", "section-modal", "section-controls-drift"]
        section_check = {}
        for sid in section_ids:
            info = page.evaluate(f"""() => {{
                const el = document.getElementById('{sid}');
                if (!el) return {{exists: false}};
                const rect = el.getBoundingClientRect();
                const h2 = el.querySelector('h2');
                return {{
                    exists: true,
                    has_h2: !!h2,
                    h2_text: h2 ? h2.textContent.trim() : null,
                    height: Math.round(rect.height),
                }};
            }}""")
            section_check[sid] = info
        results["2_sections_visible"] = section_check

        # 3. TOC anchor click
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(300)
        toc_link = page.locator('a[href="#section-tables"]').first
        toc_link.click()
        page.wait_for_timeout(500)
        scroll_y = page.evaluate("window.scrollY")
        results["3_toc_navigation"] = {
            "scrollY_after_tables_click": scroll_y,
            "navigated": scroll_y > 100,
        }

        # 4. W2 modal click
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(200)
        modal_check = page.evaluate("""() => {
            if (typeof openSupplierSearchModal === 'function') {
                openSupplierSearchModal();
                const m = document.getElementById('supplierSearchModal');
                return {function_exists: true, modal_exists: !!m, modal_active: m ? m.classList.contains('active') : null};
            }
            return {function_exists: false};
        }""")
        results["4_modal_click"] = modal_check
        page.evaluate("if (typeof closeSupplierSearchModal === 'function') closeSupplierSearchModal();")
        page.wait_for_timeout(200)

        # 5. W3 collapsible toggle
        coll_check = page.evaluate("""() => {
            const headers = document.querySelectorAll('.collapsible-header');
            const targetHeader = Array.from(headers).find(h => h.closest('#section-collapsible-form'));
            if (!targetHeader) return {error: 'no W3 collapsible-header'};
            const beforeCollapsed = targetHeader.classList.contains('collapsed');
            targetHeader.click();
            const after1 = targetHeader.classList.contains('collapsed');
            targetHeader.click();
            const after2 = targetHeader.classList.contains('collapsed');
            return {
                header_count_w3: Array.from(headers).filter(h => h.closest('#section-collapsible-form')).length,
                before: beforeCollapsed,
                after_1st: after1,
                after_2nd: after2,
                toggleSection_function: typeof toggleSection,
            };
        }""")
        results["5_collapsible_toggle"] = coll_check

        # 6. W4 radio toggle
        radio_check = page.evaluate("""() => {
            const w4 = document.getElementById('section-controls-drift');
            if (!w4) return {error: 'no W4 section'};
            const radios = w4.querySelectorAll('input[type="radio"]');
            if (radios.length < 2) return {radio_count: radios.length, error: 'need 2+ radios'};
            const groupName = radios[0].name;
            const sameGroup = Array.from(radios).filter(r => r.name === groupName);
            if (sameGroup.length < 2) return {error: `only 1 radio in group ${groupName}`};
            sameGroup[1].click();
            return {
                radio_total: radios.length,
                first_group: groupName,
                first_group_count: sameGroup.length,
                first_radio_checked: sameGroup[0].checked,
                second_radio_checked: sameGroup[1].checked,
            };
        }""")
        results["6_radio_toggle"] = radio_check

        # 7. ★source code 画面表示 0★ (商品ショールーム型核心)
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(200)
        visible_text = page.evaluate("() => document.body.innerText")
        source_patterns = ["<code>", "</code>", "style=\"flex:", "style=\"width:", "→ ', '↓', '出典", "016 L", "027 L", "049 L", "new横/", "new/016_", "L451-540", "L820-993", "L242-296"]
        source_violations = {p: visible_text.count(p) for p in source_patterns}
        results["7_visible_source_violations"] = source_violations
        results["7_visible_source_zero"] = sum(source_violations.values()) == 0

        # 8. drift 警告画面表示 0
        drift_patterns = ["⚠ drift warning", "⚠ drift", "drift warning #", "feedback_canonical", "feedback_dimco", "feedback_component"]
        drift_violations = {p: visible_text.count(p) for p in drift_patterns}
        results["8_visible_drift_violations"] = drift_violations
        results["8_drift_zero"] = sum(drift_violations.values()) == 0

        # bonus: visible text length and sample
        results["visible_text_length"] = len(visible_text)
        results["visible_text_first_400"] = visible_text[:400]
        results["visible_text_last_400"] = visible_text[-400:]

        # screenshots
        page.screenshot(path=str(OUTDIR / "catalog_top.png"), full_page=False)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(300)
        page.screenshot(path=str(OUTDIR / "catalog_bottom.png"), full_page=False)

        context.close()
        browser.close()

    out_json = OUTDIR / "_verify.json"
    out_json.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
