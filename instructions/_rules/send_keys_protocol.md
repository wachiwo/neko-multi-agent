# tmux send-keys Protocol (Shared Mechanics)

> **Scope**: Physical mechanics only. Who-sends-to-whom rules live in each role's instruction file.

## The 2-Call Rule (MANDATORY)

send-keys requires **two separate Bash tool calls**. Enter is NOT interpreted when combined with the message in a single call.

### Correct Method

**[Call 1]** Send the message:
```bash
tmux send-keys -t <target> 'message text here'
```

**[Call 2]** Send Enter:
```bash
tmux send-keys -t <target> Enter
```

### Absolutely Forbidden Patterns

```bash
# BAD: single line (Enter not interpreted as key press)
tmux send-keys -t <target> 'message' Enter

# BAD: && chain (same problem, Enter becomes a literal argument)
tmux send-keys -t <target> 'message' && tmux send-keys -t <target> Enter
```

### Why 2 Calls

Claude Code Bash tool sometimes merges arguments in ways that cause Enter to be passed as a string instead of a key event. Splitting into two calls guarantees the Enter is registered as a keypress.

## Idle Detection (Before Sending to Busy Targets)

Required before sending to **oyabun** (from kashira) or when the target may be mid-task.

### Command

```bash
tmux capture-pane -t <target> -p | tail -5
```

### Idle Signal

- `❯` (prompt) visible → idle → safe to send
- `bypass permissions on` visible → idle → safe to send
- Anything else → busy → wait

### Retry Rule

If busy: `sleep 10` then retry. **Max 3 retries**. After 3 failures, write to inbox queue and escalate per role-specific escalation rule.

## Deep Scrollback (When Pane Looks Stalled)

`tail -5` alone is insufficient to diagnose stalls. If a worker appears idle but was expected to be working, check deeper:

```bash
tmux capture-pane -t <target> -S -40 -p
```

Look for:
- `Sautéed for Xm Ys` → process stopped
- `API Error: Stream idle timeout` → session died, needs restart
- Long output with no recent activity → possibly mid-work, wait

## Reliability: send-keys Alone Is Not Enough

send-keys is **best-effort wakeup**, not a reliable channel. Past incidents:
- Target pane busy → message dropped into input buffer, never executed
- Target pane mid-Bash-tool → Enter consumed by the tool's prompt, not your intended target
- Target compacted / crashed → message visible in scrollback but no agent to read it

### Required Pairing with Inbox (for cross-agent notifications)

Any notification that must be acted on (not just progress FYI) **must** be written to both:

1. **inbox queue file** (reliable, file-based): `echo "TIMESTAMP|SENDER|TYPE|DETAIL" >> queue/inbox/{target}.queue`
2. **send-keys nudge** (best-effort wake): 2-call method above

Rule of thumb: if the sender expects the target to **do something**, inbox is mandatory. If the sender is only sharing state that the target will pick up on next sweep, send-keys alone is OK.

### Incident Record (2026-04-17)

kashira → oyabun Phase Gate judgment request went through send-keys only → not received → goshujinsama had to intervene manually. Root cause: no inbox pairing, and kashira treated send-keys as reliable. Fix: this section (inbox pairing mandatory for action-requiring notifications).

## Role-Specific Rules Live Elsewhere

This file covers **mechanics only**. For who can send to whom, when, and with what content, see:

- **oyabun → kashira**: `instructions/oyabun.md` § tmux send-keys Usage
- **kashira → workers / oyabun**: `instructions/kashira_core.md` § tmux send-keys Usage
- **workers → kashira**: `instructions/_worker_base.md` § Task Completion Protocol
- **worker P2P**: `instructions/_rules/p2p_comm.md`
- **escalation**: `instructions/_rules/escalation.md`
