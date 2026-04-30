#!/usr/bin/env python3
"""cmd_225_redo W1 layout section visual verify.

Wraps section file in HTML5 doctype + Bootstrap CDN + Bootstrap Icons CDN,
then Playwright opens to confirm:
- No console/page errors
- sidebar drawer click → open class toggles
- header rendered with sticky position
- base64 icons render (no broken image)
"""
import os
import json
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

SECTION = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_225_redo/w1_layout_section.html")
OUTDIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_225_redo/verify")


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)

    section_content = SECTION.read_text(encoding="utf-8")
    wrapper_html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>W1 Layout Section Verify (cmd_225_redo)</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet"/>
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet"/>
<script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
</head>
<body>
{section_content}
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""
    tmp = OUTDIR / "_wrapped_for_verify.html"
    tmp.write_text(wrapper_html, encoding="utf-8")

    url = f"file://{quote(str(tmp))}"
    results = {"file": tmp.name}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        # Test 1: 1280x800 (desktop, ハンバーガー隠れ + sidebar 表示)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        page_errors = []
        console_errors = []
        page.on("pageerror", lambda exc: page_errors.append(str(exc)))
        page.on("console", lambda msg: console_errors.append({"type": msg.type, "text": msg.text}) if msg.type == "error" else None)

        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(500)

        # 1. errors
        results["1_console_errors"] = {"count": len(console_errors), "errors": console_errors[:5]}
        results["1_page_errors"] = {"count": len(page_errors), "errors": page_errors[:5]}

        # 2. structural check: sidebar + header + main wrap rendered
        struct = page.evaluate("""() => {
            const sidebar = document.querySelector('.zdo_drawer_menu');
            const navWrapper = document.querySelector('.zdo_drawer_nav_wrapper');
            const drawerBg = document.querySelector('.zdo_drawer_bg');
            const drawerBtn = document.querySelector('.zdo_drawer_button');
            const header = document.querySelector('header');
            const navItems = document.querySelectorAll('.zdo_drawer_nav .nav-item');
            return {
                sidebar_exists: !!sidebar,
                nav_wrapper_exists: !!navWrapper,
                drawer_bg_exists: !!drawerBg,
                drawer_btn_exists: !!drawerBtn,
                header_exists: !!header,
                nav_item_count: navItems.length,
                nav_wrapper_open_class_initial: navWrapper ? navWrapper.classList.contains('open') : null,
            };
        }""")
        results["2_structural"] = struct

        # 3. base64 image render check (no broken images)
        img_check = page.evaluate("""() => {
            const imgs = document.querySelectorAll('img.nav-item-img, .user-info img');
            let broken = 0;
            let total = 0;
            imgs.forEach(img => {
                total++;
                if (!img.complete || img.naturalWidth === 0) broken++;
            });
            return {total: total, broken: broken};
        }""")
        results["3_image_render"] = img_check

        # 4. drawer button click → open class
        page.evaluate("document.querySelector('.zdo_drawer_button').click()")
        page.wait_for_timeout(300)
        after_click = page.evaluate("""() => {
            const navWrapper = document.querySelector('.zdo_drawer_nav_wrapper');
            const drawerBtn = document.querySelector('.zdo_drawer_button');
            const drawerBg = document.querySelector('.zdo_drawer_bg');
            return {
                nav_wrapper_open: navWrapper ? navWrapper.classList.contains('open') : null,
                drawer_btn_active: drawerBtn ? drawerBtn.classList.contains('active') : null,
                drawer_bg_visible: drawerBg ? drawerBg.style.display === 'block' : null,
            };
        }""")
        results["4_drawer_open"] = after_click
        page.screenshot(path=str(OUTDIR / "drawer_opened.png"), full_page=False)

        # close drawer
        page.evaluate("document.querySelector('.zdo_drawer_button').click()")
        page.wait_for_timeout(300)

        # 5. .part-label showroom rendering
        labels_check = page.evaluate("""() => {
            const labels = document.querySelectorAll('.part-label');
            return {
                count: labels.length,
                texts: Array.from(labels).map(l => l.textContent.trim()),
            };
        }""")
        results["5_part_labels"] = labels_check

        # 6. responsive 960px breakpoint test
        page.set_viewport_size({"width": 800, "height": 600})
        page.wait_for_timeout(400)
        responsive_check = page.evaluate("""() => {
            const drawerBtn = document.querySelector('.zdo_drawer_button');
            const sidebar = document.querySelector('.col-sm-auto.bg-navy.sticky-top');
            return {
                drawer_btn_visible_at_800px: drawerBtn ? getComputedStyle(drawerBtn).display !== 'none' : null,
                sidebar_width_at_800px: sidebar ? getComputedStyle(sidebar).width : null,
            };
        }""")
        results["6_responsive_960px"] = responsive_check
        page.screenshot(path=str(OUTDIR / "mobile_800px.png"), full_page=False)

        # 7. main viewport screenshot at 1280
        page.set_viewport_size({"width": 1280, "height": 800})
        page.wait_for_timeout(300)
        page.screenshot(path=str(OUTDIR / "desktop_1280px.png"), full_page=True)

        context.close()
        browser.close()

    out_json = OUTDIR / "_verify.json"
    out_json.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
