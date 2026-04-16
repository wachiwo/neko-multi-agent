#!/usr/bin/env python3
"""cmd_184_audit W1 v2: baseline diff (016_受注一覧 baseline)
READ-ONLY. Measures form-field / form-field-inline coverage.

Scope rules (derived from baseline 016 behavior):
- Exclude input types: radio, checkbox, hidden, submit, button, reset, file, image
- Exclude elements inside settings modal / generic modal-box / modal-content / sidebar
- Coverage = element has form-field OR form-field-inline ancestor (OR, not sum)
"""
import os
import glob
import sys
from bs4 import BeautifulSoup

NEW_DIR = "/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new"
OUTPUT_MD = "/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_184_audit/w1_baseline_diff_v2.md"

# input types that should be in form-field (data input)
FORM_INPUT_TYPES = {"text", "date", "number", "email", "tel", "url", "password", "search", "time", "datetime-local", "month", "week", "color", ""}
# ("" for default which is "text")

# Parent class patterns to exclude (modal, sidebar, etc)
EXCLUDE_ANCESTOR_CLASSES = {"modal", "modal-box", "modal-overlay", "modal-content", "modal-body", "sidebar", "settingsModal"}
EXCLUDE_ANCESTOR_IDS = {"settingsModal", "supplier-search-modal", "modalOverlay"}

def has_class_ancestor(el, cls):
    for parent in el.parents:
        classes = parent.get("class", [])
        if classes and cls in classes:
            return True
    return False

def is_excluded(el):
    """Check if element is inside an excluded area (modal, sidebar, etc)."""
    for parent in el.parents:
        classes = parent.get("class", []) or []
        pid = parent.get("id", "") or ""
        for c in classes:
            if c in EXCLUDE_ANCESTOR_CLASSES:
                return True
        if pid in EXCLUDE_ANCESTOR_IDS:
            return True
    return False

def measure_file(filepath):
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        html = f.read()
    soup = BeautifulSoup(html, "html.parser")

    # Filter: in-scope inputs (form input types, NOT in modal/sidebar)
    def in_scope_input(el):
        t = (el.get("type") or "text").lower()
        if t not in FORM_INPUT_TYPES:
            return False
        if is_excluded(el):
            return False
        return True

    def in_scope_select(el):
        return not is_excluded(el)

    def in_scope_textarea(el):
        return not is_excluded(el)

    all_inputs = soup.find_all("input")
    all_selects = soup.find_all("select")
    all_textareas = soup.find_all("textarea")

    inputs_in_scope = [el for el in all_inputs if in_scope_input(el)]
    selects_in_scope = [el for el in all_selects if in_scope_select(el)]
    textareas_in_scope = [el for el in all_textareas if in_scope_textarea(el)]

    form_fields = soup.select(".form-field")
    form_fields_inline = soup.select(".form-field-inline")
    form_rows = soup.select(".form-row")

    def ff(el): return has_class_ancestor(el, "form-field")
    def ffi(el): return has_class_ancestor(el, "form-field-inline")
    def covered(el): return ff(el) or ffi(el)

    inputs_covered = sum(1 for el in inputs_in_scope if covered(el))
    selects_covered = sum(1 for el in selects_in_scope if covered(el))
    textareas_covered = sum(1 for el in textareas_in_scope if covered(el))

    return {
        "file": os.path.basename(filepath),
        "input_total_raw": len(all_inputs),
        "input_total_scope": len(inputs_in_scope),
        "input_covered": inputs_covered,
        "select_total_raw": len(all_selects),
        "select_total_scope": len(selects_in_scope),
        "select_covered": selects_covered,
        "textarea_total_raw": len(all_textareas),
        "textarea_total_scope": len(textareas_in_scope),
        "textarea_covered": textareas_covered,
        "form_field_count": len(form_fields),
        "form_field_inline_count": len(form_fields_inline),
        "form_row_count": len(form_rows),
    }

