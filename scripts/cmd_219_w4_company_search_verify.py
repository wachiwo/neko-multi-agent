#!/usr/bin/env python3
"""cmd_219 W4 company-search.html select/date 高さ揃え verify."""
import os, sys, json
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

TARGET = Path("/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new横/company-search.html")
OUTBASE = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_219/w4_company_search_screenshots")
VIEWPORTS = [(1024, 768), (1280, 900), (1920, 1080)]


def main(mode):
    if mode not in ("before", "after"):
        sys.exit("usage: script <before|after>")
    outdir = OUTBASE / mode
    outdir.mkdir(parents=True, exist_ok=True)

    url = f"file://{quote(str(TARGET))}"
    results = {"file": TARGET.name, "mode": mode, "viewports": {}}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for w, h in VIEWPORTS:
            ctx = browser.new_context(viewport={"width": w, "height": h})
            page = ctx.new_page()
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            probe = page.evaluate("""() => {
                // Field-context inputs (canonical)
                const fieldSelect = document.querySelector('#countryName');
                const fieldText   = document.querySelector('#companyName');
                // Period-grid inputs (target of fix)
                const periodSelect = document.querySelector('#periodSelect');
                const fromDate     = document.querySelector('#fromDate');
                const toDate       = document.querySelector('#toDate');

                const measure = (el, label) => el ? {
                    label,
                    h: Math.round(el.getBoundingClientRect().height),
                    w: Math.round(el.getBoundingClientRect().width),
                    padding: getComputedStyle(el).padding,
                    border: getComputedStyle(el).border,
                    fontSize: getComputedStyle(el).fontSize,
                    borderRadius: getComputedStyle(el).borderRadius
                } : null;
                return {
                    field_countrySelect: measure(fieldSelect, '#countryName (.field select)'),
                    field_companyText:   measure(fieldText,   '#companyName (.field input)'),
                    period_periodSelect: measure(periodSelect, '#periodSelect (.period-grid select)'),
                    period_fromDate:     measure(fromDate,     '#fromDate (.period-grid date)'),
                    period_toDate:       measure(toDate,       '#toDate (.period-grid date)'),
                };
            }""")
            results["viewports"][f"{w}x{h}"] = probe
            page.screenshot(path=str(outdir / f"company_search_{mode}_{w}x{h}.png"), full_page=True)
            ctx.close()
        browser.close()

    out_json = outdir / f"_{mode}.json"
    out_json.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "before"
    main(mode)
