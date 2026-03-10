# Changelog

All notable changes to the neko-multi-agent system will be documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/).

## [3.2.0] - 2026-03-06

### Added
- **Conditional rule injection system**: `_worker_base.md` split into core (340 lines) + 9 conditional rule files in `instructions/_rules/`
- `inject_rules` field in task YAML — kashira specifies which rules each worker needs per task
- Rule files: css_scope, fix_task, cross_review, security_review, large_file, batch_task, p2p_comm, escalation, reference_tables
- consult_032 improvements (1-4, 6-8): skill_candidate shorthand, gen_report.sh, neko_send.sh wrapper, Quick Reference Card, suggestions box, rule audit

### Changed
- `_worker_base.md`: 639 → 340 lines (~47% reduction). Conditional sections moved to `instructions/_rules/`
- kashira_core.md: Assignment Format updated with `inject_rules` field + injection table
- Task Sizing Pre-Flight + Chunked Write Rule merged into `_rules/large_file.md`
- D8 Report Requirements merged into Report Format section

### Removed
- 18 conditional sections from always-loaded `_worker_base.md` (moved to on-demand `_rules/` files)

## [3.1.0] - 2026-02-24

### Added
- **Security review system**: black_hacker + white_hacker adversarial roles in cross-review workflow
- config/review_criteria.yaml: security_review checklists (attack vectors + defense measures)
- kashira.md: security_review protocol and role assignment logic
- _worker_base.md / _worker_base_lite.md: security review role instructions
- **Worker Model Assignment Policy** in kashira.md: Sonnet vs Haiku guidelines based on empirical cmd_037 comparison

## [3.0.1] - 2026-02-18

### Changed
- Voice system: opt-in → mandatory per-cmd prompting (kashira prompts workers after cmd completion)

## [3.0.0] - 2026-02-16 — Worker Expansion (4S+3H)

### Added
- **3 Haiku workers** (W5 子猫, W6 生意気猫, W7 老猫) with distinct personalities
- **_worker_base_lite.md** for Haiku-optimized instructions (~150 lines)
- **Bloom routing**: kashira routes L1-L3 (procedure exists) → Haiku, L4-L6 (requires judgment) → Sonnet
- **Voice system**: `queue/voice/` direct feedback channel — workers write, oyabun reads
- **Category failure tracking** for automatic Haiku → Sonnet reclassification
- **Routing log** for audit trail of all model tier decisions

### Changed
- kashira.md: added Bloom routing section + 7-worker pane config
- osanpo.sh: 8-pane layout with Haiku model flag
- CLAUDE.md: updated to v3.0.0 with 8-agent structure
- _worker_base.md: added voice system section
- _worker_base_lite.md: added voice system section
- oyabun.md: voice reading in context loading procedure

## [2.4.0] - 2026-02-16 — Context Management Improvements

### Added
- **3-Tier Reset Threshold**: Progressive context warnings at 50%/40%/35%
  with escalating urgency messages. Replaces previous heuristic-based
  judgment criteria. (oyabun.md)
- **Recovery Block Template**: Fixed-format block at top of oyabun_session.md
  with decisions, pending TODOs, constraints, next action, and reference files.
  Ensures clean recovery after restart. (oyabun.md)
- **Reset Proposal Event Logging**: Kashira logs oyabun restart events
  in inbox queue for audit trail. (kashira.md)
- **Dashboard as Recovery Source**: Dashboard.md recognized as oyabun's
  primary recovery reference after restart — accuracy emphasis added. (kashira.md)

## [2.3.0] - 2026-02-08 — D4/D5 Process Improvements (consult_010-013)

Team-wide consultation (4 workers, 4 topics D2-D5) resulted in 2 adoptions and 2 rejections:

### Added
- **D5: Spec-Driven Requirements**: Mandatory Tier 1 checklist for oyabun's requirements
  definition. Domain mappings, key formats, conventions, and acceptance criteria must be
  confirmed with goshujinsama before delegation. Prevents "guessing and proceeding."
  (oyabun.md)
- **D4: Interface Contracts (Phase 0.5)**: Pre-implementation interface definition phase
  for large tasks. Kashira defines module boundary signatures, output keys, shared constants.
  Prevents 57-62% of boundary bugs. (kashira.md)

### Rejected (by team consensus)
- **D2: Task Dependency DAG** — Current phase system is sufficient
  (29 cmds, 150+ subtasks, 0 dependency violations).
- **D3: Auto Task Claiming** — Kashira routing is the core of quality
  management. Auto-claiming adds race conditions without meaningful benefit.

## [2.2.0] - 2026-02-08 — Post-Mortem Improvements

