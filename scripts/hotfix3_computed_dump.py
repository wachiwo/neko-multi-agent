#!/usr/bin/env python3
"""hotfix3 computed style dump — 026 種類/STS input 縦長再発調査.

subtask_184_hotfix3_001_w3: 026 と 031 と 基準_縦 で同等 form-field の computed style を
実測し、3列比較 markdown を outputs/ に出力。static grep で立てた仮説
(grid stretch + flex:1 による縦伸び) を裏取りする目的。
"""
from __future__ import annotations

import os
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

PROJECT_ROOT = Path("/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype")
OUTPUT_MD = Path(
    "/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/"
    "cmd_184_hotfix3_input_height_regression/computed_dump_026_vs_031_vs_基準.md"
)

VIEWPORT = {"width": 1200, "height": 900}

FORM_FIELD_PROPS = [
    "display", "flex-direction", "align-items", "align-self",
    "flex-grow", "flex-shrink", "flex-basis",
    "width", "height", "min-height", "max-height",
    "gap",
]
INNER_PROPS = [
    "display", "flex-grow", "flex-shrink", "flex-basis",
    "width", "height", "min-height", "max-height",
    "align-self", "line-height", "padding", "box-sizing",
]


JS_MEASURE = r"""
(params) => {
    const { labelText, innerTag, ffProps, innerProps } = params;
    const labels = Array.from(document.querySelectorAll('.form-field > label'));
    const label = labels.find(l => l.textContent.trim() === labelText);
    if (!label) return { error: `label not found: ${labelText}` };
    const ff = label.closest('.form-field');
    if (!ff) return { error: `form-field not found for: ${labelText}` };
    const inner = ff.querySelector(innerTag);
    const get = (el, props) => {
        const cs = getComputedStyle(el);
        const rect = el.getBoundingClientRect();
        const o = { rect_h: Math.round(rect.height), rect_w: Math.round(rect.width) };
        for (const p of props) o[p] = cs.getPropertyValue(p);
        return o;
    };
    return {
        form_field: get(ff, ffProps),
        inner: inner ? get(inner, innerProps) : null,
        inner_tag: inner ? inner.tagName.toLowerCase() : null,
        row_height: Math.round(ff.parentElement.getBoundingClientRect().height),
    };
}
"""


def dump_field(page, label_text, inner_tag):
    return page.evaluate(
        JS_MEASURE,
        {
            "labelText": label_text,
            "innerTag": inner_tag,
            "ffProps": FORM_FIELD_PROPS,
            "innerProps": INNER_PROPS,
        },
    )


def open_and_measure(context, rel_path, fields):
    page = context.new_page()
    abs_path = PROJECT_ROOT / rel_path
    url = f"file://{quote(str(abs_path))}"
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(500)
    results = {}
    for label_text, inner_tag in fields:
        try:
            results[label_text] = dump_field(page, label_text, inner_tag)
        except Exception as e:
            results[label_text] = {"error": str(e)}
    page.close()
    return results


def main():
    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport=VIEWPORT)

        files_and_fields = [
            ("new/026_入庫一覧.html", [
                ("種類", "select"),
                ("STS", "select"),
                ("明細番号", "input"),
                ("営業担当者", "select"),
            ]),
            ("new/031_発送一覧.html", [
                ("営業担当者", "select"),
                ("商伝作成者", "select"),
            ]),
            ("基準テンプレ/基準_縦.html", [
                # 基準_縦 は data 不明、select のある form-field を探す
            ]),
        ]

        all_dumps = {}
        for rel, fields in files_and_fields:
            if not fields:
                # 基準_縦: label テキストで存在するもの1-2個だけ拾う (不明なので skip 可)
                continue
            all_dumps[rel] = open_and_measure(context, rel, fields)

        browser.close()

    # Markdown 出力
    lines = [
        "# 026 input 縦長再発 — computed style dump 3列比較",
        "",
        f"viewport: {VIEWPORT['width']}x{VIEWPORT['height']}",
        "",
    ]

    for rel, field_results in all_dumps.items():
        lines.append(f"## {rel}")
        lines.append("")
        for label, data in field_results.items():
            lines.append(f"### {label}")
            if "error" in data:
                lines.append(f"  - ERROR: {data['error']}")
                lines.append("")
                continue
            lines.append(f"- row (parent .form-row) height: {data['row_height']} px")
            lines.append("")
            lines.append("#### .form-field (outer div)")
            ff = data["form_field"]
            lines.append(f"- rect: {ff['rect_w']} x {ff['rect_h']} px")
            for p in FORM_FIELD_PROPS:
                lines.append(f"  - {p}: `{ff.get(p, '')}`")
            lines.append("")
            if data["inner"]:
                lines.append(f"#### inner <{data['inner_tag']}> (first input/select)")
                inner = data["inner"]
                lines.append(f"- rect: {inner['rect_w']} x {inner['rect_h']} px")
                for p in INNER_PROPS:
                    lines.append(f"  - {p}: `{inner.get(p, '')}`")
                lines.append("")

    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"written: {OUTPUT_MD}")
    # Also print summary to stdout
    for rel, field_results in all_dumps.items():
        print(f"\n== {rel} ==")
        for label, data in field_results.items():
            if "error" in data:
                print(f"  {label}: ERROR {data['error']}")
            else:
                ff_h = data["form_field"]["rect_h"]
                inner_h = data["inner"]["rect_h"] if data["inner"] else "-"
                row_h = data["row_height"]
                print(f"  {label}: row_h={row_h} form-field_h={ff_h} inner_h={inner_h}")


if __name__ == "__main__":
    main()
