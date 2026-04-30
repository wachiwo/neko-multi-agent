#!/usr/bin/env python3
"""cmd_219 W1 cross-review independent verify.

Independent re-run of W4 fix:
- period-grid select/date height = 35px canonical (vs pre-fix 19/21px)
- 4 property match .field (padding 8px 10px / border 1px / font 13px / radius 8px)
- 3 viewport (1024×768 / 1280×900 / 1920×1080)
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
    "/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new横/company-search.html"
)
OUTDIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_219/w1_xr_screenshots")

VIEWPORTS = [(1024, 768), (1280, 900), (1920, 1080)]


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    url = f"file://{quote(str(TARGET))}"
    results = {"file": TARGET.name, "viewports": {}}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for w, h in VIEWPORTS:
            context = browser.new_context(viewport={"width": w, "height": h})
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(400)

            probe = page.evaluate(
                """() => {
                const periodSel = document.querySelector('#periodSelect');
                const fromDate = document.querySelector('#fromDate');
                const toDate = document.querySelector('#toDate');
                const fieldSel = document.querySelector('.field select');
                const fieldInput = document.querySelector('.field input[type="text"]');
                const get = (el) => {
                    if (!el) return null;
                    const cs = getComputedStyle(el);
                    const r = el.getBoundingClientRect();
                    return {
                        height: Math.round(r.height * 100) / 100,
                        padding: cs.padding,
                        border: cs.border,
                        font_size: cs.fontSize,
                        border_radius: cs.borderRadius,
                    };
                };
                return {
                    period_select: get(periodSel),
                    period_from_date: get(fromDate),
                    period_to_date: get(toDate),
                    field_select_reference: get(fieldSel),
                    field_input_reference: get(fieldInput),
                };
            }"""
            )
            results["viewports"][f"{w}x{h}"] = probe
            page.screenshot(path=str(OUTDIR / f"company_search_w1xr_{w}x{h}.png"), full_page=True)
            context.close()
        browser.close()

    # Compute pass summary
    summary = {}
    for vp, probe in results["viewports"].items():
        ps = probe.get("period_select", {})
        pf = probe.get("period_from_date", {})
        pt = probe.get("period_to_date", {})
        fs = probe.get("field_select_reference", {})
        summary[vp] = {
            "period_select_height_35px": ps.get("height") if ps else None,
            "period_from_date_height_35px": pf.get("height") if pf else None,
            "period_to_date_height_35px": pt.get("height") if pt else None,
            "field_select_reference_height": fs.get("height") if fs else None,
            "padding_match_field": ps.get("padding") == fs.get("padding") if ps and fs else None,
            "border_match_field": ps.get("border") == fs.get("border") if ps and fs else None,
            "font_match_field": ps.get("font_size") == fs.get("font_size") if ps and fs else None,
            "radius_match_field": ps.get("border_radius") == fs.get("border_radius") if ps and fs else None,
        }
    out = {"results_full": results, "summary": summary}
    out_json = OUTDIR / "_xr_verify.json"
    out_json.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
