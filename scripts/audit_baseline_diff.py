#!/usr/bin/env python3
"""cmd_184_audit W1: baseline diff (001 vs all 59 files)
READ-ONLY — no file modification.
Measures form-field coverage ratio for input/select/textarea/label.
"""
import os
import glob
import sys
from bs4 import BeautifulSoup

NEW_DIR = "/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new"
OUTPUT_MD = "/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_184_audit/w1_baseline_diff.md"

def has_form_field_ancestor(el):
    """Check if element has a form-field class ancestor."""
    for parent in el.parents:
        classes = parent.get("class", [])
        if classes and "form-field" in classes:
            return True
    return False

def measure_file(filepath):
    """Return measurements for a single file."""
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        html = f.read()
    soup = BeautifulSoup(html, "html.parser")

    inputs = soup.find_all("input")
    selects = soup.find_all("select")
    textareas = soup.find_all("textarea")
    labels = soup.find_all("label")
    form_fields = soup.select(".form-field")
    form_rows = soup.select(".form-row")

    inputs_in_ff = sum(1 for el in inputs if has_form_field_ancestor(el))
    selects_in_ff = sum(1 for el in selects if has_form_field_ancestor(el))
    textareas_in_ff = sum(1 for el in textareas if has_form_field_ancestor(el))
    labels_in_ff = sum(1 for el in labels if has_form_field_ancestor(el))

    return {
        "file": os.path.basename(filepath),
        "input_total": len(inputs),
        "input_in_ff": inputs_in_ff,
        "select_total": len(selects),
        "select_in_ff": selects_in_ff,
        "textarea_total": len(textareas),
        "textarea_in_ff": textareas_in_ff,
        "label_total": len(labels),
        "label_in_ff": labels_in_ff,
        "form_field_count": len(form_fields),
        "form_row_count": len(form_rows),
    }

def pct(num, den):
    if den == 0:
        return "N/A"
    return f"{100.0 * num / den:.0f}%"

def main():
    files = sorted(glob.glob(os.path.join(NEW_DIR, "*.html")))
    print(f"Found {len(files)} HTML files", file=sys.stderr)

    results = []
    for fp in files:
        try:
            m = measure_file(fp)
            results.append(m)
        except Exception as e:
            print(f"ERROR {fp}: {e}", file=sys.stderr)

    # Write MD
    os.makedirs(os.path.dirname(OUTPUT_MD), exist_ok=True)
    lines = []
    lines.append("# cmd_184_audit W1: baseline diff (form-field 適用率 measurement)")
    lines.append("")
    lines.append("**Scope**: new/ 配下 全 59 HTML files")
    lines.append("**Baseline**: 001_個人営業管理.html (canonical 完成見本)")
    lines.append("**Method**: BeautifulSoup DOM 解析、form-field ancestor 判定")
    lines.append("**Source tag**: Python BeautifulSoup + soup.find_all / has_form_field_ancestor")
    lines.append("**Timestamp**: 2026-04-16T13:57 (audit run)")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| # | File | input (ff/total) | select (ff/total) | textarea (ff/total) | label (ff/total) | form-row | form-field | Under 100% Flags |")
    lines.append("|---|------|------------------|-------------------|---------------------|------------------|----------|------------|------------------|")

    for i, r in enumerate(results, 1):
        flags = []
        def check(name, a, b):
            if b > 0 and a < b:
                flags.append(f"{name}:{pct(a,b)}")
        check("input", r["input_in_ff"], r["input_total"])
        check("select", r["select_in_ff"], r["select_total"])
        check("textarea", r["textarea_in_ff"], r["textarea_total"])
        check("label", r["label_in_ff"], r["label_total"])
        flag_str = ", ".join(flags) if flags else "-"
        lines.append(
            f"| {i} | {r['file']} "
            f"| {r['input_in_ff']}/{r['input_total']} ({pct(r['input_in_ff'], r['input_total'])}) "
            f"| {r['select_in_ff']}/{r['select_total']} ({pct(r['select_in_ff'], r['select_total'])}) "
            f"| {r['textarea_in_ff']}/{r['textarea_total']} ({pct(r['textarea_in_ff'], r['textarea_total'])}) "
            f"| {r['label_in_ff']}/{r['label_total']} ({pct(r['label_in_ff'], r['label_total'])}) "
            f"| {r['form_row_count']} "
            f"| {r['form_field_count']} "
            f"| {flag_str} |"
        )

    lines.append("")
    lines.append("## Method (grep 実測 + BeautifulSoup)")
    lines.append("")
    lines.append("```python")
    lines.append("# soup = BeautifulSoup(open(file).read(), 'html.parser')")
    lines.append("# input_total = len(soup.find_all('input'))")
    lines.append("# input_in_ff = sum(1 for el in soup.find_all('input') if has_form_field_ancestor(el))")
    lines.append("# has_form_field_ancestor: walks el.parents, checks 'form-field' in parent.get('class', [])")
    lines.append("```")
    lines.append("")
    lines.append("## Under-100% Summary (form-field 配下率が 100% 未満の file)")
    lines.append("")

    under_100 = []
    for r in results:
        issues = []
        for name, a, b in [
            ("input", r["input_in_ff"], r["input_total"]),
            ("select", r["select_in_ff"], r["select_total"]),
            ("textarea", r["textarea_in_ff"], r["textarea_total"]),
            ("label", r["label_in_ff"], r["label_total"]),
        ]:
            if b > 0 and a < b:
                issues.append(f"{name}: {a}/{b} ({pct(a,b)})")
        if issues:
            under_100.append((r["file"], issues))

    lines.append(f"**Under-100% file count: {len(under_100)} / {len(results)}**")
    lines.append("")
    for fn, issues in under_100:
        lines.append(f"- **{fn}**: " + ", ".join(issues))

    lines.append("")
    lines.append("## Fully-Canonical Files (100% form-field coverage)")
    lines.append("")
    fully_ok = [r["file"] for r in results if (r["file"], []) not in [(f,i) for f,i in under_100] and not any(
        (b > 0 and a < b) for name, a, b in [
            ("input", r["input_in_ff"], r["input_total"]),
            ("select", r["select_in_ff"], r["select_total"]),
            ("textarea", r["textarea_in_ff"], r["textarea_total"]),
            ("label", r["label_in_ff"], r["label_total"]),
        ]
    )]
    lines.append(f"**Fully-canonical count: {len(fully_ok)} / {len(results)}**")
    lines.append("")
    for fn in fully_ok:
        lines.append(f"- {fn}")

    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"OK: wrote {OUTPUT_MD}", file=sys.stderr)
    print(f"Total files: {len(results)}", file=sys.stderr)
    print(f"Under-100%: {len(under_100)}", file=sys.stderr)
    print(f"Fully-canonical: {len(fully_ok)}", file=sys.stderr)

if __name__ == "__main__":
    main()
