#!/bin/bash
# kashira_dispatch.sh — タスク配布ヘルパー
# kashira がワーカーにタスクを配布する際の定型作業を自動化する。
#
# 処理:
#   1. ワーカー名 → tmux pane 番号を自動解決
#   2. 指定 YAML を queue/tasks/{worker}.yaml にコピー
#   3. tmux send-keys で対象 pane に通知 (メッセージ + Enter の2回)
#   4. 成功時にタイムスタンプ付きログ出力
#
# Usage:
#   bash scripts/kashira_dispatch.sh <worker_name> <yaml_path>
#   bash scripts/kashira_dispatch.sh --dry-run <worker_name> <yaml_path>
#   bash scripts/kashira_dispatch.sh --no-notify <worker_name> <yaml_path>

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# ── Pane mapping ──────────────────────────────────────────────
declare -A PANE_MAP=(
  [worker1]="multiagent:0.1"
  [worker2]="multiagent:0.2"
  [worker3]="multiagent:0.3"
  [worker4]="multiagent:0.4"
  [worker5]="multiagent:0.5"
  [worker6]="multiagent:0.6"
  [worker7]="multiagent:0.7"
)

VALID_WORKERS="${!PANE_MAP[*]}"

# ── Option parsing ────────────────────────────────────────────
DRY_RUN=false
NO_NOTIFY=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)  DRY_RUN=true; shift ;;
    --no-notify) NO_NOTIFY=true; shift ;;
    --help|-h)
      echo "Usage: bash $0 [--dry-run] [--no-notify] <worker_name> <yaml_path>"
      echo ""
      echo "Options:"
      echo "  --dry-run     Show what would be done without executing"
      echo "  --no-notify   Copy YAML only, skip send-keys notification"
      echo ""
      echo "Workers: $VALID_WORKERS"
      exit 0
      ;;
    -*)
      echo "ERROR: Unknown option: $1" >&2
      echo "Usage: bash $0 [--dry-run] [--no-notify] <worker_name> <yaml_path>" >&2
      exit 1
      ;;
    *)  break ;;
  esac
done

# ── Argument validation ──────────────────────────────────────
if [[ $# -lt 2 ]]; then
  echo "ERROR: Missing arguments." >&2
  echo "Usage: bash $0 [--dry-run] [--no-notify] <worker_name> <yaml_path>" >&2
  echo "Workers: $VALID_WORKERS" >&2
  exit 1
fi

WORKER="$1"
YAML_PATH="$2"

# Validate worker name
if [[ -z "${PANE_MAP[$WORKER]+x}" ]]; then
  echo "ERROR: Invalid worker name '$WORKER'" >&2
  echo "Valid workers: $VALID_WORKERS" >&2
  exit 1
fi

# Validate YAML file exists
if [[ ! -f "$YAML_PATH" ]]; then
  echo "ERROR: YAML file not found: $YAML_PATH" >&2
  exit 1
fi

PANE="${PANE_MAP[$WORKER]}"
DEST="$PROJECT_DIR/queue/tasks/${WORKER}.yaml"
TIMESTAMP=$(date "+%Y-%m-%dT%H:%M:%S")

# Extract task_id from YAML (simple grep, no yq dependency)
TASK_ID=$(grep -m1 'task_id:' "$YAML_PATH" | sed 's/.*task_id:[[:space:]]*//' | tr -d '"' | tr -d "'")
if [[ -z "$TASK_ID" ]]; then
  TASK_ID="(unknown)"
fi

# ── Dry-run mode ──────────────────────────────────────────────
if $DRY_RUN; then
  echo "[DRY-RUN] $TIMESTAMP"
  echo "  Worker:  $WORKER"
  echo "  Pane:    $PANE"
  echo "  Task ID: $TASK_ID"
  echo "  Source:  $YAML_PATH"
  echo "  Dest:    $DEST"
  echo "  Actions:"
  echo "    1. cp \"$YAML_PATH\" \"$DEST\""
  if $NO_NOTIFY; then
    echo "    2. (notify skipped: --no-notify)"
  else
    echo "    2. tmux send-keys -t $PANE 'New task: $TASK_ID. Check queue/tasks/${WORKER}.yaml'"
    echo "    3. tmux send-keys -t $PANE Enter"
  fi
  exit 0
fi

# ── Execute ───────────────────────────────────────────────────

# Step 1: Copy YAML to worker's task file
REAL_SRC=$(realpath "$YAML_PATH")
REAL_DEST=$(realpath "$DEST" 2>/dev/null || echo "$DEST")
if [[ "$REAL_SRC" == "$REAL_DEST" ]]; then
  echo "[$TIMESTAMP] Source and dest are the same file — skip copy"
else
  cp "$YAML_PATH" "$DEST"
  echo "[$TIMESTAMP] Copied $YAML_PATH -> $DEST"
fi

# Step 2: Send notification via tmux (unless --no-notify)
if $NO_NOTIFY; then
  echo "[$TIMESTAMP] Notification skipped (--no-notify)"
else
  # Check if tmux session exists
  if ! tmux has-session -t multiagent 2>/dev/null; then
    echo "WARNING: tmux session 'multiagent' not found. YAML copied but notification skipped." >&2
  else
    tmux send-keys -t "$PANE" "New task: $TASK_ID. Check queue/tasks/${WORKER}.yaml"
    sleep 0.3
    tmux send-keys -t "$PANE" Enter
    echo "[$TIMESTAMP] Notified $WORKER (pane $PANE) — task: $TASK_ID"
  fi
fi
