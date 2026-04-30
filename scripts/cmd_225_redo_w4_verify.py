#!/usr/bin/env python3
"""cmd_225_redo W4 form+input section verify."""
from __future__ import annotations
import os
import sys
import json
import re
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

F = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_225_redo/w4_form_input_section.html")
OUT = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_225_redo/w4_screenshots")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    src = F.read_text(encoding="utf-8")

    src_results = {
        "part_label_count": len(re.findall(r'class="part-label"', src)),
        "form_control_count": len(re.findall(r'class="form-control[^"]*"', src)),
        "form_select_count": len(re.findall(r'class="form-select[^"]*"', src)),
        "required_mark_count": len(re.findall(r'class="required-mark"', src)),
        "optional_mark_count": len(re.findall(r'class="optional-mark"', src)),
        "is_invalid_count": len(re.findall(r'is-invalid', src)),
        "invalid_feedback_count": len(re.findall(r'class="invalid-feedback"', src)),
        "char_counter_count": len(re.findall(r'class="char-counter"', src)),
        "form_inline_group_count": len(re.findall(r'class="form-inline-group"', src)),
        "form_field_inline_count": len(re.findall(r'class="form-field-inline"', src)),
        "input_group_count": len(re.findall(r'class="input-group"', src)),
        "section_divider_count": len(re.findall(r'class="section-divider"', src)),
        "showroom_card_count": len(re.findall(r'class="showroom-card"', src)),
    }

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        page.goto(f"file://{quote(str(F))}", wait_until="networkidle")
        page.wait_for_timeout(1000)

        runtime = page.evaluate("""() => {
            const partLabels = document.querySelectorAll('.part-label');
            const formControls = document.querySelectorAll('.form-control');
            const formSelects = document.querySelectorAll('.form-select');
            const requiredMarks = document.querySelectorAll('.required-mark');
            const optionalMarks = document.querySelectorAll('.optional-mark');
            const isInvalids = document.querySelectorAll('.is-invalid');
            const invalidFeedbacks = document.querySelectorAll('.invalid-feedback');
            const charCounters = document.querySelectorAll('.char-counter');
            const formInlineGroups = document.querySelectorAll('.form-inline-group');
            const formFieldInlines = document.querySelectorAll('.form-field-inline');
            const inputGroups = document.querySelectorAll('.input-group');
            const showroomCards = document.querySelectorAll('.showroom-card');

            // Compute first .part-label style
            const firstPartLabel = partLabels[0];
            const partLabelStyle = firstPartLabel ? {
                bg: getComputedStyle(firstPartLabel).backgroundColor,
                color: getComputedStyle(firstPartLabel).color,
                fontSize: getComputedStyle(firstPartLabel).fontSize,
                fontWeight: getComputedStyle(firstPartLabel).fontWeight,
            } : null;

            // Compute first .required-mark style
            const firstRequired = requiredMarks[0];
            const requiredStyle = firstRequired ? {
                bg: getComputedStyle(firstRequired).backgroundColor,
                color: getComputedStyle(firstRequired).color,
            } : null;

            // Compute first .form-control width (default + max-width constrained)
            const fc = formControls[0];
            const fcStyle = fc ? {
                width: getComputedStyle(fc).width,
                maxWidth: getComputedStyle(fc).maxWidth,
            } : null;

            // Compute is-invalid borderColor (Bootstrap)
            const inv = document.querySelector('.is-invalid');
            const invBorderColor = inv ? getComputedStyle(inv).borderColor : null;

            return {
                part_label_count: partLabels.length,
                form_control_count: formControls.length,
                form_select_count: formSelects.length,
                required_mark_count: requiredMarks.length,
                optional_mark_count: optionalMarks.length,
                is_invalid_count: isInvalids.length,
                invalid_feedback_count: invalidFeedbacks.length,
                char_counter_count: charCounters.length,
                form_inline_group_count: formInlineGroups.length,
                form_field_inline_count: formFieldInlines.length,
                input_group_count: inputGroups.length,
                showroom_card_count: showroomCards.length,
                first_part_label_style: partLabelStyle,
                first_required_style: requiredStyle,
                first_form_control_style: fcStyle,
                is_invalid_border_color: invBorderColor,
            };
        }""")

        # Char counter test
        page.evaluate("""() => {
            const ta = document.getElementById('sw-remarks');
            ta.value = 'hello world';
            ta.dispatchEvent(new Event('input'));
        }""")
        page.wait_for_timeout(200)
        counter = page.evaluate("""() => document.getElementById('sw-remarks-count').textContent""")

        page.screenshot(path=str(OUT / "showroom_full.png"), full_page=True)
        ctx.close()
        browser.close()

    out = OUT / "_verify.json"
    out.write_text(json.dumps({
        "src_results": src_results,
        "runtime": runtime,
        "char_counter_after_input": counter,
        "console_errors": errs,
    }, ensure_ascii=False, indent=2))
    print(json.dumps({
        "src_results": src_results,
        "runtime": runtime,
        "char_counter_after_input": counter,
        "console_errors": errs,
    }, ensure_ascii=False, indent=2))

    issues = []
    # Quality checks
    if src_results["part_label_count"] < 12:
        issues.append(f".part-label count = {src_results['part_label_count']}, expected >= 12 (showroom 全部品 + バッジ + バリデーション)")
    if src_results["required_mark_count"] < 5:
        issues.append(f"required-mark count = {src_results['required_mark_count']}, expected >= 5")
    if src_results["optional_mark_count"] < 5:
        issues.append(f"optional-mark count = {src_results['optional_mark_count']}, expected >= 5")
    if src_results["is_invalid_count"] < 3:
        issues.append(f"is-invalid count = {src_results['is_invalid_count']}, expected >= 3 (validation samples)")
    if src_results["form_control_count"] < 10:
        issues.append(f"form-control count = {src_results['form_control_count']}, expected >= 10")
    if src_results["form_select_count"] < 4:
        issues.append(f"form-select count = {src_results['form_select_count']}, expected >= 4")
    if src_results["showroom_card_count"] != 6:
        issues.append(f"showroom-card count = {src_results['showroom_card_count']}, expected 6")
    # Runtime quality
    if runtime["first_part_label_style"]["bg"] != "rgb(233, 236, 239)":
        issues.append(f"part-label bg = {runtime['first_part_label_style']['bg']!r}, expected 'rgb(233, 236, 239)' (#e9ecef)")
    if runtime["first_required_style"]["bg"] != "rgb(220, 53, 69)":
        issues.append(f"required-mark bg = {runtime['first_required_style']['bg']!r}, expected 'rgb(220, 53, 69)' (#dc3545)")
    if counter != "11":
        issues.append(f"char counter after 'hello world' (11 chars) = {counter!r}, expected '11'")
    if errs:
        issues.append(f"console errors: {errs}")

    print()
    print("=" * 60)
    if issues:
        print("VERDICT: ISSUES FOUND")
        for i in issues:
            print(f"  - {i}")
        sys.exit(1)
    else:
        print("VERDICT: ALL_PASS — degawa SSOT準拠 part-label + 必須/任意/is-invalid + form-control/select + char-counter 動作")


if __name__ == "__main__":
    main()
