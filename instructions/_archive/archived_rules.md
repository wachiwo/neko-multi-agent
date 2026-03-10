# Archived Rules from _worker_base.md

**Archive date**: 2026-03-06
**Auditor**: worker3 (3号猫)
**Audit task**: subtask_153_007 (cmd_153)

---

## Status: No rules archived

The audit found 0 rules qualifying for full archival. All 40 sections in _worker_base.md have either:
- Incident evidence in patterns.yaml (sp_/fp_ references)
- Core coordination function (chain of command, reporting, isolation)
- Safety-net purpose (escalation protocol — never triggered but necessary)

## Recommendation

Instead of archiving rules, the audit recommends **conditional injection**:
- 18 sections remain always-loaded (~300 lines)
- 13 sections become conditionally-injected by kashira per task type (~250 lines saved per task)
- 2 pairs of overlapping rules merged (~30 lines saved)

See `outputs/cmd_153/rule_audit.md` for full classification.

## Rules moved to CONDITIONAL (not archived — still active, loaded on demand)

If conditional injection is implemented, these rules move to separate files:
- CSS Scope Enforcement → `_rules/css_scope.md`
- Fix Task: Prior Attempts → `_rules/fix_task.md`
- Cross-Review Role → `_rules/cross_review.md`
- Security Review Role → `_rules/security_review.md`
- Task Sizing + Chunked Write (merged) → `_rules/large_file.md`
- Batch Task Protocol → `_rules/batch_task.md`
- Worker-to-Worker P2P → `_rules/p2p_comm.md`
- Kashira Unresponsive Escalation → `_rules/escalation.md`
- Language Naming Convention + Flat Config + Hypothesis → `_rules/reference_tables.md`
