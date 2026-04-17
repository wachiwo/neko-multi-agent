# Skill Auto-Crafting

> **Purpose**: Repeating work patterns across cmds should become reusable skills. This turns "we did this 3 times" into "we call this skill", shrinking future dispatches.

## When to Propose a Skill

Detection triggers (any ONE makes it a candidate):

1. **Retrospective signal**: `patterns_to_save` in a retrospective synthesis names a concrete procedure (not a one-off insight)
2. **Repeat count**: The same procedure has been written out in cmd YAMLs 3+ times across different cmds
3. **Worker pain signal**: A worker's report contains "this was tricky" or "took me longer than expected" for a mechanical task
4. **Complexity reduction**: A cmd's `approved_procedure` section is > 6 steps and the steps are algorithmic (could be a script)

**Do NOT auto-skill**:
- One-off project-specific work (e.g., "fix the 049 table" is not a skill)
- Anything requiring goshujinsama judgment (skills execute mechanically)
- Anything touching production systems without approval

## Proposal Flow

### Step 1: kashira drafts skill spec (during retrospective synthesis or cmd post-mortem)

Write a proposal YAML to `queue/skill_proposals/{skill_name}.yaml`:

```yaml
skill_proposal:
  name: "neko-{verb}-{noun}"         # follows existing naming convention
  trigger: "what makes a worker reach for this skill"
  inputs: ["arg1: description", "arg2: description"]
  outputs: ["what the skill produces"]
  procedure:
    - "step 1"
    - "step 2"
  evidence:
    - "cmd_XXX used this pattern (date)"
    - "cmd_YYY used this pattern (date)"
    - "cmd_ZZZ used this pattern (date)"
  effort_saved_estimate: "each invocation saves ~N minutes"
  risk: "what could go wrong if skill misfires"
```

### Step 2: oyabun reviews

Oyabun reads the proposal and either:
- **Approve** → green-light creation, assign to a worker or kashira
- **Modify** → push back with scope/naming adjustments
- **Reject** → one-off, not skill-worthy. Close with reason.
- **Escalate** → high-risk or ambiguous scope → ask goshujinsama

### Step 3: Skill creation

If approved, the implementer:
1. Creates `~/.claude/skills/{skill_name}/` with `SKILL.md` and supporting files
2. Tests the skill on one historical cmd that would have used it (verify output matches)
3. Updates the skill proposal with `status: implemented` and path
4. Reports back via inbox + send-keys

### Step 4: Adoption

Kashira starts using the skill in new dispatches. After 2-3 successful uses, the proposal is archived (`queue/skill_proposals/_archive/`) and the skill is considered stable.

## Existing Skills Catalog

Location: `~/.claude/skills/` (user-level, shared across projects)

When proposing a new skill, FIRST check if an existing one covers it or could be extended:
```bash
ls ~/.claude/skills/ | grep -i <keyword>
```

## Anti-Patterns

- **Over-abstracting**: Don't skillify until 3+ actual uses. Premature abstraction creates maintenance burden for rare code paths.
- **Scope creep in skills**: A skill that "mostly does X but also Y and Z" should be 3 skills. Keep them single-purpose.
- **Skills that wrap judgment**: If the skill has `if/else` based on goshujinsama's preference, that's not mechanical — leave it in the instruction.
- **Hidden dependencies**: A skill that silently reads `queue/...` or `memory/...` is fragile. Declare inputs explicitly.

## Integration Points

- Detection: `_rules/retrospective.md` § synthesis.patterns_to_save
- Proposals: `queue/skill_proposals/` (new directory, kashira creates on first proposal)
- Registry: `~/.claude/skills/` (file system is the source of truth)
- Invocation: Claude Code auto-discovers skills; agents invoke via `Skill` tool
