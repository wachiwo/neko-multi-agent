#!/usr/bin/env python3
"""cmd_184_phase_a2_b2 Phase 0 DOM probe (親分判断 2 mandatory 化).

4 files × 3 probes (form-field flex-direction / table table-layout / th inline width)
読み取り専用、Playwright computed style 取得 + grep 補助。

b1_pilot 3-way 収斂 (W1 037 finding 1 + W4 memo 3 + W2 041/042 impl) を体系化。
"""
from __future__ import annotations

import os
import re
import sys
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
import yaml

SRC_DIR = Path("/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new")
OUT_DIR = Path(
    "/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_184_phase_a2_b2/phase0_dom_probe"
)

FILES = [
    ("021", "021_作業予定一覧.html"),
    ("023", "023_出荷.html"),
    ("035", "035_入金予定表出力指示.html"),
    ("045", "045_買掛一覧表出力指示.html"),
]


def probe_file(page, fname: str) -> dict:
    path = SRC_DIR / fname
    content = path.read_text(encoding="utf-8", errors="replace")
    url = f"file://{quote(str(path))}"
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(400)

    # Probe 1: form-field flex-direction
    probe1 = page.evaluate(
        """() => {
            const els = Array.from(document.querySelectorAll('.form-field'));
            return els.map((el, idx) => {
                const cs = getComputedStyle(el);
                const label = el.querySelector('label');
                return {
                    idx: idx,
                    flex_direction: cs.flexDirection,
                    align_items: cs.alignItems,
                    display: cs.display,
                    label_text: label ? label.textContent.trim().slice(0, 20) : null,
                };
            });
        }"""
    )

    # Probe 2: table / .data-table table-layout
    probe2 = page.evaluate(
        """() => {
            const tables = Array.from(document.querySelectorAll('table'));
            return tables.map((el, idx) => {
                const cs = getComputedStyle(el);
                const classList = Array.from(el.classList);
                const id = el.id || null;
                return {
                    idx: idx,
                    id: id,
                    classes: classList,
                    table_layout: cs.tableLayout,
                    min_width_computed: cs.minWidth,
                };
            });
        }"""
    )

    # Probe 3: th inline width (grep-based count + examples)
    th_inline_matches = re.findall(r'<th[^>]*\bstyle="[^"]*\bwidth:\s*(\d+)px[^"]*"', content)
    th_inline_count = len(th_inline_matches)
    th_inline_samples = [{"width_px": int(w)} for w in th_inline_matches[:10]]
    # Also check inline max-width on th
    th_inline_maxwidth = len(re.findall(r'<th[^>]*\bstyle="[^"]*\bmax-width:\s*(\d+)px', content))

    # Summary per probe
    p1_total = len(probe1)
    p1_column = sum(1 for e in probe1 if e["flex_direction"] == "column")
    p1_non_column = [e for e in probe1 if e["flex_direction"] != "column"]

    p2_total = len(probe2)
    p2_fixed = sum(1 for e in probe2 if e["table_layout"] == "fixed")
    p2_auto = sum(1 for e in probe2 if e["table_layout"] == "auto")

    result = {
        "file": fname,
        "size_kb": round(path.stat().st_size / 1024, 1),
        "line_count": content.count("\n") + 1,
        "probe_1_form_field_flex_direction": {
            "total_form_fields": p1_total,
            "column_canonical": p1_column,
            "non_column_count": len(p1_non_column),
            "non_column_details": p1_non_column[:20],  # cap for readability
            "verdict": (
                "PASS_all_column" if p1_total == p1_column and p1_total > 0
                else "NO_form_field_elements" if p1_total == 0
                else "FAIL_pre_existing_bug_detected"
            ),
        },
        "probe_2_table_table_layout": {
            "total_tables": p2_total,
            "fixed_count": p2_fixed,
            "auto_count": p2_auto,
            "breakdown": probe2,
            "verdict": (
                "N/A_no_table" if p2_total == 0
                else "PASS_all_fixed" if p2_total == p2_fixed
                else "FAIL_sp_041_partial" if p2_fixed > 0
                else "FAIL_sp_041_not_applied"
            ),
        },
        "probe_3_th_inline_width": {
            "count": th_inline_count,
            "max_width_count": th_inline_maxwidth,
            "samples": th_inline_samples,
            "verdict": "PASS_zero" if th_inline_count == 0 else "FAIL_sp_041_partial_migration",
        },
    }
    return result


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    all_results = {}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()
        for key, fname in FILES:
            print(f"[probe] {fname}", file=sys.stderr)
            r = probe_file(page, fname)
            print(
                f"  P1: {r['probe_1_form_field_flex_direction']['verdict']} "
                f"({r['probe_1_form_field_flex_direction']['column_canonical']}/"
                f"{r['probe_1_form_field_flex_direction']['total_form_fields']} column)",
                file=sys.stderr,
            )
            print(
                f"  P2: {r['probe_2_table_table_layout']['verdict']} "
                f"({r['probe_2_table_table_layout']['fixed_count']}/"
                f"{r['probe_2_table_table_layout']['total_tables']} fixed)",
                file=sys.stderr,
            )
            print(
                f"  P3: {r['probe_3_th_inline_width']['verdict']} "
                f"(count={r['probe_3_th_inline_width']['count']})",
                file=sys.stderr,
            )
            out_file = OUT_DIR / f"probe_{key}.yaml"
            out_file.write_text(
                yaml.safe_dump(r, sort_keys=False, allow_unicode=True, width=120)
            )
            all_results[key] = r
        context.close()
        browser.close()

    # Summary
    summary = {
        "generated_at": "2026-04-15T18:55:00",
        "files_total": len(all_results),
        "probe_1_summary": {
            "files_pass": sum(
                1 for r in all_results.values()
                if r["probe_1_form_field_flex_direction"]["verdict"] == "PASS_all_column"
            ),
            "files_fail_pre_existing_bug": sum(
                1 for r in all_results.values()
                if r["probe_1_form_field_flex_direction"]["verdict"] == "FAIL_pre_existing_bug_detected"
            ),
            "files_no_form_field": sum(
                1 for r in all_results.values()
                if r["probe_1_form_field_flex_direction"]["verdict"] == "NO_form_field_elements"
            ),
        },
        "probe_2_summary": {
            "files_pass_all_fixed": sum(
                1 for r in all_results.values()
                if r["probe_2_table_table_layout"]["verdict"] == "PASS_all_fixed"
            ),
            "files_na_no_table": sum(
                1 for r in all_results.values()
                if r["probe_2_table_table_layout"]["verdict"] == "N/A_no_table"
            ),
            "files_fail_sp_041_partial": sum(
                1 for r in all_results.values()
                if r["probe_2_table_table_layout"]["verdict"] == "FAIL_sp_041_partial"
            ),
            "files_fail_sp_041_not_applied": sum(
                1 for r in all_results.values()
                if r["probe_2_table_table_layout"]["verdict"] == "FAIL_sp_041_not_applied"
            ),
        },
        "probe_3_summary": {
            "files_pass_zero": sum(
                1 for r in all_results.values()
                if r["probe_3_th_inline_width"]["verdict"] == "PASS_zero"
            ),
            "files_fail_partial_migration": sum(
                1 for r in all_results.values()
                if r["probe_3_th_inline_width"]["verdict"] == "FAIL_sp_041_partial_migration"
            ),
        },
        "per_file_quick_status": {
            key: {
                "tier_kb": r["size_kb"],
                "p1": r["probe_1_form_field_flex_direction"]["verdict"],
                "p1_column_ratio": f"{r['probe_1_form_field_flex_direction']['column_canonical']}/{r['probe_1_form_field_flex_direction']['total_form_fields']}",
                "p2": r["probe_2_table_table_layout"]["verdict"],
                "p2_fixed_ratio": f"{r['probe_2_table_table_layout']['fixed_count']}/{r['probe_2_table_table_layout']['total_tables']}",
                "p3": r["probe_3_th_inline_width"]["verdict"],
                "p3_count": r["probe_3_th_inline_width"]["count"],
            }
            for key, r in all_results.items()
        },
    }

    summary_file = OUT_DIR / "summary.yaml"
    summary_file.write_text(
        yaml.safe_dump(summary, sort_keys=False, allow_unicode=True, width=120)
    )

    print("\n=== SUMMARY ===", file=sys.stderr)
    print(yaml.safe_dump(summary, sort_keys=False, allow_unicode=True, width=120), file=sys.stderr)
    print(f"\n[done] outputs: {OUT_DIR}", file=sys.stderr)


if __name__ == "__main__":
    main()
