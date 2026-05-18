#!/usr/bin/env python3
"""cmd_262 Phase 4b hotfix W2 — 015 エンドユーザ「部門CD」削除 verify
3 viewport screenshot + modal functional test (9 trial) 再実行."""
from __future__ import annotations

import os
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
    "/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/002_new横/015_見積明細.html"
)
OUTDIR = Path("/mnt/c/tools/neko-multi-agent/outputs/cmd_262/phase4b_hotfix_w2_screenshots")
VIEWPORTS = [
    ("375", 375, 800),
    ("960", 960, 800),
    ("1920", 1920, 1080),
]

MODAL_TRIALS = [
    ("tokui", "tokui-cd", "tokui-name", 0, "T00001", "株式会社ABC商事"),
    ("hanbaiten", "hanbaiten-cd", "hanbaiten-name", 1, "T00002", "有限会社山田製作所"),
    ("enduser", "enduser-cd", "enduser-name", 2, "T00003", "合同会社スズキ工業"),
]


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    url = f"file://{quote(str(TARGET))}"
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for tag, w, h in VIEWPORTS:
            # baseline screenshot per viewport
            context = browser.new_context(viewport={"width": w, "height": h})
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(500)
            page.evaluate("""
                document.querySelectorAll('.collapsible-content').forEach(el => {
                    el.style.display = 'block';
                });
            """)
            page.wait_for_timeout(300)

            # field count audit per 3 sections
            field_counts = page.evaluate("""
                () => {
                    function inputsInRow(headText) {
                        const ths = document.querySelectorAll('th');
                        for (const th of ths) {
                            if (th.textContent.trim() === headText) {
                                const td = th.nextElementSibling;
                                if (td) {
                                    const inputs = td.querySelectorAll('input[type="text"], input:not([type])');
                                    return Array.from(inputs).map(i => i.placeholder || i.id || '');
                                }
                            }
                        }
                        return null;
                    }
                    return {
                        tokui_row: inputsInRow('得意先名'),
                        hanbaiten_row: inputsInRow('販売店名'),
                        enduser_row: inputsInRow('エンドユーザ名称'),
                    };
                }
            """)
            shot_path = OUTDIR / f"015_vw{tag}_baseline.png"
            page.screenshot(path=str(shot_path), full_page=True)
            print(f"[{tag} baseline] field_counts: {field_counts}")
            context.close()

            # modal functional test
            for kind, cd_id, name_id, btn_idx, expected_cd, expected_name in MODAL_TRIALS:
                context = browser.new_context(viewport={"width": w, "height": h})
                page = context.new_page()
                page.goto(url, wait_until="domcontentloaded")
                page.wait_for_timeout(300)
                page.evaluate("""
                    document.querySelectorAll('.collapsible-content').forEach(el => {
                        el.style.display = 'block';
                    });
                """)
                page.wait_for_timeout(200)

                btn_sel = f"button[onclick*='openCustomerSearchModal'] >> nth={btn_idx}"
                try:
                    page.locator(btn_sel).first.click(force=True, timeout=3000)
                    page.wait_for_timeout(300)
                except Exception as e:
                    results.append({"viewport": tag, "modal": kind, "error": str(e)})
                    context.close()
                    continue

                active_target_info = page.evaluate("""
                    () => {
                        const t = window.activeCustomerTarget;
                        if (!t) return null;
                        const cd = t.querySelector('input[id$="-cd"]');
                        const name = t.querySelector('input[id$="-name"]');
                        return {
                            tag: t.tagName,
                            cd_id: cd ? cd.id : null,
                            name_id: name ? name.id : null,
                        };
                    }
                """)

                page.locator(f'input[name="customerSelect"][value="{expected_cd}"]').click(force=True, timeout=3000)
                page.wait_for_timeout(200)
                page.locator('button.modal-btn-primary[onclick*="confirmCustomerSelection"]').click(force=True, timeout=3000)
                page.wait_for_timeout(300)

                actual_cd = page.evaluate(f"() => document.getElementById('{cd_id}').value")
                actual_name = page.evaluate(f"() => document.getElementById('{name_id}').value")

                status = "PASS" if actual_cd == expected_cd and actual_name == expected_name else "FAIL"
                results.append({
                    "viewport": tag, "modal": kind, "status": status,
                    "expected_cd": expected_cd, "actual_cd": actual_cd,
                    "expected_name": expected_name, "actual_name": actual_name,
                    "active_target": active_target_info,
                })

                shot_path = OUTDIR / f"015_vw{tag}_{kind}_after_select.png"
                page.screenshot(path=str(shot_path), full_page=False)
                context.close()
        browser.close()

    print("\n" + "=" * 70)
    print("Modal Functional Test Results")
    print("=" * 70)
    pass_count = sum(1 for r in results if r.get("status") == "PASS")
    fail_count = sum(1 for r in results if r.get("status") != "PASS")
    for r in results:
        print(f"[{r.get('viewport')}] {r.get('modal'):10s} {r.get('status', 'ERR')}")
        print(f"  cd: {r.get('actual_cd')} (expected {r.get('expected_cd')})")
        print(f"  name: {r.get('actual_name')} (expected {r.get('expected_name')})")
        print(f"  active_target: {r.get('active_target')}")
    print(f"\nTotal: {pass_count}/9 PASS, {fail_count}/9 FAIL")


if __name__ == "__main__":
    main()
