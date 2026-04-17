# Worker-to-Worker Communication (P2P Review & Heads-Up)

> **send-keys mechanics**: see `instructions/_rules/send_keys_protocol.md`.

Workers can message each other directly ONLY when the task YAML enables it:

| Type | Trigger | Purpose | Response expected? |
|------|---------|---------|-------------------|
| `p2p_review` | `p2p_review: true` in review task | Review findings, fix confirmations, code clarifications | Yes (resolve + notify kashira) |
| `heads_up` | `heads_up: true` in task | Share discovered patterns/pitfalls with sibling workers | No |

**Protocol** (same for both types):

1. Write to target worker's inbox: `echo "TIMESTAMP|{{WORKER_ID}}|TYPE|MESSAGE" >> queue/inbox/{target}.queue`
2. **CC to kashira (MANDATORY)**: `echo "TIMESTAMP|{{WORKER_ID}}|TYPE|to:{target}|summary:BRIEF" >> queue/inbox/kashira.queue`
3. Nudge target worker via send-keys (2-call method)

**Scope limits** — direct messaging is NOT for: task assignments, problem escalation, direction/scope changes. These go through kashira.

**P2P resolution**: After resolving all findings, author sends: `echo "TIMESTAMP|{{WORKER_ID}}|p2p_resolved|All findings resolved for TASK_ID" >> queue/inbox/kashira.queue`

**Receiving heads-up**: Read the finding (may save you from hitting the same problem). No response required. Mention useful findings in your report under `learning`.
