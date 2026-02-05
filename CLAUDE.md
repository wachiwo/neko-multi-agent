# neko-multi-agent System Configuration

> **Version**: 2.1.0
> **Last Updated**: 2026-02-03

## Overview
neko-multi-agent is a multi-agent parallel development platform using Claude Code + tmux.
It uses a hierarchical structure themed around a cat team, capable of managing multiple projects in parallel.

## Post-Compaction Recovery (Mandatory for All Agents)

After compaction, always execute the following before resuming work:

1. **Check your pane name**: `tmux display-message -p '#W'`
2. **Read the corresponding instructions**:
   - oyabun → instructions/oyabun.md
   - kashira (multiagent:0.0) → instructions/kashira.md
   - worker1 (multiagent:0.1) → instructions/1gou-neko.md
   - worker2 (multiagent:0.2) → instructions/2gou-inu.md
   - worker3 (multiagent:0.3) → instructions/3gou-neko.md
   - worker4 (multiagent:0.4) → instructions/4gou-neko.md
3. **Confirm forbidden actions before starting work**

Do NOT immediately act on summary's "next steps". First confirm who you are.

## Hierarchy

```
Master (Human)
  │
  ▼ Instructions
┌──────────────┐
│   OYABUN     │ ← Boss cat (project oversight)
└──────┬───────┘
       │ via YAML files
       ▼
┌──────────────┐
│   KASHIRA    │ ← Head cat (task management & distribution)
└──────┬───────┘
       │ via YAML files
       ▼
┌──────┬──────┬──────┬──────┐
│  W1  │  W2  │  W3  │  W4  │ ← Workers (execution team)
└──────┴──────┴──────┴──────┘
```

### Worker-Pane Mapping (identity reference only)

| Pane | ID | Instruction File |
|------|-----|-----------------|
| multiagent:0.1 | worker1 | instructions/1gou-neko.md |
| multiagent:0.2 | worker2 | instructions/2gou-inu.md |
| multiagent:0.3 | worker3 | instructions/3gou-neko.md |
| multiagent:0.4 | worker4 | instructions/4gou-neko.md |

**Personality and speech style are defined in each worker's instruction file only. Do NOT assume identity from this table.**

## Communication Protocol

### Event-Driven Communication (YAML + send-keys + inbox)
- Polling is forbidden (to save API costs)
- Instructions and reports are written in YAML files
- Notifications use tmux send-keys to wake the target (always use Enter, never C-m)
- File-based inbox (`queue/inbox/{agent}.queue`) provides reliable message delivery as backup

### Reporting Flow (Interrupt Prevention Design)
- **Bottom-up reports**: Workers write report YAML + send-keys notification to kashira. Kashira updates dashboard.md on task reception and report reception
- **Top-down instructions**: Wake via YAML + send-keys
- Kashira → Oyabun send-keys: Only allowed when all cmd subtasks complete (after idle check)
- Worker → Oyabun send-keys: Forbidden (must go through kashira)

### File Structure
```
config/projects.yaml                # Project list
config/settings.yaml                # Language & logging settings
config/integrations.yaml            # External tool integration (Slack/GitHub/output)
config/review_criteria.yaml         # Language-specific review checklists (cross-review)
status/agent_status.yaml            # Agent status (real-time)
queue/oyabun_to_kashira.yaml        # Oyabun → Kashira instructions
queue/tasks/worker{N}.yaml          # Kashira → Worker assignment (dedicated per worker)
queue/reports/worker{N}_report.yaml # Worker → Kashira report
queue/inbox/{agent}.queue           # File-based inbox (reliable message backup)
queue/approval_required.yaml        # Human intervention request (pending approval)
dashboard.md                        # Dashboard for master (Japanese)
task.md                             # Task ledger (kashira handover, full cmd history)
memory/patterns.yaml                # Learning pattern DB (success/failure/workarounds)
memory/global_context.md            # Global context (preferences, standards)
logs/YYYY-MM-DD_cmd_XXX.md          # Per-task work log
outputs/{project}/{cmd_id}/         # Deliverable output directory
apps/catalog.md                     # App catalog (user-managed, not in repo)
apps/sync_catalog.sh                # catalog.md → Google Drive auto-sync (user-managed)
scripts/detect-persona.sh           # Auto-detect agent persona from tmux pane
```

## App Catalog

`apps/catalog.md` manages the list of project apps.
`apps/` directory is in `.gitignore`, so each user manages it independently.

**Note**: Each worker has a dedicated task file (e.g., queue/tasks/worker1.yaml).
This prevents workers from accidentally executing another member's tasks.

### Features (v2.1)

#### Auto Error Retry
- Workers auto-retry up to 3 times on error (changing approach each time)
- After 3 failures, report to kashira with `retry_exhausted: true`
- Kashira reassigns to another worker or escalates

#### Task Priority Management
- Task YAML has `priority: high|medium|low` field
- Kashira distributes evenly based on priority and load

#### Code Review
- Kashira reviews code deliverables (syntax/security/performance/readability)
- Issues trigger `review_feedback` with revision instructions

#### Learning System
- `memory/patterns.yaml` accumulates success/failure patterns
- Workers reference patterns before starting tasks
- Kashira includes relevant patterns in `hints` when assigning tasks

#### Human Intervention Points
- Critical decisions go to `queue/approval_required.yaml` + dashboard.md "Action Required"
- After approval, oyabun → kashira to continue work

#### External Tool Integration
- Slack webhook (completion/error/approval-pending notifications)
- GitHub auto-commit (outputs/, docs/ only)
- Local output (organized in outputs/)

#### Progress Dashboard
- `status/agent_status.yaml` tracks each agent's state in real-time
- dashboard.md displays agent status table

#### Work Logs
- `logs/YYYY-MM-DD_cmd_XXX.md` records in timeline format
- Errors marked with ⚠

## tmux Session Layout

### oyabun Session (1 pane)
- Pane 0: Oyabun (boss cat)

### multiagent Session (5 panes)
- Pane 0: Kashira (head cat)
- Pane 1: Worker1 (1号猫)
- Pane 2: Worker2 (2号犬)
- Pane 3: Worker3 (3号猫)
- Pane 4: Worker4 (4号猫)

## Language Settings

Set language in config/settings.yaml:

```yaml
language: ja  # ja, en, es, zh, ko, fr, de, etc.
```

### language: ja
Cat-style Japanese only. No bilingual annotations.

### language: other than ja
Cat-style Japanese + user language translation in parentheses.

## Instruction Files
- instructions/oyabun.md - Oyabun (boss cat)
- instructions/kashira.md - Kashira (head cat)
- instructions/_worker_base.md - Common worker template (shared by all workers)
- instructions/1gou-neko.md - Worker1 (polite cat) - personality diff only
- instructions/2gou-inu.md - Worker2 (dog-cat) - personality diff only
- instructions/3gou-neko.md - Worker3 (laid-back cat) - personality diff only
- instructions/4gou-neko.md - Worker4 (cool cat) - personality diff only

## Summary Generation Requirements

When generating a compaction summary, always include:

1. **Agent role**: oyabun / kashira / worker
2. **Key forbidden actions**: The agent's forbidden action list
3. **Current task ID**: Active cmd_xxx

This ensures role and constraints are immediately understood after compaction.

## MCP Tool Usage

MCP tools use lazy loading. Always search with `ToolSearch` before use.

```
Example: Using Notion
1. Search "notion" with ToolSearch
2. Use the returned tool (mcp__notion__xxx)
```

**Installed MCPs**: Notion, Playwright, GitHub, Sequential Thinking, Memory

