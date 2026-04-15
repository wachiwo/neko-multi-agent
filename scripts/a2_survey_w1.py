#!/usr/bin/env python3
"""cmd_184_phase_a2_retrofit_planning W1 survey (read-only).

9 files × 9 dimensions observation. Outputs YAML structured report.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

SRC_DIR = Path("/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new")
OUT_DIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_184_phase_a2_plan")
LIC_OUT = Path("/tmp/w1_a2_survey")
SCRIPTS_DIR = Path("/mnt/c/tools/neko-multi-agent/scripts")

FILES = [
    "052_受注画面(受注明細).html",
    "015_見積明細.html",
    "048_引合一覧.html",
    "053_海外入力_プロフォーマ.html",
    "020_未発注一覧.html",
    "030_発送.html",
    "055_仕入先見積管理明細.html",
    "033_在庫棚卸.html",
    "037_仕掛在庫一覧表出力指示.html",
]

PEER_8STACK = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans JP', sans-serif"

DIALECT_PATTERNS = [
    "filter-section", "filter-row", "filter-group",
    "input-group", "input-label", "header-section",
    "period-group", "period-label", "period-input", "period-suffix",
    "date-input", "date-separator", "date-wrapper", "date-range",
    "btn-search", "btn-output", "btn-primary", "btn-secondary",
    "search-btn", "clear-btn",
    "output-section", "output-label", "output-select", "output-btn",
    "year-select", "month-select", "month-display",
    "select-input",
    "search-form-row", "search-form-field",
    "form-group",
]

DATA_COMPONENT_TYPES = [
    "InputLayout", "SearchPanel", "CollapsibleSection",
    "InputFieldContainer", "DataGridTable", "InlineFieldGroup",
    "ActionBar", "AdminInfo",
]


def run(cmd, capture=True, timeout=120):
    r = subprocess.run(cmd, shell=True, capture_output=capture, text=True, timeout=timeout)
    return r.stdout, r.stderr, r.returncode


def survey_file(fname: str) -> dict:
    path = SRC_DIR / fname
    content = path.read_text(encoding="utf-8", errors="replace")
    size_kb = round(path.stat().st_size / 1024, 1)
    line_count = content.count("\n") + 1

    # Dim 5: body font
    font_m = re.search(r"body\s*\{[^}]*font-family:\s*([^;}]+)", content)
    body_font_raw = (font_m.group(1).strip() if font_m else "").replace("  ", " ")
    body_font_8stack_match = PEER_8STACK in content  # check fragment presence

    # Dim 1: form-row / form-field adoption
    form_row_class_count = len(re.findall(r'class="[^"]*\bform-row\b', content))
    form_field_class_count = len(re.findall(r'class="form-field\b', content))
    form_field_inline_count = len(re.findall(r'class="form-field-inline\b', content))
    form_group_class_count = len(re.findall(r'class="form-group\b', content))

    # Dim 6: dialect residue
    dialect_class_counts = {}
    dialect_css_counts = {}
    for d in DIALECT_PATTERNS:
        dialect_class_counts[d] = len(re.findall(r'class="[^"]*\b' + re.escape(d) + r'\b', content))
        dialect_css_counts[d] = len(re.findall(r"^\s*\." + re.escape(d) + r"\s*[\{,:\.\s]", content, re.MULTILINE))
    dialect_class_total = sum(dialect_class_counts.values())
    dialect_css_total = sum(dialect_css_counts.values())
    active_dialects = {d: {"class_attr": c, "css_rule": s} for d, c, s in
                       zip(DIALECT_PATTERNS, dialect_class_counts.values(), dialect_css_counts.values())
                       if c > 0 or s > 0}

    # Dim 2: sp_041 markers (tables, table-layout:fixed, cell min-width)
    table_count = len(re.findall(r"<table\b", content))
    table_layout_fixed_count = len(re.findall(r"table-layout\s*:\s*fixed", content))
    data_table_class_count = len(re.findall(r'class="[^"]*\bdata-table\b', content))
    table_min_width_count = len(re.findall(r"table\s*\{[^}]*min-width\s*:\s*\d+", content))
    cell_min_width_count = len(re.findall(r"^\s*min-width:\s*\d+(px|em|rem)", content, re.MULTILINE))
    nth_child_pct_count = len(re.findall(r"nth-child\([^)]+\).*?width:\s*\d+%", content, re.DOTALL))
    nth_child_px_count = len(re.findall(r"nth-child\([^)]+\).*?min-width:\s*\d+px", content, re.DOTALL))
    text_overflow_ellipsis_count = content.count("text-overflow: ellipsis") + content.count("text-overflow:ellipsis")

    # Dim 3: sp_042 markers (date-range)
    date_input_count = len(re.findall(r'<input[^>]*type="date"', content))
    # Check pattern: form-field-inline > input[date] + span + input[date]
    sp042_structure = bool(re.search(
        r'class="form-field-inline"[^>]*>\s*<input[^>]*type="date"[^>]*>\s*<span>[^<]*</span>\s*<input[^>]*type="date"',
        content, re.DOTALL))
    separator_ascii_tilde = len(re.findall(r"<span>~</span>", content))
    separator_fullwidth = len(re.findall(r"<span>～</span>|<span>〜</span>", content))
    date_range_class_count = dialect_class_counts.get("date-range", 0)  # legacy dialect

    # Dim 4: button placement
    search_button_row_count = len(re.findall(r'class="search-button-row\b', content))
    # Find 検索 buttons, note their parent context
    search_btn_legacy = dialect_class_counts.get("search-btn", 0) + dialect_class_counts.get("btn-search", 0)

    # Dim 8: data-component counts
    dc_counts = {}
    for t in DATA_COMPONENT_TYPES:
        dc_counts[t] = len(re.findall(r'data-component="' + t + r'"', content))
    dc_total = sum(dc_counts.values())
    dc_missing_canonical5 = [t for t in ["InputLayout", "SearchPanel", "CollapsibleSection",
                                          "InputFieldContainer", "DataGridTable"] if dc_counts.get(t, 0) == 0]

    # cmd_183 forbidden
    scrollheight_count = content.count("scrollHeight")
    keyframes_count = len(re.findall(r"@keyframes", content))
    animation_named_count = len(re.findall(r"animation:\s*[a-zA-Z_]", content))
    settimeout_count = content.count("setTimeout")

    # toggleSection JS
    toggle_section_js = bool(re.search(r"function\s+toggleSection\s*\(", content))

    # Tier estimate (S/M/L based on size + dialect + canonical adoption)
    if size_kb < 30:
        tier_size = "S"
    elif size_kb < 60:
        tier_size = "M"
    else:
        tier_size = "L"

    # Adoption grade
    canonical_5_present = sum(1 for t in ["InputLayout", "SearchPanel", "CollapsibleSection",
                                           "InputFieldContainer", "DataGridTable"] if dc_counts.get(t, 0) > 0)

    if form_field_class_count > 0 and form_row_class_count > 0 and dialect_class_total == 0:
        form_adoption = "full"
    elif form_field_class_count > 0 and form_row_class_count > 0 and dialect_class_total <= 2:
        form_adoption = "partial-minor-residue"
    elif form_row_class_count > 0 and form_group_class_count > 0:
        form_adoption = "partial-form-group-legacy"
    elif form_group_class_count > 0 or dialect_class_total > 5:
        form_adoption = "legacy-dialect-heavy"
    elif form_row_class_count == 0 and form_field_class_count == 0 and dialect_class_total == 0:
        form_adoption = "none-no-form-elements"
    else:
        form_adoption = "missing-or-other"

    # sp_041 status
    if table_count == 0:
        sp041_status = "N/A-no-table"
    elif table_layout_fixed_count > 0 and cell_min_width_count == 0 and text_overflow_ellipsis_count > 0:
        sp041_status = "applied-full"
    elif table_layout_fixed_count > 0:
        sp041_status = "applied-partial"
    elif table_min_width_count > 0 or nth_child_px_count > 0:
        sp041_status = "not-applied-legacy-fixed-width"
    else:
        sp041_status = "not-applied"

    # sp_042 status
    if date_input_count == 0:
        sp042_status = "N/A-no-date-input"
    elif sp042_structure:
        sp042_status = "applied-canonical"
    elif date_range_class_count > 0:
        sp042_status = "legacy-date-range-dialect"
    elif form_field_inline_count > 0 and date_input_count >= 2:
        sp042_status = "partial-inline-no-structure-match"
    else:
        sp042_status = "date-input-not-in-inline"

    # button placement
    if search_button_row_count > 0:
        button_placement = "search-button-row-canonical"
    elif search_btn_legacy > 0:
        button_placement = "search-btn-legacy-dialect"
    else:
        button_placement = "N/A-or-other"

    return {
        "file": fname,
        "size_kb": size_kb,
        "line_count": line_count,
        "tier_size": tier_size,
        "dim_1_form_adoption": {
            "status": form_adoption,
            "form_row_class_count": form_row_class_count,
            "form_field_class_count": form_field_class_count,
            "form_field_inline_count": form_field_inline_count,
            "form_group_class_count": form_group_class_count,
        },
        "dim_2_sp_041_status": {
            "status": sp041_status,
            "table_count": table_count,
            "data_table_class_count": data_table_class_count,
            "table_layout_fixed_count": table_layout_fixed_count,
            "table_min_width_count": table_min_width_count,
            "cell_min_width_count": cell_min_width_count,
            "nth_child_pct_count": nth_child_pct_count,
            "nth_child_px_count": nth_child_px_count,
            "text_overflow_ellipsis_count": text_overflow_ellipsis_count,
        },
        "dim_3_sp_042_status": {
            "status": sp042_status,
            "date_input_count": date_input_count,
            "sp042_structure_match": sp042_structure,
            "separator_ascii_tilde_count": separator_ascii_tilde,
            "separator_fullwidth_count": separator_fullwidth,
            "date_range_legacy_dialect_count": date_range_class_count,
        },
        "dim_4_button_placement": {
            "status": button_placement,
            "search_button_row_count": search_button_row_count,
            "search_btn_legacy_count": search_btn_legacy,
        },
        "dim_5_body_font": {
            "8stack_match": body_font_8stack_match,
            "body_font_raw_first_80": (body_font_raw[:80] if body_font_raw else ""),
        },
        "dim_6_dialect_residue": {
            "total_class_attr_count": dialect_class_total,
            "total_css_rule_count": dialect_css_total,
            "active_dialects": active_dialects,
        },
        "dim_8_data_component": {
            "total_count": dc_total,
            "canonical_5_present_count": canonical_5_present,
            "canonical_5_missing": dc_missing_canonical5,
            "breakdown": {k: v for k, v in dc_counts.items() if v > 0},
        },
        "dim_9_notes": {
            "toggle_section_js_present": toggle_section_js,
            "cmd_183_markers": {
                "scrollHeight": scrollheight_count,
                "keyframes": keyframes_count,
                "animation_named": animation_named_count,
                "setTimeout": settimeout_count,
            },
        },
    }


def run_layout_invariant(fname: str) -> dict:
    """Dim 7: viewport-overflow status via layout_invariant_check.py."""
    path = SRC_DIR / fname
    LIC_OUT.mkdir(parents=True, exist_ok=True)
    cmd = (
        f"python3 {SCRIPTS_DIR}/layout_invariant_check.py "
        f'--target-file "{path}" '
        f"--expected {SCRIPTS_DIR}/expected_縦.yaml "
        f'--output-dir "{LIC_OUT}" 2>&1 | tail -3'
    )
    out, err, rc = run(cmd, timeout=180)
    # Read JSON
    json_path = LIC_OUT / f"layout_invariants_{fname}.json"
    if not json_path.exists():
        return {"error": "json not found", "stdout": out}
    data = json.loads(json_path.read_text(encoding="utf-8"))
    summary = {"rules_passed": 0, "rules_failed": 0, "viewport_overflow_fails": []}
    for r in data.get("rules_evaluated", []):
        if r["passed"]:
            summary["rules_passed"] += 1
        else:
            summary["rules_failed"] += 1
        if r["rule_id"] == "viewport-overflow-check-multi-zoom":
            summary["viewport_overflow_passed"] = r["passed"]
            fails = r.get("fails", [])
            summary["viewport_overflow_fail_count"] = len(fails)
            # Categorize: sidebar-only FP vs real table/element overflow
            sidebar_only = all(
                (f.get("selector") == "button" and "個人設定" in f.get("text", ""))
                for f in fails
            ) if fails else True
            summary["viewport_overflow_sidebar_only_fp"] = sidebar_only
            summary["viewport_overflow_other_elements"] = [
                {"selector": f.get("selector"), "text": f.get("text", "")[:30],
                 "reason": f.get("reason"), "viewport": f.get("viewport")}
                for f in fails
                if not (f.get("selector") == "button" and "個人設定" in f.get("text", ""))
            ]
    return summary


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results = {"files": [], "summary": {}}
    for fname in FILES:
        print(f"[survey] {fname}", file=sys.stderr)
        entry = survey_file(fname)
        print(f"  tier={entry['tier_size']} form_adopt={entry['dim_1_form_adoption']['status']}", file=sys.stderr)
        print(f"  sp_041={entry['dim_2_sp_041_status']['status']} sp_042={entry['dim_3_sp_042_status']['status']}", file=sys.stderr)
        print(f"  running layout_invariant...", file=sys.stderr)
        try:
            entry["dim_7_viewport_overflow"] = run_layout_invariant(fname)
        except Exception as e:
            entry["dim_7_viewport_overflow"] = {"error": str(e)}
        results["files"].append(entry)

    # Summary
    tiers = {}
    adoption = {}
    sp041 = {}
    sp042 = {}
    vp_fail_other = 0
    for e in results["files"]:
        tiers[e["tier_size"]] = tiers.get(e["tier_size"], 0) + 1
        adoption[e["dim_1_form_adoption"]["status"]] = adoption.get(e["dim_1_form_adoption"]["status"], 0) + 1
        sp041[e["dim_2_sp_041_status"]["status"]] = sp041.get(e["dim_2_sp_041_status"]["status"], 0) + 1
        sp042[e["dim_3_sp_042_status"]["status"]] = sp042.get(e["dim_3_sp_042_status"]["status"], 0) + 1
        vpo = e.get("dim_7_viewport_overflow", {})
        if vpo.get("viewport_overflow_other_elements"):
            vp_fail_other += 1
    results["summary"] = {
        "total_files": len(results["files"]),
        "tier_distribution": tiers,
        "form_adoption_distribution": adoption,
        "sp_041_distribution": sp041,
        "sp_042_distribution": sp042,
        "files_with_non_fp_overflow": vp_fail_other,
    }

    out_file = OUT_DIR / "w1_survey.yaml"
    import yaml
    out_file.write_text(yaml.safe_dump(results, sort_keys=False, allow_unicode=True, width=120))
    print(f"\n[done] saved: {out_file}", file=sys.stderr)
    print(yaml.safe_dump(results["summary"], sort_keys=False, allow_unicode=True), file=sys.stderr)


if __name__ == "__main__":
    main()
