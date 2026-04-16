#!/usr/bin/env python3
"""
cmd_184_audit: Playwright 視覚縦並び実測 (W2 担当)
- 全 form-field 内の label + input/select/textarea の bounding box 取得
- label.bottom <= input.top → 縦並び (canonical 達成)
- label.right <= input.left → 横並び (未達)
- 重なり → unknown

READ-ONLY、推定禁止 (bounding box 実測のみ)
"""
import asyncio
import json
import sys
from pathlib import Path
from playwright.async_api import async_playwright

NEW_DIR = Path("/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new")
OUT_DIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_184_audit")
JSON_DIR = OUT_DIR / "json_w2"
SHOT_DIR = OUT_DIR / "screenshots_w2"
VIEWPORT_W = 1200
VIEWPORT_H = 900
TOLERANCE_PX = 2  # label.bottom <= input.top + 2px tolerance


async def audit_file(page, html_path: Path):
    """Render single file, measure all .form-field label+input bounding boxes."""
    file_url = f"file://{html_path}"
    try:
        await page.goto(file_url, wait_until="domcontentloaded", timeout=15000)
        await page.wait_for_timeout(500)  # let layout settle
    except Exception as e:
        return {"file": html_path.name, "error": str(e), "form_fields": []}

    # Get bounding boxes for all .form-field elements
    measurements = await page.evaluate("""
() => {
    const results = [];
    const fields = document.querySelectorAll('.form-field');
    fields.forEach((field, idx) => {
        const label = field.querySelector('label');
        const input = field.querySelector('input, select, textarea');
        if (!label || !input) {
            results.push({idx, has_label: !!label, has_input: !!input, skipped: true});
            return;
        }
        const lr = label.getBoundingClientRect();
        const ir = input.getBoundingClientRect();
        // skip hidden elements (size 0)
        if (lr.width === 0 || lr.height === 0 || ir.width === 0 || ir.height === 0) {
            results.push({idx, hidden: true});
            return;
        }
        results.push({
            idx,
            label: {top: lr.top, left: lr.left, right: lr.right, bottom: lr.bottom, w: lr.width, h: lr.height},
            input: {top: ir.top, left: ir.left, right: ir.right, bottom: ir.bottom, w: ir.width, h: ir.height},
            input_tag: input.tagName.toLowerCase()
        });
    });
    return results;
}
""")

    # Classify each form-field
    vertical = 0
    horizontal = 0
    unknown = 0
    skipped = 0
    details = []
    for m in measurements:
        if m.get("skipped") or m.get("hidden"):
            skipped += 1
            details.append({**m, "verdict": "skipped"})
            continue
        l, i = m["label"], m["input"]
        # Vertical: label sits above input (label.bottom <= input.top + tolerance)
        # Horizontal: label sits left of input (label.right <= input.left + tolerance) AND not vertical
        if l["bottom"] <= i["top"] + TOLERANCE_PX:
            vertical += 1
            verdict = "vertical"
        elif l["right"] <= i["left"] + TOLERANCE_PX:
            horizontal += 1
            verdict = "horizontal"
        else:
            unknown += 1
            verdict = "unknown"
        details.append({**m, "verdict": verdict})

    total = vertical + horizontal + unknown
    apply_rate = round(100.0 * vertical / total, 1) if total > 0 else None

    # Take screenshot
    shot_path = SHOT_DIR / f"{html_path.stem}.png"
    try:
        await page.screenshot(path=str(shot_path), full_page=False)
    except Exception:
        pass

    return {
        "file": html_path.name,
        "viewport": {"w": VIEWPORT_W, "h": VIEWPORT_H},
        "total_form_fields": len(measurements),
        "vertical": vertical,
        "horizontal": horizontal,
        "unknown": unknown,
        "skipped": skipped,
        "vertical_apply_rate_pct": apply_rate,
        "screenshot": str(shot_path),
        "details": details,
    }


async def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    JSON_DIR.mkdir(parents=True, exist_ok=True)
    SHOT_DIR.mkdir(parents=True, exist_ok=True)

    files = sorted(NEW_DIR.glob("*.html"))
    print(f"Auditing {len(files)} files at viewport {VIEWPORT_W}x{VIEWPORT_H}")

    summaries = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport={"width": VIEWPORT_W, "height": VIEWPORT_H})
        page = await ctx.new_page()

        for i, f in enumerate(files, 1):
            print(f"  [{i}/{len(files)}] {f.name}", flush=True)
            res = await audit_file(page, f)
            # Save per-file JSON
            jpath = JSON_DIR / f"{f.stem}.json"
            with jpath.open("w", encoding="utf-8") as fp:
                json.dump(res, fp, ensure_ascii=False, indent=2)
            res["json_path"] = str(jpath)
            summaries.append(res)

        await browser.close()

    # Write aggregated JSON
    agg_path = OUT_DIR / "w2_visual_audit_summary.json"
    with agg_path.open("w", encoding="utf-8") as fp:
        json.dump(summaries, fp, ensure_ascii=False, indent=2)
    print(f"\nWrote {agg_path}")
    return summaries


if __name__ == "__main__":
    asyncio.run(main())
