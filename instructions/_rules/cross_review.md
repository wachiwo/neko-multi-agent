# Cross-Review Role

When assigned a `type: cross_review` task, you act as a **reviewer**, not an implementer.

## Review Procedure

1. Read the target files listed in `review_target.files`
2. Run the **base checklist** (B1-B5: syntax, security, performance, readability, spec compliance)
3. Run the **language-specific checklist** from `config/review_criteria.yaml` (matched by `review_criteria` field)
4. Check any `focus_areas` specified in the task
5. Submit a cross-review report

## Review Mindset

- **Be constructive**: Suggest improvements, don't just criticize
- **Classify severity**: `high` = must fix before merge, `medium` = should fix, `low` = nice to have
- **LGTM is valid**: If no issues are found, say so clearly
- **Read only**: Reviewers must NOT modify target files. Report findings only.

## Cross-Review Report Format

```yaml
worker_id: {{WORKER_ID}}
task_id: review_subtask_001
timestamp: "2026-01-25T10:30:00"
type: cross_review_report
review_result: lgtm            # lgtm | minor_issues | major_issues
findings:
  - id: F1
    severity: high             # high | medium | low
    file: "/path/to/file.cs"
    line: 42
    issue: "Description of the problem"
    suggestion: "Proposed fix"
summary: "Overall evaluation comment"
skill_candidate: none    # Use full block only when found: true
```
