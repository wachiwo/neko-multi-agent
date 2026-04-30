#!/usr/bin/env python3
"""cmd_215 W1 cross-review (axis 2 + axis 3 W2 fix verify).

4 files × 3 viewports independent re-verify:
- 043: collapsible structure + toggle (post W2 axis 2 fix)
- 015/036/042: visual unchanged confirm (post W2 axis 3 :root statement)
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

BASE = Path("/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new横")
OUTDIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_215/w1_043_root_xr_screenshots")

TARGETS = [
    ("043", BASE / "043_得意先売上一覧表.html"),
    ("015", BASE / "015_見積明細.html"),
    ("036", BASE / "036_入金予定一覧.html"),
    ("042", BASE / "042_請求書出力指示.html"),
]

VIEWPORTS = [(1024, 768), (1280, 900), (1920, 1080)]


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch()

        for fname, path in TARGETS:
            url = f"file://{quote(str(path))}"
            results[fname] = {"viewports": {}, "toggle": {}, "hold_list": {}}

            for w, h in VIEWPORTS:
                context = browser.new_context(viewport={"width": w, "height": h})
                page = context.new_page()
                page.goto(url, wait_until="domcontentloaded")
                page.wait_for_timeout(400)

                probe = page.evaluate(
                    """() => {
                    const sec = document.querySelectorAll('.collapsible-section');
                    const titles = document.querySelectorAll('.collapsible-title');
                    const contents = document.querySelectorAll('.collapsible-content');
                    const indicators = document.querySelectorAll('.collapse-indicator');
                    const ph = document.querySelector('.page-header');
                    const root = getComputedStyle(document.documentElement);
                    return {
                        section_count: sec.length,
                        title_count: titles.length,
                        content_count: contents.length,
                        indicator_count: indicators.length,
                        page_header_pos: ph ? getComputedStyle(ph).position : null,
                        first_title_bg: titles[0] ? getComputedStyle(titles[0]).backgroundColor : null,
                        first_title_color: titles[0] ? getComputedStyle(titles[0]).color : null,
                        css_lighter_blue: root.getPropertyValue('--lighter-blue').trim(),
                        css_accent_blue: root.getPropertyValue('--accent-blue').trim(),
                        css_pink_dark: root.getPropertyValue('--pink-dark').trim(),
                        css_pink_darker: root.getPropertyValue('--pink-darker').trim(),
                    };
                }"""
                )
                results[fname]["viewports"][f"{w}x{h}"] = probe
                page.screenshot(
                    path=str(OUTDIR / f"{fname}_w1xr_{w}x{h}_expanded.png"),
                    full_page=True,
                )
                context.close()

            # 015 hold-list independent probe
            if fname == "015":
                context = browser.new_context(viewport={"width": 1280, "height": 900})
                page = context.new_page()
                page.goto(url, wait_until="domcontentloaded")
                page.wait_for_timeout(400)
                hold = page.evaluate(
                    """() => {
                    const allSelects = Array.from(document.querySelectorAll('select'));
                    const sel180 = allSelects.filter(s => s.style && s.style.width === '180px');
                    const sel180Widths = sel180.map(s => s.getBoundingClientRect().width);
                    const allInputs = Array.from(document.querySelectorAll('input'));
                    const inp22 = allInputs.filter(i => i.style && i.style.width === '22ch');
                    const inp22Widths = inp22.map(i => i.getBoundingClientRect().width);
                    return {
                        selects_180px_count: sel180.length,
                        selects_180px_widths: sel180Widths,
                        inputs_22ch_count: inp22.length,
                        inputs_22ch_widths_first3: inp22Widths.slice(0, 3),
                    };
                }"""
                )
                results[fname]["hold_list"] = hold
                context.close()

            # 043 toggle test (post-fix functional verify)
            if fname == "043":
                context = browser.new_context(viewport={"width": 1280, "height": 900})
                page = context.new_page()
                page.goto(url, wait_until="domcontentloaded")
                page.wait_for_timeout(400)
                before = page.evaluate(
                    """() => {
                    const t = document.querySelector('.collapsible-title');
                    const c = document.querySelector('.collapsible-content');
                    return {
                        title_collapsed: t ? t.classList.contains('collapsed') : null,
                        content_max_height: c ? c.style.maxHeight : null,
                    };
                }"""
                )
                page.click('.collapsible-title')
                page.wait_for_timeout(500)
                page.click('.collapsible-title')
                page.wait_for_timeout(500)
                collapsed = page.evaluate(
                    """() => {
                    const t = document.querySelector('.collapsible-title');
                    const c = document.querySelector('.collapsible-content');
                    return {
                        title_collapsed: t ? t.classList.contains('collapsed') : null,
                        content_max_height: c ? c.style.maxHeight : null,
                    };
                }"""
                )
                page.screenshot(
                    path=str(OUTDIR / "043_w1xr_1280x900_collapsed.png"),
                    full_page=True,
                )
                results[fname]["toggle"] = {"initial": before, "after_2nd_click": collapsed}
                context.close()

        browser.close()

    out_json = OUTDIR / "_xr_verify.json"
    out_json.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
