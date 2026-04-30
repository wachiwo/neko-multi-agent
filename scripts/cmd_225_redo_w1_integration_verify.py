#!/usr/bin/env python3
"""cmd_225_redo dimco-parts-catalog.html browser verify (8 mandatory checks)."""
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
OUTDIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_225_redo/integration_verify")


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
        page.wait_for_timeout(800)

        # 1. errors
        results["1_console_errors"] = {"count": len(console_errors), "errors": console_errors[:5]}
        results["1_page_errors"] = {"count": len(page_errors), "errors": page_errors[:5]}

        # 2. 4 sections visible
        section_ids = ["section-layout", "section-modal-button", "section-table", "section-form-input"]
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
                    h2_text: h2 ? h2.textContent.trim().slice(0, 80) : null,
                    height: Math.round(rect.height),
                }};
            }}""")
            section_check[sid] = info
        results["2_sections_visible"] = section_check

        # 3. TOC navigation
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(200)
        page.evaluate("document.querySelector('a[href=\"#section-table\"]').click()")
        page.wait_for_timeout(500)
        scroll_y = page.evaluate("window.scrollY")
        results["3_toc_navigation"] = {"scrollY_after_table_click": scroll_y, "navigated": scroll_y > 100}

        # 4. W2 modal click test (use first available open* function)
        modal_check = page.evaluate("""() => {
            const fnNames = Object.keys(window).filter(k => /^open\\w+SearchModal$/.test(k));
            if (fnNames.length === 0) {
                // fallback to W2 .modal-card pattern
                const modal = document.querySelector('.modal-card, .modal-overlay');
                return {open_function_names: [], modal_pattern_present: !!modal};
            }
            // Use first one
            const first = fnNames[0];
            try { window[first](); } catch(e) { return {error: e.message}; }
            return {open_function_names: fnNames.slice(0, 5), function_called: first};
        }""")
        results["4_modal_click"] = modal_check

        # 5. W1 sidebar drawer toggle
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(200)
        drawer_check = page.evaluate("""() => {
            const drawerBtn = document.querySelector('.zdo_drawer_button');
            const navWrapper = document.querySelector('.zdo_drawer_nav_wrapper');
            if (!drawerBtn || !navWrapper) return {error: 'no drawer'};
            const before = navWrapper.classList.contains('open');
            drawerBtn.click();
            const after = navWrapper.classList.contains('open');
            // close
            drawerBtn.click();
            return {before_open: before, after_click_open: after};
        }""")
        results["5_drawer_toggle"] = drawer_check

        # 6. W3 table render (variants count)
        table_check = page.evaluate("""() => {
            const w3 = document.getElementById('section-table');
            if (!w3) return {error: 'no W3'};
            const tables = w3.querySelectorAll('table');
            return {table_count: tables.length};
        }""")
        results["6_table_render"] = table_check

        # 7. W4 form input render
        form_check = page.evaluate("""() => {
            const w4 = document.getElementById('section-form-input');
            if (!w4) return {error: 'no W4'};
            const inputs = w4.querySelectorAll('input, textarea, select');
            return {input_count: inputs.length};
        }""")
        results["7_form_render"] = form_check

        # 8. PENDING finding visibility (二段ヘッダー)
        pending_check = page.evaluate("""() => {
            const visibleText = document.body.innerText;
            return {
                has_pending_badge: visibleText.includes('PENDING: 二段ヘッダー'),
                has_finding_keyword: visibleText.includes('二段ヘッダー'),
                has_degawa_unset_finding: visibleText.includes('degawa') && (visibleText.includes('不在') || visibleText.includes('literal 不在')),
            };
        }""")
        results["8_pending_finding"] = pending_check

        # bonus: full page screenshot
        page.screenshot(path=str(OUTDIR / "catalog_top.png"), full_page=False)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(300)
        page.screenshot(path=str(OUTDIR / "catalog_bottom.png"), full_page=False)

        # visible text length check
        visible_text = page.evaluate("() => document.body.innerText")
        results["visible_text_length"] = len(visible_text)
        results["visible_text_first_500"] = visible_text[:500]

        context.close()
        browser.close()

    out_json = OUTDIR / "_verify.json"
    out_json.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
