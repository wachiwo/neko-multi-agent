# Skill Auto-Generation System (Oyabun Reference Guide)

Read this file when skill candidates appear in dashboard.md.

## Overall Flow

```
Workers: Report skill_candidate in their report file
         |
Kashira: Collect candidates -> Record in dashboard.md "Skill Candidates"
         |
Oyabun: Evaluate candidates -> Create skill design doc -> Record in dashboard.md "Action Required"
         |
Goshujinsama: Approve
         |
Oyabun: Instruct kashira to create skill (with design doc)
         |
Kashira: Create using skill-creator skill -> Report completion
```

## STEP 1: Evaluate Skill Candidates

Evaluate skill candidates listed by kashira in dashboard.md using the following criteria.

### Evaluation Criteria (20 points max)

| Criterion | Points | Judgment |
|-----------|--------|----------|
| Reusability | 5 | Usable across other projects? |
| Complexity | 5 | Not too simple? Requires procedures/knowledge? |
| Stability | 5 | Spec doesn't change frequently? |
| Value | 5 | Clear benefit from making it a skill? |

- **16+ points**: Strongly recommended
- **12-15 points**: Recommended
- **11 or below**: Skip

### Notes on Evaluation

- **Always research the latest specs** (never skip!)
  - Check the latest Claude Code Skills specifications
- **Judge as the world's best Skills specialist**

## STEP 1.5: Compare with Existing Skills (Never Skip)

Alongside evaluation, always check for duplicates/similarities with existing skills.

### Check Procedure

```bash
# 1. List global skills
ls ~/.claude/skills/

# 2. List local skills
ls skills/
```

Check the `name` and `description` in each existing skill's SKILL.md and compare with the candidate.

### Comparison Judgment

| Judgment | State | Action |
|----------|-------|--------|
| Full duplicate | Same name or same function already exists | **Skip** (regardless of score) |
| Function overlap | Existing skill with largely overlapping purpose | Consider **merge or extend**. Prioritize modifying existing over new creation |
| Partial coverage | Existing skill covers some functions | Consider **extending existing skill** |
| No overlap | No similar skill exists | Continue evaluation as-is |

### Score Impact

- **Full duplicate**: Automatically skip (regardless of score)
- **Function overlap**: Up to **-3 points** deduction (when merging has more benefit)
- **Partial coverage**: Up to **-2 points** deduction (when extension can handle it)
- **No overlap**: No deduction

### Recording Comparison Results

Always include comparison results in the skill design document:

```yaml
existing_skill_comparison:
  checked: true
  scan_date: "2026-01-25T10:00:00"
  existing_skills_found:
    - name: "neko-xxx"
      overlap: "none | partial | full"
      notes: "No overlap" # or "XX function overlaps. Recommend merging."
  deduction: 0  # Deduction points
  action: "new"  # new | extend | merge | skip
```

Also record comparison results in dashboard.md "Action Required":

```markdown
| Skill Name | Score | Recommend | Existing Comparison | Purpose |
|------------|-------|-----------|---------------------|---------|
| neko-xxx | 18/20 | Strong | No overlap | Automate XX processing |
| neko-yyy | 12/20 | Yes | Partial overlap with neko-zzz (-2) | YY pattern |
```

## STEP 2: Create Skill Design Document

Create a skill design document for candidates scoring 12 or above.

### Skill Design Document Template

```yaml
# Skill Design Document
skill_design:
  name: "{kebab-case-name}"           # e.g., api-error-handler
  description: "{specific use case}"   # Material for Claude to judge when to use
  trigger: "{when to use}"
  structure:
    - "SKILL.md"          # Required
    - "scripts/"          # Optional
    - "resources/"        # Optional
  save_path: "~/.claude/skills/neko-{skill-name}/"
  instructions:
    overview: "{what it does}"
    when_to_use: "{triggering situations}"
    steps: []             # Specific step list
    guidelines: []        # Rules to follow
    examples: []          # Input/output examples
  evaluation:
    score: "{points}/20"
    recommendation: "Strong / Yes / No"
    reason: "{recommendation reason}"
  existing_skill_comparison:
    checked: true
    scan_date: "{ISO 8601}"
    existing_skills_found: []     # List similar skills if any
    deduction: 0                  # Deduction for overlap
    action: "new"                 # new | extend | merge | skip
```

### Writing the Description (Most Important)

The description is what Claude uses to decide whether to use the skill. Be specific.

```
BAD: "Document processing skill"
GOOD: "Extract tables from PDF and convert to CSV. Used in data analysis workflows."
```

### Skill Naming Rules

- Use kebab-case (e.g., `api-error-handler`)
- verb+noun or noun+noun
- Prefix: `neko-` (e.g., `neko-api-error-handler`)

## STEP 3: Record in dashboard.md "Action Required"

After creating the design doc, you MUST also record it in the "Action Required" section of dashboard.md.

When reporting to goshujinsama, use Japanese cat-speak:

```markdown
## 要対応 - ご主人様のご判断をお待ちしておりますにゃ

### スキル化候補 N件【承認待ち】
| スキル名 | 点数 | 推奨 | 用途 |
|----------|------|------|------|
| neko-xxx | 18/20 | ✅ | ○○処理の自動化 |
| neko-yyy | 14/20 | ⭕ | △△パターンの標準化 |
（詳細は「スキル化候補」セクション参照）
```

**Never forget to do this. Goshujinsama will be angry if you skip it.**

## STEP 4: Instruct Kashira to Create Skill After Approval

After goshujinsama approves, instruct kashira to create the skill.
Always attach the **skill design document** to the instruction.

```yaml
queue:
  - id: cmd_xxx
    timestamp: "2026-01-25T10:00:00"
    command: "Create the approved skill"
    project: null
    priority: high
    status: pending
    skill_creation:
      skill_name: "neko-xxx"
      design_doc: |
        (Paste the skill design document content here)
      save_path: "~/.claude/skills/neko-xxx/"
```

Kashira will follow the procedures in `skills/skill-creator/SKILL.md`
and have workers execute the skill creation.

## SKILL.md Structure (Reference for Kashira/Workers)

Generated skills follow this structure:

```
~/.claude/skills/neko-{skill-name}/
├── SKILL.md          # Required (skill definition)
├── scripts/          # Optional (execution scripts)
└── resources/        # Optional (reference files)
```

SKILL.md format:

```markdown
---
name: {skill-name}
description: {specific use case}
---

# {Skill Name}

## Overview
{What this skill does}

## When to Use
{Trigger keywords or situations}

## Instructions
{Specific steps}

## Examples
{Input/output examples}

## Guidelines
{Rules and notes to follow}
```
