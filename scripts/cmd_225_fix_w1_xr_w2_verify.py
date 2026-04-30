#!/usr/bin/env python3
"""cmd_225_fix W1 reviews W2 modals: section-modal area showroom + 5 modal × 3 step.

Checks:
- section-modal area visible text: source code 0, line ref 0, drift 警告 0 (商品ショールーム型 核心)
- 5 modal × 3 step (open/select/confirm bind) functional verify
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

TARGET = Path("/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new/dimco-parts-catalog.html")
OUTDIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_225_fix/xr_w1_reviews_w2")

MODALS = [
    {"name": "supplier", "id_prefix": "supplier", "handler_prefix": "Supplier", "display_id": "supplierDisplay"},
    {"name": "product",  "id_prefix": "product",  "handler_prefix": "Product",  "display_id": "productDisplay"},
    {"name": "customer", "id_prefix": "customer", "handler_prefix": "Customer", "display_id": "customerDisplay"},
    {"name": "hanbaiten", "id_prefix": "hanbaiten", "handler_prefix": "Hanbaiten", "display_id": "hanbaitenDisplay"},
    {"name": "enduser",  "id_prefix": "enduser",  "handler_prefix": "EndUser",  "display_id": "enduserDisplay"},
]


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    url = f"file://{quote(str(TARGET))}"
    results = {"file": TARGET.name, "modals": {}}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        page_errors = []
        page.on("pageerror", lambda exc: page_errors.append(str(exc)))

        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(800)

        # 1. section-modal area visible text scan (showroom verify)
        section_modal_text = page.evaluate("""() => {
            const el = document.getElementById('section-modal');
            return el ? el.innerText : '';
        }""")
        results["1_section_modal_visible_text_length"] = len(section_modal_text)
        results["1_section_modal_text_excerpt"] = section_modal_text[:500]

        source_patterns = ["<code>", "</code>", "style=\"", "→ ', '↓', '出典", "018 L", "L1860-1915", "L1971-2003", "L700-732", "new/018_", "new横/", "→ canonical:"]
        source_violations = {p: section_modal_text.count(p) for p in source_patterns}
        results["1_source_in_modal_section"] = source_violations
        results["1_source_zero"] = sum(source_violations.values()) == 0

        drift_patterns = ["⚠ drift warning", "⚠ drift", "drift warning #", "feedback_canonical", "feedback_dimco"]
        drift_violations = {p: section_modal_text.count(p) for p in drift_patterns}
        results["1_drift_in_modal_section"] = drift_violations
        results["1_drift_zero"] = sum(drift_violations.values()) == 0

        # Inject bind targets (catalog has demo modals only; need <input id> for confirm to bind)
        page.evaluate("""() => {
            const ids = ['supplierDisplay', 'productDisplay', 'customerDisplay', 'hanbaitenDisplay', 'enduserDisplay'];
            const tmp = document.createElement('div');
            tmp.id = 'tmp-bind-target-container';
            tmp.style.display = 'none';
            ids.forEach(id => {
                if (!document.getElementById(id)) {
                    const inp = document.createElement('input');
                    inp.id = id;
                    tmp.appendChild(inp);
                }
            });
            document.body.appendChild(tmp);
        }""")

        # 2. 5 modal × 3 step
        for modal in MODALS:
            name = modal["name"]
            iprefix = modal["id_prefix"]
            hprefix = modal["handler_prefix"]
            display_id = modal["display_id"]

            modal_result = {}

            opened = page.evaluate(f"""() => {{
                const fname = 'open{hprefix}SearchModal';
                if (typeof window[fname] !== 'function') return {{error: fname + ' not function'}};
                window[fname]();
                const m = document.getElementById('{iprefix}SearchModal');
                return {{
                    handler_exists: true,
                    modal_active: m ? m.classList.contains('active') : false,
                }};
            }}""")
            modal_result["1_open"] = opened
            page.wait_for_timeout(150)

            selected = page.evaluate(f"""() => {{
                const tbody = document.getElementById('{iprefix}SearchResults');
                if (!tbody) return {{error: 'no tbody'}};
                const firstRow = tbody.querySelector('tr');
                if (!firstRow) return {{error: 'no row'}};
                const fname = 'select{hprefix}';
                if (typeof window[fname] !== 'function') return {{error: fname + ' not function'}};
                window[fname](firstRow);
                const radio = firstRow.querySelector('input[type="radio"]');
                return {{
                    row_selected: firstRow.classList.contains('selected'),
                    radio_checked: radio ? radio.checked : false,
                    data_code: firstRow.dataset.code,
                    data_name: firstRow.dataset.name,
                }};
            }}""")
            modal_result["2_select"] = selected

            confirmed = page.evaluate(f"""() => {{
                const fname = 'confirm{hprefix}Selection';
                if (typeof window[fname] !== 'function') return {{error: fname + ' not function'}};
                window[fname]();
                const target = document.getElementById('{display_id}');
                const m = document.getElementById('{iprefix}SearchModal');
                return {{
                    bind_value: target ? target.value : null,
                    modal_closed: m ? !m.classList.contains('active') : null,
                }};
            }}""")
            modal_result["3_confirm"] = confirmed

            results["modals"][name] = modal_result

        results["page_errors"] = page_errors

        # screenshot of section-modal area
        page.evaluate("document.getElementById('section-modal').scrollIntoView()")
        page.wait_for_timeout(300)
        page.screenshot(path=str(OUTDIR / "modal_section.png"), full_page=False)

        context.close()
        browser.close()

    out_json = OUTDIR / "_verify.json"
    out_json.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
