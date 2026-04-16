#!/usr/bin/env python3
"""cmd_186 Phase 2 W2: re-audit 7 files after changes"""
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

NEW_DIR = Path("/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new")
OUT_DIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_186_phase2_vertical")
FILES = ["014_見積一覧","020_未発注一覧","022_作業予定表","023_出荷","025_入庫","027_納期回答一覧","028_納品書一覧"]

async def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await (await browser.new_context(viewport={"width":1200,"height":900})).new_page()
        results = []
        for n in FILES:
            html = NEW_DIR / f"{n}.html"
            await page.goto(f"file://{html}", wait_until="domcontentloaded", timeout=15000)
            await page.wait_for_timeout(400)
            m = await page.evaluate("""
() => {
    const out = [];
    const fields = document.querySelectorAll('.form-field');
    fields.forEach(f => {
        const l = f.querySelector('label');
        const i = f.querySelector('input, select, textarea');
        if (!l || !i) { out.push({skip: true}); return; }
        const lr = l.getBoundingClientRect();
        const ir = i.getBoundingClientRect();
        if (lr.width === 0 || ir.width === 0) { out.push({hidden: true}); return; }
        out.push({label: {top:lr.top, left:lr.left, right:lr.right, bottom:lr.bottom},
                  input: {top:ir.top, left:ir.left, right:ir.right, bottom:ir.bottom}});
    });
    return out;
}""")
            v = h = u = sk = 0
            for x in m:
                if x.get("skip") or x.get("hidden"): sk += 1; continue
                lb, ib = x["label"], x["input"]
                if lb["bottom"] <= ib["top"] + 2: v += 1
                elif lb["right"] <= ib["left"] + 2: h += 1
                else: u += 1
            tot = v + h + u
            rate = round(100.0*v/tot, 1) if tot > 0 else None
            results.append({"file": f"{n}.html", "form_fields": len(m), "vertical": v, "horizontal": h, "unknown": u, "skipped": sk, "rate": rate})
            print(f"  {n}: ff={len(m)} v={v} h={h} u={u} sk={sk} rate={rate}%")
        await browser.close()
    with (OUT_DIR / "audit_post_phase2.json").open("w") as fp:
        json.dump(results, fp, ensure_ascii=False, indent=2)

asyncio.run(main())
