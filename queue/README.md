# queue/ Directory Guide

Runtime message bus for the neko multi-agent system. **All files here are
ignored by git** (see `.gitignore`) — they represent per-machine ephemeral
state, not source of truth.

## Top-level files

| Path | Owner | Purpose |
|------|-------|---------|
| `oyabun_to_kashira.yaml` | oyabun writes, kashira reads | Active cmd list with status. The authoritative queue of what's being worked on. |
| `approval_required.yaml` | kashira writes, oyabun reads | Human intervention requests. Surfaces in dashboard.md "Action Required". |
| `pending_files.yaml` | kashira | Files awaiting review/commit. |
| `upgrade_plan.yaml` | kashira | Multi-step upgrade roadmaps that outlive a single cmd. |

## Subdirectories

### `tasks/` — Kashira → Worker assignments
- `worker{1..4}.yaml` — one file per worker (prevents a worker from grabbing another worker's task by accident).

### `reports/` — Worker → Kashira reports
- `worker{N}_{slug}_report.yaml` — per-subtask deliverable report.
- `_archive/YYYY-MM/` — auto-moved by `scripts/archive-reports.sh` after the cmd closes and 7 days pass.

### `inbox/` — File-based message backup (reliable delivery)
- `{agent}.queue` — append-only log of notifications. Written in pair with `tmux send-keys` so a missed keystroke can still be recovered.
- Format: `<ISO-8601>|<sender>|<event>|<detail>`
- Agents: `oyabun.queue`, `kashira.queue`, `worker{1..4}.queue`.
- Legacy: `worker{5..7}.queue` exist but are empty (Haiku workers, deprecated — see commit 5de15ad).

### `voice/` — Direct worker feedback channel (oyabun reads)
- `consult_NNN_wN.md` — worker-initiated consultation when they need oyabun-level judgment mid-task. Bypasses kashira for speed but is visible to kashira.
- `kashira_cmd_NNN.md` — kashira's scratch / talking-points for an in-progress cmd, before formal queue entries.
- Read on demand; no rotation.

### `suggestions/` — Improvement proposals
- See `suggestions/README.md` for structure.
- Workers/kashira drop proposals here; oyabun reviews async.

### `skill_proposals/` — New skill proposals
- Workers use this when they spot a repeatable pattern that should become a reusable skill under `skills/neko-*`.
- `_archive/` holds rejected/implemented proposals.

### `templates/` — Starter files
- `cmd_template.yaml` — copy into `oyabun_to_kashira.yaml` when drafting a new cmd.

## Locking

Concurrent writers (kashira + workers) should use `scripts/yaml-append.sh`
for atomic appends. Direct `Edit`/`Write` is tolerated but risks merge
corruption if two agents hit the same file within ~1s.

## Retention

| Path | Policy |
|------|--------|
| `reports/*.yaml` | `scripts/archive-reports.sh` — closed-cmd reports > 7 days old → `_archive/YYYY-MM/`. |
| `inbox/*.queue` | append-only, no auto-rotation. Prune manually if > 10k lines. |
| `voice/*.md` | append-only, no auto-rotation. |
