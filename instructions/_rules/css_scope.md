# CSS Scope Enforcement

Batch CSS tasks: ONLY change properties listed in task YAML `scope_lock.change_only`.

**Protected properties** — these MUST NOT be changed unless explicitly listed in `scope_lock.change_only`:
- `overflow` (all variants: overflow-x, overflow-y, overflow)
- `z-index`
- `position`
- `display`
- `visibility`

**Workflow:**
1. Before changes: note existing CSS structure of target elements
2. Make ONLY the specified changes
3. After changes: run `diff` to verify no out-of-scope properties were modified
4. Any out-of-scope changes found → report in `unverified_risks`

**If `scope_lock.do_not_change` exists in task YAML**: those properties are absolutely forbidden to modify, regardless of context.

**Violation handling**: Unreported scope violations discovered in cross-review are treated as defects (severity: high).
