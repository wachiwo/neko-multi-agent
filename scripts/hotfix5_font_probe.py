#!/usr/bin/env python3
"""hotfix5 precision audit — computed font-size dump 5 files × critical elements.

subtask_184_hotfix5_004_w3: 前回 grep base『一致』判定を computed 実測で裏取り、
ご主人様目視『032 だけ文字サイズ大きい』の真相特定。
"""
from __future__ import annotations
import os, json
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
    "cmd_184_hotfix5_typography_unify/font_size_precision_audit_032_vs_others.md"
)
VIEWPORT = {"width": 1200, "height": 900}

FILES = [
    "new/032_在庫一覧.html",
    "new/026_入庫一覧.html",
    "new/028_納品書一覧.html",
    "new/029_納品書作成.html",
    "new/031_発送一覧.html",
]

# 'selector: description'
SELECTORS = [
    ("body", "root / body"),
    ("h1", "main h1"),
    (".page-header h1", "page-header h1"),
    (".sidebar-header h1", "sidebar header h1"),
    (".menu-item", "sidebar menu-item"),
    (".form-field > label", "form-field label (first)"),
    (".form-field input[type='text']", "form-field text input (first)"),
    (".form-field select", "form-field select (first)"),
    (".data-table th", "data-table th (first)"),
    (".data-table td", "data-table td (first)"),
    ("button.btn, button.search-btn, button.action-btn", "button (first)"),
    ("input[placeholder='連番'], input[placeholder='明細番号']", "商伝番号/明細番号 input"),
]


JS_MEASURE = r"""
(selectors) => {
    const results = {};
    results['__html_font_size'] = getComputedStyle(document.documentElement).fontSize;
    results['__body_font_size_computed'] = getComputedStyle(document.body).fontSize;
    results['__body_font_family'] = getComputedStyle(document.body).fontFamily;
    for (const [sel, desc] of selectors) {
        const el = document.querySelector(sel);
        if (!el) { results[sel] = { desc, found: false }; continue; }
        const cs = getComputedStyle(el);
        const rect = el.getBoundingClientRect();
        results[sel] = {
            desc,
            found: true,
            font_size: cs.fontSize,
            line_height: cs.lineHeight,
            font_weight: cs.fontWeight,
            bounding_h: Math.round(rect.height),
            tag: el.tagName.toLowerCase(),
        };
    }
    return results;
}
"""


def measure_file(context, rel_path):
    page = context.new_page()
    url = f"file://{quote(str(PROJECT_ROOT / rel_path))}"
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(400)
    res = page.evaluate(JS_MEASURE, SELECTORS)
    page.close()
    return res


def main():
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    all_results = {}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport=VIEWPORT)
        for rel in FILES:
            try:
                all_results[rel] = measure_file(ctx, rel)
            except Exception as e:
                all_results[rel] = {"error": str(e)}
        browser.close()

    # Summary table
    lines = [
        "# hotfix5 precision audit — computed font-size dump",
        "",
        f"viewport: {VIEWPORT['width']}x{VIEWPORT['height']}",
        "",
        "## Root / body baseline",
        "",
        "| file | html fontSize | body fontSize | body fontFamily (head) |",
        "|---|---|---|---|",
    ]
    for rel in FILES:
        r = all_results[rel]
        if "error" in r:
            lines.append(f"| `{rel}` | — | — | ERROR {r['error']} |")
            continue
        ff = r.get('__body_font_family', '')
        ff_head = (ff[:60] + '...') if len(ff) > 60 else ff
        lines.append(f"| `{rel}` | {r.get('__html_font_size')} | {r.get('__body_font_size_computed')} | `{ff_head}` |")

    lines.append("")
    lines.append("## Critical elements font-size computed (per file)")
    lines.append("")

    # Build per-selector comparison table
    for sel, desc in SELECTORS:
        lines.append(f"### `{sel}` — {desc}")
        lines.append("")
        lines.append("| file | found | fontSize | lineHeight | fontWeight | bounding_h |")
        lines.append("|---|---|---|---|---|---|")
        values_032 = None
        ref_values = []
        for rel in FILES:
            r = all_results[rel]
            if "error" in r:
                lines.append(f"| `{rel}` | — | — | — | — | ERROR |")
                continue
            info = r.get(sel, {"found": False, "desc": desc})
            if not info.get("found"):
                lines.append(f"| `{rel}` | ❌ | — | — | — | — |")
                continue
            lines.append(f"| `{rel}` | ✓ ({info['tag']}) | **{info['font_size']}** | {info['line_height']} | {info['font_weight']} | {info['bounding_h']}px |")
            if "032_在庫一覧" in rel:
                values_032 = info
            else:
                ref_values.append((rel, info))
        # Delta summary
        if values_032 and ref_values:
            try:
                v032 = float(values_032['font_size'].replace('px', ''))
                refs_px = []
                for rel, info in ref_values:
                    refs_px.append(float(info['font_size'].replace('px', '')))
                if refs_px:
                    maj = max(set(refs_px), key=refs_px.count)  # mode
                    delta = v032 - maj
                    visible = "★VISIBLE (≥1px)" if abs(delta) >= 1 else "within-1px"
                    lines.append(f"- **Δ vs majority**: 032={v032}px majority={maj}px delta={delta:+.2f}px {visible}")
            except Exception:
                pass
        lines.append("")

    lines.append("## Raw JSON")
    lines.append("```json")
    lines.append(json.dumps(all_results, ensure_ascii=False, indent=2))
    lines.append("```")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"written: {OUT_MD}")

    # Console summary
    print("\n=== FONT-SIZE COMPARISON SUMMARY ===")
    for sel, desc in SELECTORS:
        row = [sel[:30], desc[:20]]
        for rel in FILES:
            r = all_results[rel]
            if "error" in r:
                row.append("ERR")
                continue
            info = r.get(sel, {"found": False})
            if info.get("found"):
                row.append(info['font_size'].replace('px', ''))
            else:
                row.append("—")
        print("  " + " | ".join(f"{s:>8}" if i >= 2 else f"{s:<32}" for i, s in enumerate(row)))


if __name__ == "__main__":
    main()
