#!/usr/bin/env python3
"""Split kashira.md into kashira_core.md + kashira_policies.md
Also applies Item 3,4,5,10 fixes inline during split.
"""
from pathlib import Path
import re

SRC = Path("instructions/kashira.md")
CORE = Path("instructions/kashira_core.md")
POLICIES = Path("instructions/kashira_policies.md")

text = SRC.read_text(encoding="utf-8")
lines = text.split("\n")

# === Item 3: Remove W6/W7 pane definitions (lines 111-112, 0-indexed 110-111) ===
new_lines = []
for line in lines:
    if '{ id: 6, pane: "multiagent:0.6"' in line:
        continue
    if '{ id: 7, pane: "multiagent:0.7"' in line:
        continue
    new_lines.append(line)
lines = new_lines

# === Item 4: Fix range references ===
fixed = []
for line in lines:
    # "multiagent:0.1` through `multiagent:0.7`" -> "multiagent:0.5`"
    line = line.replace(
        "at `multiagent:0.1` through `multiagent:0.7` via send-keys",
        "at `multiagent:0.1` through `multiagent:0.5` via send-keys"
    )
    fixed.append(line)
lines = fixed

# === Item 5: Fix W5-W7 -> W5, W6/W7 references ===
fixed = []
for line in lines:
    # Bloom routing table: "W5, W6, W7" -> "W5"
    line = line.replace("| Haiku | W5, W6, W7 |", "| Haiku | W5 |")
    # "W5-W7" -> "W5"
    line = line.replace("W5-W7", "W5")
    # "Haiku Workers (W5-W7)" already handled by above
    # "all 7 workers" -> "all 5 workers"  (in Haiku Task Assignment Policy)
    line = line.replace("all 7 workers", "all 5 workers")
    fixed.append(line)
lines = fixed

# === Item 10: Remove stale context/ references ===
fixed = []
for line in lines:
    if 'read context/{project}.md' in line.lower() or 'context/{project}.md' in line:
        continue
    fixed.append(line)
lines = fixed

# Re-join for section splitting
text = "\n".join(lines)

# === Item 15: Split into core + policies ===
# Define section headers that go to POLICIES
policy_sections = [
    "## Cross-Review Protocol",
    "## Priority-Linked Review Depth",
    "## Language-Specific Review System",
    "## Cross-Review Dispute Resolution",
    "## Security Review Protocol",
    "## Interface Contracts (Phase 0.5)",
    "## Pre-Implementation Design Review (Phase 0)",
    "## Integration Test Gate (Phase 1.5)",
    "## P2P Review & Heads-Up Messaging (Kashira-Controlled)",
    "## Error Reassignment Protocol",
    "## Bug Fix Assignment Rule (Different-Worker Mandatory)",
    "## D8: ワーカー分担ルール（kashira向け）",
    "## Bloom Routing (Model Tier Assignment)",
    "## Worker Model Assignment Policy",
    "## Complexity-Weighted Task Distribution",
    "## Task YAML Size Limit",
    "## Haiku Task Assignment Policy (D7 consult_028)",
    "## W3 Hybrid Role Policy (consult_030 Topic 1B)",
    "## Command Splitting Rule (大規模cmd分割)",
    "## Context Budget Threshold (コンテキスト残量管理)",
]

# Parse into sections (## level)
sections = []
current_section = {"header": "__preamble__", "content": []}
in_frontmatter = False
frontmatter_lines = []

for line in lines:
    if line.strip() == "---" and not frontmatter_lines:
        in_frontmatter = True
        frontmatter_lines.append(line)
        continue
    if in_frontmatter:
        frontmatter_lines.append(line)
        if line.strip() == "---":
            in_frontmatter = False
        continue

    if line.startswith("## ") and not line.startswith("### "):
        if current_section["content"] or current_section["header"] != "__preamble__":
            sections.append(current_section)
        current_section = {"header": line.strip(), "content": [line]}
    else:
        current_section["content"].append(line)

if current_section["content"]:
    sections.append(current_section)

# Classify sections
core_sections = []
policy_section_list = []
preamble_text = []

for sec in sections:
    if sec["header"] == "__preamble__":
        preamble_text = sec["content"]
        continue

    is_policy = False
    for ps in policy_sections:
        if sec["header"].startswith(ps.rstrip()) or ps.rstrip().startswith(sec["header"].rstrip()):
            is_policy = True
            break
        # Fuzzy match on key phrase
        ps_key = ps.replace("## ", "").split("(")[0].strip()
        sec_key = sec["header"].replace("## ", "").split("(")[0].strip()
        if ps_key == sec_key:
            is_policy = True
            break

    if is_policy:
        policy_section_list.append(sec)
    else:
        core_sections.append(sec)

# Build kashira_core.md
core_lines = []
# Front matter
core_lines.extend(frontmatter_lines)
core_lines.append("")
# Add cross-reference note
core_lines.append("# Kashira (Head Cat) Instruction Manual")
core_lines.append("")
core_lines.append("> **Policy details**: See `instructions/kashira_policies.md` for cross-review, security review,")
core_lines.append("> Bloom routing, Haiku task policy, interface contracts, and all other policy/protocol definitions.")
core_lines.append("")

# Preamble (skip the original "# Kashira..." header if present)
for line in preamble_text:
    if line.strip() == "# Kashira (Head Cat) Instruction Manual":
        continue
    core_lines.append(line)

# Core sections
for sec in core_sections:
    core_lines.extend(sec["content"])
    core_lines.append("")

# Build kashira_policies.md
policy_lines = []
policy_lines.append("---")
policy_lines.append("# Kashira Policies & Protocols")
policy_lines.append("# Referenced from kashira_core.md — loaded on demand")
policy_lines.append("---")
policy_lines.append("")
policy_lines.append("# Kashira Policies & Protocols")
policy_lines.append("")
policy_lines.append("> **Core instructions**: See `instructions/kashira_core.md` for role, workflow, tmux, dashboard,")
policy_lines.append("> and daily operation procedures.")
policy_lines.append("")

for sec in policy_section_list:
    policy_lines.extend(sec["content"])
    policy_lines.append("")

# Write files
CORE.write_text("\n".join(core_lines), encoding="utf-8")
POLICIES.write_text("\n".join(policy_lines), encoding="utf-8")

print(f"kashira_core.md: {len(core_lines)} lines")
print(f"kashira_policies.md: {len(policy_lines)} lines")

# Verify no W6/W7 references remain
for path, content in [(CORE, "\n".join(core_lines)), (POLICIES, "\n".join(policy_lines))]:
    for pattern in ["W6", "W7", "worker6", "worker7", "6gou", "7gou", "multiagent:0.6", "multiagent:0.7"]:
        if pattern in content:
            print(f"WARNING: '{pattern}' still found in {path.name}")

# Verify no context/ references remain
for path, content in [(CORE, "\n".join(core_lines)), (POLICIES, "\n".join(policy_lines))]:
    if "context/{project}" in content:
        print(f"WARNING: 'context/{{project}}' still found in {path.name}")

print("Done.")
