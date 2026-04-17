#!/usr/bin/env bash
# audit-skills.sh - Skill inventory audit
# Detects: duplicate descriptions, missing front matter, unused skills, naming drift.
# Writes report to logs/audit_skills_YYYY-MM-DD.md

set -uo pipefail

SKILL_DIR="${HOME}/.claude/skills"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DATE=$(date +%Y-%m-%d)
REPORT="${REPO_ROOT}/logs/audit_skills_${DATE}.md"

mkdir -p "$(dirname "$REPORT")"

{
  echo "# Skill Inventory Audit — ${DATE}"
  echo ""
  echo "Source: \`${SKILL_DIR}\`"
  echo ""
} > "$REPORT"

# 1. Count skills
total=$(find "$SKILL_DIR" -maxdepth 1 -mindepth 1 -type d ! -name '_archive' | wc -l)
echo "## Summary" >> "$REPORT"
echo "- total_skills: ${total}" >> "$REPORT"

# 2. Missing front matter check
missing_fm=()
for dir in "$SKILL_DIR"/*/; do
  name=$(basename "$dir")
  [ "$name" = "_archive" ] && continue
  skill_md="${dir}SKILL.md"
  if [ ! -f "$skill_md" ]; then
    missing_fm+=("$name (no SKILL.md)")
  elif ! head -1 "$skill_md" | grep -q "^---$"; then
    missing_fm+=("$name (no front matter)")
  fi
done
echo "- missing_front_matter: ${#missing_fm[@]}" >> "$REPORT"

# 3. Naming convention check (should be neko-*)
non_neko=()
for dir in "$SKILL_DIR"/*/; do
  name=$(basename "$dir")
  [ "$name" = "_archive" ] && continue
  case "$name" in
    neko-*) ;;
    *) non_neko+=("$name") ;;
  esac
done
echo "- non_neko_prefix: ${#non_neko[@]}" >> "$REPORT"

# 4. Description duplicate detection (first 50 chars)
declare -A desc_map
dup_desc=()
for dir in "$SKILL_DIR"/*/; do
  name=$(basename "$dir")
  [ "$name" = "_archive" ] && continue
  skill_md="${dir}SKILL.md"
  [ ! -f "$skill_md" ] && continue
  desc=$(grep -m1 "^description:" "$skill_md" 2>/dev/null | sed 's/description: *//; s/"//g' | head -c 80)
  [ -z "$desc" ] && continue
  if [ -n "${desc_map[$desc]:-}" ]; then
    dup_desc+=("${desc_map[$desc]} ↔ $name")
  else
    desc_map[$desc]="$name"
  fi
done
echo "- duplicate_descriptions: ${#dup_desc[@]}" >> "$REPORT"

# 5. Usage count (pre-index all skill-name mentions once, then count per skill)
#    Primary source: logs/skill_usage.log (written by PostToolUse hook).
#    Fallback: grep reports/ logs/ for skill-name mentions.
index_file=$(mktemp)
USAGE_LOG="${REPO_ROOT}/logs/skill_usage.log"
if [ -f "$USAGE_LOG" ]; then
  awk -F'|' '{print $3}' "$USAGE_LOG" | sort | uniq -c \
    | awk '{print $1" "$2}' > "$index_file"
else
  grep -rho --include='*.yaml' --include='*.md' 'neko-[a-z0-9-]\+' \
    "${REPO_ROOT}/queue/reports" "${REPO_ROOT}/logs" 2>/dev/null \
    | sort | uniq -c > "$index_file" || true
fi

used=()
unused=()
for dir in "$SKILL_DIR"/*/; do
  name=$(basename "$dir")
  [ "$name" = "_archive" ] && continue
  count=$(awk -v n="$name" '$2 == n {print $1}' "$index_file")
  count=${count:-0}
  if [ "$count" -eq 0 ]; then
    unused+=("$name")
  else
    used+=("$name ($count refs)")
  fi
done
rm -f "$index_file"
echo "- unused_skills: ${#unused[@]}" >> "$REPORT"
echo "" >> "$REPORT"

# Details sections
echo "## Missing Front Matter" >> "$REPORT"
if [ ${#missing_fm[@]} -eq 0 ]; then
  echo "_none_" >> "$REPORT"
else
  for s in "${missing_fm[@]}"; do echo "- $s" >> "$REPORT"; done
fi
echo "" >> "$REPORT"

echo "## Non-neko Prefix" >> "$REPORT"
if [ ${#non_neko[@]} -eq 0 ]; then
  echo "_none_" >> "$REPORT"
else
  for s in "${non_neko[@]}"; do echo "- $s" >> "$REPORT"; done
fi
echo "" >> "$REPORT"

echo "## Duplicate Descriptions (first 80 chars)" >> "$REPORT"
if [ ${#dup_desc[@]} -eq 0 ]; then
  echo "_none_" >> "$REPORT"
else
  for s in "${dup_desc[@]}"; do echo "- $s" >> "$REPORT"; done
fi
echo "" >> "$REPORT"

echo "## Unused Skills (0 references in reports/ logs/)" >> "$REPORT"
if [ ${#unused[@]} -eq 0 ]; then
  echo "_none_" >> "$REPORT"
else
  for s in "${unused[@]}"; do echo "- $s" >> "$REPORT"; done
  echo "" >> "$REPORT"
  echo "_Note: 'unused' may mean either truly unused OR skill_usage.log not wired up yet._" >> "$REPORT"
fi
echo "" >> "$REPORT"

echo "## Used Skills" >> "$REPORT"
for s in "${used[@]}"; do echo "- $s" >> "$REPORT"; done
echo "" >> "$REPORT"

echo "Report: ${REPORT}"
