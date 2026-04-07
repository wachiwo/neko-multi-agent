---
# Kashira Policies & Protocols
# Referenced from kashira_core.md — loaded on demand
---

# Kashira Policies & Protocols

> **Core instructions**: See `instructions/kashira_core.md` for role, workflow, tmux, dashboard,
> and daily operation procedures.

## Command Splitting Rule (大規模cmd分割)

Large cmds exhaust kashira's context before completion. **Estimate context cost upfront and split when needed.**

### Context Cost Estimation

Each report-processing cycle (assign task + read report + update dashboard) costs context.
Estimate total cycles: **phases × workers = cycles**.

| Phases | Workers | Est. Cycles | Verdict |
|--------|---------|-------------|---------|
| 1 | 1-4 | 1-4 | No split needed |
| 2 | 1-4 | 2-8 | Split recommended if 4 workers |
| 3+ | 1-2 | 3-6 | Split recommended |
| 2+ | 3-4 | 6-12 | **Split recommended** |
| 3+ | 3-4 | 9-16+ | **Split mandatory** |

**Rule of thumb**: 10+ report cycles in one session → split mandatory.

### How to Split

1. **Identify phase boundaries** — natural break points where state is fully captured in files
2. **Create sub-cmds**: `cmd_XXXa` (Phase 1), `cmd_XXXb` (Phase 2), `cmd_XXXc` (Phase 3)
3. **Each sub-cmd is a self-contained session** — kashira can be restarted between them
4. **State handoff via task.md** — record all subtask outcomes before ending sub-cmd

Example:
```
cmd_021 (3 phases × 4 workers = 12 cycles) → SHOULD HAVE BEEN:
  cmd_021a: Phase 1 brainstorm (4 workers, 4 cycles) → /compact
  cmd_021b: Phase 2 implementation (4 workers, 4 cycles) → /compact
  cmd_021c: Phase 3 review+fix (4 workers, 4 cycles) → /compact
```

### Split Proposal Format

When kashira detects a cmd needs splitting, propose to oyabun:
```
cmd_XXXは推定N cycles（Xフェーズ × Yワーカー）のため、sub-cmd分割を提案:
  cmd_XXXa: [Phase 1 description] (est. N cycles)
  cmd_XXXb: [Phase 2 description] (est. N cycles)
```

### State Handoff Between Sub-cmds

Before ending a sub-cmd:
1. Update task.md with all subtask outcomes (the primary state source)
2. Update dashboard.md progress
3. Run `/compact`
4. Notify oyabun: "sub-cmd完了。次のsub-cmd開始を指示してください"

After restart for next sub-cmd:
1. Read task.md to restore full state
2. Continue from where the previous sub-cmd left off

### Relationship to Task Decomposition

This rule does NOT change how tasks are decomposed (see "Think Before Decomposing Tasks").
It only changes **when kashira checkpoints and restarts** during multi-phase execution.
Task quality, worker count, and persona design remain kashira's independent decisions.


## Context Budget Threshold (コンテキスト残量管理)

Kashira must self-monitor context consumption and proactively checkpoint before exhaustion.

### Threshold Triggers

Checkpoint when ANY of the following conditions are met:

| Trigger | Threshold | Action |
|---------|-----------|--------|
| Report count | 8+ reports read in current session | Checkpoint recommended |
| Phase count | 3+ phases processed | Checkpoint mandatory |
| Conversation length | Conversation feels long (many tool calls, large outputs) | Checkpoint recommended |

### Checkpoint Procedure

When a threshold is reached and all currently-assigned workers have reported:

1. **Update task.md** — record all subtask statuses, current phase, next steps
2. **Update dashboard.md** — reflect latest progress
3. **Update agent_status.yaml** — accurate agent states
4. **Notify oyabun**: "context節約のため再起動を推奨にゃ。task.mdに状態記録済み。次のsub-cmd指示をお願いしますにゃ"
5. **Run `/compact`**

### Recovery After Restart

task.md is the single source of truth for state recovery:
1. Read task.md → understand cmd progress, completed subtasks, pending work
2. Read dashboard.md → verify master-facing status
3. Resume coordination from the recorded state

### What NOT to Do

- Do NOT checkpoint while workers are actively processing (reports not yet received)
- Do NOT skip task.md update before checkpointing (state would be lost)
- Do NOT wait until 0% context — checkpoint proactively at the threshold triggers above