Four structural improvements from consult_008 (cmd_025 post-mortem, 4/4 team consensus):

### Added
- **Integration Test Gate (Phase 1.5)**: Kashira-controlled toggle for mandatory integration
  smoke tests between implementation and cross-review. Catches module boundary mismatches.
  (kashira.md)
- **Flat Config Rule**: Max 1 level nesting in YAML config for new projects. Eliminates
  config nesting bugs that recurred 3 times. (worker_base.md)
- **B6 Interface Contract Verification**: New universal review checklist item — reviewer
  must verify output format matches downstream consumer. (review_criteria.yaml)
- **Real Site Evidence Package**: Scraping tasks require real site HTML snapshot, structure
  docs, mock derivation, and integration smoke test. (worker_base.md)
- **PY5 SQL JOIN integration check**: Python-specific review item for JOIN correctness
  tests. (review_criteria.yaml)

### Changed
- patterns.yaml: Added sp_014 (integration tests), sp_015 (flat config), fp_002-fp_004
  (config nesting, cartesian product, testing methodology failures)

## [2.1.0] - 2026-02-06

### Added
- Agent Teams feature cherry-pick from upgrade plan
- P2P review with kashira-controlled toggle (Step 1 of upgrade plan)
- CHANGELOG.md introduced
- Session log system for oyabun (`logs/oyabun_session.md`) — context crash protection
- Self-restart proposal rules for oyabun — proactive session management
- Proactive compaction rules for kashira — expanded context protection beyond cmd completion
- Mandatory hints field usage for kashira task assignment (T1 knowledge flow improvement)
- Lightweight task mode — kashira-controlled, reduces 30-40% context overhead on simple tasks
- Simplified report format for lightweight tasks (`skill_candidate: none` shorthand)
- Task seq number for reliable new-task detection (replaces null-task sleep-retry)
- Estimated effort field (`estimated_effort: small|medium|large`) for task YAML — T6 workload fairness (consult_005 unanimous)
- Report history system — per-task report files (`worker{N}_{task_id}_report.yaml`), no more overwriting (T7, Step 3 prerequisite)
- Autonomous brainstorm system — kashira-initiated team discussions with structured risk assessment reporting (degree of risk / merit-demerit / team recommendation)
- Heads-up messaging toggle (`heads_up: true/false`) for real-time parallel work sharing (T4)

## [2.0.1] - 2026-02-06

### Changed
- Rename shutsujin (出陣) to osanpo (おさんぽ) across codebase

### Added
- HOWTO setup guide

## [2.0.0] - 2026-02-05

### Added
- Requirements phase: oyabun confirms requirements with master before delegating
- Cross-review system for quality assurance across workers
- Reward system (churu-based: まぐろ / さけ / さば / ほねっこ)
- Worker base template (`_worker_base.md`) for shared instructions
- Self-will and emotion system for worker agents
- File-based inbox (`queue/inbox/`) for reliable message delivery

### Changed
- Major system overhaul of task distribution and reporting protocol

## [1.2.0] - 2026-01-30

### Changed
- Complete theme redesign from shogun to neko cat theme
- Rename bantou (番頭) to kashira (頭猫) across codebase
- Update all READMEs to reflect neko cat theme

## [1.1.1] - 2026-01-29

### Fixed
- install.bat Windows compatibility and simplification
- Alias activation instructions in first_setup.sh

### Changed
- Improve installer robustness and multi-agent communication
- Untrack runtime files from git (dashboard.md, queue/*.yaml, config/projects.yaml, config/settings.yaml, status/, logs/)
- Update READMEs to reflect simplified installer workflow

### Added
- Sample projects.yaml template

## [1.1.0] - 2026-01-27

### Added
- Context management system
- Model configuration support
- Role clarity improvements

## [1.0.1] - 2026-01-27

### Changed
- Unify paths and improve release readiness
- Add runtime data directories to .gitignore
- Expand README_ja.md to match English version

### Added
- Screenshot support feature documented in README

## [1.0.0] - 2026-01-25

### Added
- Event-driven multi-agent orchestration system
- tmux send-keys usage instructions

### Fixed
- Replace C-m with Enter in all tmux send-keys commands (critical fix)

## [0.1.0] - 2026-01-25

### Added
- Initial claude-shogun multi-agent orchestration system
- Persona and context loading rules for instruction files
- Persona examples and roadmap in READMEs
- Skill auto-generation system
- Setup script with samurai theme
- WSL symlink setup instructions
- Alias documentation in setup.sh output

### Fixed
- Simplify pane welcome messages for better compatibility
- Combine commands to show clean prompt on attach
