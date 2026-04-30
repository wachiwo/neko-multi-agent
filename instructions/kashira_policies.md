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


## Spec Drafting Quality (2026-04-30 cmd_217/cmd_216 spec error incidents)

**背景**: cmd_217 で kashira が collapsible canonical pattern を `<h2 + class="indicator">` と起票したが、実 縦版 016 SSOT は `<div + class="collapsible-indicator">`、命名 drift 混入で W4 hotfix 必要に。さらに cmd_216 #7 で aggregation doc の 043/015 取り違えを着手前に detect できず、W4 self-detect で訂正発生。両件とも ★着手前 5 分の actual file 検証★ で防げた事案。

### Rule 1: Canonical literal 引用 (要約禁止)

spec で canonical pattern (HTML structure / function signature / CSS rule 等) を定義する時:

- ★actual baseline file から literal copy + line range 引用 MUST★
- 要約 / 推測 / 記憶からの再現 ★禁止★
- 引用 format 例:
  ```markdown
  ### Canonical 基準値 (横版 016 SSOT line 99-105)

  `/mnt/i/.../new横/016_受注一覧.html` line 99-105 から literal copy:

  ```css
  .page-header .export-section {
      display: flex;
      ...
  }
  ```
  ```

- file path + line range が必ず示されている
- worker は spec の literal block を byte-match で port する

**理由 (W1+W4 提案統合)**: 要約 spec は記憶ノイズ混入リスク、line ref + literal copy は 100% 再現可能。

### Rule 2: Unverified assumptions section (任意箇所明示)

spec 起票時に **kashira 自身が「未検証 / 推測ベース」と認識する箇所** を明示する section を含める:

```markdown
## 🚨 Unverified Assumptions (kashira self-flag)

- 「053×4 file は 全て collapsible-section pattern を使用している」 — cmd_215 audit 経由の確認、本 spec 起票時に再 grep していない
- 「.export-section CSS rule の gap 値は 15px」 — 016 SSOT で確認したが他 file は cmd_217 着手前に未確認
- ...
```

worker (実装者 / reviewer) は本 section を ★最優先 audit 対象★ として確認、矛盾発見時に kashira/spec 訂正を escalate。

**理由 (W2 提案)**: kashira が「ここは未検証」と書き出せば worker が真っ先 audit、見逃し激減。

### Rule 3: 着手前 5 分 baseline byte diff (kashira 自己 task)

spec dispatch 前に kashira が:
1. 主張する canonical pattern を実 baseline file から literal grep で確認
2. 主張する数値 (▽ 10 件等) を実 file で count verify
3. 上記不整合あれば spec 訂正してから dispatch

**理由 (W4 提案)**: 後付け hotfix より着手前 5 分 audit で防げる。

### 適用条件

| Condition | Apply? |
|-----------|:---:|
| canonical pattern を新規定義する spec | **MUST** (Rule 1+2+3) |
| 既存 canonical を引用するだけ | Rule 1 のみ (line ref 必須) |
| trivial fix / typo only | 任意 |

### 関連 memory

- `feedback_spec_vs_baseline_diff_required.md` (W4 起源、本 rule の起源)
- `feedback_canonical_var_drift_fix_immediately.md` (drift 即時解消の精神延長)

### 自己採用日

2026-04-30 (consult_032 retrospective、ご主人様承認受領)


## Catalog Reference Discipline (2026-04-30 cmd_227、Tier 2 = 参照規律 4 rules)

**背景**: cmd_225_redo (2026-04-30) で degawa 007_部品一覧/ 4 sample = ★真の canonical SSOT★ が確立、worker 推測 SSOT (016/049/027) 採用禁止が ご主人様 18:30 真意で確定。dimco-parts-catalog.html (cbfbf22) が catalog SSOT、★誰が作っても同じ構造★を仕組み化するため 4 rules 体系化。

cmd_226 以降の DIMCO 全 cmd で適用 MUST。Spec Drafting Quality 3 rules (上記) と補完関係 (Spec = canonical 起票時、Catalog = 既存 catalog 参照時)。

### Rule 1: Catalog 参照 MUST

worker は新規実装 / 修正タスク受領時、★dimco-parts-catalog.html を必ず先に参照★ MUST。

- 該当部品 (table / form / modal / button / 等) を catalog で確認
- catalog 内 line ref (canonical 引用元 + line range) を report に明示
- catalog 未参照のまま実装着手禁止

**理由**: cmd_225_redo 以前は worker 推測 SSOT (016/049/027 各々) で drift 続発、各 worker 「自分の知っている baseline」起点で実装。catalog 参照を強制すれば SSOT 一元化。

### Rule 2: 推測実装禁止