## Cross-Review Protocol

Cross-review assigns a **different worker** to review code produced by the original author.

### When to Apply

| Task Type | Cross-Review? | Reason |
|-----------|:---:|--------|
| New code ≥ 50 lines | Yes | High logic volume |
| Bug fix / refactor | Yes | Regression risk |
| Security-related config | Yes | Second eye mandatory |
| Text / documentation | No | Low risk |
| Single file < 30 lines | No | Kashira review sufficient |
| Trivial (1 file, <=10 lines) | No | Auto-verification sufficient |

**Precedence**: Priority-Linked Review Depth (below) refines these rules by task priority. When in conflict, Priority-Linked overrides this table.

### Reviewer Assignment

1. **Different worker** from author (mandatory)
2. **Idle worker** preferred (check via `tmux capture-pane`)
3. **Rotation** — avoid same reviewer pair consecutively
4. **Language experience** — prefer workers with track record in the language
5. **Fallback** — if all busy, kashira performs solo review

### Cross-Review Flow

```
Author → report (awaiting_review: true)
  → Kashira creates review task for reviewer
  → Reviewer reads + reviews (does NOT modify code)
  → cross_review_report
  → Kashira: lgtm → done | minor → fix instructions | major → fix + error log
```

### Task YAML Fields

Implementation task: include `language`, `cross_review` block (`enabled`, `reviewer_worker`, `review_criteria`, `focus_areas`).

Review task: include `type: cross_review`, `review_target` (`original_worker`, `original_task_id`, `files`), `language`, `review_criteria`, `focus_areas`, `p2p_review` (optional).

See `queue/reports/` for YAML examples.


## Priority-Linked Review Depth

Review effort scales with task priority. Not all tasks deserve full cross-review ceremony.

| Priority | Review Type | Reviewer | Checklist |
|----------|-----------|----------|-----------|
| high | Full cross-review | Different worker | B1-B5 + language-specific |
| medium | Lightweight review | Kashira solo | B1-B5 only |
| low | Self-review | Original worker | B1-B3 (syntax, security, perf) |
| trivial | Auto-verify only | N/A (skip) | Auto-verification command |

### Override Rules

| Condition | Action |
|-----------|--------|
| medium + security-related | Escalate → full cross-review |
| medium + estimated_effort: large | Escalate → full cross-review |
| medium + new code ≥ 50 lines | Escalate → full cross-review |
| low + new code ≥ 50 lines | Escalate → lightweight review |
| Any + goshujinsama says "internal use only" | May skip cross-review entirely |

Self-review tasks: worker adds `self_review: { checked: [B1, B2, B3], notes: "..." }` to report.


## Language-Specific Review System

Use `config/review_criteria.yaml` for structured, language-aware reviews.

### Language Auto-Detection

| Extension | Language Key |
|-----------|-------------|
| .html, .htm, .css | html_css |
| .php | php |
| .cs | csharp |
| .scss, .sass | scss |
| .cpp, .cc, .h, .hpp | cpp |

When multiple languages: `review_criteria: "csharp,html_css"`

### Embedding Checklists in Review Tasks

1. Read `config/review_criteria.yaml`
2. Look up language key(s) from `extension_map`
3. Include base checklist (B1-B5) + language-specific items in `focus_areas`
4. Add task-specific focus areas on top

Kashira does NOT modify review_criteria.yaml — it is reference-only.


## Cross-Review Dispute Resolution

When the original author disagrees with a reviewer's finding, kashira acts as final arbiter.

### Dispute Flow

```
Author: "I disagree with F1"
  → Kashira reads review + objection
  → Final call: Uphold → must fix | Dismiss → no action | Compromise → alternative
  → Record decision in work log
```

### Decision Criteria

| Factor | Consider |
|--------|----------|
| Severity | high findings get stricter scrutiny |
| Spec compliance | Does the code meet the original objective? |
| Best practice | Is the reviewer's suggestion actually better? |
| Pragmatism | Is the fix worth the effort? |

Kashira's decision is **final** for the current task. If uncertain, escalate to dashboard.md "要対応".


## Package Installation Safety (SLOP-001)

LLMs hallucinate package names. Attackers register these names with malware (slopsquatting).

### Kashira's Role

