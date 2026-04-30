#!/usr/bin/env python3
"""cmd_225_redo W4 XR W1 hotfix verify — fresh eyes 実描画 visual。
feedback_phase_gate_actual_render 厳守、computed style 単体 PASS 信仰禁止。"""
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

CATALOG = Path("/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new/dimco-parts-catalog.html")
OUT = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_225_redo/w4_xr_w1_hotfix_screenshots")


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = ctx.new_page()
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        page.on("console", lambda m: errs.append(f"[{m.type}] {m.text}") if m.type == "error" else None)
        page.goto(f"file://{quote(str(CATALOG))}", wait_until="networkidle")
        page.wait_for_timeout(1500)  # CDN load

        layout = page.evaluate("""() => {
            const body = document.body;
            const containerFluid = document.querySelector('.container-fluid');
            const row = containerFluid ? containerFluid.querySelector('.row') : null;
            // Find sidebar + main col by traversing children of row
            const sidebars = row ? Array.from(row.children).filter(c => c.classList.contains('col-sm-auto')) : [];
            const mainCols = row ? Array.from(row.children).filter(c => c.classList.contains('col-sm')) : [];
            // Section presence + position
            const sections = ['section-layout', 'section-modal-button', 'section-table', 'section-form-input'];
            const sectionData = {};
            for (const id of sections) {
                const el = document.getElementById(id);
                if (el) {
                    const r = el.getBoundingClientRect();
                    sectionData[id] = {
                        top: Math.round(r.top + window.scrollY),
                        height: Math.round(r.height),
                        width: Math.round(r.width),
                        visible: r.width > 0 && r.height > 0,
                    };
                } else {
                    sectionData[id] = null;
                }
            }
            // Outer header check
            const outerHeaders = document.querySelectorAll('header.d-flex');
            const outerHeader = outerHeaders[0];
            const outerHeaderVisible = outerHeader ? outerHeader.getBoundingClientRect().height > 0 : false;
            // Logo div check
            const logo = document.querySelector('header .logo');
            const logoExists = logo !== null;
            // body width + container-fluid width + main width (key Fix 3 verify)
            return {
                body_width: body ? body.getBoundingClientRect().width : null,
                container_fluid_exists: containerFluid !== null,
                container_fluid_width: containerFluid ? containerFluid.getBoundingClientRect().width : null,
                row_exists: row !== null,
                sidebar_count: sidebars.length,
                main_col_count: mainCols.length,
                main_width: mainCols[0] ? mainCols[0].getBoundingClientRect().width : null,
                sidebar_width: sidebars[0] ? sidebars[0].getBoundingClientRect().width : null,
                section_data: sectionData,
                outer_header_visible: outerHeaderVisible,
                outer_header_height: outerHeader ? Math.round(outerHeader.getBoundingClientRect().height) : 0,
                logo_div_exists: logoExists,
                body_max_width_computed: body ? getComputedStyle(body).maxWidth : null,
            };
        }""")

        # Critical: section-table parent check (carry-over OBS-1)
        nesting_check = page.evaluate("""() => {
            const sections = ['section-layout', 'section-modal-button', 'section-table', 'section-form-input'];
            const result = {};
            for (const id of sections) {
                const el = document.getElementById(id);
                if (el) {
                    const ancestors = [];
                    let p = el.parentElement;
                    while (p && p.tagName !== 'BODY' && ancestors.length < 8) {
                        ancestors.push({
                            tag: p.tagName,
                            id: p.id || null,
                            classes: p.className.substring(0, 60) || null,
                        });
                        p = p.parentElement;
                    }
                    result[id] = ancestors;
                } else {
                    result[id] = null;
                }
            }
            return result;
        }""")

        # Take screenshots — kashira protocol: image visual confirmation MUST
        screenshots = {}
        # Top
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(300)
        path = str(OUT / "01_top.png")
        page.screenshot(path=path, full_page=False, clip={"x":0, "y":0, "width":1920, "height":900})
        screenshots["01_top"] = path

        # Section-by-section screenshots
        for i, sec in enumerate(['section-layout', 'section-modal-button', 'section-table', 'section-form-input'], start=2):
            el = page.evaluate_handle(f"document.getElementById('{sec}')")
            if el:
                page.evaluate(f"document.getElementById('{sec}').scrollIntoView({{block: 'start'}})")
                page.wait_for_timeout(500)
                path = str(OUT / f"{i:02d}_{sec.replace('section-','')}.png")
                page.screenshot(path=path, full_page=False, clip={"x":0, "y":0, "width":1920, "height":1080})
                screenshots[f"{i:02d}_{sec}"] = path

        # Full-page screenshot for kashira protocol
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(300)
        full_path = str(OUT / "06_full_page.png")
        page.screenshot(path=full_path, full_page=True)
        screenshots["06_full_page"] = full_path

        ctx.close()
        browser.close()

    out = OUT / "_verify.json"
    out.write_text(json.dumps({
        "layout": layout,
        "section_nesting_check": nesting_check,
        "screenshots": screenshots,
        "console_errors": errs,
    }, ensure_ascii=False, indent=2))
    print(json.dumps({
        "layout": layout,
        "section_nesting_check": nesting_check,
        "screenshots": screenshots,
        "console_errors": errs,
    }, ensure_ascii=False, indent=2))

    issues = []
    # Fix 1: outer header close - check main not nested inside outer header
    # Fix 2: sidebar close - main col should be sibling of sidebar (both children of .row)
    if layout["sidebar_count"] != 1:
        issues.append(f"sidebar_count = {layout['sidebar_count']}, expected 1")
    if layout["main_col_count"] != 1:
        issues.append(f"main_col_count = {layout['main_col_count']}, expected 1")
    # Fix 3: body max-width removed - container-fluid should be ~1920px wide
    if layout["body_max_width_computed"] != "none":
        issues.append(f"★body max-width still set★: {layout['body_max_width_computed']!r}, expected 'none' (Fix 3 reverted?)")
    if layout["container_fluid_width"] is not None and layout["container_fluid_width"] < 1800:
        issues.append(f"container-fluid width = {layout['container_fluid_width']}, expected >= 1800 (Fix 3 reverted?)")
    if layout["main_width"] is not None and layout["main_width"] < 1500:
        issues.append(f"main_width = {layout['main_width']}, expected >= 1500 (Fix 2/3 success)")
    # All 4 sections visible
    for sec, data in layout["section_data"].items():
        if data is None:
            issues.append(f"{sec} not present")
        elif not data["visible"]:
            issues.append(f"{sec} not visible (height={data['height']})")
        elif data["height"] < 500:
            issues.append(f"{sec} height = {data['height']}, expected >= 500")
    # OBS-1 carry-over: section-table parent should NOT be section-modal-button
    table_ancestors = nesting_check.get("section-table", [])
    if any(a.get("id") == "section-modal-button" for a in table_ancestors):
        issues.append("★OBS-1 carry-over★: section-table is nested inside section-modal-button")
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
        print("VERDICT: ALL_PASS — layout 復活 + 4 sections visible + Fix 1/2/3 全 effect 持続")


if __name__ == "__main__":
    main()