★worker が canonical を判断しない、catalog にない部品はカタログ追加から始める MUST★。

- catalog に該当部品がない → 「推測でこれが canonical だろう」で実装禁止
- 代わりに kashira 経由で catalog 追加 dispatch 起票 (cmd_226+ で別 phase)
- catalog 追加完遂後、catalog 準拠で実装

**理由**: cmd_225 W3 critical finding (二段ヘッダー = degawa 不在) で「worker 推測せず escalate」が適切判断と確認、worker は推測しないことが正解。

### Rule 3: コピペ + データ差替方式 MUST

★catalog 部品を literal copy + データ差替★ で実装。独自実装禁止。

- HTML structure / class 名 / inline style = catalog 部品 byte-match copy
- ★差し替えるのは ★data 部分 (input value / option text / label テキスト等) のみ★★
- structure / class / style 改変禁止

**理由**: cmd_206 第 5 段階 (DIMCO form 構造 049 .excel-table 統一) + cmd_217 collapsible 命名 hybrid drift (kashira spec 起票 error → W4 hotfix) 等の drift 事故 root cause = worker 独自実装。コピペ徹底で root prevention。

### Rule 4: drift 発見時 → catalog 準拠に戻す MUST

drift 発見時、★catalog 準拠に戻す★ MUST。drift 残置禁止。

- cross-review / audit / ご主人様目視 で drift 発見
- 即時 catalog 準拠に戻す hotfix dispatch (cmd_217 hotfix / cmd_225_redo emergency hotfix と同 protocol)
- drift 残置 = 次 cmd で別 worker が drift を canonical と誤認するリスク (cmd_205 撤回事故起因)

**理由**: feedback_canonical_var_drift_fix_immediately.md (cmd_205 教訓) を catalog 起点で再強化、drift 即時解消が PERMANENT rule の核心。

### 自己採用日

2026-04-30 (cmd_227、ご主人様 19:32『全部進めて』指示)


## Integration Quality Gates (2026-04-30 cmd_227、Tier 4 = 統合品質 3 rules)

**背景**: cmd_225_redo emergency hotfix 事故 (2026-04-30 18:40 ご主人様発見『パーツ全然おかしい、ほぼ何も表示されていない』) が root cause = subtask_225_redo_005 W1 reintegration で「Playwright 8 mandatory check ALL PASS」報告したが HTML 多重ネスト破綻 (outer header unclosed + sidebar 3 closing div 欠落 + body max-width:1100px 制約) で layout 崩壊。computed style 単体 PASS 信仰 = feedback_phase_gate_actual_render 直撃違反。3 段階 deep fix で hotfix 64e1eee 完遂。本 3 rules で system level verify gap 解消、cmd_226 以降全 integration cmd で適用 MUST。

### Rule 1: HTML validator 通過確認 MUST

統合担当 (kashira / 統合 worker) は HTML 統合後、★HTML validator (htmlhint or W3C) 通過確認★ MUST。

- validator 実行 (htmlhint CLI or W3C validator API)
- output が clean (errors 0) を report に明示
- unclosed tag / nesting bug を実装段階で catch

**理由**: cmd_225_redo subtask_005 で outer header + div.logo unclosed + sidebar 3 closing div 欠落 = HTML validator 通せば 1 段階目で即発見可能だった。3 段階 deep fix が必要にならなかった。

memory: feedback_html_validator_required.md (W1 起票)

### Rule 2: Playwright integration_verify は visual screenshot 目視確認 MUST

Playwright JSON ALL PASS 報告前に、★Read tool で screenshot 画像を開いて目視確認★ MUST。

- 全 viewport (375 / 960 / 1920) screenshot 撮影
- ★Read tool で image 開いて目視 verify★ (visible layout / content render / no overflow)
- Playwright check 出力 vs image visual 不整合あれば image visual 優先
- kashira / 統合担当 / cross-reviewer ★3 重 image visual verify★ MUST (cmd_225_redo hotfix で実証)

**理由**: cmd_225_redo subtask_005 W1「Playwright 8 ALL PASS」は computed style + element exists 自動 check のみで visible layout 崩壊 detect 不可能だった。feedback_phase_gate_actual_render (cmd_202 教訓) と同型 incident 再発 = system level rule 強化必要。

memory: feedback_visual_screenshot_verify_must.md (W2 起票)、feedback_phase_gate_actual_render.md (補完)

### Rule 3: Cross-review はセクション単位 + 統合後全体 review MUST

Multi-worker integration cmd では、★(a) section 単位 mutual cross-review + (b) 統合後 全体 HTML structure review★ の 2 段階 MUST。