1. **When assigning tasks that involve new dependencies**: Add `slopsquatting_check: true` to the task YAML hints.
2. **When reviewing worker reports**: If a worker installed a new package, verify the package name is legitimate before marking the task as done.
3. **If a worker reports `blocked` due to an unverified package**: Check the registry yourself (npm/PyPI). If still uncertain, escalate to dashboard.md "要対応" for goshujinsama's decision.

### Red Flags

- Package name looks like two real packages combined (e.g., `express-mongoose`)
- Package registered very recently with few downloads
- Publisher has no other packages or no profile
- Package name exists in one ecosystem but was suggested for another (e.g., Python name used for npm)

## Security Review Protocol

Security review adds attacker/defender analysis to the cross-review phase. Triggered by `security_review: required` on the parent cmd. Default is `security_review: skip` (no action needed).

### When to Trigger

| `security_review` value | Action |
|--------------------------|--------|
| `required` | Assign 2 workers with opposing security roles |
| `skip` (default) | No security review — standard cross-review only |

### Assignment Rules

1. During cross-review phase, assign **2 separate workers** to security review (in addition to normal cross-review)
2. One worker gets `security_role: black_hacker`, the other gets `security_role: white_hacker`
3. Both review the **same deliverables** from opposite perspectives
4. Kashira decides role assignment — oyabun does not specify which worker gets which role
5. Prefer assigning workers who did NOT implement the deliverable under review
6. Workers use checklists from `config/review_criteria.yaml` → `security_review` section

### Security Review Task YAML Format

```yaml
task:
  task_id: security_review_{cmd_id}_{NNN}
  parent_cmd: cmd_XXX
  type: security_review
  security_role: black_hacker  # or white_hacker
  priority: high
  description: "Security review from attacker/defender perspective"
  review_target:
    files:
      - "outputs/project/file1.cs"
      - "outputs/project/file2.cs"
  review_criteria: security_review  # points to security_review section in review_criteria.yaml
  status: assigned
```

### Report Handling

- Security review reports use the same cross-review report format (`type: cross_review_report`)
- Add `security_role: black_hacker|white_hacker` to the report for traceability
- Findings with `severity: high` from either role block the deliverable (same as normal cross-review)
- Kashira consolidates both reports before marking deliverable as approved


## Interface Contracts (Phase 0.5)

Before Phase 1 (implementation), kashira defines module interface contracts for large tasks.
Prevents boundary mismatches — root cause of cmd_025's cartesian product disaster.

### When to Apply

| estimated_effort | Interface Contract? |
|-----------------|:---:|
| small | No |
| medium | Optional (if 2+ workers produce connected modules) |
| large | **Mandatory** |

### What to Define (Boundaries Only)

| Include | Exclude |
|---------|---------|
| Function signatures with types | Internal helper functions |
| Output dict keys + value types | Algorithm choices |
| Shared constants (mappings, enums) | Variable names |
| Conventions (difference formula, config format) | Test strategy |
| Edge cases (empty values, None, missing) | Performance optimization |

**Maximum 40 lines per contract.** Exceeding 40 = over-specification.

### Generic Template

```yaml
interface_contract:
  modules:
    - name: "module_a.function_name"
      signature: "function_name(args) -> return_type"
      output_keys: [key1, key2, key3]
      output_types: { key1: str, key2: "int|None" }
    - name: "module_b.consumer"
      input_source: "module_a.function_name output"
      required_keys: [key1, key2]
  shared_constants:
    MAPPING_NAME: { value1: "mapped1", value2: "mapped2" }
  conventions:
    calculation: "description of formula"
  edge_cases:
    - "empty input handling"
    - "no match: field=None, status='unknown'"
```

### Phase Flow

```
Phase 0:   Design Review (large tasks only — see Pre-Implementation Design Review)
  → Phase 0.5: Interface Contracts (kashira defines)
  → Phase 1: Implementation (parallel workers)
  → Phase 1.5: Integration Test Gate (1 non-author worker)
  → Phase 2: Cross-Review (parallel reviewers)
  → Phase 3: Fix (if needed)
```

### Creating Interface Contracts

1. Read oyabun's spec
2. Identify module boundaries (which workers produce/consume shared data)
3. Write contract: function signatures, output keys, shared constants, edge cases
4. Include in each worker's task YAML (or reference shared contract file)
5. Workers implement accordingly — internal approach is their choice

### Relationship to D5 (Spec-Driven Requirements)

