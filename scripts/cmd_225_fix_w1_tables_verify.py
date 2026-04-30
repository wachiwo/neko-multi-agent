#!/usr/bin/env python3
"""cmd_225_fix W1 tables refactor browser visibility verify.

Wraps w1_tables_refactored.html with minimal HTML5 doctype to enable browser render,
then Playwright reads visible body.innerText to confirm:
- No source code (e.g., 'style="flex: 1;"' as plain text) visible
- No line refs (e.g., '016 L983') visible
- showroom inputs render correctly
"""
import os
import json
from pathlib import Path
from urllib.parse import quote
import tempfile

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

W1_REFACTORED = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_225_fix/w1_tables_refactored.html")
OUTDIR = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_225_fix/verify")


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)

    # Wrap section file in minimal HTML5 doctype + :root vars (mimics catalog integration)
    section_content = W1_REFACTORED.read_text(encoding="utf-8")
    wrapper_html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>W1 Tables Refactor Verify</title>
<style>
:root {{
    --primary-blue: #004B87;
    --primary-blue-dark: #003d6b;
    --primary-blue-light: #0070C0;
    --secondary-blue: #4A90D9;
    --light-blue: #D6E8F6;
    --lighter-blue: #EBF3FA;
    --accent-blue: #004B87;
    --text-dark: #1e293b;
    --text-gray: #64748b;
    --border-color: #cbd5e1;
    --shadow: 0 2px 8px rgba(0, 93, 168, 0.1);
    --shadow-hover: 0 4px 12px rgba(0, 93, 168, 0.15);
}}
body {{ font-family: -apple-system, sans-serif; background: #eeeeee; padding: 24px; }}
.catalog-section {{ background: white; padding: 24px; border-radius: 8px; margin-bottom: 24px; box-shadow: var(--shadow); }}
.catalog-section h2 {{ color: var(--primary-blue); border-bottom: 2px solid var(--primary-blue); padding-bottom: 8px; margin: 0 0 16px 0; }}
.demo-area {{ padding: 16px; border: 1px dashed var(--border-color); border-radius: 6px; margin: 12px 0; background: #fafafa; }}
</style>
</head>
<body>
{section_content}
</body>
</html>
"""
    tmp_file = OUTDIR / "_wrapped_for_verify.html"
    tmp_file.write_text(wrapper_html, encoding="utf-8")

    url = f"file://{quote(str(tmp_file))}"
    results = {"file": tmp_file.name}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        page_errors = []
        console_errors = []
        page.on("pageerror", lambda exc: page_errors.append(str(exc)))
        page.on("console", lambda msg: console_errors.append({"type": msg.type, "text": msg.text}) if msg.type == "error" else None)

        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(500)

        # 1. Visible body innerText scan (no comments, only rendered content)
        visible_text = page.evaluate("() => document.body.innerText")
        results["1_visible_text_length"] = len(visible_text)
        results["1_visible_text_sample"] = visible_text[:600]

        # 2. Check for source code patterns (style=, flex: 1, etc.) in visible text
        source_code_patterns = ["style=\"", "<code>", "</code>", 'flex: 1;', '016 L', '027 L', '049 L', 'new横/027']
        results["2_source_in_visible_text"] = {p: visible_text.count(p) for p in source_code_patterns}

        # 3. Check showroom inputs render
        input_check = page.evaluate("""() => {
            const inputs = document.querySelectorAll('.input-canonical-card input, .input-canonical-card select');
            const labels = document.querySelectorAll('.input-canonical-card .label');
            return {
                input_count: inputs.length,
                label_count: labels.length,
                first_label: labels[0] ? labels[0].textContent.trim() : null,
                first_input_value: inputs[0] ? inputs[0].value : null,
            };
        }""")
        results["3_showroom_inputs"] = input_check

        # 4. .excel-table render check
        table_check = page.evaluate("""() => {
            const tables = document.querySelectorAll('.excel-table');
            const rows = document.querySelectorAll('.excel-table tr');
            return {
                excel_table_count: tables.length,
                excel_table_row_count: rows.length,
            };
        }""")
        results["4_excel_table_render"] = table_check

        # 5. Errors
        results["5_page_errors"] = page_errors
        results["5_console_errors"] = console_errors

        page.screenshot(path=str(OUTDIR / "showroom_render.png"), full_page=True)

        context.close()
        browser.close()

    out_json = OUTDIR / "_verify.json"
    out_json.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