- section 単位 mutual XR = Bug Fix Rule 通常運用 (各担当 section の verify)
- ★統合後全体 review = 1 名の worker (or kashira) が file 全体を読み、HTML tag pair balance + 全 section 連結部 structure 整合性 verify★
- HTML validator (Rule 1) + image visual (Rule 2) と組合せで 3 重防衛

**理由**: cmd_225_redo で 4 worker section 各々 mutual XR LGTM (blocker 0) だったが、W1 統合 (subtask_005) 段階で sidebar wrapper 3 closing div 欠落 + outer header unclosed が混入、各 reviewer は自分の担当 section のみ verify で 統合後の構造破綻を見逃した。section 単位 review の盲点 = 統合後全体 review なし。

memory: feedback_integration_whole_review.md (W3 起票)

### 適用条件

| Condition | Apply? |
|-----------|:---:|
| Multi-worker section 統合 cmd (catalog / 60 file 展開等) | **MUST** (Rule 1+2+3) |
| Single-worker file edit | Rule 2 のみ (image visual verify) |
| Trivial fix / typo only | 任意 |

### 自己採用日

2026-04-30 (cmd_227、ご主人様 19:32『全部進めて』指示、cmd_225_redo emergency hotfix root prevention)


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
| **Retrospective trigger** | After writing `cmd_complete` to inbox, check retrospective conditions (see `instructions/_rules/retrospective.md`). If triggered, dispatch retrospective task before moving to next cmd. |
| **Skill autocraft trigger** | During retrospective synthesis, evaluate `patterns_to_save` against skill criteria (see `instructions/_rules/skill_autocraft.md`). If a pattern qualifies, draft a proposal to `queue/skill_proposals/`. |


## Kashira→Oyabun 判断要請通知プロトコル (2026-04-14 親分指摘 運用ルール追加)

**背景**: cmd_184 B2 発行時、kashira が提案を dashboard のみ反映して親分待機時間ロス発生 → 親分要請で送信タイミング拡張。

**旧ルール** (kashira_core.md L214 "send-keys to Oyabun (cmd completion only)"): cmd 完了時のみ送信。

**新ルール (追加)**: 判断要請時は全ケース send-keys 必須。

**対象トリガー**:
- バッチ構成提案時 (A/B/C 選択等含む)
- LGTM 待ち (cmd 完了、hotfix 完了、sub-cmd 完了)
- BLOCKER エスカレーション時
- ご主人様に代わって親分が判断する必要があるすべてのケース

**手順** (mechanics は `instructions/_rules/send_keys_protocol.md` 参照):
1. dashboard / task.md 更新
2. **inbox 書き込み必須** (2026-04-17 届かない事故の教訓):
   ```bash
   echo "$(date +%Y-%m-%dT%H:%M:%S)|kashira|{type}|{detail}" >> queue/inbox/oyabun.queue
   ```
   - type 例: `cmd_complete` / `judgment_request` / `blocker` / `proposal`
3. oyabun pane に対し idle check → retry
4. Idle 確認後、2-call 送信:
   - Call 1: `tmux send-keys -t oyabun '【kashira→親分】{notification content}'`
   - Call 2: `tmux send-keys -t oyabun Enter`

**通知内容形式**:
- "【kashira→親分】{cmd_name} {状態} dashboard 参照、判断お願いしますにゃ"
- 状態 = 提案書式 / LGTM待ち / BLOCKER / etc.

**patterns.yaml**: sp_040

**違反時の対策**: 親分から `kashira_check` の明示要請があれば、kashira は dashboard + チャネル双方で報告する運用に立ち戻る。

## DIMCO ドメインルール (2026-04-14 ご主人様指示)

DIMCO HTMLプロトタイプの★画面間一貫性★を kashira/worker が自動的に担保するためのルール群。発見即適用、ご主人様追認立場。

### 共通原則 (第1号/第2号 共通)

- **発動**: 他画面と不統一な画面を発見した時
- **正典特定** (2026-04-14 paradigm shift 後):
  - **第一優先**: ご主人様意向の明示値 (指示があれば即採用)
  - **暫定**: ご主人様未指定なら多数派値を暫定正典として採用、目視判断で違和感あれば確認
  - ★★ 多数派 ≠ 正典の可能性を常に念頭に (hotfix6 教訓) ★★
- **実装パターン** (2026-04-14 spec 拡張):
  - 既存値の置換 / 欠落プロパティの追加 どちらも可 (正典揃え目的ならば)
  - 新規装飾/独自スタイル追加は禁止 (cmd_183 独自装飾禁止ルール継続)
- **運用**: 正典確定時は確認不要で kashira/worker 判断、ご主人様は追認立場
- **cross-review**: 完了時 reviewer は置換網羅性 (grep 漏れゼロ + audit mapping 一致) + computed 実測での正典一致を diff-based + 独立 grep で確認