```
D5 (Oyabun Spec) ──> D4 (Interface Contracts) ──> Phase 1 (Implementation)
                                                     │
                                       Phase 1.5 verifies contract compliance
```

- D5 provides domain knowledge from oyabun/goshujinsama
- D4 translates domain knowledge into technical contracts
- Phase 1.5 verifies implementations comply
- If D5 is wrong, interface contracts propagate the error


## Pre-Implementation Design Review (Phase 0)

For large tasks, require a design review before parallel implementation begins.

### When to Apply

| Trigger | Design Review? |
|---------|:---:|
| estimated_effort: large | **Mandatory** |
| estimated_effort: medium + 3+ workers | Optional (kashira decides) |
| estimated_effort: small/medium + 1-2 workers | No |

### Design Review Flow

```
Step 1: One worker writes design doc → outputs/{cmd_id}/design.md
Step 2: Different worker reviews design doc
  → Pass: Proceed to Phase 0.5 (Interface Contracts), then Phase 1
  → Fail: Author revises, re-review (max 2 rounds)
```

### Design Doc Requirements (max 80 lines)

| Section | Content |
|---------|---------|
| Architecture | Module decomposition, data flow |
| Interfaces | Key function signatures, shared data formats |
| Risks | Known risks and mitigation |
| Acceptance criteria | How to verify the implementation is correct |

### Assignment Rules

- Design author: worker with most domain experience for the task
- Design reviewer: different worker (mandatory)
- After design review passes, kashira creates Phase 0.5 interface contracts as usual


## Integration Test Gate (Phase 1.5)

After Phase 1 and before Phase 2, kashira can insert integration smoke tests.
A non-author worker writes 3-5 tests tracing data through the full pipeline.

### When to Enable

| `integration_test_gate` | When |
|---------|-------------|
| `true` | Multi-module tasks (2+ connected workers), DB JOIN tasks, scraping tasks |
| `false` (default) | Single-file edits, docs, consultations, lightweight, single-worker |

### Integration Task Assignment

After all Phase 1 workers report done, assign integration task:
- **Non-author** worker (mandatory — must NOT have written any module being tested)
- Include: `type: integration_test`, `modules` (worker + output_format for each), `expected_checks`
- See `queue/reports/` for integration task YAML examples

### What the Tester Does

1. Read all modules listed
2. Write 3-5 smoke tests connecting modules end-to-end
3. Run tests
4. Pass → `status: done` | Fail → `status: failed` with interface mismatches identified

### If Integration Fails

Kashira creates fix tasks for relevant workers. Tester re-runs after fixes.
Cross-review (Phase 2) does NOT start until integration passes.

### Minimum Checks

| Check | Why |
|-------|-----|
| Row count sanity | Catches cartesian products (fp_004) |
| Key set equality | Catches model name mismatches |
| NULL field detection | Catches JOIN failures |
| Config access paths | Catches config nesting mismatches (fp_002) |


## P2P Review & Heads-Up Messaging (Kashira-Controlled)

Both allow direct worker-to-worker communication. Kashira controls both toggles per task. Both default to off.

### P2P Review (`p2p_review: true`)

For cross-review tasks. Workers exchange review feedback directly.

| Setting | When to Use |
|---------|-------------|
| `false` (default) | Complex tasks, high-risk changes, unfamiliar workers |
| `true` | Simple reviews, low-risk, both workers experienced |

### Heads-Up (`heads_up: true`)

For parallel work. Workers share real-time findings (patterns, pitfalls) with siblings.

| Setting | When to Use |
|---------|-------------|
| `false` (default) | Independent file work, lightweight tasks, consultations |
| `true` | Same codebase parallel work, heavy tasks with shared pitfalls |

### Common Rules

1. **CC to kashira is MANDATORY** — every message appended to `queue/inbox/kashira.queue`
2. CC format: `timestamp|sender|{p2p_review|heads_up}|to:{target}|summary:{description}`
3. Kashira monitors CC during inbox sweep; intervenes on scope creep or confusion
4. P2P exceeds **3 round-trips** without resolution → kashira takes over
5. Workers who skip CC get a warning (repeat → feature disabled)

### What Neither Changes

- Task assignment → kashira only
- Escalation → kashira only
- Direction/scope changes → kashira only
- Final review result → normal report YAML to kashira


## Error Reassignment Protocol

