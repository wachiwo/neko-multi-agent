#!/usr/bin/env python3
"""cmd_224 W4 052+001 verify (modal port + sticky header)."""
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

F052 = Path("/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new/052_受注画面(受注明細).html")
F001 = Path("/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new/001_個人営業管理.html")
OUTBASE = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_224/w4_screenshots")


def main():
    OUTBASE.mkdir(parents=True, exist_ok=True)
    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch()

        # ===== 052 modal verify =====
        ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        page.goto(f"file://{quote(str(F052))}", wait_until="domcontentloaded")
        page.wait_for_timeout(500)

        # Initial probe
        before = page.evaluate("""() => {
            const overlay = document.getElementById('productSearchModal');
            const dialog = document.getElementById('productSearchDialog');
            const rows = document.querySelectorAll('#productSearchResults tr');
            const cancelBtn = document.querySelector('#productSearchModal .modal-btn-secondary');
            const confirmBtn = document.querySelector('#productSearchModal .modal-btn-primary');
            return {
                modal_overlay_exists: overlay !== null,
                modal_overlay_active: overlay ? overlay.classList.contains('active') : false,
                stale_dialog_exists: dialog !== null,
                row_count: rows.length,
                has_cancel_btn: cancelBtn !== null,
                has_confirm_btn: confirmBtn !== null,
                cancel_text: cancelBtn ? cancelBtn.textContent.trim() : null,
                confirm_text: confirmBtn ? confirmBtn.textContent.trim() : null,
            };
        }""")

        # Open modal via 仕入内容 商品検索 button (uses productDisplay target)
        page.evaluate("openProductSearchModal('productDisplay')")
        page.wait_for_timeout(300)
        opened = page.evaluate("""() => {
            const overlay = document.getElementById('productSearchModal');
            return {
                active: overlay.classList.contains('active'),
                display: getComputedStyle(overlay).display,
            };
        }""")

        # Click 1st row → confirm selected highlighting
        page.evaluate("""() => {
            const row = document.querySelector('#productSearchResults tr');
            row.click();
        }""")
        page.wait_for_timeout(300)
        after_select = page.evaluate("""() => {
            const sel = document.querySelectorAll('#productSearchResults tr.selected').length;
            const radio = document.querySelector('#productSearchResults tr.selected input[type=radio]');
            return {
                selected_count: sel,
                radio_checked: radio ? radio.checked : null,
            };
        }""")

        # Confirm selection
        page.evaluate("confirmProductSelection()")
        page.wait_for_timeout(300)
        after_confirm = page.evaluate("""() => {
            const overlay = document.getElementById('productSearchModal');
            const target = document.getElementById('productDisplay');
            return {
                overlay_active: overlay.classList.contains('active'),
                target_value: target ? target.value : null,
            };
        }""")

        page.screenshot(path=str(OUTBASE / "052_after_modal_use.png"), full_page=False)
        results["052"] = {
            "before": before,
            "opened": opened,
            "after_select_first_row": after_select,
            "after_confirm": after_confirm,
            "console_errors": errs,
        }
        ctx.close()

        # ===== 001 sticky header verify =====
        ctx = browser.new_context(viewport={"width": 1280, "height": 700})
        page = ctx.new_page()
        errs2 = []
        page.on("pageerror", lambda e: errs2.append(str(e)))
        page.goto(f"file://{quote(str(F001))}", wait_until="domcontentloaded")
        page.wait_for_timeout(500)

        # Initial: get page-header position
        initial = page.evaluate("""() => {
            const ph = document.querySelector('.page-header');
            const cs = ph ? getComputedStyle(ph) : null;
            const rect = ph ? ph.getBoundingClientRect() : null;
            const search = document.querySelector('.page-header .btn');
            return {
                position: cs ? cs.position : null,
                top: cs ? cs.top : null,
                zIndex: cs ? cs.zIndex : null,
                rect_top: rect ? rect.top : null,
                rect_height: rect ? rect.height : null,
                search_btn_text: search ? search.textContent.trim() : null,
                search_btn_in_page_header: search !== null,
            };
        }""")

        # Scroll the .content div down 500px
        page.evaluate("""() => {
            const content = document.querySelector('.content');
            if (content) content.scrollTop = 500;
        }""")
        page.wait_for_timeout(500)

        after_scroll = page.evaluate("""() => {
            const ph = document.querySelector('.page-header');
            const rect = ph ? ph.getBoundingClientRect() : null;
            const content = document.querySelector('.content');
            return {
                rect_top: rect ? rect.top : null,
                content_scrollTop: content ? content.scrollTop : null,
            };
        }""")

        page.screenshot(path=str(OUTBASE / "001_after_scroll.png"), full_page=False)
        results["001"] = {
            "initial": initial,
            "after_scroll_500px": after_scroll,
            "sticky_works": (
                initial.get("position") == "sticky"
                and after_scroll.get("rect_top") is not None
                and after_scroll.get("rect_top") <= 50  # header still near top after scroll
            ),
            "console_errors": errs2,
        }
        ctx.close()

        browser.close()

    out = OUTBASE / "_verify.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(json.dumps(results, ensure_ascii=False, indent=2))

    # Verdict
    print()
    print("=" * 50)
    issues = []
    r52 = results["052"]
    if not r52["before"]["modal_overlay_exists"]:
        issues.append("052: modal-overlay productSearchModal missing")
    if r52["before"]["stale_dialog_exists"]:
        issues.append("052: stale productSearchDialog still present")
    if r52["before"]["row_count"] != 10:
        issues.append(f"052: expected 10 rows, got {r52['before']['row_count']}")
    if not r52["before"]["has_cancel_btn"]:
        issues.append("052: missing cancel button")
    if not r52["before"]["has_confirm_btn"]:
        issues.append("052: missing confirm button")
    if r52["before"]["cancel_text"] != "キャンセル":
        issues.append(f"052: cancel button text = {r52['before']['cancel_text']!r}")
    if r52["before"]["confirm_text"] != "選択":
        issues.append(f"052: confirm button text = {r52['before']['confirm_text']!r}")
    if not r52["opened"]["active"]:
        issues.append("052: openProductSearchModal didn't add active class")
    if r52["opened"]["display"] != "flex":
        issues.append(f"052: modal display = {r52['opened']['display']!r}")
    if r52["after_select_first_row"]["selected_count"] != 1:
        issues.append(f"052: after row click, selected count = {r52['after_select_first_row']['selected_count']}")
    if not r52["after_select_first_row"]["radio_checked"]:
        issues.append("052: radio not checked after row click")
    if r52["after_confirm"]["overlay_active"]:
        issues.append("052: modal still active after confirm")
    if not r52["after_confirm"]["target_value"] or "P-001" not in r52["after_confirm"]["target_value"]:
        issues.append(f"052: confirm bind value wrong: {r52['after_confirm']['target_value']!r}")
    if r52["console_errors"]:
        issues.append(f"052: console errors: {r52['console_errors']}")

    r01 = results["001"]
    if r01["initial"]["position"] != "sticky":
        issues.append(f"001: page-header position = {r01['initial']['position']!r}, expected sticky")
    if not r01["initial"]["search_btn_in_page_header"]:
        issues.append("001: search btn not inside page-header")
    if not r01["sticky_works"]:
        issues.append(f"001: sticky behavior failed (rect_top after scroll = {r01['after_scroll_500px']['rect_top']})")
    if r01["console_errors"]:
        issues.append(f"001: console errors: {r01['console_errors']}")

    if issues:
        print("VERDICT: ISSUES FOUND")
        for i in issues:
            print(f"  - {i}")
        sys.exit(1)
    else:
        print("VERDICT: ALL_PASS — 052 modal port (open/select/confirm/bind/close) + 001 sticky header")


if __name__ == "__main__":
    main()
