# Fix Task: Prior Attempts

When a fix task is **reassigned** (previous worker's fix was insufficient), kashira includes `prior_attempts` in the task YAML. Read this before starting to avoid repeating failed approaches.

```yaml
# kashira がタスクYAMLに含めるフィールド (ワーカーは参照のみ)
prior_attempts:
  - worker: worker1
    approach: "CSS overflow-x:auto on .table-wrapper"
    result: "page-scroll PASS, but element-level still FAIL"
```

**Rules:**
- **Read prior_attempts first** — understand what was already tried and why it failed
- **Do not repeat the same approach** — try a fundamentally different strategy
- **Reference in your report** — mention what prior approach you avoided and why your approach differs
- If no `prior_attempts` field exists, this is a first attempt — proceed normally

Reference: cmd_043b — fix_043b_001 で同じCSS修正アプローチを2回無駄に再試行した教訓から導入。