When a worker fails after 3 retries (`retry_exhausted: true`):
- Another worker can handle it → Reassign (include `original_worker`, `original_error`, `retry_history` in task)
- No worker can handle it → Escalate to dashboard.md "要対応"


## Bug Fix Assignment Rule (Different-Worker Mandatory)

When a bug is found in a worker's output:
1. **NEVER** assign the fix to the same worker who produced the buggy output
2. The original worker has confirmation bias from creating the file
3. Assign to a **DIFFERENT** worker for fresh eyes

Exception: if only 1 worker is available, allowed but MUST note: "Same-worker assignment (only worker available) — confirmation bias risk acknowledged"

### Layout Task Verification

For layout-affecting tasks (Bootstrap conversion, CSS changes, grid/sidebar):
1. Verify OUTCOME (symptom resolved), not just ACTION (change applied)
2. Worker reports must include Playwright screenshot evidence OR explicit disclaimer: "Visual/layout verification not possible from CLI — browser check required"
3. Never accept "ALL CLEAN" for layout tasks without visual evidence or explicit disclaimer


## D8: ワーカー分担ルール（kashira向け）

外部bridgeタスクの結果をdone報告する前に、以下の機械チェックを実施すること（fail-closed）:

| # | チェック項目 | 失敗時 |
|---|-------------|--------|
| 1 | `worker_report_paths` のファイルが全て実在する | blocked |
| 2 | レポートの `task_id` が当該タスクと一致する | blocked |
| 3 | レポートファイルが空でない（最低限「結論」セクションが存在する） | blocked |

追加の責務:
- `worker_count` の正確性を最終確認してから outbox に記載する
- 分担必須タスク（レビュー、分析、大量処理等）で単独実行が報告された場合、差し戻す


## Bloom Routing (Model Tier Assignment)

Kashira routes tasks to the appropriate model tier based on Bloom's Taxonomy.

### Decision Rule

Ask one question: **"Does a procedure or skill exist for this task?"**

| Answer | Bloom Level | Model | Workers | Instruction Set |
|--------|-------------|-------|---------|-----------------|
| ALL tasks | L1-L6 | Sonnet | W1, W2, W3, W4 | _worker_base.md |

> **Note**: W5 (Haiku) was removed from active roster (2026-03-11). All tasks go to Sonnet W1-W4.


## Complexity-Weighted Task Distribution

When distributing batch tasks, weight by complexity, not file count:

| Type | Points |
|------|--------|
| Simple (config, docs, small edits) | 1 |
| Medium (list screens, standard forms) | 2 |
| Complex (multi-tab, many fields) | 3 |
| Very Complex (1000+ lines, nested structures) | 5 |

Target: equal points per worker, not equal files.


## Batch CSS Quality Gate (G1)

Batch CSS tasks (modifying 5+ files) require mandatory quality controls. Introduced after cmd_080 (84 files, cross_review: skip) caused regressions requiring cmd_088 emergency scan.

### Rule: Cross-Review Never Skipped

| Condition | cross_review |
|-----------|:---:|
| Batch CSS modifying 5+ files | **required** (never skip) |
| Batch CSS modifying < 5 files | Normal priority-linked rules apply |

Rationale: cmd_080 skipped cross-review for speed. Workers introduced scope-external CSS changes (overflow:hidden, narrow regex) that went undetected until goshujinsama found them manually.

### scope_lock Mandate

All batch CSS task YAMLs MUST include a `scope_lock` block:

```yaml
scope_lock:
  do_not_change:
    - "overflow (on any element)"
    - "z-index"
    - "position"
  change_only:
    - "max-width"
    - "@media (max-width: 960px) blocks"
```

Workers who change properties outside `change_only` MUST report it in `unverified_risks`. Kashira rejects reports where diff shows undeclared property changes.

### Regex Standardization

Kashira specifies exact regex patterns in the task YAML. Workers MUST NOT invent their own.

| Bad (cmd_080) | Good |
|---------------|------|
| W1: `1900px`, W2: `1[89]00px`, W3: `1[4-9]00px` | All workers: `max-width:\s*1[0-9]00px` (kashira-specified) |

Worker autonomy on regex caused 8 files to slip through in cmd_080. Kashira provides the regex; workers apply it verbatim.

### Post-Fix Unified Scan

After batch CSS completion, assign **1 worker** to scan ALL modified files for cross-worker inconsistencies:

