#!/usr/bin/env python3
"""cmd_218 W1 019 executeApprove() 機能 verify (3 シナリオ).

Scenario 1: only 1 checkbox checked → only that 1 item gets .approved class
Scenario 2: 0 checkboxes checked → no items get .approved class
Scenario 3: all 7 checkboxes checked → all 7 items get .approved class

In all scenarios, ALL items should be disabled after execute (per spec).
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
    "/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new横/019_発注明細.html"
)
OUTDIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_218/w1_019_screenshots")


def setup_state(page, num_checked):
    """Set checkbox state. num_checked = 0/1/7"""
    # Uncheck all first
    page.evaluate(
        """() => {
        document.querySelectorAll('.approval-item input[type=checkbox]').forEach(cb => cb.checked = false);
    }"""
    )
    if num_checked >= 1:
        page.evaluate(
            f"""() => {{
            const cbs = document.querySelectorAll('.approval-item input[type=checkbox]');
            for (let i = 0; i < {num_checked} && i < cbs.length; i++) {{
                cbs[i].checked = true;
            }}
        }}"""
        )


def execute_approve_flow(page):
    """Click 承認 → OK in modal."""
    page.click('.btn-approve')
    page.wait_for_timeout(300)
    page.click('.modal-btn-ok')
    page.wait_for_timeout(300)


def probe_state(page):
    return page.evaluate(
        """() => {
        const items = document.querySelectorAll('.approval-item');
        const result = [];
        items.forEach((item, i) => {
            const cb = item.querySelector('input[type=checkbox]');
            const label = item.querySelector('label');
            result.push({
                index: i,
                label: label ? label.textContent.trim() : null,
                checked: cb ? cb.checked : null,
                disabled: cb ? cb.disabled : null,
                approved_class: item.classList.contains('approved'),
            });
        });
        return result;
    }"""
    )


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    url = f"file://{quote(str(TARGET))}"
    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch()

        # Scenario 1: 1 件 check (社長 only)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(400)
        setup_state(page, 1)
        before_s1 = probe_state(page)
        execute_approve_flow(page)
        after_s1 = probe_state(page)
        page.screenshot(path=str(OUTDIR / "s1_1_check_after.png"), full_page=False)
        results["scenario_1_1_check"] = {"before": before_s1, "after": after_s1}
        context.close()

        # Scenario 2: 0 件 check (空承認)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(400)
        setup_state(page, 0)
        before_s2 = probe_state(page)
        execute_approve_flow(page)
        after_s2 = probe_state(page)
        page.screenshot(path=str(OUTDIR / "s2_0_check_after.png"), full_page=False)
        results["scenario_2_0_check"] = {"before": before_s2, "after": after_s2}
        context.close()

        # Scenario 3: 全 7 件 check
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(400)
        setup_state(page, 7)
        before_s3 = probe_state(page)
        execute_approve_flow(page)
        after_s3 = probe_state(page)
        page.screenshot(path=str(OUTDIR / "s3_7_check_after.png"), full_page=False)
        results["scenario_3_7_check"] = {"before": before_s3, "after": after_s3}
        context.close()
        browser.close()

    # Compute pass/fail summary
    summary = {}
    for sname, sdata in results.items():
        after = sdata["after"]
        before = sdata["before"]
        approved_count = sum(1 for a in after if a["approved_class"])
        disabled_count = sum(1 for a in after if a["disabled"])
        checked_count_before = sum(1 for b in before if b["checked"])
        checked_count_after = sum(1 for a in after if a["checked"])
        summary[sname] = {
            "checked_before": checked_count_before,
            "checked_after": checked_count_after,
            "approved_count_after": approved_count,
            "disabled_count_after": disabled_count,
            "expected_approved": checked_count_before,
            "expected_disabled": 7,
            "PASS_approved": approved_count == checked_count_before,
            "PASS_disabled_all": disabled_count == 7,
            "PASS_unchecked_not_force_checked": checked_count_after == checked_count_before,
        }

    out = {"results_full": results, "summary": summary}
    out_json = OUTDIR / "_verify.json"
    out_json.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
