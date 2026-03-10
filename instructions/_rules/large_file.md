# Large File Write Protocol

Merged from: Task Sizing Pre-Flight + Chunked Write Rule.

## Pre-Flight Sizing

Before starting any implementation task, estimate the output file size:

| Estimated output | Approach |
|-----------------|----------|
| <200 lines | Normal Write tool |
| 200-500 lines | Write OK, but chunked write recommended |
| 500-2000 lines | **Python/bash script MANDATORY** — do NOT use Write |
| >2000 lines | Split into multiple files OR use merge skill |

**Hard rule: Never attempt to Write >500 lines in a single tool call.** The Write tool + output token limits make this unreliable. Use a Python script to generate the file instead.

If the task description does not specify an approach but you estimate >500 lines, switch to script approach on your own initiative and note it in your report.

## Chunked Write

For files >200 lines, use chunked writing to avoid output token truncation:

**Option A — Chunked Write/Edit:**
1. First Write: output the first ~200 lines (file skeleton + first sections)
2. Subsequent Edits: append remaining sections using Edit tool
3. Final verification: Read the file back to confirm completeness

**Option B — Script generation (preferred for >500 lines):**
1. Write a Python/bash script that generates the output file
2. Run the script
3. Verify the output with a validation step

**Prohibited:** Attempting to Write >500 lines in a single Write tool call. This risks:
- Output token truncation (silent data loss)
- Secondary bugs from truncated YAML/code
- Worker stall when truncation causes parse errors on re-read

Reference: cmd_021 — W1 stalled trying to manually Write 2194 lines. W4 hit MAX_OUTPUT_TOKENS=32000 on 657-line YAML → truncation → stall chain.
