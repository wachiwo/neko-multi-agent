#!/usr/bin/env bash
# archive_task_md.sh — Move completed cmd sections from task.md to task_archive.md
# Keeps latest N completed sections in task.md (default: 5)
# Usage: bash scripts/archive_task_md.sh [--dry-run] [--force] [--keep N]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

python3 "$SCRIPT_DIR/_archive_task_md_core.py" \
  --task-md "$PROJECT_ROOT/task.md" \
  --archive-md "$PROJECT_ROOT/task_archive.md" \
  "$@"