def pct(num, den):
    if den == 0:
        return "N/A"
    return f"{100.0 * num / den:.0f}%"

def main():
    files = sorted(glob.glob(os.path.join(NEW_DIR, "*.html")))
    print(f"Found {len(files)} HTML files", file=sys.stderr)

    baseline_file = "016_受注一覧.html"

    results = []
    for fp in files:
        try:
            m = measure_file(fp)
            results.append(m)
        except Exception as e:
            print(f"ERROR {fp}: {e}", file=sys.stderr)

    baseline = next((r for r in results if r["file"] == baseline_file), None)

    os.makedirs(os.path.dirname(OUTPUT_MD), exist_ok=True)
    lines = []
    lines.append("# cmd_184_audit W1 v2: baseline diff (baseline=016_受注一覧)")
    lines.append("")
    lines.append("**Scope**: new/ 配下 全 60 HTML files")
    lines.append("**Baseline**: 016_受注一覧.html (★唯一ご主人様 OK 確定 file★)")
    lines.append("**Method**: BeautifulSoup DOM 解析、form-field OR form-field-inline 覆率測定")
    lines.append("")
    lines.append("**Scope filters (baseline 016 から派生)**:")
    lines.append(f"- Input types in scope: {sorted(FORM_INPUT_TYPES)}")
    lines.append(f"- Excluded ancestor classes: {sorted(EXCLUDE_ANCESTOR_CLASSES)}")
    lines.append(f"- Excluded ancestor IDs: {sorted(EXCLUDE_ANCESTOR_IDS)}")
    lines.append("- Rationale: radio/checkbox/button/hidden/file, modal 内要素, sidebar 内要素は form-field 対象外")
    lines.append("")
    lines.append("**Source tag**: Python BeautifulSoup + soup.find_all / has_class_ancestor / is_excluded")
    lines.append("**Timestamp**: 2026-04-16 (v2 audit run, scope-filtered)")
    lines.append("**Script**: /mnt/c/tools/neko-multi-agent/scripts/audit_baseline_diff_v2.py")
    lines.append("")
    lines.append("## Baseline 016 Verification")
    lines.append("")
    lines.append("| metric | kashira_note | grep 実測 | match |")
    lines.append("|--------|--------------|-----------|-------|")
    lines.append(f"| form-row | 13 | {baseline['form_row_count']} | {'✅' if baseline['form_row_count']==13 else '❌'} |")
    lines.append(f"| form-field | 25 | {baseline['form_field_count']} | {'✅' if baseline['form_field_count']==25 else '❌'} |")
    lines.append(f"| form-field-inline | 9 | {baseline['form_field_inline_count']} | {'✅' if baseline['form_field_inline_count']==9 else '❌'} |")
    lines.append(f"| input total (raw) | 21 | {baseline['input_total_raw']} | {'✅' if baseline['input_total_raw']==21 else '❌'} |")
    lines.append(f"| select total (raw) | 10 | {baseline['select_total_raw']} | {'✅' if baseline['select_total_raw']==10 else '❌'} |")
    lines.append(f"| textarea total (raw) | 4 | {baseline['textarea_total_raw']} | {'✅' if baseline['textarea_total_raw']==4 else '❌'} |")
    lines.append("")
    b_cov = baseline['input_covered'] + baseline['select_covered'] + baseline['textarea_covered']
    b_tot_scope = baseline['input_total_scope'] + baseline['select_total_scope'] + baseline['textarea_total_scope']
    b_tot_raw = baseline['input_total_raw'] + baseline['select_total_raw'] + baseline['textarea_total_raw']
    lines.append(f"Baseline 016 coverage (scope-filtered): {b_cov}/{b_tot_scope} = {pct(b_cov, b_tot_scope)}")
    lines.append(f"(raw total {b_tot_raw}, excluded {b_tot_raw - b_tot_scope} elements in modal/radio/checkbox)")
    lines.append("")

    lines.append("## Full Matrix (scope-filtered)")
    lines.append("")
    lines.append("| # | file | input cov/scope/raw | select cov/scope/raw | textarea cov/scope/raw | form-row | form-field | form-field-inline | Status |")
    lines.append("|---|------|----------------------|-----------------------|-------------------------|----------|------------|-------------------|--------|")

    ok_count = 0
    ng_count = 0
    na_count = 0
    for i, r in enumerate(results, 1):
        total = r["input_total_scope"] + r["select_total_scope"] + r["textarea_total_scope"]
        covered = r["input_covered"] + r["select_covered"] + r["textarea_covered"]
        if total == 0:
            status = "N/A (no scope elements)"
            na_count += 1
        elif covered == total:
            status = "✅ OK (100%)"
            ok_count += 1
        else:
            uncovered = total - covered
            status = f"❌ NG ({covered}/{total} = {pct(covered, total)})"
            ng_count += 1

        is_baseline = " ★BASELINE★" if r["file"] == baseline_file else ""
        lines.append(
            f"| {i} | {r['file']}{is_baseline} "
            f"| {r['input_covered']}/{r['input_total_scope']}/{r['input_total_raw']} "
            f"| {r['select_covered']}/{r['select_total_scope']}/{r['select_total_raw']} "
            f"| {r['textarea_covered']}/{r['textarea_total_scope']}/{r['textarea_total_raw']} "
            f"| {r['form_row_count']} "
            f"| {r['form_field_count']} "
            f"| {r['form_field_inline_count']} "
            f"| {status} |"
        )

    lines.append("")
    lines.append(f"## Summary (grep 実測)")
    lines.append("")
    lines.append(f"- Total files: {len(results)}")
    lines.append(f"- **✅ OK (100% scope coverage)**: {ok_count}")
    lines.append(f"- **❌ NG**: {ng_count}")
    lines.append(f"- N/A (no scope elements): {na_count}")
    lines.append("")

    ng_files = []
    for r in results:
        total = r["input_total_scope"] + r["select_total_scope"] + r["textarea_total_scope"]
        covered = r["input_covered"] + r["select_covered"] + r["textarea_covered"]
        if total > 0 and covered < total:
            ng_files.append((r, total, covered))

    ng_files.sort(key=lambda x: x[2] / x[1] if x[1] > 0 else 1.0)

    lines.append("## NG Files — sorted by coverage (worst first)")
    lines.append("")
    for r, total, covered in ng_files:
        pct_cov = f"{100.0*covered/total:.0f}%"
        severity = "🔴 CRITICAL" if covered == 0 else ("🟠 MAJOR" if covered/total < 0.5 else "🟡 MINOR")
        lines.append(f"- {severity} **{r['file']}**: {covered}/{total} ({pct_cov}) | ff={r['form_field_count']} ffi={r['form_field_inline_count']} form-row={r['form_row_count']}")

    lines.append("")
    lines.append("## OK Files (100% coverage)")
    lines.append("")
    for r in results:
        total = r["input_total_scope"] + r["select_total_scope"] + r["textarea_total_scope"]
        covered = r["input_covered"] + r["select_covered"] + r["textarea_covered"]
        if total > 0 and covered == total:
            lines.append(f"- **{r['file']}**: {total} elements all covered (ff={r['form_field_count']} ffi={r['form_field_inline_count']})")

    lines.append("")
    lines.append("## N/A Files (no scope elements)")
    lines.append("")
    for r in results:
        total = r["input_total_scope"] + r["select_total_scope"] + r["textarea_total_scope"]
        if total == 0:
            lines.append(f"- {r['file']}")

    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"OK: wrote {OUTPUT_MD}", file=sys.stderr)
    print(f"Total: {len(results)}, OK: {ok_count}, NG: {ng_count}, N/A: {na_count}", file=sys.stderr)

if __name__ == "__main__":
    main()
