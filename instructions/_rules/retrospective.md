# Retrospective (Post-Cmd Review)

> **Purpose**: After every large cmd completes, the team spends ~5 minutes reflecting on what went well, what went poorly, and what to carry forward. Modeled on agile retrospectives but lightweight and async.

## When to Trigger

**Mandatory** (kashira auto-triggers after writing cmd_complete to inbox):
- Any cmd with `effort: L` or total effort > 4 hours
- Any cmd with ≥ 3 subtasks
- Any cmd that hit a BLOCKER during execution
- Any cmd that goshujinsama flagged as important (via `retrospective_required: true` in YAML)

**Optional** (kashira may trigger):
- Small cmds that surfaced a new pattern worth capturing
- Any cmd where a worker said "this was hard" in their report

**Skip** (don't waste cycles):
- Trivial cmds (effort S, 1 subtask, no issues)

## Protocol

**Duration target**: 5 minutes of wall time. If longer is needed, split into per-worker async async input + 5-min kashira synthesis.

### Step 1: Kashira prepares the prompt

Kashira writes a retrospective task to `queue/tasks/retrospective_{cmd_id}.yaml`:

```yaml
retrospective:
  cmd_id: cmd_XXX
  participants: [worker1, worker3, worker4]   # only workers who participated
  questions:
    - "What went well? (1 line)"
    - "What went poorly or surprised you? (1 line)"
    - "What should we do differently next time? (1 line, actionable)"
  output_file: "queue/reports/retrospective_{cmd_id}.yaml"
  deadline: "2 hours from dispatch"   # soft; if missed, kashira proceeds without
```

### Step 2: Kashira notifies participants (2-call send-keys per worker)

Message: `"Retrospective for {cmd_id}. Add your input to queue/reports/retrospective_{cmd_id}.yaml within 2h. See queue/tasks/retrospective_{cmd_id}.yaml."`

### Step 3: Workers append their input

Each worker appends (not overwrites) their section to the output file:

```yaml
worker1:
  went_well: "..."
  went_poorly: "..."
  next_time: "..."
```

No send-keys notification needed — kashira checks the file after deadline.

### Step 4: Kashira synthesizes

Kashira reads all inputs, writes a synthesis section at the top:

```yaml
synthesis:
  patterns_to_save: [...]     # → memory/patterns.yaml candidates
  process_improvements: [...] # → CLAUDE.md or instructions/ updates
  team_mood: "positive | neutral | fatigued"
  handoff_to_oyabun: [...]    # items needing goshujinsama awareness
```

### Step 5: Kashira reports to oyabun (inbox + send-keys)

```bash
echo "$(date +%Y-%m-%dT%H:%M:%S)|kashira|retrospective_done|cmd_XXX" >> queue/inbox/oyabun.queue
```

Send-keys message: `"Retrospective for {cmd_id} complete. See queue/reports/retrospective_{cmd_id}.yaml. {N} improvement items to review."`

### Step 6: Oyabun decides

Oyabun reads the synthesis and:
- Saves patterns to `memory/patterns.yaml` (if pattern candidates)
- Updates CLAUDE.md / instructions (if process improvements)
- Forwards relevant items to goshujinsama (if handoff_to_oyabun has content)
- Archives the retrospective file (no delete — historical record)

## Anti-Patterns

- **Blame culture**: never mention "X messed up". Focus on process, not people.
- **Wishful thinking**: "next_time" must be actionable, not "we should be more careful"
- **Skipping when things went well**: successes also teach. Capture what to repeat.
- **Long retros on small cmds**: 5-min cap is a feature, not a bug.

## Integration Points

- Triggers: `kashira_policies.md` § cmd_completion_protocol
- Output sink: `memory/patterns.yaml` (patterns), CLAUDE.md (process)
- Historical: `queue/reports/retrospective_*.yaml` accumulate over time
