"""fix_select_defaults.py — Batch fix <select> defaults in 42 HTML files.

Rules:
1. Remove selected="" from all <option> elements
2. For each <select>, check the first <option>:
   - If already "選択してください" with value="" → skip
   - If "選択" only (with or without value="") → change text to "選択してください", ensure value=""
   - If no default option (all options have real values) → insert <option value="">選択してください</option> at top
3. Exception: "unit-like" selects where all options are concrete values (PCE/KG/JPY/式/kg/様/御中 etc.)
   should NOT get a default option added — only selected="" removal applies.
"""

import os
import re
import glob
from bs4 import BeautifulSoup

TARGET_DIR = "/mnt/g/共有ドライブ/[PJ]ディムコ/01_再構築プロジェクト/90_personal/degawa/004_長瀬さんスタイル/"

# Stats
stats = {
    "files_modified": 0,
    "files_total": 0,
    "selects_processed": 0,
    "selected_removed": 0,
    "sentaku_fixed": 0,       # 「選択」→「選択してください」
    "default_added": 0,       # デフォルトオプション追加
    "skipped_unit_selects": 0,
    "modified_files": [],
}

# Unit-like select heuristic: if first option text matches these, don't add default
UNIT_PATTERNS = re.compile(
    r'^(PCE|SET|LOT|M|KG|LB|G|JPY|USD|EUR|GBP|CNY|'
    r'式|kg|本|個|台|枚|m|mm|cm|L|'
    r'様|御中|各位|'
    r'送料|加工|材料|'
    r'DYMCO|天龍|'
    r'でがわ|山田|佐藤|田中|八戸|高橋).*$'
)


def is_unit_select(select_tag):
    """Check if a select is a 'unit/value' type where all options are concrete values."""
    options = select_tag.find_all("option")
    if not options:
        return False
    first = options[0]
    first_text = first.get_text(strip=True)
    first_value = first.get("value", None)
    # If first option already has value="" or is 選択/選択してください, it's not a unit select
    if first_value == "" or first_text in ("選択", "選択してください"):
        return False
    # Check if first option looks like a unit/concrete value
    if UNIT_PATTERNS.match(first_text):
        return True
    # If no option has value="" and none start with 選択, treat as unit select
    has_empty_value = any(opt.get("value", "NOATTR") == "" for opt in options)
    if not has_empty_value:
        return True
    return False


def process_file(filepath):
    """Process a single HTML file. Returns True if modified."""
    with open(filepath, "r", encoding="utf-8") as f:
        original = f.read()

    soup = BeautifulSoup(original, "html.parser")
    modified = False
    file_selects = 0

    for select in soup.find_all("select"):
        file_selects += 1
        stats["selects_processed"] += 1
        options = select.find_all("option")

        # Step 1: Remove selected="" from all options
        for opt in options:
            if opt.has_attr("selected"):
                del opt["selected"]
                stats["selected_removed"] += 1
                modified = True

        if not options:
            continue

        first_opt = options[0]
        first_text = first_opt.get_text(strip=True)
        first_value = first_opt.get("value", None)

        # Step 2: Check first option
        if first_text == "選択してください" and first_value == "":
            # Already correct
            continue
        elif first_text == "選択":
            # Fix text: 「選択」→「選択してください」
            first_opt.string = "選択してください"
            if first_value is None or first_value != "":
                first_opt["value"] = ""
            stats["sentaku_fixed"] += 1
            modified = True
        elif first_value == "" and first_text == "選択してください":
            # Already correct (different attribute order)
            continue
        else:
            # No default option — check if it's a unit select
            if is_unit_select(select):
                stats["skipped_unit_selects"] += 1
                continue
            # Add default option at top
            new_opt = soup.new_tag("option", value="")
            new_opt.string = "選択してください"
            select.insert(0, new_opt)
            stats["default_added"] += 1
            modified = True

    if not modified:
        return False

    # Save — use str(soup) to minimize formatting changes (no prettify!)
    result = str(soup)
    # BeautifulSoup str() output: preserve original as much as possible
    # Only write if actually different
    if result == original:
        return False

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(result)

    return True


def main():
    files = sorted(glob.glob(os.path.join(glob.escape(TARGET_DIR), "*.html")))
    stats["files_total"] = len(files)
    print(f"Processing {len(files)} HTML files...")

    for filepath in files:
        fname = os.path.basename(filepath)
        was_modified = process_file(filepath)
        if was_modified:
            stats["files_modified"] += 1
            stats["modified_files"].append(fname)
            print(f"  [MODIFIED] {fname}")
        else:
            print(f"  [OK]       {fname}")

    print()
    print("=" * 60)
    print(f"SUMMARY")
    print(f"  Files: {stats['files_modified']}/{stats['files_total']} modified")
    print(f"  Selects processed: {stats['selects_processed']}")
    print(f"  selected= removed: {stats['selected_removed']}")
    print(f"  「選択」→「選択してください」: {stats['sentaku_fixed']}")
    print(f"  Default option added: {stats['default_added']}")
    print(f"  Unit selects skipped: {stats['skipped_unit_selects']}")
    print(f"  Modified files: {stats['modified_files']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