### 第1号: カラー統一ルール

**対象箇所**: ヘッダー/ボタン/枠線/アクセント/リンク等 すべての色使用箇所
- CSS 変数 / 直接 hex / rgba / inline style すべて grep 対象
- 多数派色 = 紺色 (2026-04-14 時点)

**patterns.yaml**: sp_028
**第1号適用**: cmd_184_hotfix4 item_E (032 カラー統一)

### 第2号: タイポグラフィ統一ルール

**対象プロパティ**: `font-family` / `font-size` / `font-weight` / `line-height`
- CSS 変数 / CSS rule / inline style すべて grep 対象
- 用途別 (body/heading/label/input/button/table 等) に正典判定

**実装パターン (2026-04-14 spec 拡張)**:
- **既存値の置換**: 既存値あり + 多数派と異なる → 多数派値に置換
- **欠落プロパティの追加**: プロパティ自体不在 + 多数派で明示 → 多数派値で補完
- いずれも多数派揃え目的なら cmd_183 独自装飾禁止ルールに抵触しない

**重要な手順 (hotfix5 教訓)**: grep だけでは『欠落』検出困難 → ★Playwright computed 実測★必須。ご主人様目視と grep 結果に乖離あれば実測を信じる。

**除外**: 画面固有の正当な要望 (例: hotfix4 item_8 032 font-size:15px Option B 限定) は統一対象外、個別除外判定。

**patterns.yaml**: sp_029
**第1号適用**: cmd_184_hotfix5 (032 タイポグラフィ統一 — 第1ラウンド body font-family 置換 + 追加実装 .form-field label font-size 欠落補完)

### kashira 運用フロー (発見から完了まで)

1. 画面改修/バッチ/新規追加タスク発行時に★毎回チェック★(task YAML に組込)
2. 発動 cmd で W3 (or W1) に『全値 grep + 多数派 grep + 置換 mapping 作成』調査依頼 (修正なし)
3. 調査 LGTM 後、別ワーカー (Bug Fix Rule 準拠) に実修正 dispatch
4. W4 最終 verify (3viewport スクショ + 他画面並列比較 + 独立 grep leak 再実行)
5. W3 cross-review (diff + W4 機械検証出力 + mapping 一致確認)
6. 親分報告

### 第3号: DIMCO Express lane (軽量フロー選択)

色・フォントの CSS property 変更のみで完結するタスクは、従来3層防御をスキップして軽量フローを採用。

**適用条件 (3つ全部満たす)**:
1. 変更プロパティ = 色系 (color/background/border) or フォント系 (font-family/font-size/font-weight/line-height) のみ
2. レイアウト系 (width/height/padding/margin/flex/grid/position/display) ★一切触らない★
3. 1-数ファイルのスコープロック明確

**Express lane フロー (10-15分目標)**:
1. W3/W1/W2 いずれか 1 名が★直接★ grep + 置換 (調査 Phase と実装 Phase 統合)
2. W4 が 3viewport Playwright 確認
3. kashira 判断で commit
4. cross-review 省略可 (差分自明のため)

**標準フロー (3層防御) 継続適用ケース**:
- レイアウト系を触る場合
- 構造変更
- 複数ファイル束 + デグレリスクあり
- カラー・フォント以外のプロパティ変更

**判定ミス時の挙動**:
『色・フォントだと思ったら CSS 競合でレイアウト崩れ』事案発生時 → Express 判定を 1段厳しく (基準画面との computed style diff 追加)。事故学習で閾値調整。

**patterns.yaml**: sp_039
**第1適用想定**: 次回の色・フォント統一系 cmd 以降 (hotfix6 は既に標準フロー進行中のため対象外)

### 中期タスク候補

全画面デザイン一貫性監査: `cmd_184_design_consistency_audit` (カラー+タイポグラフィ両方、全画面対象) — 親分判断で発行。

### 機械検証 rule 網羅性レビュー (2026-04-14 cmd_184_hotfix2 教訓)

cross-review で reviewer は『機械検証ツール (layout_invariant_check 等) の expected 定義が当該 cmd に十分網羅的か』も確認する。

**背景**: cmd_184_hotfix2 完遂 verdict=ALL_PASS_goshujin_visual_final の報告直後、ご主人様目視で 026 input 縦長再発 (hotfix3) が発覚。原因は expected_縦.yaml が構造層 (display/flex-direction) のみで、input intrinsic height 等の『内部層』をカバーしていなかったこと。

**レビュー観点**:
- rule が cmd 対象の全 UI 層 (構造層/内部層/視覚層) をカバーするか
- 視覚 regression 疑いあれば reviewer が追加 rule 提案

**patterns.yaml**: fp_029 に記載。

