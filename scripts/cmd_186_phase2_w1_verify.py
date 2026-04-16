#!/usr/bin/env python3
"""cmd_186 Phase 2 W1 verify: bbox check (label.bottom < input.top for vertical)."""
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

NEW_DIR = Path("/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new")
OUTDIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_186_phase2/screenshots_w1")
FILES = [
    "002_国別累計仕入先上位分析表.html",
    "003_国別累計得意先上位分析表 (粗利).html",
    "005_受注区分別実績表.html",
    "007_製品区分別累計上位分析表.html",
    "008_売上実績表.html",
    "009_売上粗利表.html",
    "047_請求予定一覧.html",
]

def slug(n): return n.replace(".html","").replace(" ","_").replace("(","").replace(")","").replace("（","_").replace("）","")

def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for filename in FILES:
            target = NEW_DIR / filename
            url = f"file://{quote(str(target))}"
            context = browser.new_context(viewport={"width": 1280, "height": 900})
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(300)
            probe = page.evaluate("""() => {
                const formFields = Array.from(document.querySelectorAll('.form-field'));
                let vertical_count = 0, horizontal_count = 0;
                formFields.forEach(ff => {
                    const label = ff.querySelector('label');
                    const input = ff.querySelector('input, select, textarea');
                    if (label && input) {
                        const lb = label.getBoundingClientRect();
                        const ib = input.getBoundingClientRect();
                        if (lb.bottom <= ib.top + 2) vertical_count++;
                        else horizontal_count++;
                    }
                });
                // page-header sticky
                const ph = document.querySelector('.page-header');
                const ph_sticky = ph ? getComputedStyle(ph).position : null;
                const ph_top = ph ? getComputedStyle(ph).top : null;
                const export_section = document.querySelector('.export-section');
                const search_btns = export_section ? export_section.querySelectorAll('button') : [];
                const search_btn_texts = Array.from(search_btns).map(b => b.textContent.trim().slice(0, 15));
                return {
                    form_field_total: formFields.length,
                    form_field_vertical: vertical_count,
                    form_field_horizontal: horizontal_count,
                    page_header_position: ph_sticky,
                    page_header_top: ph_top,
                    export_section_button_count: search_btns.length,
                    export_section_buttons: search_btn_texts,
                };
            }""")
            # Screenshot at zoom 100%
            out = OUTDIR / f"{slug(filename)}_after.png"
            page.screenshot(path=str(out), full_page=True)
            results.append({"file": filename, "probe": probe})
            print(f"{filename}: vertical={probe['form_field_vertical']}/{probe['form_field_total']}, sticky={probe['page_header_position']} top={probe['page_header_top']}, export-btns={probe['export_section_buttons']}")
            context.close()
        browser.close()
    json_path = OUTDIR / "verify_summary.json"
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nOK: {json_path}")

if __name__ == "__main__":
    main()
