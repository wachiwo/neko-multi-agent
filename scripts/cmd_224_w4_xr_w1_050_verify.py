#!/usr/bin/env python3
"""cmd_224 W4 XR of W1 050: independent reproduce reasonMaster + scroll-list bind."""
from __future__ import annotations
import os
import sys
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

F = Path("/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new/050_海外引合.html")
OUT = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_224/w4_xr_w1_050_screenshots")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    results = {}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        page.goto(f"file://{quote(str(F))}", wait_until="domcontentloaded")
        page.wait_for_timeout(500)

        # Static probe
        results["static_options"] = page.evaluate("""() => {
            const orderSel = document.getElementById('order-probability');
            const currentSel = document.getElementById('current-probability');
            const mainSel = document.getElementById('probability-reason-main');
            const subSel = document.getElementById('probability-reason-sub');
            const wrapper = document.querySelector('.scroll-list-wrapper');
            const tags = document.getElementById('kyoumi-tags');
            const list = document.getElementById('kyoumi-list');
            return {
                order_options: orderSel ? Array.from(orderSel.options).map(o => o.text) : null,
                current_options: currentSel ? Array.from(currentSel.options).map(o => o.text) : null,
                main_options: mainSel ? Array.from(mainSel.options).map(o => o.text) : null,
                sub_initial: subSel ? Array.from(subSel.options).map(o => o.text) : null,
                wrapper_exists: wrapper !== null,
                tags_exists: tags !== null,
                list_exists: list !== null,
                kyoumi_checkbox_count: list ? list.querySelectorAll('input[type="checkbox"]').length : 0,
            };
        }""")

        # 50-2 UP branch test: order=低い + current=高い
        page.evaluate("""() => {
            const order = document.getElementById('order-probability');
            const current = document.getElementById('current-probability');
            const main = document.getElementById('probability-reason-main');
            order.value = '低い';
            current.value = '高い';
            main.value = '技術・製品要因';
            // Trigger updateReasonSub
            if (typeof updateReasonSub === 'function') updateReasonSub();
            else main.dispatchEvent(new Event('change'));
        }""")
        page.wait_for_timeout(300)
        results["up_branch"] = page.evaluate("""() => {
            const sub = document.getElementById('probability-reason-sub');
            return {
                sub_options: sub ? Array.from(sub.options).map(o => o.text) : null,
                sub_count: sub ? sub.options.length : 0,
            };
        }""")

        # 50-2 DOWN branch test: order=高い + current=低い
        page.evaluate("""() => {
            const order = document.getElementById('order-probability');
            const current = document.getElementById('current-probability');
            const main = document.getElementById('probability-reason-main');
            order.value = '高い';
            current.value = '低い';
            main.value = '顧客要因';
            if (typeof updateReasonSub === 'function') updateReasonSub();
            else main.dispatchEvent(new Event('change'));
        }""")
        page.wait_for_timeout(300)
        results["down_branch"] = page.evaluate("""() => {
            const sub = document.getElementById('probability-reason-sub');
            return {
                sub_options: sub ? Array.from(sub.options).map(o => o.text) : null,
                sub_count: sub ? sub.options.length : 0,
            };
        }""")

        # 50-3 bind test: click 1st + 3rd checkboxes
        page.evaluate("""() => {
            const checkboxes = document.querySelectorAll('#kyoumi-list input[type="checkbox"]');
            checkboxes[0].click();
            checkboxes[2].click();
        }""")
        page.wait_for_timeout(300)
        results["bind_after_2_click"] = page.evaluate("""() => {
            const tags = document.querySelectorAll('#kyoumi-tags .scroll-list-tag');
            return {
                tag_count: tags.length,
                tag_labels: Array.from(tags).map(t => t.dataset.label || t.textContent.trim()),
            };
        }""")

        # Remove first tag
        page.evaluate("""() => {
            const remove = document.querySelector('#kyoumi-tags .tag-remove');
            if (remove) remove.click();
        }""")
        page.wait_for_timeout(300)
        results["after_remove_first_tag"] = page.evaluate("""() => {
            const tags = document.querySelectorAll('#kyoumi-tags .scroll-list-tag');
            const checked = document.querySelectorAll('#kyoumi-list input[type="checkbox"]:checked');
            return {
                tag_count: tags.length,
                checked_count: checked.length,
            };
        }""")

        results["console_errors"] = errs
        page.screenshot(path=str(OUT / "050_xr_after_test.png"), full_page=False)
        ctx.close()
        browser.close()

    out = OUT / "_verify.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(json.dumps(results, ensure_ascii=False, indent=2))

    # Verdict
    print()
    print("=" * 60)
    issues = []
    so = results["static_options"]
    expected_4 = ["選択してください", "高い", "やや高い", "やや低い", "低い"]
    if so["order_options"] != expected_4:
        issues.append(f"order_options drift: {so['order_options']}")
    if so["current_options"] != expected_4:
        issues.append(f"current_options drift: {so['current_options']}")
    if so["kyoumi_checkbox_count"] < 9:
        issues.append(f"kyoumi checkbox count = {so['kyoumi_checkbox_count']}, expected >= 9")

    up = results["up_branch"]
    if up["sub_count"] < 5:
        issues.append(f"up_branch sub_count = {up['sub_count']}, expected >= 5")

    down = results["down_branch"]
    if down["sub_count"] < 5:
        issues.append(f"down_branch sub_count = {down['sub_count']}, expected >= 5")

    bind = results["bind_after_2_click"]
    if bind["tag_count"] != 2:
        issues.append(f"bind tag_count = {bind['tag_count']}, expected 2")

    after = results["after_remove_first_tag"]
    if after["tag_count"] != 1:
        issues.append(f"after_remove tag_count = {after['tag_count']}, expected 1")
    if after["checked_count"] != 1:
        issues.append(f"after_remove checked_count = {after['checked_count']}, expected 1")

    if errs:
        issues.append(f"console errors: {errs}")

    if issues:
        print("VERDICT: ISSUES FOUND")
        for i in issues:
            print(f"  - {i}")
        sys.exit(1)
    else:
        print("VERDICT: ALL_PASS — independent reproduce of W1's reasonMaster + bind work")


if __name__ == "__main__":
    main()
