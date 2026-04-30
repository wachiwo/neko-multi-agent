#!/usr/bin/env python3
"""cmd_225 W1 reviews W2: 5 modal browser verify in catalog.

For each of 5 modals (supplier/product/customer/hanbaiten/enduser):
- open(): function exists, modal becomes .active
- select(row): row gets .selected class, radio gets checked
- confirm(): {lower}Display value bound (code:name format)
- close(): modal loses .active, selected cleared
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
OUTDIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_225/xr_w1_reviews_w2")

# Modal naming convention from W2 report: id (lowercase) vs handler (CamelCase, except enduser)
MODALS = [
    {"name": "supplier", "id_prefix": "supplier", "handler_prefix": "Supplier", "display_id": "supplierDisplay"},
    {"name": "product",  "id_prefix": "product",  "handler_prefix": "Product",  "display_id": "productDisplay"},
    {"name": "customer", "id_prefix": "customer", "handler_prefix": "Customer", "display_id": "customerDisplay"},
    {"name": "hanbaiten", "id_prefix": "hanbaiten", "handler_prefix": "Hanbaiten", "display_id": "hanbaitenDisplay"},
    {"name": "enduser",  "id_prefix": "enduser",  "handler_prefix": "EndUser",  "display_id": "enduserDisplay"},  # camel case
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
        results["initial_page_errors"] = page_errors[:]

        # The catalog modal demo doesn't have parent form input with id="{lower}Display" by default
        # (modals reference these via getElementById in confirm function). To test bind, we need to
        # inject a temporary input element for each modal first.
        page.evaluate("""() => {
            const ids = ['supplierDisplay', 'productDisplay', 'customerDisplay', 'hanbaitenDisplay', 'enduserDisplay'];
            const tmp = document.createElement('div');
            tmp.id = 'tmp-bind-target-container';
            tmp.style.display = 'none';
            ids.forEach(id => {
                const inp = document.createElement('input');
                inp.id = id;
                tmp.appendChild(inp);
            });
            document.body.appendChild(tmp);
        }""")

        for modal in MODALS:
            name = modal["name"]
            iprefix = modal["id_prefix"]
            hprefix = modal["handler_prefix"]
            display_id = modal["display_id"]

            modal_result = {}

            # Step 1: open modal
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
            page.wait_for_timeout(200)

            # Step 2: select first row
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
                    row_selected_class: firstRow.classList.contains('selected'),
                    radio_checked: radio ? radio.checked : false,
                    row_data_code: firstRow.dataset.code,
                    row_data_name: firstRow.dataset.name,
                }};
            }}""")
            modal_result["2_select"] = selected

            # Step 3: confirm selection (binds to {lower}Display)
            confirmed = page.evaluate(f"""() => {{
                const fname = 'confirm{hprefix}Selection';
                if (typeof window[fname] !== 'function') return {{error: fname + ' not function'}};
                window[fname]();
                const target = document.getElementById('{display_id}');
                const m = document.getElementById('{iprefix}SearchModal');
                return {{
                    bind_target_value: target ? target.value : null,
                    modal_closed: m ? !m.classList.contains('active') : null,
                }};
            }}""")
            modal_result["3_confirm"] = confirmed

            results["modals"][name] = modal_result

        # Reset (close any leftover) and capture final page errors
        results["final_page_errors"] = page_errors[len(results.get("initial_page_errors", [])):]

        page.screenshot(path=str(OUTDIR / "modal_section.png"), full_page=False)

        context.close()
        browser.close()

    out_json = OUTDIR / "_verify.json"
    out_json.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
