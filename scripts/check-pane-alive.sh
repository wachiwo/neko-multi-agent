#!/usr/bin/env bash
# check-pane-alive.sh - Verify a tmux pane has Claude Code running
#
# Purpose: Before send-keys to kashira / workers, confirm the pane is not just
# a bare shell. If Claude crashed or exited, send-keys would fire as a shell
# command — which could be catastrophic (e.g. pasting "rm -rf" or leaking keys).
#
# Detection:
#   - Check the pane's current_command (tmux display-message -p '#{pane_current_command}')
#   - Alive: node | claude | bash-running-claude
#   - Dead:  plain bash/zsh prompt with no active process, or empty
#
# Also checks the last 3 scrollback lines for the Claude UI markers (❯ prompt
# line, ⏵⏵ permissions indicator, ● spinner).
#
# Exit codes:
#   0 = alive (Claude process detected)
#   1 = dead (bare shell / no Claude UI)
#   2 = pane not found
#
# Usage:
#   scripts/check-pane-alive.sh multiagent:0.0
#   if bash scripts/check-pane-alive.sh multiagent:0.0; then
#     tmux send-keys ...
#   else
#     echo "WARN: kashira pane is not running Claude"
#   fi

set -uo pipefail

PANE="${1:-}"
[ -z "$PANE" ] && { echo "Usage: $0 <tmux-pane>" >&2; exit 2; }

# Does the pane exist? tmux display-message -t <bad> still exits 0 in some
# versions; cross-check with list-panes to be sure.
if ! tmux list-panes -a -F '#{session_name}:#{window_index}.#{pane_index}' 2>/dev/null | grep -qxF "$PANE"; then
  echo "[check-pane-alive] pane '$PANE' not found" >&2
  exit 2
fi

CMD=$(tmux display-message -t "$PANE" -p '#{pane_current_command}' 2>/dev/null)
SCROLLBACK=$(tmux capture-pane -t "$PANE" -p -S -3 2>/dev/null || true)

# Alive heuristics
if echo "$CMD" | grep -qE '^(node|claude|python|python3)$'; then
  exit 0
fi

# Claude CLI UI markers
if echo "$SCROLLBACK" | grep -qE '(⏵⏵|esc to interrupt|bypass permissions)'; then
  exit 0
fi

# Bare shell detection
if echo "$CMD" | grep -qE '^(bash|zsh|sh|fish)$'; then
  # Could be Claude having just quit, or a fresh shell — treat as dead
  echo "[check-pane-alive] pane '$PANE' is a bare shell (current_command=${CMD})" >&2
  exit 1
fi

# Unknown state — conservative: warn, treat as alive
echo "[check-pane-alive] pane '$PANE' state unclear (current_command=${CMD}), treating as alive" >&2
exit 0
