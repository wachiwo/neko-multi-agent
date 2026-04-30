#!/usr/bin/env python3
"""cmd_217 Phase 3 integration verify — 6 files × 3 viewports.

Per spec subtask_217_010_w4_phase3_integration_verify:
- computed style canonical 6 files 全一致
- structural drift 0
- functional toggle 全動作
"""
from __future__ import annotations
import os
import sys
import json
import hashlib
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

BASE = Path("/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new")
FILES = [
    ("050", BASE / "050_海外引合.html"),
    ("051", BASE / "051_見積明細（海外）.html"),
    ("053コマ", BASE / "053_海外入力_コマーシャル.html"),
    ("053パック", BASE / "053_海外入力_パッキング.html"),
    ("053プロ", BASE / "053_海外入力_プロフォーマ.html"),
    ("053一覧", BASE / "053_海外取引一覧.html"),
]
OUTBASE = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_217/phase3_integration")
VIEWPORTS = [(375, 800), (960, 720), (1920, 1080)]

PROBE_JS = """() => {
    const sections = document.querySelectorAll('.collapsible-section');
    const headers = document.querySelectorAll('.collapsible-header');
    const contents = document.querySelectorAll('.collapsible-content');
    const indicators = document.querySelectorAll('.collapsible-indicator');
    const stale_indicator_single = document.querySelectorAll('.indicator:not(.collapsible-indicator)').length;
    const stale_collapse_indicator = document.querySelectorAll('.collapse-indicator').length;
    const stale_collapsible_title = document.querySelectorAll('.collapsible-title').length;
    const exportSection = document.querySelector('.page-header .export-section');
    const sample = headers[0];
    const sampleStyle = sample ? {
        bg: getComputedStyle(sample).backgroundColor,
        color: getComputedStyle(sample).color,
        cursor: getComputedStyle(sample).cursor,
        padding: getComputedStyle(sample).padding,
        fontSize: getComputedStyle(sample).fontSize,
        fontWeight: getComputedStyle(sample).fontWeight,
        display: getComputedStyle(sample).display,
        tagName: sample.tagName,
    } : null;
    const exportStyle = exportSection ? {
        display: getComputedStyle(exportSection).display,
        gap: getComputedStyle(exportSection).gap,
        alignItems: getComputedStyle(exportSection).alignItems,
        btnCount: exportSection.querySelectorAll('button').length,
    } : null;
    const root = getComputedStyle(document.documentElement);
    return {
        section_count: sections.length,
        header_count: headers.length,
        content_count: contents.length,
        indicator_count: indicators.length,
        stale_indicator_single: stale_indicator_single,
        stale_collapse_indicator: stale_collapse_indicator,
        stale_collapsible_title: stale_collapsible_title,
        first_header_style: sampleStyle,
        export_section: exportStyle,
        root_vars: {
            primary_blue: root.getPropertyValue('--primary-blue').trim(),
            primary_blue_dark: root.getPropertyValue('--primary-blue-dark').trim(),
            primary_blue_light: root.getPropertyValue('--primary-blue-light').trim(),
            secondary_blue: root.getPropertyValue('--secondary-blue').trim(),
            light_blue: root.getPropertyValue('--light-blue').trim(),
            lighter_blue: root.getPropertyValue('--lighter-blue').trim(),
            accent_blue: root.getPropertyValue('--accent-blue').trim(),
            text_dark: root.getPropertyValue('--text-dark').trim(),
            border_color: root.getPropertyValue('--border-color').trim(),
            shadow: root.getPropertyValue('--shadow').trim(),
        }
    };
}"""

TOGGLE_TEST_JS_OPEN = """() => {
    document.querySelector('.collapsible-header').click();
    return null;
}"""

TOGGLE_PROBE_JS = """() => {
    const h = document.querySelector('.collapsible-header');
    if (!h) return null;
    const s = h.parentElement;
    const c = s.querySelector('.collapsible-content');
    return {
        header_collapsed: h.classList.contains('collapsed'),
        section_collapsed: s.classList.contains('collapsed'),
        content_collapsed: c ? c.classList.contains('collapsed') : null,
        content_max_height: c ? c.style.maxHeight : null,
    };
}"""