1. Verify all workers applied the same transformation consistently
2. Check for scope-external changes (overflow, z-index, position)
3. Report discrepancies before marking cmd as done

This catches boundary inconsistencies that per-worker self-review cannot detect (e.g., W1 regex `1900px` vs W2 regex `1[89]00px`).


## Task YAML Size Limit

Task description MUST be under 40 lines. For complex tasks:
- Write detailed spec in a separate file (e.g., `outputs/cmd_XXX/spec.md`)
- Reference it in description: "See outputs/cmd_XXX/spec.md for full spec"
- Task YAML contains only: objective, file list, critical rules, hints


## (Haiku Policy — Archived)

> W5 (Haiku) removed from active roster (2026-03-11). All tasks assigned to Sonnet W1-W4.


## Conditional Rule Injection Protocol

Workers' _worker_base.md contains ~40 rules, but only ~18 are needed every task.
The remaining ~13 are CONDITIONAL — inject them per task type to reduce worker context load.

### Source of Truth

`config/rule_profiles.yaml` defines:
- **Profiles**: 7 task type profiles mapping to rule sets
- **Auto-inject**: rules triggered by task YAML fields (priority, p2p_review, etc.)
- **Rule sections**: maps rule IDs to _worker_base.md line ranges
- **Fallback**: inject all conditional rules when task type is unclear

### How Kashira Uses This

When creating a task YAML for a worker:

1. **Determine task type** from the task description/action
2. **Select profile(s)** from `config/rule_profiles.yaml`
   - Primary: one of `css_task`, `cross_review`, `security_review`, `implementation`, `fix_task`, `batch_task`, `consultation`
   - Modifiers: add extra profiles if task has multiple aspects (e.g., batch CSS fix = `css_task` + `batch_task`)
3. **Auto-inject fires automatically** based on task YAML fields (priority, p2p_review, etc.)
4. **Combine and deduplicate** all rule sets
5. **Write `inject_rules` field** to the task YAML

### Task YAML Format

```yaml
task:
  task_id: subtask_XXX_YYY
  # ... standard fields ...
  inject_rules:          # NEW FIELD — kashira adds this
    - css_scope
    - visual_disclaimer
    - batch_protocol
```

### Worker Behavior

- Workers read ONLY core rules (KEEP sections in _worker_base.md) by default
- When `inject_rules` is present, workers ALSO read the listed conditional sections
- When `inject_rules` is absent, workers read ALL rules (backward-compatible fallback)
- Workers do NOT need to know about profiles — they only see the final rule list

### Fallback Safety

| Condition | Behavior |
|-----------|----------|
| `inject_rules` present | Worker reads core + listed rules only |
| `inject_rules` absent | Worker reads ALL rules (current behavior) |
| `inject_rules: []` | Worker reads core rules only (minimal — for consultation tasks) |
| Kashira unsure of task type | Omit `inject_rules` → full rules load (safe default) |

### Rollout Plan

Phase 1 (immediate): kashira adds `inject_rules` to task YAMLs. Workers ignore it (no _worker_base.md change yet).
Phase 2 (after _worker_base.md refactor): _worker_base.md split into core + conditional sections. Workers respect `inject_rules`.
Phase 3 (mature): conditional rules moved to `instructions/_rules/*.md` files. Workers read only referenced files.

### Relationship to Bloom Routing

`inject_rules` is orthogonal to Bloom routing (model tier selection).
All workers (W1-W4) receive the same `inject_rules` field via _worker_base.md.


## Script Dry-Run Gate (2026-03-13, cmd_159 incident)

Any script that batch-modifies multiple HTML/code files MUST pass a trial run before full deployment.

### Rule

1. **Before full batch run**: Assign 1 worker to run the script on exactly 2 representative files
2. **Review trial output**: Kashira (or cross-reviewer) checks `git diff` of the 2 files
3. **Pass criteria**: Only expected changes appear (e.g., maxlength additions), zero corruption, zero unexpected property changes
4. **Fail → fix → re-trial**: If trial shows ANY corruption or unexpected changes, fix the script and re-trial. Do NOT proceed to full batch.
5. **Pass → full deployment**: Only after trial passes, assign remaining files to workers

### Evidence

cmd_159: `field_width_adjuster.py` was run on 23 files without trial. 17 files corrupted (self-closing tag bug, CSS property doubling, stray text after `>`). A trial run on 2 files would have caught all 3 bugs before they spread.

### Exceptions

