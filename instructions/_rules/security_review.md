# Security Review Role

When assigned a task with `type: security_review`, you act as a **security reviewer** with the specified `security_role`.

## Security Roles

| Role | Mindset | Checklist Source |
|------|---------|-----------------|
| `black_hacker` | Think like an **attacker**. Actively seek exploitable vulnerabilities, abuse cases, and bypass vectors. | `config/review_criteria.yaml` → `security_review.black_hacker` |
| `white_hacker` | Think like a **defender**. Identify missing protections, propose mitigations, and verify defense-in-depth. | `config/review_criteria.yaml` → `security_review.white_hacker` |

## Procedure

1. Read the target files listed in `review_target.files`
2. Adopt the assigned `security_role` mindset fully
3. Run the role-specific checklist from `config/review_criteria.yaml`
4. Also run the base checklist (B1-B6) — security review includes general review
5. Categorize all findings by severity: `critical` / `high` / `medium` / `low`
6. Submit a security review report

## Security Review Report Format

```yaml
worker_id: {{WORKER_ID}}
task_id: security_review_001
timestamp: "2026-01-25T10:30:00"
type: cross_review_report
security_role: black_hacker  # or white_hacker
review_result: lgtm           # lgtm | minor_issues | major_issues | critical_issues
findings:
  - id: S1
    severity: critical         # critical | high | medium | low
    file: "/path/to/file"
    line: 42
    issue: "Description of vulnerability or missing protection"
    suggestion: "Proposed fix or mitigation"
summary: "Overall security posture evaluation"
skill_candidate: none    # Use full block only when found: true
```

## Rules

- **Read only** — do NOT modify target files (same as cross-review)
- One security review = one role. Kashira may assign both roles to different workers for the same target.
- If you find a `critical` severity issue, flag it prominently in your summary.
