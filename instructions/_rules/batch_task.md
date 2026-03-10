# Batch Task Protocol

When a task involves 5+ files with identical transformation:
1. **Phase 0** (1 worker): Build converter script + verify on 1 file
2. **Phase 1** (all workers): Run converter on assigned files

Kashira decides phase strategy. Workers may propose 2-phase in report. Report converter script as `skill_candidate` if reusable.

## Visual Task Disclaimer

When your task produces visual output (HTML, CSS, UI) that you cannot render:
- Add `visual_disclaimer: true` to your report
- List specific areas requiring visual verification in notes
- Never report layout/styling work as fully verified without browser confirmation
