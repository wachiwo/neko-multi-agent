#!/usr/bin/env python3
"""
archive_task_md_core.py — Core logic for archiving completed sections from task.md.

Parses task.md into H2 sections, identifies [完了] sections,
keeps the latest N in task.md, moves the rest to task_archive.md.

Never touches [進行中] sections.
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path


H2_PATTERN = re.compile(r"^## ", re.MULTILINE)


def parse_sections(text: str) -> tuple[str, list[dict]]:
    """Split task.md into header (before first ##) and a list of H2 sections.

    Each section dict:
      - heading: str (the ## line)
      - body: str (everything until next ## or EOF)
      - raw: str (heading + body, preserving original text)
      - status: 'completed' | 'in_progress' | 'unknown'
    """
    lines = text.split("\n")
    header_lines = []
    sections = []
    current_heading = None
    current_lines = []

    for line in lines:
        if line.startswith("## "):
            if current_heading is not None:
                raw = current_heading + "\n" + "\n".join(current_lines)
                status = _detect_status(current_heading)
                sections.append({
                    "heading": current_heading,
                    "body": "\n".join(current_lines),
                    "raw": raw,
                    "status": status,
                })
            else:
                # Everything before the first ## is the header
                header_lines = current_lines[:]
            current_heading = line
            current_lines = []
        else:
            current_lines.append(line)

    # Last section
    if current_heading is not None:
        raw = current_heading + "\n" + "\n".join(current_lines)
        status = _detect_status(current_heading)
        sections.append({
            "heading": current_heading,
            "body": "\n".join(current_lines),
            "raw": raw,
            "status": status,
        })
    else:
        header_lines = current_lines[:]

    header = "\n".join(header_lines)
    return header, sections


def _detect_status(heading: str) -> str:
    if "[完了]" in heading:
        return "completed"
    if "[進行中]" in heading:
        return "in_progress"
    return "unknown"


def main():
    parser = argparse.ArgumentParser(
        description="Archive completed cmd sections from task.md to task_archive.md"
    )
    parser.add_argument("--task-md", required=True, help="Path to task.md")
    parser.add_argument("--archive-md", required=True, help="Path to task_archive.md")
    parser.add_argument("--keep", type=int, default=5,
                        help="Number of latest [完了] sections to keep (default: 5)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be moved without making changes")
    parser.add_argument("--force", action="store_true",
                        help="Skip confirmation prompt")
    args = parser.parse_args()

    task_path = Path(args.task_md)
    archive_path = Path(args.archive_md)

    if not task_path.exists():
        print(f"Error: {task_path} not found", file=sys.stderr)
        sys.exit(1)

    text = task_path.read_text(encoding="utf-8")
    header, sections = parse_sections(text)

    # Separate completed vs non-completed
    completed = [s for s in sections if s["status"] == "completed"]
    non_completed = [s for s in sections if s["status"] != "completed"]

    # Keep latest N completed (they appear in document order; latest = first in file)
    keep_completed = completed[:args.keep]
    archive_completed = completed[args.keep:]

    if not archive_completed:
        print("No sections to archive. All [完了] sections fit within --keep limit.")
        sys.exit(0)

    # Display summary
    print(f"task.md: {len(sections)} total sections")
    print(f"  [完了]: {len(completed)}")
    print(f"  [進行中] / other: {len(non_completed)}")
    print(f"  Keep in task.md: {len(keep_completed)} latest [完了]")
    print(f"  Archive target:  {len(archive_completed)} [完了] sections")
    print()

    if args.dry_run:
        print("=== DRY RUN — sections that WOULD be archived ===")
        for s in archive_completed:
            print(f"  {s['heading']}")
        print()
        print("No changes made.")
        sys.exit(0)

    # Confirmation prompt (unless --force)
    if not args.force:
        print(f"Will move {len(archive_completed)} sections to {archive_path.name}.")
        answer = input("Proceed? [y/N] ").strip().lower()
        if answer != "y":
            print("Aborted.")
            sys.exit(0)

    # Build archive content
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    archive_block = f"\n<!-- archived {timestamp} — {len(archive_completed)} sections -->\n\n"
    for s in archive_completed:
        archive_block += s["raw"].rstrip() + "\n\n"

    # Append to archive file
    if archive_path.exists():
        existing = archive_path.read_text(encoding="utf-8")
        archive_path.write_text(existing.rstrip() + "\n" + archive_block, encoding="utf-8")
    else:
        preamble = "# タスク管理台帳 — アーカイブ\n\n"
        archive_path.write_text(preamble + archive_block, encoding="utf-8")

    # Rebuild task.md
    new_parts = [header.rstrip()]
    # Non-completed sections first (they include [進行中] and unknown)
    for s in non_completed:
        new_parts.append(s["raw"].rstrip())
    # Then kept completed sections
    for s in keep_completed:
        new_parts.append(s["raw"].rstrip())

    new_task_md = "\n\n".join(new_parts) + "\n"
    task_path.write_text(new_task_md, encoding="utf-8")

    print(f"Done. Archived {len(archive_completed)} sections to {archive_path.name}.")
    print(f"task.md: {len(non_completed) + len(keep_completed)} sections remaining.")


if __name__ == "__main__":
    main()
