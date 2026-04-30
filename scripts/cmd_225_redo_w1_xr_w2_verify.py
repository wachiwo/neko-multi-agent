#!/usr/bin/env python3
"""cmd_225_redo W1 reviews W2 modal+button verify."""
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
OUTDIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_225_redo/xr_w1_reviews_w2")


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    url = f"file://{quote(str(TARGET))}"
    results = {"file": TARGET.name}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        page_errors = []
        page.on("pageerror", lambda exc: page_errors.append(str(exc)))
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(800)

        # 1. section-modal-button visible content
        section_text = page.evaluate("""() => {
            const el = document.getElementById('section-modal-button');
            return el ? el.innerText : '';
        }""")
        results["1_section_text_length"] = len(section_text)
        results["1_section_text_first_500"] = section_text[:500]

        # 2. degawa SSOT byte-match indicators
        source_violations = {p: section_text.count(p) for p in [
            "modal-overlay", "modal-result-table", "supplierSearchModal", "L103-139", "byte-match", "<code>", "style=\""
        ]}
        results["2_source_in_section_visible"] = source_violations
        results["2_source_zero_visible"] = sum(source_violations.values()) == 0

        # 3. degawa modal pattern presence
        modal_check = page.evaluate("""() => {
            const cards = document.querySelectorAll('.modal-card');
            const backdrops = document.querySelectorAll('.modal-backdrop-custom');
            const oldOverlays = document.querySelectorAll('.modal-overlay');
            return {
                modal_card_count: cards.length,
                modal_backdrop_custom_count: backdrops.length,
                old_modal_overlay_count: oldOverlays.length,
            };
        }""")
        results["3_modal_pattern"] = modal_check

        # 4. Button variants check
        btn_check = page.evaluate("""() => {
            const btns = document.querySelectorAll('#section-modal-button button, #section-modal-button .page-btn, #section-modal-button .action-btn');
            const variants = {};
            btns.forEach(b => {
                const cls = b.className.trim();
                variants[cls] = (variants[cls] || 0) + 1;
            });
            return {
                total_btn_in_w2: btns.length,
                unique_classes: Object.keys(variants).length,
                sample_variants: variants,
            };
        }""")
        results["4_button_variants"] = btn_check

        # 5. Modal trigger click test
        modal_trigger = page.evaluate("""() => {
            // Look for any button that triggers modal (data-bs-toggle="modal" or onclick="...modal...")
            const trigger = document.querySelector('#section-modal-button [data-bs-toggle="modal"], #section-modal-button button[onclick*="modal"], #section-modal-button button[onclick*="Modal"]');
            if (!trigger) return {trigger_found: false};
            trigger.click();
            // After click, check if any .modal-card / .show class appeared
            const shown = document.querySelector('.modal-backdrop-custom.show, .modal-card.show, .modal.show');
            return {
                trigger_found: true,
                trigger_text: trigger.textContent.trim().slice(0, 30),
                modal_shown_after_click: !!shown,
            };
        }""")
        results["5_modal_trigger"] = modal_trigger

        # 6. drift warning visibility check (should be 0)
        drift_check = section_text.count("⚠ drift") + section_text.count("DW-1")
        results["6_drift_visible_count"] = drift_check

        # screenshot
        page.evaluate("document.getElementById('section-modal-button').scrollIntoView()")
        page.wait_for_timeout(500)
        page.screenshot(path=str(OUTDIR / "modal_button_section.png"), full_page=False)

        results["page_errors"] = page_errors
        context.close()
        browser.close()

    out_json = OUTDIR / "_verify.json"
    out_json.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
