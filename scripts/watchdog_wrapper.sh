#!/bin/bash
# =^._.^= Watchdog Wrapper for Claude Code agents
# Replaces raw "while true" loops with logging, backoff, and restart limits.
#
# Usage:
#   scripts/watchdog_wrapper.sh <agent_name> <claude_args> <prompt>
#
# Environment:
#   DRY_RUN=1       — log and exit without launching claude
#   MAX_RESTARTS=N  — override max restarts per hour (default: 5)
#
# Example:
#   scripts/watchdog_wrapper.sh oyabun "--model opus --permission-mode bypassPermissions" "Read instructions/oyabun.md"

set -euo pipefail

# ═══════════════════════════════════════════════════════════════════════════════
# Arguments
# ═══════════════════════════════════════════════════════════════════════════════
AGENT_NAME="${1:?Usage: watchdog_wrapper.sh <agent_name> <claude_args> <prompt>}"
CLAUDE_ARGS="${2:?Usage: watchdog_wrapper.sh <agent_name> <claude_args> <prompt>}"
PROMPT="${3:?Usage: watchdog_wrapper.sh <agent_name> <claude_args> <prompt>}"

# ═══════════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════════
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_FILE="${SCRIPT_DIR}/logs/agent_restarts.log"
MAX_RESTARTS_PER_HOUR="${MAX_RESTARTS:-5}"
BACKOFF_SCHEDULE=(2 4 8 16 30)  # seconds — cap at 30
HEALTHY_RUN_THRESHOLD=60        # seconds — reset backoff if run lasted this long

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# ═══════════════════════════════════════════════════════════════════════════════
# Logging
# ═══════════════════════════════════════════════════════════════════════════════
log_event() {
    local event="$1"
    local detail="${2:-}"
    local timestamp
    timestamp="$(date '+%Y-%m-%dT%H:%M:%S')"
    echo "${timestamp}|${AGENT_NAME}|${event}|${detail}" >> "$LOG_FILE"
}

# ═══════════════════════════════════════════════════════════════════════════════
# Restart tracking (rolling 1-hour window)
# ═══════════════════════════════════════════════════════════════════════════════
# Store restart timestamps in a simple array
declare -a RESTART_TIMESTAMPS=()

count_recent_restarts() {
    local now
    now="$(date +%s)"
    local cutoff=$((now - 3600))
    local count=0
    local new_timestamps=()
    if [ ${#RESTART_TIMESTAMPS[@]} -gt 0 ]; then
        for ts in "${RESTART_TIMESTAMPS[@]}"; do
            if [ "$ts" -ge "$cutoff" ]; then
                count=$((count + 1))
                new_timestamps+=("$ts")
            fi
        done
    fi
    RESTART_TIMESTAMPS=("${new_timestamps[@]+"${new_timestamps[@]}"}")
    echo "$count"
}

# ═══════════════════════════════════════════════════════════════════════════════
# DRY_RUN mode
# ═══════════════════════════════════════════════════════════════════════════════
if [ "${DRY_RUN:-0}" = "1" ]; then
    log_event "DRY_RUN" "agent=${AGENT_NAME} args=${CLAUDE_ARGS} prompt_len=${#PROMPT}"
    echo "[watchdog] DRY_RUN mode — ${AGENT_NAME} would launch with:"
    echo "  claude ${CLAUDE_ARGS} \"${PROMPT}\""
    echo "  log_file: ${LOG_FILE}"
    echo "  max_restarts/hour: ${MAX_RESTARTS_PER_HOUR}"
    exit 0
fi

# ═══════════════════════════════════════════════════════════════════════════════
# Signal handling (F1: forward signals to child, prevent orphan claude processes)
# ═══════════════════════════════════════════════════════════════════════════════
CHILD_PID=0

cleanup() {
    local sig="${1:-UNKNOWN}"
    log_event "SIGNAL" "received=${sig} child_pid=${CHILD_PID}"
    if [ "$CHILD_PID" -gt 0 ]; then
        kill -TERM "$CHILD_PID" 2>/dev/null || true
        wait "$CHILD_PID" 2>/dev/null || true
    fi
    echo "=^._.^= ${AGENT_NAME}: watchdog stopped by ${sig}"
    exit 0
}

trap 'cleanup SIGTERM' SIGTERM
trap 'cleanup SIGINT' SIGINT

# ═══════════════════════════════════════════════════════════════════════════════
# Main loop
# ═══════════════════════════════════════════════════════════════════════════════
CONSECUTIVE_FAILURES=0

log_event "START" "max_restarts=${MAX_RESTARTS_PER_HOUR}"

while true; do
    # Check restart limit (rolling 1-hour window)
    RECENT=$(count_recent_restarts)
    if [ "$RECENT" -ge "$MAX_RESTARTS_PER_HOUR" ]; then
        log_event "MAX_RESTARTS_EXCEEDED" "count=${RECENT} in last hour — stopping"
        echo "=^._.^= ${AGENT_NAME}: MAX_RESTARTS_EXCEEDED (${RECENT}/${MAX_RESTARTS_PER_HOUR} in 1h) — stopping watchdog"
        exit 1
    fi

    # Record start time
    RUN_START="$(date +%s)"

    # Launch claude in background to allow signal forwarding
    EXIT_CODE=0
    # shellcheck disable=SC2086
    claude ${CLAUDE_ARGS} "${PROMPT}" &
    CHILD_PID=$!
    wait "$CHILD_PID" || EXIT_CODE=$?
    CHILD_PID=0

    # Record end time and duration
    RUN_END="$(date +%s)"
    RUN_DURATION=$((RUN_END - RUN_START))

    # Determine reason
    if [ "$EXIT_CODE" -eq 0 ]; then
        REASON="normal_exit(context_exhaustion)"
    else
        REASON="crash(exit_code=${EXIT_CODE})"
    fi

    # Log restart
    RESTART_TIMESTAMPS+=("$RUN_END")
    RECENT=$((RECENT + 1))
    log_event "RESTART" "reason=${REASON} duration=${RUN_DURATION}s count=${RECENT}/${MAX_RESTARTS_PER_HOUR}"

    echo "=^._.^= ${AGENT_NAME}、再起動するにゃ... (${REASON}, ran ${RUN_DURATION}s)"

    # Backoff logic
    if [ "$RUN_DURATION" -ge "$HEALTHY_RUN_THRESHOLD" ]; then
        # Healthy run — reset backoff
        CONSECUTIVE_FAILURES=0
        sleep 2
    else
        # Short run — apply exponential backoff
        BACKOFF_IDX=$CONSECUTIVE_FAILURES
        if [ "$BACKOFF_IDX" -ge "${#BACKOFF_SCHEDULE[@]}" ]; then
            BACKOFF_IDX=$(( ${#BACKOFF_SCHEDULE[@]} - 1 ))
        fi
        BACKOFF_SECS="${BACKOFF_SCHEDULE[$BACKOFF_IDX]}"
        CONSECUTIVE_FAILURES=$((CONSECUTIVE_FAILURES + 1))
        log_event "BACKOFF" "wait=${BACKOFF_SECS}s consecutive_failures=${CONSECUTIVE_FAILURES}"
        echo "  [watchdog] Backoff: waiting ${BACKOFF_SECS}s before restart..."
        sleep "$BACKOFF_SECS"
    fi
done
