#!/usr/bin/env bash
# stop-watchdog.sh — graceful shutdown for stream-watchdog daemon
# (cmd_199 P0-b / subtask_199_002_p0b)
#
# Reads PID from scripts/watchdog-config.yaml (pid_file key, default
# /tmp/neko_watchdog.pid), sends SIGTERM, and removes the PID file.
# Safe to run even when daemon is not active.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG_FILE="${REPO_ROOT}/scripts/watchdog-config.yaml"

PID_FILE=$(awk '
  /^[[:space:]]*#/ { next }
  /^pid_file:/ {
    sub(/^pid_file:[[:space:]]*/, "")
    sub(/[[:space:]]*#.*$/, "")
    gsub(/^[[:space:]]+|[[:space:]]+$/, "")
    gsub(/^"|"$/, "")
    print; exit
  }
' "$CONFIG_FILE" 2>/dev/null)
: "${PID_FILE:=/tmp/neko_watchdog.pid}"

if [ ! -f "$PID_FILE" ]; then
  echo "[stop-watchdog] no PID file at $PID_FILE — daemon not running"
  exit 0
fi

pid=$(cat "$PID_FILE" 2>/dev/null || echo "")
if [ -z "$pid" ]; then
  echo "[stop-watchdog] empty PID file — removing"
  rm -f "$PID_FILE"
  exit 0
fi

if kill -0 "$pid" 2>/dev/null; then
  kill -TERM "$pid" 2>/dev/null || true
  echo "[stop-watchdog] SIGTERM sent to pid=$pid"
  # Wait briefly for graceful exit (daemon removes its own PID file on trap).
  for _ in 1 2 3 4 5; do
    if ! kill -0 "$pid" 2>/dev/null; then break; fi
    sleep 1
  done
  if kill -0 "$pid" 2>/dev/null; then
    echo "[stop-watchdog] still alive after 5s — escalating to SIGKILL"
    kill -KILL "$pid" 2>/dev/null || true
  fi
else
  echo "[stop-watchdog] pid=$pid not running (stale PID file)"
fi

rm -f "$PID_FILE" 2>/dev/null || true
exit 0