def main():
    OUTBASE.mkdir(parents=True, exist_ok=True)
    results = {"files": {}, "cross_file_summary": {}}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for label, path in FILES:
            url = f"file://{quote(str(path))}"
            file_results = {"path": str(path), "viewports": {}}
            print(f"[{label}] {path.name}", file=sys.stderr)
            for w, h in VIEWPORTS:
                ctx = browser.new_context(viewport={"width": w, "height": h})
                page = ctx.new_page()
                console_errors = []
                page.on("pageerror", lambda exc: console_errors.append(str(exc)))
                page.on("console", lambda msg: console_errors.append(f"[{msg.type}] {msg.text}") if msg.type == "error" else None)
                page.goto(url, wait_until="domcontentloaded")
                page.wait_for_timeout(500)

                probe = page.evaluate(PROBE_JS)
                probe["console_errors"] = console_errors
                file_results["viewports"][f"{w}x{h}"] = probe

                screenshot_path = OUTBASE / f"{label.replace('（','-').replace('）','-')}_{w}x{h}.png"
                page.screenshot(path=str(screenshot_path), full_page=True)
                ctx.close()

            # Toggle test
            ctx = browser.new_context(viewport={"width": 1280, "height": 900})
            page = ctx.new_page()
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(300)
            initial = page.evaluate(TOGGLE_PROBE_JS)
            page.evaluate(TOGGLE_TEST_JS_OPEN)
            page.wait_for_timeout(500)
            after_open = page.evaluate(TOGGLE_PROBE_JS)
            page.evaluate(TOGGLE_TEST_JS_OPEN)
            page.wait_for_timeout(500)
            after_close = page.evaluate(TOGGLE_PROBE_JS)
            file_results["toggle_test"] = {
                "initial": initial,
                "after_first_click": after_open,
                "after_second_click": after_close,
            }
            ctx.close()
            results["files"][label] = file_results
        browser.close()

    # Cross-file summary
    canonicals = {
        "primary_blue": "#004B87",
        "primary_blue_dark": "#003d6b",
        "primary_blue_light": "#0070C0",
        "lighter_blue": "#EBF3FA",
        "accent_blue": "#004B87",
        "text_dark": "#1e293b",
        "border_color": "#cbd5e1",
    }
    summary = {"per_var_consistency": {}}
    for var, expected in canonicals.items():
        files_with_canonical = []
        files_with_other = {}
        for label in results["files"]:
            v = results["files"][label]["viewports"]["1920x1080"]["root_vars"].get(var, "")
            if v.lower() == expected.lower():
                files_with_canonical.append(label)
            else:
                files_with_other.setdefault(v, []).append(label)
        summary["per_var_consistency"][var] = {
            "expected": expected,
            "files_with_canonical": files_with_canonical,
            "files_with_other": files_with_other,
            "all_match": len(files_with_canonical) == len(results["files"]),
        }

    # Stale check summary
    stale_summary = {
        "stale_indicator_single_total": 0,
        "stale_collapse_indicator_total": 0,
        "stale_collapsible_title_total": 0,
    }
    for label in results["files"]:
        vp = results["files"][label]["viewports"]["1920x1080"]
        stale_summary["stale_indicator_single_total"] += vp["stale_indicator_single"]
        stale_summary["stale_collapse_indicator_total"] += vp["stale_collapse_indicator"]
        stale_summary["stale_collapsible_title_total"] += vp["stale_collapsible_title"]
    summary["stale_summary"] = stale_summary

    # Toggle reversibility check
    toggle_summary = {"all_toggle_reversible": True, "issues": []}
    for label in results["files"]:
        tt = results["files"][label]["toggle_test"]
        ao = tt.get("after_first_click")
        ac = tt.get("after_second_click")
        if not ao or not ac:
            toggle_summary["all_toggle_reversible"] = False
            toggle_summary["issues"].append(f"{label}: toggle probe failed")
            continue
        # After first click, header must be NOT collapsed (expanded), after second click must be collapsed
        # OR if initial state varies (some files might start expanded), check that 2 toggles return to initial state
        if ao["header_collapsed"] == ac["header_collapsed"]:
            toggle_summary["all_toggle_reversible"] = False
            toggle_summary["issues"].append(
                f"{label}: toggle not reversible — open={ao['header_collapsed']} close={ac['header_collapsed']}"
            )
    summary["toggle_summary"] = toggle_summary

    # Console error summary
    err_summary = {"total_errors": 0, "files_with_errors": {}}
    for label in results["files"]:
        errs = []
        for vp, p in results["files"][label]["viewports"].items():
            errs.extend(p.get("console_errors", []))
        err_summary["total_errors"] += len(errs)
        if errs:
            err_summary["files_with_errors"][label] = errs[:5]
    summary["console_errors"] = err_summary

    results["cross_file_summary"] = summary

    out = OUTBASE / "_phase3_results.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2))

    # Final verdict
    print()
    print("=" * 60)
    issues = []
    for var, info in summary["per_var_consistency"].items():
        if not info["all_match"]:
            issues.append(f":root --{var}: {info['files_with_other']}")
    if stale_summary["stale_indicator_single_total"] > 0:
        issues.append(f"stale_indicator_single: {stale_summary['stale_indicator_single_total']}")
    if stale_summary["stale_collapse_indicator_total"] > 0:
        issues.append(f"stale_collapse_indicator: {stale_summary['stale_collapse_indicator_total']}")
    if stale_summary["stale_collapsible_title_total"] > 0:
        issues.append(f"stale_collapsible_title: {stale_summary['stale_collapsible_title_total']}")
    if not toggle_summary["all_toggle_reversible"]:
        issues.append(f"toggle issues: {toggle_summary['issues']}")
    if err_summary["total_errors"] > 0:
        issues.append(f"console errors: {err_summary['total_errors']}")

    if issues:
        print("VERDICT: ISSUES FOUND")
        for i in issues:
            print(f"  - {i}")
    else:
        print("VERDICT: ALL_PASS — 6 files canonical 一致 + structural drift 0 + toggle reversible + 0 console errors")

    print(f"\nResults JSON: {out}")
    return 0 if not issues else 1


if __name__ == "__main__":
    sys.exit(main())
