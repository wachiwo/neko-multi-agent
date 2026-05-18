#!/usr/bin/env python3
"""cmd_262 Phase 4b W2 — 015 modal functional test (3 modal x 3 viewport = 9 trials)
+ screenshot for visual verify."""
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
OUTDIR = Path("/mnt/c/tools/neko-multi-agent/outputs/cmd_262/phase4b_w2_screenshots")
VIEWPORTS = [
    ("375", 375, 800),
    ("960", 960, 800),
    ("1920", 1920, 1080),
]

# (modal target group cd id, name id, trigger button locator, expected cd, expected name)
MODAL_TRIALS = [
    ("tokui", "tokui-cd", "tokui-name", "button[onclick*='openCustomerSearchModal'] >> nth=0",
     "T00001", "株式会社ABC商事"),
    ("hanbaiten", "hanbaiten-cd", "hanbaiten-name", "button[onclick*='openCustomerSearchModal'] >> nth=1",
     "T00002", "有限会社山田製作所"),
    ("enduser", "enduser-cd", "enduser-name", "button[onclick*='openCustomerSearchModal'] >> nth=2",
     "T00003", "合同会社スズキ工業"),
]


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    url = f"file://{quote(str(TARGET))}"
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for tag, w, h in VIEWPORTS:
            for trial_idx, (kind, cd_id, name_id, btn_sel, expected_cd, expected_name) in enumerate(MODAL_TRIALS):
                context = browser.new_context(viewport={"width": w, "height": h})
                page = context.new_page()
                page.goto(url, wait_until="domcontentloaded")
                page.wait_for_timeout(300)

                # まず該当 section の collapsible を expand する必要があるかも
                # 得意先/販売店/エンドユーザ section は default で表示されている想定だが、念のため
                page.evaluate("""
                    document.querySelectorAll('.collapsible-content').forEach(el => {
                        el.style.display = 'block';
                    });
                """)
                page.wait_for_timeout(200)

                # 該当 modal trigger button をクリック
                try:
                    page.locator(btn_sel).first.click(force=True, timeout=3000)
                    page.wait_for_timeout(300)
                except Exception as e:
                    results.append({
                        "viewport": tag, "modal": kind, "step": "open_modal_failed",
                        "error": str(e),
                    })
                    context.close()
                    continue

                # modal が open 状態か
                modal_open = page.evaluate("""
                    () => document.getElementById('customerSearchModal').classList.contains('active')
                """)
                if not modal_open:
                    results.append({
                        "viewport": tag, "modal": kind, "step": "modal_not_active",
                    })
                    context.close()
                    continue

                # activeCustomerTarget 確認
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

                # 対応 radio をクリック
                page.locator(f'input[name="customerSelect"][value="{expected_cd}"]').click(force=True, timeout=3000)
                page.wait_for_timeout(200)

                # 選択 button (confirm) をクリック
                page.locator('button.modal-btn-primary[onclick*="confirmCustomerSelection"]').click(force=True, timeout=3000)
                page.wait_for_timeout(300)

                # 結果を input から読み取り
                actual_cd = page.evaluate(f"() => document.getElementById('{cd_id}').value")
                actual_name = page.evaluate(f"() => document.getElementById('{name_id}').value")

                # 他の input が誤って上書きされていないか cross-check
                other_inputs = page.evaluate("""
                    () => ({
                        tokui_cd: document.getElementById('tokui-cd').value,
                        tokui_name: document.getElementById('tokui-name').value,
                        hanbaiten_cd: document.getElementById('hanbaiten-cd').value,
                        hanbaiten_name: document.getElementById('hanbaiten-name').value,
                        enduser_cd: document.getElementById('enduser-cd').value,
                        enduser_name: document.getElementById('enduser-name').value,
                    })
                """)

                status = "PASS" if actual_cd == expected_cd and actual_name == expected_name else "FAIL"
                results.append({
                    "viewport": tag,
                    "modal": kind,
                    "active_target_info": active_target_info,
                    "expected_cd": expected_cd,
                    "actual_cd": actual_cd,
                    "expected_name": expected_name,
                    "actual_name": actual_name,
                    "other_inputs": other_inputs,
                    "status": status,
                })

                # screenshot 1 枚 (各 trial の最終状態)
                shot_path = OUTDIR / f"015_vw{tag}_{kind}_after_select.png"
                page.screenshot(path=str(shot_path), full_page=False)
                context.close()

            # viewport ごとに baseline screenshot 1 枚 (modal 閉じた状態)
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
            shot_path = OUTDIR / f"015_vw{tag}_baseline.png"
            page.screenshot(path=str(shot_path), full_page=True)
            context.close()

        browser.close()

    # 結果 print
    print("=" * 70)
    print("015 Modal Functional Test Results (3 modal x 3 viewport = 9 trials)")
    print("=" * 70)
    pass_count = 0
    fail_count = 0
    for r in results:
        status = r.get("status", "ERROR")
        if status == "PASS":
            pass_count += 1
        else:
            fail_count += 1
        print(f"[{r.get('viewport')}] {r.get('modal'):10s} {status}")
        print(f"  expected: cd={r.get('expected_cd')}, name={r.get('expected_name')}")
        print(f"  actual:   cd={r.get('actual_cd')}, name={r.get('actual_name')}")
        print(f"  active_target: {r.get('active_target_info')}")
        if status != "PASS":
            print(f"  other:    {r.get('other_inputs')}")
    print(f"\nTotal: {pass_count}/9 PASS, {fail_count}/9 FAIL")


if __name__ == "__main__":
    main()