- Trivial mechanical changes with zero ambiguity (e.g., `sed 's/oldstring/newstring/g'` on known-safe patterns) may skip trial
- Single-file scripts (by definition, no batch risk)


## Cross-Review Diff-Based Verification (2026-03-13, cmd_159b incident)

Cross-reviewers MUST include `git diff --stat` output in their report. Pattern-match verification alone is insufficient.

### Rule

1. **Run `git diff --stat`** on all files modified by the original worker
2. **Compare actual vs expected change volume**: e.g., "maxlength additions should be ~1-3 lines per file; if a file shows 20+ changed lines, flag as anomaly"
3. **Include in report**:
   ```yaml
   diff_check:
     expected_lines_per_file: 3
     actual_total: 47
     anomaly: true
     anomaly_files:
       - "024_出荷一覧.html: 22 lines changed (expected ~3)"
   ```
4. **Anomaly = mandatory investigation**: reviewer must examine the anomalous file's diff line-by-line before issuing LGTM

### Evidence

cmd_159b: W4's automated verification reported "Corruption: 0" on all files. W1 and W2 found 9 corruption artifacts across 2 files by manual review. A `git diff --stat` check would have immediately flagged the anomalous change volume.

### Relationship to Existing Cross-Review

This is an ADDITIONAL check, not a replacement. The existing review checklist (B1-B5 + language-specific) still applies. Diff check is a fast pre-screen that catches gross corruption before detailed review begins.


## W3 Hybrid Role Policy (consult_030 Topic 1B)

W3はトリアージ+スキル作成の専任ではなく、ハイブリッド方式で運用する。

### 役割配分
- **修正 30%**: トリアージ全件実施後、HEAVYファイルの上位2-3件を自分で修正
- **スキル 70%**: 残り時間でスキル作成/改良

### 根拠
- HEAVYファイルはトリアージ時に最も深く見ているW3が担当すると引き継ぎロスが最小
- MODERATE以下は修正パターンが定型化しやすく、引き継ぎロスが小さい → 他Wが担当
- 修正を先にやって知見を得てから、その知見をスキルに反映する流れが効率的

### kashiraの運用
- バッチ修正タスク(10+ファイル)でW3にトリアージを割り当てる場合:
  1. W3にトリアージ全件 + HEAVY上位2-3件の修正を同時割り当て
  2. W3トリアージ完了後、MODERATE/MINOR修正を他Wに配分
  3. W3は修正完了後、スキル作成に移行
- 小規模タスクではこのポリシーは適用不要(通常の割り当てルール)

## Multi-Cmd Queue Processing (キュー順次処理ポリシー)

Oyabun may stack multiple cmds in `queue/oyabun_to_kashira.yaml`. Kashira processes them sequentially without waiting for a new send-keys wakeup between cmds.

### Processing Order

1. **Default: FIFO** — Process cmds in the order they appear in the YAML queue (top to bottom)
2. **Exception: `priority: urgent`** — Urgent cmds preempt the queue. Finish the **current subtask** (do not abandon mid-task), then switch to the urgent cmd before continuing the remaining queue.
3. **Skip already-processed cmds** — Only pick cmds with `status: pending`. Ignore `done` or `in_progress`.

### Lifecycle

```
[Oyabun stacks cmd_A, cmd_B, cmd_C in queue]
  → Kashira reads queue
  → Picks cmd_A (first pending, or urgent if any)
  → Executes cmd_A (assign workers, collect reports, update dashboard)
  → Marks cmd_A status: done in queue YAML
  → Checks queue → cmd_B is next pending
  → Executes cmd_B
  → ...continues until no pending cmds remain
  → All done → send-keys to oyabun with summary of all completed cmds
```

### Rules

| Rule | Detail |
|------|--------|
| **Report to oyabun** | Send ONE summary send-keys to oyabun after ALL queued cmds are complete (not after each cmd). Exception: urgent cmds report immediately. |
| **Dashboard updates** | Update dashboard.md after EACH cmd completion (not batched). |
| **Urgent preemption** | If a new send-keys arrives with "urgent" while processing, finish current subtask, then read queue for the urgent cmd. |
| **Context protection** | If context is running low mid-queue, complete current cmd, save progress, and propose restart. Do NOT try to squeeze in more cmds. |
| **Status tracking** | Mark each cmd `status: in_progress` when starting, `status: done` when complete. |

