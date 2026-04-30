#!/usr/bin/env python3
"""cmd_224 W1 縦版 050_海外引合 data recovery verify.

50-1: 期待度/確度 4 option 復元
50-2: 確度理由(大/小) 049 canonical port + reasonMaster JS
50-3: 興味を持った理由 scroll-list bind 動作 (049 canonical port)
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
    "/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new/050_海外引合.html"
)
OUTDIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_224/w1_050_screenshots")


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    url = f"file://{quote(str(TARGET))}"
    results = {"file": TARGET.name}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(500)

        # Open the 期待度 collapsible to make selects accessible
        page.evaluate("""() => {
            const headers = document.querySelectorAll('.collapsible-header');
            headers.forEach(h => {
                if (h.textContent.includes('期待度') || h.textContent.includes('引合情報')) {
                    h.click();
                }
            });
        }""")
        page.wait_for_timeout(500)

        # 50-1 / 50-2: option count probe
        opt_check = page.evaluate("""() => {
            return {
                order_probability_options: Array.from(document.querySelectorAll('#order-probability option')).map(o => o.value),
                current_probability_options: Array.from(document.querySelectorAll('#current-probability option')).map(o => o.value),
                reason_main_options: Array.from(document.querySelectorAll('#probability-reason-main option')).map(o => o.value),
                reason_sub_initial_options: Array.from(document.querySelectorAll('#probability-reason-sub option')).map(o => o.value),
            };
        }""")
        results["50-1_50-2_option_check"] = opt_check

        # 50-2 dynamic: simulate user interaction to trigger updateReasonSub
        # Set order=低い, current=高い → score 4 > 1 = up branch with 技術・製品要因
        page.evaluate("""() => {
            const o = document.getElementById('order-probability'); o.value = '低い'; o.dispatchEvent(new Event('change'));
            const c = document.getElementById('current-probability'); c.value = '高い'; c.dispatchEvent(new Event('change'));
            const m = document.getElementById('probability-reason-main'); m.value = '技術・製品要因'; m.dispatchEvent(new Event('change'));
        }""")
        page.wait_for_timeout(300)
        dyn_check_up = page.evaluate("""() => {
            return {
                reason_sub_options_after_up: Array.from(document.querySelectorAll('#probability-reason-sub option')).map(o => o.value),
            };
        }""")
        results["50-2_dynamic_up"] = dyn_check_up

        # Test down branch: order=高い, current=低い (score 1 < 4 = down)
        page.evaluate("""() => {
            const o = document.getElementById('order-probability'); o.value = '高い'; o.dispatchEvent(new Event('change'));
            const c = document.getElementById('current-probability'); c.value = '低い'; c.dispatchEvent(new Event('change'));
            const m = document.getElementById('probability-reason-main'); m.value = '顧客要因'; m.dispatchEvent(new Event('change'));
        }""")
        page.wait_for_timeout(300)
        dyn_check_down = page.evaluate("""() => {
            return {
                reason_sub_options_after_down: Array.from(document.querySelectorAll('#probability-reason-sub option')).map(o => o.value),
            };
        }""")
        results["50-2_dynamic_down"] = dyn_check_down

        # 50-3: 興味を持った理由 click 2 boxes, verify tags display
        page.evaluate("""() => {
            const list = document.getElementById('kyoumi-list');
            const boxes = list.querySelectorAll('input[type="checkbox"]');
            // Click first two
            boxes[0].click();
            boxes[2].click();
        }""")
        page.wait_for_timeout(300)
        tag_check_2 = page.evaluate("""() => {
            const tagsContainer = document.getElementById('kyoumi-tags');
            return {
                tags_innerHTML_length: tagsContainer.innerHTML.length,
                tag_count: tagsContainer.querySelectorAll('.scroll-list-tag').length,
                tag_labels: Array.from(tagsContainer.querySelectorAll('.scroll-list-tag')).map(t => t.dataset.label),
            };
        }""")
        results["50-3_bind_after_2_click"] = tag_check_2

        # Test removeScrollTag
        page.evaluate("""() => {
            const removeBtn = document.querySelector('#kyoumi-tags .tag-remove');
            if (removeBtn) removeBtn.click();
        }""")
        page.wait_for_timeout(300)
        tag_check_after_remove = page.evaluate("""() => {
            const tagsContainer = document.getElementById('kyoumi-tags');
            const list = document.getElementById('kyoumi-list');
            const checked = list.querySelectorAll('input[type="checkbox"]:checked').length;
            return {
                tag_count: tagsContainer.querySelectorAll('.scroll-list-tag').length,
                remaining_checkbox_checked: checked,
            };
        }""")
        results["50-3_after_remove_tag"] = tag_check_after_remove

        page.screenshot(path=str(OUTDIR / "050_w1_1920_full.png"), full_page=True)
        context.close()
        browser.close()

    out_json = OUTDIR / "_verify.json"
    out_json.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
