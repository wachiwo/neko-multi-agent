#!/usr/bin/env python3
"""cmd_225 dimco-parts-catalog.html browser open verify.

6 mandatory checks:
1. console errors = 0
2. 4 section visible (#section-layout, #section-collapsible-form, #section-modal, #section-controls-drift)
3. TOC anchor links navigate
4. W2 modal click animation works
5. W3 collapsible toggle works
6. W4 radio toggle works (if any)
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
OUTDIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_225/integration_verify")


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

        # Check 1: console errors
        results["1_console_errors"] = {"count": len(console_errors), "errors": console_errors}
        results["1_page_errors"] = {"count": len(page_errors), "errors": page_errors}

        # Check 2: 4 section presence + visibility
        section_ids = ["section-layout", "section-collapsible-form", "section-modal", "section-controls-drift"]
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

        # Check 3: TOC anchor click navigates
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(300)
        toc_link = page.locator('a[href="#section-modal"]').first
        toc_link.click()
        page.wait_for_timeout(500)
        scroll_y_after = page.evaluate("window.scrollY")
        results["3_toc_navigation"] = {
            "scrollY_after_modal_click": scroll_y_after,
            "navigated": scroll_y_after > 100,
        }

        # Check 4: W2 modal click — open supplier modal
        page.evaluate("window.scrollTo(0, document.querySelector('#section-modal').offsetTop)")
        page.wait_for_timeout(300)
        modal_check = page.evaluate("""() => {
            // Try opening supplier modal via the open button (look for openSupplierSearchModal call)
            if (typeof openSupplierSearchModal === 'function') {
                openSupplierSearchModal();
                const m = document.getElementById('supplierSearchModal');
                return {
                    function_exists: true,
                    modal_exists: !!m,
                    modal_active: m ? m.classList.contains('active') : null,
                };
            }
            return {function_exists: false};
        }""")
        results["4_modal_click"] = modal_check

        # Close modal
        page.evaluate("""() => {
            if (typeof closeSupplierSearchModal === 'function') closeSupplierSearchModal();
        }""")
        page.wait_for_timeout(200)

        # Check 5: W3 collapsible toggle
        coll_check = page.evaluate("""() => {
            const headers = document.querySelectorAll('.collapsible-header');
            if (headers.length === 0) return {error: 'no collapsible-header'};
            // First W3 demo collapsible
            const targetHeader = Array.from(headers).find(h => h.closest('#section-collapsible-form'));
            if (!targetHeader) return {error: 'no W3 collapsible-header'};
            // Click to toggle
            const beforeCollapsed = targetHeader.classList.contains('collapsed');
            targetHeader.click();
            const afterClick1 = targetHeader.classList.contains('collapsed');
            targetHeader.click();
            const afterClick2 = targetHeader.classList.contains('collapsed');
            return {
                header_count_in_w3: Array.from(headers).filter(h => h.closest('#section-collapsible-form')).length,
                before: beforeCollapsed,
                after_1st_click: afterClick1,
                after_2nd_click: afterClick2,
                toggleSection_function: typeof toggleSection,
            };
        }""")
        results["5_collapsible_toggle"] = coll_check

        # Check 6: W4 radio toggle
        radio_check = page.evaluate("""() => {
            const w4 = document.getElementById('section-controls-drift');
            if (!w4) return {error: 'no W4 section'};
            const radios = w4.querySelectorAll('input[type="radio"]');
            if (radios.length < 2) return {radio_count: radios.length, error: 'need at least 2 radios'};
            // Click 2nd radio in same group
            const firstRadio = radios[0];
            const groupName = firstRadio.name;
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

        # Final: full-page screenshot + scroll to bottom
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(300)
        page.screenshot(path=str(OUTDIR / "catalog_top.png"), full_page=False)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(300)
        page.screenshot(path=str(OUTDIR / "catalog_bottom.png"), full_page=False)
        page.screenshot(path=str(OUTDIR / "catalog_full.png"), full_page=True)

        context.close()
        browser.close()

    out_json = OUTDIR / "_verify.json"
    out_json.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
