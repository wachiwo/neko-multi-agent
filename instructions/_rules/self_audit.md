# Self-Audit (Neko System Complexity Management)

> **Purpose**: The neko system accumulates rules, skills, and scripts over time. Without periodic pruning, it becomes impossible for goshujinsama (and even oyabun) to keep a mental model of what the system does. Self-audit is oyabun's routine to detect and surface complexity debt.

## When to Audit

**Automatic triggers** (oyabun self-initiates):

1. **Monthly cadence**: First oyabun session of each month → run audit
2. **After major cmd cluster**: When 5+ cmds complete in a short span (often leaves residue)
3. **After instructions edit**: Any commit to `instructions/` by oyabun → mini-audit of that area

**Manual trigger**: goshujinsama says "audit" or "snapshot" or "棚卸し"

## Audit Checklist

### 1. Orphan Detection

Find unreferenced artifacts:
```bash
# Scripts not called by any hook, workflow, or other script
for s in scripts/*.sh scripts/*.py; do
  name=$(basename "$s")
  count=$(grep -r --include='*.md' --include='*.sh' --include='*.py' --include='*.json' --include='*.yaml' -l "$name" . 2>/dev/null | grep -v "^./$s$" | wc -l)
  [ "$count" = "0" ] && echo "ORPHAN: $s"
done

# Instructions files not referenced by others
for f in instructions/**/*.md; do
  name=$(basename "$f")
  count=$(grep -r --include='*.md' -l "$name" instructions/ | grep -v "^$f$" | wc -l)
  [ "$count" = "0" ] && echo "ORPHAN: $f"
done
```

### 2. Rule Duplication Check

Look for same rule stated multiple times:
```bash
# Common duplicate subjects to grep for
for kw in "send-keys" "idle check" "context threshold" "cross-review" "scope_lock"; do
  locs=$(grep -l "$kw" instructions/**/*.md | wc -l)
  [ "$locs" -ge 3 ] && echo "DUP CANDIDATE: '$kw' in $locs files"
done
```

### 3. Dead Rules

Rules that reference removed agents, archived features, or stale incidents:
- Any mention of worker5/6/7 (removed)
- Any mention of Haiku policy (archived)
- Any "旧ルール" (旧/legacy) markers that can be deleted now

### 4. Policy Bloat

Check file sizes:
```bash
wc -l instructions/**/*.md | sort -n | tail -5
```
If any single file is > 800 lines, consider splitting.

### 5. Skill Inventory Drift

Compare `~/.claude/skills/` with skills actually used in the last 30 days:
```bash
# Used skills (rough: mentioned in queue/reports recently)
grep -rh "Skill(" queue/reports/ logs/ 2>/dev/null | grep -oE 'neko-[a-z-]+' | sort -u > /tmp/used.txt
# Installed skills
ls ~/.claude/skills/ | grep '^neko-' > /tmp/installed.txt
# Diff
comm -23 /tmp/installed.txt /tmp/used.txt   # installed but unused → candidate for archive
```

## Audit Output

Write findings to `logs/audit_YYYY-MM-DD.md`:

```markdown
# Neko System Audit — YYYY-MM-DD

## Summary
- orphans_found: N
- duplicates_found: N
- dead_rules: N
- policy_files_over_800_lines: N
- unused_skills: N

## Action Items (oyabun auto-executes if low-risk)
- [ ] Delete scripts/X.sh (0 references, reason: orphan)
- [ ] Consolidate rule "Y" (3 copies, reason: duplicate)

## Requires goshujinsama Review
- Splitting instructions/kashira_policies.md (1200 lines) into 3 files
- Archiving skill Z (no use in 60 days)
```

## Risk Gates

Oyabun may self-execute ONLY:
- Deleting files with **zero** references (confirmed by grep)
- Removing rules explicitly marked 旧/legacy/archived
- Consolidating duplicate rules where mechanics match exactly

Oyabun must ESCALATE to goshujinsama for:
- Splitting large files (architectural change)
- Archiving skills (might be used outside logs/)
- Any deletion touching `memory/` or `.claude/`
- Renaming rules that affect external integrations

## Anti-Patterns

- **Rewriting history**: Don't rewrite commits during audit. Create new commits that supersede.
- **Silent deletion**: Every deletion must appear in the audit log AND commit message.
- **Cosmetic refactors**: Don't reformat files just because you're there. Change only what reduces real complexity.
- **Audit paralysis**: If nothing changes in a month, that's fine. Note "no action needed" and move on.

## Integration Points

- Output: `logs/audit_YYYY-MM-DD.md`
- Feeds into: memory (if new lessons surface) and CLAUDE.md (if structure changes)
- Referenced from: `oyabun.md` § periodic_duties
