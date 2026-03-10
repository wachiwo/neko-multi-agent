#!/usr/bin/env bash
# neko_send.sh — tmux send-keys wrapper (2-call split handled internally)
# Usage: neko_send.sh <target_pane> '<message>'
# Example: neko_send.sh multiagent:0.1 'Check queue/tasks/worker1.yaml'

set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <target_pane> <message>" >&2
  echo "Example: $0 multiagent:0.0 'Worker1 task complete.'" >&2
  exit 1
fi

TARGET_PANE="$1"
shift
MESSAGE="$*"

tmux send-keys -t "$TARGET_PANE" "$MESSAGE"
sleep 0.1
tmux send-keys -t "$TARGET_PANE" Enter
