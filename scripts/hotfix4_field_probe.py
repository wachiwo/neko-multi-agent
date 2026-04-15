#!/usr/bin/env python3
"""hotfix4 field width probe — A/B/C/D overflow 実測.

Long-value ダミーを各 target input に set し、clientWidth/scrollWidth を実測して
overflow 有無と推奨幅を算出。subtask_184_hotfix4_001_w3 の評価 evidence。
"""
from __future__ import annotations
import os, json, sys
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
OUT_MD = Path(
    "/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/"
    "cmd_184_hotfix4_field_width_tuning/width_measurement_4files.md"
)

VIEWPORT = {"width": 1200, "height": 900}

DUMMIES = {
    "supplier_name": "○○商事株式会社東京本店",
    "supplier_content": "パッキング材料詰替用一式",
    "billing_name": "○○商事株式会社東京本店",
    "customer_name": "○○商事株式会社東京本店",
    "stress_test": "日本ディムコプレシジョンテクノロジー株式会社",
}

TARGETS = [
    # (rel_path, label_text, dummy_key, item_id)
    ("new/031_発送一覧.html", "仕入先", "supplier_name", "A_031_supplier"),
    ("new/026_入庫一覧.html", "仕入先名称", "supplier_name", "B_026_supplier_name"),
    ("new/026_入庫一覧.html", "仕入内容", "supplier_content", "B_026_supplier_content"),
    ("new/028_納品書一覧.html", "請求先", "billing_name", "C_028_billing"),
    ("new/029_納品書作成.html", "得意先", "customer_name", "D_029_customer"),
]

JS_MEASURE = r"""
(params) => {
    const { labelText, dummyValue } = params;
    const labels = Array.from(document.querySelectorAll('.form-field > label'));
    const label = labels.find(l => l.textContent.trim() === labelText);
    if (!label) return { error: `label not found: ${labelText}` };
    const ff = label.closest('.form-field');
    const input = ff.querySelector('input[type="text"], input:not([type])');
    if (!input) return { error: `input not found under label: ${labelText}` };

    const before = {
        clientWidth: Math.round(input.clientWidth),
        scrollWidth: Math.round(input.scrollWidth),
        inline_width: input.style.width || null,
        computed_width: getComputedStyle(input).width,
        placeholder: input.placeholder,
        maxlength: input.maxLength,
        wrapper_parent_tag: input.parentElement.tagName.toLowerCase(),
        wrapper_parent_style: input.parentElement.getAttribute('style') || null,
    };
    input.value = dummyValue;
    input.dispatchEvent(new Event('input', {bubbles: true}));
    const after = {
        clientWidth: Math.round(input.clientWidth),
        scrollWidth: Math.round(input.scrollWidth),
        value_length: input.value.length,
        overflow: input.scrollWidth > input.clientWidth,
        overflow_px: input.scrollWidth - input.clientWidth,
    };
    return { before, after, dummy: dummyValue };
}
"""


def measure(context, rel_path, label, dummy):
    page = context.new_page()
    url = f"file://{quote(str(PROJECT_ROOT / rel_path))}"
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(400)
    res = page.evaluate(JS_MEASURE, {"labelText": label, "dummyValue": dummy})
    page.close()
    return res


def main():
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport=VIEWPORT)
        for rel, label, dkey, item in TARGETS:
            dummy = DUMMIES[dkey]
            res = measure(ctx, rel, label, dummy)
            res["rel"] = rel
            res["label"] = label
            res["item"] = item
            rows.append(res)
            # print summary
            if "error" in res:
                print(f"[{item}] {rel}::{label}  ERROR {res['error']}")
            else:
                b, a = res["before"], res["after"]
                flag = "OVERFLOW" if a["overflow"] else "ok"
                print(f"[{item}] {rel}::{label}  clientW={b['clientWidth']}  "
                      f"after value='{dummy}' scrollW={a['scrollWidth']} overflow_px={a['overflow_px']} [{flag}]")
        browser.close()

    # Markdown
    lines = [
        "# hotfix4 field width probe — A/B/C/D overflow measurement",
        "",
        f"viewport: {VIEWPORT['width']}x{VIEWPORT['height']}",
        "dummy values: " + ", ".join(f"`{k}`=\"{v}\"" for k, v in DUMMIES.items()),
        "",
        "| item | file | label | inline_width | clientW (empty) | dummy | scrollW (filled) | overflow_px | verdict |",
        "|---|---|---|---|---:|---|---:|---:|:---:|",
    ]
    for r in rows:
        if "error" in r:
            lines.append(f"| {r['item']} | `{r['rel']}` | {r['label']} | — | — | — | — | — | ❌ {r['error']} |")
            continue
        b, a = r["before"], r["after"]
        v = "⚠ OVERFLOW" if a["overflow"] else "✓ fit"
        lines.append(
            f"| {r['item']} | `{r['rel']}` | {r['label']} | "
            f"`{b['inline_width'] or '—'}` | {b['clientWidth']} | "
            f"`{r['dummy']}` ({a['value_length']}char) | {a['scrollWidth']} | "
            f"{a['overflow_px']} | {v} |"
        )
    lines.append("")
    lines.append("## Raw JSON")
    lines.append("```json")
    lines.append(json.dumps(rows, ensure_ascii=False, indent=2))
    lines.append("```")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nwritten: {OUT_MD}")


if __name__ == "__main__":
    main()
