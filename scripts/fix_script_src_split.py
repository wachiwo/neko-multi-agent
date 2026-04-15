#!/usr/bin/env python3
"""
fix_script_src_split.py — Split <script src="mock-draft-skeleton.js">...inline...</script>
into <script src="mock-draft-skeleton.js"></script>\n<script>...inline...</script>

Browser ignores inline content when src attribute is present (fp_023).
Safe to run on already-fixed files (no-op).
"""

import re
import sys

# Pattern: <script src="mock-draft-skeleton.js"> followed by non-empty inline code then </script>
# Captures:
#   group(1): the <script src="..."> opening tag (with any attributes)
#   group(2): the inline code between the tags (must contain non-whitespace)
PATTERN = re.compile(
    r'(<script\s+src="mock-draft-skeleton\.js"[^>]*>)'  # opening tag with src
    r'(.*?)'                                              # inline content (lazy)
    r'(</script>)',                                       # closing tag
    re.DOTALL
)


def detect_encoding(filepath):
    """Detect file encoding: check BOM, then try utf-8, fall back to cp932."""
    with open(filepath, 'rb') as f:
        head = f.read(3)
    if head[:3] == b'\xef\xbb\xbf':
        return 'utf-8-sig'  # BOM present, preserve it
    for enc in ('utf-8', 'cp932'):
        try:
            with open(filepath, 'r', encoding=enc) as f:
                f.read()
            return enc
        except (UnicodeDecodeError, UnicodeError):
            continue
    return 'utf-8'  # fallback


def fix_file(filepath, dry_run=False):
    """Fix a single HTML file. Returns (changed: bool, message: str)."""
    enc = detect_encoding(filepath)
    with open(filepath, 'r', encoding=enc) as f:
        content = f.read()

    def replacer(m):
        opening_tag = m.group(1)
        inline_code = m.group(2)
        closing_tag = m.group(3)

        # If inline code is only whitespace, already correct — no-op
        if not inline_code.strip():
            return m.group(0)

        # Split: self-closing src tag + new <script> with inline code
        return f'{opening_tag}{closing_tag}\n<script>{inline_code}{closing_tag}'

    new_content, count = PATTERN.subn(replacer, content)

    if new_content == content:
        return False, f"NO CHANGE (already correct or no match): {filepath}"

    if not dry_run:
        with open(filepath, 'w', encoding=enc, newline='') as f:
            f.write(new_content)
        return True, f"FIXED ({count} replacement(s)): {filepath}"
    else:
        return True, f"DRY-RUN would fix ({count} replacement(s)): {filepath}"


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Split <script src> with inline code into two tags')
    parser.add_argument('files', nargs='+', help='HTML files to fix')
    parser.add_argument('--dry-run', action='store_true', help='Show what would change without writing')
    args = parser.parse_args()

    changed_count = 0
    for filepath in args.files:
        changed, msg = fix_file(filepath, dry_run=args.dry_run)
        print(msg)
        if changed:
            changed_count += 1

    print(f"\n--- Summary: {changed_count}/{len(args.files)} file(s) {'would be ' if args.dry_run else ''}modified ---")
    return 0 if changed_count >= 0 else 1


if __name__ == '__main__':
    sys.exit(main())
