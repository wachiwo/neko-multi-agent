#!/usr/bin/env python3
"""cmd_218 W2 019 cross-review independent verify (3 scenarios).

Independent re-run of W1 functional verify to validate executeApprove fix.
Same 3 scenarios as W1, output to W2 dir for byte comparison.
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

TARGET = Path("/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new横/019_発注明細.html")
OUTDIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_218/w2_019_xr_screenshots")


def setup_state(page, num_checked):
    page.evaluate("""() => { document.querySelectorAll('.approval-item input[type=checkbox]').forEach(cb => cb.checked = false); }""")
    if num_checked >= 1:
        page.evaluate(f"""() => {{
            const cbs = document.querySelectorAll('.approval-item input[type=checkbox]');
            for (let i = 0; i < {num_checked} && i < cbs.length; i++) {{ cbs[i].checked = true; }}
        }}""")


def execute_approve_flow(page):
    page.click('.btn-approve')
    page.wait_for_timeout(300)
    page.click('.modal-btn-ok')
    page.wait_for_timeout(300)


def probe_state(page):
    return page.evaluate("""() => {
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
    }""")


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    url = f"file://{quote(str(TARGET))}"
    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for scenario_id, num_checked in [(1, 1), (2, 0), (3, 7)]:
            context = browser.new_context(viewport={"width": 1280, "height": 900})
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(400)
            setup_state(page, num_checked)
            before = probe_state(page)
            execute_approve_flow(page)
            after = probe_state(page)
            png_name = f"s{scenario_id}_{num_checked}_check_after.png"
            page.screenshot(path=str(OUTDIR / png_name), full_page=False)
            results[f"scenario_{scenario_id}_{num_checked}_check"] = {"before": before, "after": after}
            context.close()
        browser.close()

    # Summary
    summary = {}
    for key, data in results.items():
        after = data["after"]
        approved_count = sum(1 for x in after if x["approved_class"])
        disabled_count = sum(1 for x in after if x["disabled"])
        summary[key] = {"approved_count": approved_count, "disabled_count": disabled_count}

    with (OUTDIR / "_xr_verify.json").open("w") as f:
        json.dump({"results": results, "summary": summary}, f, indent=2, ensure_ascii=False)

    print("=== W2 independent verify summary ===")
    for k, v in summary.items():
        print(f"  {k}: approved={v['approved_count']}, disabled={v['disabled_count']}")
    print(f"\nResults JSON: {OUTDIR / '_xr_verify.json'}")


if __name__ == "__main__":
    main()
