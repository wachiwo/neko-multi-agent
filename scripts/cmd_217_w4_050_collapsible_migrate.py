#!/usr/bin/env python3
"""cmd_217 W4: 050_海外引合 collapsible 12 sections 縦版 SSOT 移植.

For each .collapsible-title pair:
  - Wrap (<div class="collapsible-title ...">) ... </div> + <div id="XXX-content" class="collapsible-content...">...</div>
    in <div class="collapsible-section">...</div>
  - Rename outer <div class="collapsible-title ..."> -> <h2 class="collapsible-header ...">
  - onclick="toggleSection('XXX-content')" -> onclick="toggleSection(this)"
  - <span class="collapse-indicator"> -> <span class="indicator" id="ind-XXX">
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

PATH = Path("/mnt/i/仕事/001_ディムコ/001_ソース/001_モック/dimco-prototype/new/050_海外引合.html")

src = PATH.read_text(encoding="utf-8")
lines = src.splitlines(keepends=True)

# Find lines with collapsible-title open
title_re = re.compile(r'<div(?P<idattr>[^>]*?)class="collapsible-title([^"]*)"\s+onclick="toggleSection\(\'([a-z0-9_-]+)-content\'\)">')
content_open_re = re.compile(r'<div id="([a-z0-9_-]+-content)" class="collapsible-content collapsed" style="max-height: 0px;">')

# First pass: locate all sections (title open line, title close line, content open line, content close line)
sections = []
i = 0
while i < len(lines):
    m = title_re.search(lines[i])
    if m:
        title_open_idx = i
        title_indent = len(lines[i]) - len(lines[i].lstrip())
        # find close </div> for the title at same indent
        j = i + 1
        while j < len(lines):
            stripped = lines[j].strip()
            curr_indent = len(lines[j]) - len(lines[j].lstrip())
            if stripped == "</div>" and curr_indent == title_indent:
                title_close_idx = j
                break
            j += 1
        else:
            raise RuntimeError(f"title close not found from line {i+1}")
        # next non-blank after title close should be content open
        k = title_close_idx + 1
        content_open_idx = None
        while k < len(lines):
            mc = content_open_re.search(lines[k])
            if mc:
                content_open_idx = k
                break
            if lines[k].strip() != "":
                raise RuntimeError(f"unexpected line between title close and content open at {k+1}: {lines[k]!r}")
            k += 1
        if content_open_idx is None:
            raise RuntimeError(f"content open not found after line {title_close_idx+1}")
        content_indent = len(lines[content_open_idx]) - len(lines[content_open_idx].lstrip())
        # confirm indents match
        assert title_indent == content_indent, f"indent mismatch at section starting line {title_open_idx+1}: title={title_indent} content={content_indent}"
        # find matching </div> for the content by counting <div / </div> at any depth
        # but simpler: find next </div> at same indent as content_open
        l = content_open_idx + 1
        depth = 1  # we're inside the content div
        while l < len(lines):
            line = lines[l]
            # Count opening divs (excluding self-closing)
            opens = len(re.findall(r'<div(?:\s|>)', line))
            closes = len(re.findall(r'</div>', line))
            depth += opens - closes
            if depth == 0:
                content_close_idx = l
                break
            l += 1
        else:
            raise RuntimeError(f"content close not found from line {content_open_idx+1}")
        section_id = m.group(3)
        title_classes = m.group(2).strip()  # e.g. "collapsed" or "white-title collapsed"
        if title_classes:
            full_classes = "collapsible-header " + title_classes
        else:
            full_classes = "collapsible-header"
        # collect inner span title text from lines title_open_idx+1 .. title_close_idx-1
        inner = "".join(lines[title_open_idx+1:title_close_idx])
        # replace collapse-indicator span
        new_inner = re.sub(
            r'<span class="collapse-indicator">▼</span>',
            f'<span class="indicator" id="ind-{section_id}">▼</span>',
            inner,
        )
        sections.append({
            "title_open": title_open_idx,
            "title_close": title_close_idx,
            "content_open": content_open_idx,
            "content_close": content_close_idx,
            "indent": title_indent,
            "section_id": section_id,
            "full_classes": full_classes,
            "new_inner": new_inner,
            "id_attr": m.group("idattr").strip(),  # e.g. id="agent-section"
        })
        i = content_close_idx + 1
    else:
        i += 1

print(f"Found {len(sections)} collapsible sections")

# Build output by processing in order
out_lines = []
prev_end = 0
for s in sections:
    # copy lines before title_open
    out_lines.extend(lines[prev_end:s["title_open"]])
    indent = " " * s["indent"]
    # insert section wrapper open
    out_lines.append(f'{indent}<div class="collapsible-section">\n')
    # write h2 open with canonical onclick
    # drop existing id attr on title element (e.g. id="agent-section") — orphan, not referenced
    out_lines.append(
        f'{indent}<h2 class="{s["full_classes"]}" onclick="toggleSection(this)">\n'
    )
    # write inner (with indicator class swap)
    out_lines.append(s["new_inner"])
    # close h2 (replacing the </div>)
    out_lines.append(f'{indent}</h2>\n')
    # write content open through content close
    out_lines.extend(lines[s["content_open"]:s["content_close"]+1])
    # insert section wrapper close
    out_lines.append(f'{indent}</div>\n')
    prev_end = s["content_close"] + 1

out_lines.extend(lines[prev_end:])
new_src = "".join(out_lines)

PATH.write_text(new_src, encoding="utf-8")
print(f"Wrote {PATH} ({len(new_src)} bytes)")

# Print first section diff for sanity
print("---")
print("First section transform preview:")
print(f"  section_id={sections[0]['section_id']}")
print(f"  title_open line={sections[0]['title_open']+1}")
print(f"  content_close line={sections[0]['content_close']+1}")
