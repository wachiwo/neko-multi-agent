#!/usr/bin/env python3
"""Generate markdown report from w2_visual_audit_summary.json"""
import json
from pathlib import Path
from datetime import datetime

OUT_DIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_184_audit")
SUMMARY_JSON = OUT_DIR / "w2_visual_audit_summary.json"
MD_OUT = OUT_DIR / "w2_visual_audit.md"

# 13 files reportedly flagged by 親分 (oyabun) — placeholder, will mark in table
OYABUN_13_LIST = []  # If kashira provides list, fill here. Otherwise mark all <100% as flag

with SUMMARY_JSON.open() as fp:
    summaries = json.load(fp)

# Aggregate
total_files = len(summaries)
files_100 = sum(1 for s in summaries if s.get("vertical_apply_rate_pct") == 100.0)
files_no_form = sum(1 for s in summaries if s.get("total_form_fields", 0) == 0)
files_with_horizontal = sum(1 for s in summaries if (s.get("horizontal", 0) > 0))
files_with_unknown = sum(1 for s in summaries if (s.get("unknown", 0) > 0))
files_below_100 = sum(1 for s in summaries
                      if s.get("vertical_apply_rate_pct") is not None
                      and s.get("vertical_apply_rate_pct") < 100.0)

lines = []
lines.append("# cmd_184 audit — W2 視覚縦並び実測 (Playwright bounding box)")
lines.append("")
lines.append(f"- 生成日時: {datetime.now().isoformat()}")
lines.append(f"- viewport: 1200x900 (固定)")
lines.append(f"- 判定方式: label.bottom <= input.top + 2px → 縦並び (canonical 達成)")
lines.append(f"- 判定方式: label.right <= input.left + 2px → 横並び (canonical 未達)")
lines.append(f"- 判定方式: 上記いずれも該当せず → unknown (重なり等)")
lines.append(f"- ★READ-ONLY、推定禁止、bounding box 実測のみ★")
lines.append("")
lines.append("## 集計")
lines.append("")
lines.append(f"| 項目 | 数 |")
lines.append(f"|------|----|")
lines.append(f"| 総ファイル数 | {total_files} |")
lines.append(f"| form-field なし (測定対象外) | {files_no_form} |")
lines.append(f"| 視覚適用率 100% (canonical 達成) | {files_100} |")
lines.append(f"| 視覚適用率 < 100% | {files_below_100} |")
lines.append(f"| 横並び含む file | {files_with_horizontal} |")
lines.append(f"| unknown 含む file | {files_with_unknown} |")
lines.append("")
lines.append("## file 別詳細 (sorted by file name)")
lines.append("")
lines.append("| file | 全 form-field | 縦 | 横 | unknown | skipped | 視覚適用率% | flag | screenshot |")
lines.append("|------|---------------|-----|-----|---------|---------|-------------|------|------------|")

for s in summaries:
    name = s["file"]
    if s.get("error"):
        lines.append(f"| {name} | ERROR | - | - | - | - | - | ★error★ | - |")
        continue
    total = s.get("total_form_fields", 0)
    v = s.get("vertical", 0)
    h = s.get("horizontal", 0)
    u = s.get("unknown", 0)
    sk = s.get("skipped", 0)
    rate = s.get("vertical_apply_rate_pct")
    rate_str = f"{rate}%" if rate is not None else "N/A"
    # flags
    flag = ""
    if rate is None and total == 0:
        flag = "no form-field"
    elif h > 0:
        flag = "★横並び★"
    elif u > 0:
        flag = "unknown"
    elif rate == 100.0:
        flag = "✅ canonical"
    shot = Path(s.get("screenshot", "")).name if s.get("screenshot") else "-"
    lines.append(f"| {name} | {total} | {v} | {h} | {u} | {sk} | {rate_str} | {flag} | {shot} |")

lines.append("")
lines.append("## ★視覚未達 file リスト (横並び/unknown あり、または rate < 100%)★")
lines.append("")
problem_files = [s for s in summaries if (s.get("horizontal", 0) > 0 or s.get("unknown", 0) > 0)]
if not problem_files:
    lines.append("**問題 file ゼロ — 全 file 縦並び canonical 視覚達成にゃわん！**")
else:
    lines.append("| file | 縦 | 横 | unknown | rate% | source JSON |")
    lines.append("|------|-----|-----|---------|-------|-------------|")
    for s in problem_files:
        jp = Path(s.get("json_path", "")).name
        rate = s.get("vertical_apply_rate_pct")
        rate_str = f"{rate}%" if rate is not None else "N/A"
        lines.append(f"| {s['file']} | {s.get('vertical',0)} | {s.get('horizontal',0)} | {s.get('unknown',0)} | {rate_str} | {jp} |")

lines.append("")
lines.append("## source 一次データ")
lines.append("")
lines.append(f"- 集計 JSON: `{SUMMARY_JSON.relative_to(Path('/mnt/c/tools/neko-multi-agent'))}`")
lines.append(f"- file 別 JSON: `outputs/dimco-prototype/cmd_184_audit/json_w2/<file>.json`")
lines.append(f"- screenshot: `outputs/dimco-prototype/cmd_184_audit/screenshots_w2/<file>.png`")
lines.append("")
lines.append("各 file 別 JSON の `details[]` 配列に label/input bounding box (top/left/right/bottom/w/h) 全件記録。")
lines.append("verdict は実測値からの機械判定 — 推定ゼロ。")

with MD_OUT.open("w", encoding="utf-8") as fp:
    fp.write("\n".join(lines))

print(f"Wrote {MD_OUT}")
print(f"\n--- summary ---")
print(f"total: {total_files}")
print(f"canonical 100%: {files_100}")
print(f"problem (horizontal/unknown): {len(problem_files)}")
