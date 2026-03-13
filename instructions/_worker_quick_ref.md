# Worker Quick Reference Card

## Forbidden (F001-F005)
- No direct report to oyabun — go through kashira
- No direct user contact — go through kashira
- No unauthorized work — assigned tasks only
- No polling — event-driven only
- No skipping context reading

## Report Essentials
```yaml
worker_id: / task_id: / timestamp: / status: done|failed|blocked
result: { summary: "...", files_modified: [...] }
one_line_summary: "concrete, quantified result"
unverified_risks: ["..."]      # REQUIRED even if none
skill_candidate: none           # full block only when found: true
```

## Error Handling
1. Try ONE alternative approach
2. If still fails → report `status: failed` + notify kashira inbox

## Key Paths
- Task: `queue/tasks/{{WORKER_ID}}.yaml`
- Report: `queue/reports/{{WORKER_ID}}_{{TASK_ID}}_report.yaml`
- Inbox: `queue/inbox/{{WORKER_ID}}.queue`
- Kashira inbox: `queue/inbox/kashira.queue`

## Timestamp & send-keys
- Timestamp: `date "+%Y-%m-%dT%H:%M:%S"`
- send-keys: **Always 2 calls** — Call 1: message, Call 2: `Enter`
