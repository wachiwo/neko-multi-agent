#!/usr/bin/env python3
"""cmd_184 Phase A2 retrofit planning - W4 survey (8 files, read-only).

9 dimensions per file, no modifications. Output: w4_survey.yaml
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

BASE = Path("/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new")
OUTDIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_184_phase_a2_plan")
OUTDIR.mkdir(parents=True, exist_ok=True)

TARGETS = [
    ("051", "051_見積明細（海外）.html"),
    ("017", "017_商談一覧.html"),
    ("053", "053_海外入力_パッキング.html"),
    ("032", "032_在庫一覧.html"),
    ("054", "054_仕入先見積管理一覧.html"),
    ("034", "034_得意先別受注件数一覧.html"),
    ("029", "029_納品書作成.html"),
    ("045", "045_買掛一覧表出力指示.html"),
]

FONT_8STACK = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans JP', sans-serif"

DIALECT_PATTERNS = [
    "form-group", "date-range", "header-section", "input-group", "input-label",
    "select-input", "search-btn", "btn-search", "btn-output", "output-[a-z]+",
    "year-select", "month-select", "month-display", "period-group",
    "date-separator", "date-input", "date-wrapper", "filter-[a-z]+",
    "action-buttons", "detail-form-row", "search-form-row", "search-form-field"
]

CMD_183_PATTERNS = [
    (r"scrollHeight", "scrollHeight"),
    (r"setTimeout[^;]*\.style", "setTimeout+style"),
    (r"@keyframes", "@keyframes"),
    (r"^[[:space:]]*animation:", "animation:"),
]


def analyze_file(tag: str, fname: str) -> dict:
    path = BASE / fname
    size_bytes = path.stat().st_size
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.split("\n")
    line_count = len(lines)

    # --- dim 1: form-row/form-field adoption ---
    form_row_count = len(re.findall(r'class="[^"]*\bform-row\b', text))
    form_field_count = len(re.findall(r'class="[^"]*\bform-field\b(?!-inline)', text))
    form_field_inline_count = len(re.findall(r'class="[^"]*\bform-field-inline\b', text))
    form_group_count = len(re.findall(r'class="[^"]*\bform-group\b', text))

    # --- dim 2: sp_041 wide-table ---
    table_count = len(re.findall(r"<table\b", text))
    table_layout_fixed = bool(re.search(r"table-layout\s*:\s*fixed", text))
    data_table_class_on_table = bool(re.search(r'<table[^>]*class="[^"]*\bdata-table\b', text))
    # cell min-width check: look for min-width inside th/td CSS blocks or rows-table etc
    table_level_min_width_px = re.findall(r'\.(?:data-table|rows-table|detail-table|[a-z-]*table)\s*\{[^}]*min-width\s*:\s*(\d+)px', text)
    # nth-child %
    nth_child_widths = re.findall(r'nth-child\(\s*(\d+|n\+\d+)\s*\)[^{]*\{[^}]*width\s*:\s*(\d+)%', text)
    nth_child_sum = None
    if nth_child_widths:
        # only sum numeric (not n+2)
        nums = [int(w) for (sel, w) in nth_child_widths if sel.isdigit()]
        nth_child_sum = sum(nums) if nums else None

    # --- dim 3: sp_042 date-range ---
    input_date_count = len(re.findall(r'<input[^>]*type="date"', text))
    has_date_range = input_date_count >= 2
    sp_042_form_field_inline_with_dates = bool(
        re.search(r'class="form-field-inline"[^>]*>[^<]*<input[^>]*type="date"', text, re.DOTALL)
    )

    # --- dim 4: canonical 007 (search-button-row + btn) ---
    search_button_row = len(re.findall(r'class="[^"]*\bsearch-button-row\b', text))
    btn_class_usage = len(re.findall(r'class="[^"]*\bbtn\b', text))
    # 007 pattern: form-row 外に <div style="text-align: right"> の button OR .search-button-row
    inline_right_btn = len(re.findall(r'text-align\s*:\s*right[^>]*>\s*<button', text))

    # --- dim 5: body font 8-stack ---
    body_font_line_idx = None
    body_font_value = None
    for i, ln in enumerate(lines, 1):
        m = re.search(r'body\s*\{[^}]*font-family\s*:\s*([^;]+);', ln)
        if m:
            body_font_line_idx = i
            body_font_value = m.group(1).strip()
            break
    body_font_8stack_match = bool(body_font_value and "-apple-system" in body_font_value and "BlinkMacSystemFont" in body_font_value and "Noto Sans JP" in body_font_value)

    # --- dim 6: 独自 CSS (dialects) ---
    dialect_class_attr_hits: dict[str, int] = {}
    for pat in DIALECT_PATTERNS:
        # match as whole-word class token
        regex = rf'class="[^"]*\b({pat})\b[^"]*"'
        hits = re.findall(regex, text)
        if hits:
            for h in hits:
                dialect_class_attr_hits[h] = dialect_class_attr_hits.get(h, 0) + 1
    dialect_total = sum(dialect_class_attr_hits.values())
    # CSS definitions for canonical dialects
    dialect_css_defs = []
    for pat in ["form-group", "date-range", "header-section", "action-buttons", "detail-form-row", "input-group", "search-form-row"]:
        if re.search(rf'^\s*\.{pat}\s*\{{', text, re.MULTILINE):
            dialect_css_defs.append(pat)

    # --- dim 7: 3viewport overflow (via layout_invariant_check.py) ---
    # We run the W4 tool to get actual machine readings; this is the read-only check
    # Skip if we already have a per-file output
    inv_result = run_layout_invariant(path, tag)

    # --- dim 8: data-component ---
    data_components = sorted(set(re.findall(r'data-component="([^"]+)"', text)))
    canonical_5 = {"InputLayout", "SearchPanel", "CollapsibleSection", "InputFieldContainer", "DataGridTable"}
    canonical_5_present = canonical_5 & set(data_components)
    canonical_5_missing = canonical_5 - set(data_components)
    extra_components = set(data_components) - canonical_5

    # --- dim 9: 特記事項 ---
    notable = []
    # cmd_183 forbidden
    cmd_183_hits = {}
    for (pat, name) in CMD_183_PATTERNS:
        hits = len(re.findall(pat, text, re.MULTILINE))
        if hits:
            cmd_183_hits[name] = hits
    # ActionBar 5th observation
    if "ActionBar" in data_components:
        notable.append("ActionBar data-component (canonical 5 外、044 同系の business-specific header UI)")
    # Large form-groups remaining
    if form_group_count > 0:
        notable.append(f"form-group dialect 残存 {form_group_count} 箇所 (→ form-field への正規化必要)")
    # Custom sidebar/modal
    if re.search(r'\.modal-overlay|\.modal-dialog', text):
        notable.append("modal UI あり (scope 外、改修時 untouched 推奨)")
    # detail-panel / detail-table / detail-row
    if re.search(r'\.detail-panel|\.detail-row', text):
        notable.append("detail-panel/detail-row あり (展開 UI、sp_041 scope 外)")
    # Tabs
    if re.search(r'\.tabs\s*\{|\.tab-button\s*\{', text):
        notable.append("タブ UI あり (scope 外、untouched 推奨)")
    # Large CSS block
    css_block_match = re.search(r"<style>(.*?)</style>", text, re.DOTALL)
    css_size = len(css_block_match.group(1)) if css_block_match else 0
    # date-range without form-field-inline conversion
    if has_date_range and not sp_042_form_field_inline_with_dates:
        notable.append(f"date-range impl あるが form-field-inline (sp_042) 未適用 (input[type=date] x {input_date_count})")
    # tfoot/sticky etc
    if "<tfoot" in text:
        notable.append("table tfoot あり (fixed column 時注意)")

    # --- Tier estimate ---
    # heuristic: size, dialect count, canonical 5 missing, sp_041 needed
    score = 0
    if size_bytes >= 100_000:
        score += 3
    elif size_bytes >= 50_000:
        score += 2
    elif size_bytes >= 30_000:
        score += 1
    score += min(form_group_count, 10) // 2
    score += len(canonical_5_missing)
    if table_count > 0 and not table_layout_fixed:
        score += 1
    if has_date_range and not sp_042_form_field_inline_with_dates:
        score += 1
    if dialect_total >= 10:
        score += 2
    elif dialect_total >= 5:
        score += 1
    if "<tfoot" in text or re.search(r'\.tabs\s*\{', text):
        score += 1
    # tier
    if score >= 7:
        tier = "L"
    elif score >= 4:
        tier = "M"
    else:
        tier = "S"

    return {
        "tag": tag,
        "filename": fname,
        "size_bytes": size_bytes,
        "line_count": line_count,
        "css_block_size": css_size,
        "dim_1_form_row_field": {
            "form_row_count": form_row_count,
            "form_field_count": form_field_count,
            "form_field_inline_count": form_field_inline_count,
            "form_group_dialect_count": form_group_count,
            "adoption_verdict": "CANONICAL" if (form_row_count >= 1 and form_field_count >= 1 and form_group_count == 0) else ("PARTIAL" if form_row_count >= 1 else "NOT_ADOPTED"),
        },
        "dim_2_sp_041": {
            "table_count": table_count,
            "table_layout_fixed_present": table_layout_fixed,
            "data_table_class_on_html": data_table_class_on_table,
            "table_level_min_width_px": table_level_min_width_px,
            "nth_child_width_entries": len(nth_child_widths),
            "nth_child_explicit_sum_percent": nth_child_sum,
            "needs_sp_041_retrofit": table_count > 0 and not table_layout_fixed,
        },
        "dim_3_sp_042": {
            "input_type_date_count": input_date_count,
            "has_date_range_pattern": has_date_range,
            "form_field_inline_with_dates": sp_042_form_field_inline_with_dates,
            "needs_sp_042_retrofit": has_date_range and not sp_042_form_field_inline_with_dates,
        },
        "dim_4_canonical_007": {
            "search_button_row_count": search_button_row,
            "inline_right_btn_count": inline_right_btn,
            "btn_class_usage": btn_class_usage,
            "canonical_search_button_present": search_button_row >= 1 or inline_right_btn >= 1,
        },
        "dim_5_body_font": {
            "body_font_line": body_font_line_idx,
            "body_font_8stack_match": body_font_8stack_match,
            "body_font_value_sample": (body_font_value or "")[:150],
        },
        "dim_6_dialects": {
            "class_attr_hits_by_dialect": dialect_class_attr_hits,
            "total_dialect_class_attrs": dialect_total,
            "dialect_css_definitions_present": dialect_css_defs,
        },
        "dim_7_viewport_overflow": inv_result,
        "dim_8_data_component": {
            "found": data_components,
            "canonical_5_present": sorted(canonical_5_present),
            "canonical_5_missing": sorted(canonical_5_missing),
            "extra_non_canonical": sorted(extra_components),
        },
        "dim_9_notable": {
            "items": notable,
            "cmd_183_forbidden_hits": cmd_183_hits,
        },
        "tier_estimate": tier,
        "tier_score_components": {
            "size_bytes": size_bytes,
            "dialect_total": dialect_total,
            "canonical_missing": len(canonical_5_missing),
            "table_needs_sp_041": table_count > 0 and not table_layout_fixed,
            "date_range_needs_sp_042": has_date_range and not sp_042_form_field_inline_with_dates,
            "raw_score": score,
        },
    }


def run_layout_invariant(path: Path, tag: str) -> dict:
    """Run W4 tool 0a9820a to get 3-viewport overflow reading."""
    sub_outdir = OUTDIR / "layout_invariant_per_file" / tag
    sub_outdir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    for p in (
        "/tmp/libasound/usr/lib/x86_64-linux-gnu/libasound.so.2",
        "/tmp/libasound_extract/usr/lib/x86_64-linux-gnu/libasound.so.2",
    ):
        if os.path.exists(p):
            env["LD_PRELOAD"] = p
            break
    try:
        result = subprocess.run(
            [
                "python3",
                "/mnt/c/tools/neko-multi-agent/scripts/layout_invariant_check.py",
                "--target-file", str(path),
                "--expected", "/mnt/c/tools/neko-multi-agent/scripts/expected_縦.yaml",
                "--output-dir", str(sub_outdir),
            ],
            capture_output=True, text=True, timeout=180, env=env,
        )
        # Read JSON
        json_files = list(sub_outdir.glob("layout_invariants_*.json"))
        if json_files:
            data = json.loads(json_files[0].read_text(encoding="utf-8"))
            rules = data.get("rules_evaluated", [])
            passed = [r["rule_id"] for r in rules if r.get("passed")]
            failed = [(r["rule_id"], r.get("note", ""), len(r.get("fails", []))) for r in rules if not r.get("passed")]
            # Separate table overflow vs button overflow
            table_overflow = 0
            button_overflow = 0
            for r in rules:
                if r["rule_id"] == "viewport-overflow-check-multi-zoom":
                    for f in r.get("fails", []):
                        sel = f.get("selector", "")
                        if sel == "table" or sel == ".table-wrapper":
                            table_overflow += 1
                        elif sel == "button":
                            button_overflow += 1
            return {
                "tool": "scripts/layout_invariant_check.py 0a9820a",
                "rules_passed": len(passed),
                "rules_failed": len(failed),
                "high_failures": data.get("high_severity_failures", 0),
                "failed_rules": [f[0] for f in failed],
                "table_overflow_total": table_overflow,
                "button_overflow_total": button_overflow,
                "table_overflow_zero": table_overflow == 0,
                "button_overflow_is_sidebar_FP": button_overflow > 0,
            }
        return {"error": "no JSON output", "stdout": result.stdout[-500:], "stderr": result.stderr[-500:]}
    except subprocess.TimeoutExpired:
        return {"error": "timeout after 180s"}
    except Exception as e:
        return {"error": str(e)[:200]}


def main():
    print(f"[W4 survey] 8 files, 9 dimensions each, read-only...")
    results = []
    for tag, fname in TARGETS:
        print(f"  [{tag}] {fname} ...", flush=True)
        r = analyze_file(tag, fname)
        results.append(r)
        inv = r["dim_7_viewport_overflow"]
        if "rules_passed" in inv:
            print(f"    tier={r['tier_estimate']} size={r['size_bytes']//1024}KB inv={inv['rules_passed']}/{inv['rules_passed']+inv['rules_failed']} PASS table_overflow={inv.get('table_overflow_total', '?')} form-group={r['dim_1_form_row_field']['form_group_dialect_count']}")
        else:
            print(f"    tier={r['tier_estimate']} size={r['size_bytes']//1024}KB inv=ERR: {inv.get('error', '?')}")

    out_path = OUTDIR / "w4_survey.yaml"
    # Write as YAML via custom — simple sufficient since nested dicts/lists
    try:
        import yaml
        with open(out_path, "w", encoding="utf-8") as f:
            yaml.dump(
                {
                    "surveyor": "worker4",
                    "parent_cmd": "cmd_184_phase_a2_retrofit_planning",
                    "task_id": "subtask_184_a2_plan_survey_w4",
                    "file_count": len(results),
                    "tool_used": "scripts/layout_invariant_check.py 0a9820a (W4 自作)",
                    "scope_lock": "read-only, no modifications",
                    "tier_summary": {
                        "L": [r["tag"] for r in results if r["tier_estimate"] == "L"],
                        "M": [r["tag"] for r in results if r["tier_estimate"] == "M"],
                        "S": [r["tag"] for r in results if r["tier_estimate"] == "S"],
                    },
                    "files": results,
                },
                f, allow_unicode=True, sort_keys=False, default_flow_style=False,
            )
    except ImportError:
        out_path.with_suffix(".json").write_text(json.dumps(results, indent=2, ensure_ascii=False))
        print(f"pyyaml not available, wrote JSON instead")

    print(f"\n[done] survey output: {out_path}")
    # Print summary
    tier_counts = {"S": 0, "M": 0, "L": 0}
    for r in results:
        tier_counts[r["tier_estimate"]] += 1
    print(f"[tier summary] L={tier_counts['L']} M={tier_counts['M']} S={tier_counts['S']}")


if __name__ == "__main__":
    main()
