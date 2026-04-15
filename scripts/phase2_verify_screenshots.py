#!/usr/bin/env python3
"""Phase2 verify: 7 files x 3 viewports screenshots + console-error capture.

subtask_184_hotfix_horizontal_004_w4: Playwright で 21枚スクショ + console error を取得。
"""
from __future__ import annotations

import json
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
DEFAULT_OUTPUT = "/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_184_hotfix_horizontal_stays/phase2_verify"
OUTPUT_DIR = Path(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUTPUT)

DEFAULT_TARGETS = [
    "new/025_入庫.html",
    "new/026_入庫一覧.html",
    "new/027_納期回答一覧.html",
    "new/028_納品書一覧.html",
    "new/029_納品書作成.html",
    "new/031_発送一覧.html",
    "new/032_在庫一覧.html",
]
# arg 2+ override targets (comma-separated relative paths OR repeated args)
if len(sys.argv) > 2:
    raw = ",".join(sys.argv[2:])
    TARGETS = [t.strip() for t in raw.split(",") if t.strip()]
else:
    TARGETS = DEFAULT_TARGETS

VIEWPORTS = [
    (1200, "100pct"),
    (800, "150pct"),
    (600, "200pct"),
]


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for rel in TARGETS:
            abs_path = PROJECT_ROOT / rel
            if not abs_path.exists():
                print(f"SKIP missing: {abs_path}", file=sys.stderr)
                continue
            file_url = "file://" + quote(str(abs_path), safe="/:")
            stem = abs_path.stem

            for vw, label in VIEWPORTS:
                context = browser.new_context(viewport={"width": vw, "height": 900})
                page = context.new_page()
                errs = []
                page.on("console", lambda msg, e=errs: e.append({"type": msg.type, "text": msg.text}) if msg.type == "error" else None)
                page.on("pageerror", lambda exc, e=errs: e.append({"type": "pageerror", "text": str(exc)}))

                page.goto(file_url, wait_until="networkidle", timeout=30000)
                page.wait_for_timeout(300)

                out_png = OUTPUT_DIR / f"{stem}_{vw}w_{label}.png"
                page.screenshot(path=str(out_png), full_page=True)

                # measure overflow (sidebar false-positive filter: exclude buttons with left < 0)
                overflow_info = page.evaluate(
                    """(vw) => {
                        const docOverflow = document.documentElement.scrollWidth > vw;
                        const violators = [];
                        const selectors = ['input','button','label','.form-field','.table-wrapper','table'];
                        for (const sel of selectors) {
                            const els = document.querySelectorAll(sel);
                            for (const el of els) {
                                const r = el.getBoundingClientRect();
                                if (r.right > vw + 1 || r.left < -1) {
                                    // false-positive filter: off-canvas sidebar buttons with left<-200
                                    if (el.tagName === 'BUTTON' && r.left <= -200) continue;
                                    violators.push({sel, left: Math.round(r.left), right: Math.round(r.right), tag: el.tagName, text: (el.textContent||'').trim().slice(0,30)});
                                    if (violators.length >= 30) break;
                                }
                            }
                            if (violators.length >= 30) break;
                        }
                        return {docOverflow, scrollWidth: document.documentElement.scrollWidth, violators};
                    }""",
                    vw,
                )

                results.append({
                    "file": rel,
                    "viewport": vw,
                    "zoom_label": label,
                    "screenshot": str(out_png.relative_to(OUTPUT_DIR.parent.parent.parent)),
                    "console_errors": errs,
                    "doc_overflow": overflow_info["docOverflow"],
                    "scroll_width": overflow_info["scrollWidth"],
                    "overflow_violators": overflow_info["violators"],
                })
                context.close()
                print(f"OK {stem} @ {vw}w ({label}) errs={len(errs)} overflow={overflow_info['docOverflow']} viol={len(overflow_info['violators'])}")
        browser.close()

    summary = OUTPUT_DIR / "screenshot_summary.json"
    summary.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"\nSummary: {summary}")
    print(f"Total screenshots: {len(results)}")


if __name__ == "__main__":
    main()
