#!/usr/bin/env python3
"""Fix sticky prerequisite CSS chain in HTML files.
Target pattern (from 002 reference):
  body { height: 100vh; overflow: hidden; }
  .app-container { display: flex; height: 100vh; }  (NO flex-wrap, NO min-height)
  .main-content { flex: 1; display: flex; flex-direction: column; overflow: hidden; }  (NO flex-wrap)
"""
import re
import sys

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    original = content
    changes = []

    # 1. body: min-height: 100vh → height: 100vh
    new = re.sub(r'(body\s*\{[^}]*?)min-height\s*:\s*100vh', r'\1height: 100vh', content, flags=re.DOTALL)
    if new != content:
        changes.append('body: min-height→height')
        content = new

    # 2. body: overflow-y: auto; overflow-x: hidden → overflow: hidden
    new = re.sub(r'(body\s*\{[^}]*?)overflow-y\s*:\s*auto\s*;\s*\n?\s*overflow-x\s*:\s*hidden\s*;', r'\1overflow: hidden;', content, flags=re.DOTALL)
    if new != content:
        changes.append('body: overflow-y:auto;overflow-x:hidden→overflow:hidden')
        content = new

    # 2b. body: overflow-y: auto (standalone, no overflow-x following)
    new = re.sub(r'(body\s*\{[^}]*?)overflow-y\s*:\s*auto\s*;', r'\1overflow: hidden;', content, flags=re.DOTALL)
    if new != content:
        changes.append('body: overflow-y:auto→overflow:hidden')
        content = new

    # 2c. body: remove now-orphaned overflow-x: hidden (if overflow: hidden already present)
    def remove_orphan_overflow_x(m):
        block = m.group(0)
        if 'overflow: hidden' in block and 'overflow-x: hidden' in block:
            block = re.sub(r'\s*overflow-x\s*:\s*hidden\s*;', '', block)
            changes.append('body: removed orphaned overflow-x:hidden')
        return block
    content = re.sub(r'body\s*\{[^}]*\}', remove_orphan_overflow_x, content, flags=re.DOTALL)

    # 3. .app-container: remove flex-wrap: wrap
    def fix_app_container(m):
        block = m.group(0)
        new_block = block
        new_block = re.sub(r'\s*flex-wrap\s*:\s*wrap\s*;', '', new_block)
        new_block = re.sub(r'\s*min-height\s*:\s*100vh\s*;', '', new_block)
        if new_block != block:
            if 'flex-wrap' in block and 'flex-wrap' not in new_block:
                changes.append('.app-container: removed flex-wrap:wrap')
            if 'min-height' in block and 'min-height' not in new_block:
                changes.append('.app-container: removed min-height:100vh')
        return new_block
    content = re.sub(r'\.app-container\s*\{[^}]*\}', fix_app_container, content, flags=re.DOTALL)

    # 4. .main-content: remove flex-wrap: wrap (but NOT within @media blocks — handle both)
    def fix_main_content(m):
        block = m.group(0)
        new_block = re.sub(r'\s*flex-wrap\s*:\s*wrap\s*;', '', block)
        if new_block != block:
            changes.append('.main-content: removed flex-wrap:wrap')
        return new_block
    content = re.sub(r'\.main-content\s*\{[^}]*\}', fix_main_content, content, flags=re.DOTALL)

    # 5. @media .main-content: remove overflow-y: auto (W2 found this in 011)
    def fix_media_main_content(m):
        block = m.group(0)
        if '.main-content' in block and 'overflow-y: auto' in block:
            new_block = re.sub(r'(\.main-content\s*\{[^}]*?)overflow-y\s*:\s*auto\s*;', r'\1', block)
            if new_block != block:
                changes.append('@media .main-content: removed overflow-y:auto')
                return new_block
        return block
    content = re.sub(r'@media[^{]*\{[^}]*\.main-content\s*\{[^}]*\}[^}]*\}', fix_media_main_content, content, flags=re.DOTALL)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return changes
    return []

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 fix_sticky_prerequisites.py file1.html [file2.html ...]")
        sys.exit(1)
    for fp in sys.argv[1:]:
        changes = fix_file(fp)
        if changes:
            print(f"FIXED: {fp}")
            for c in changes:
                print(f"  - {c}")
        else:
            print(f"CLEAN: {fp}")
