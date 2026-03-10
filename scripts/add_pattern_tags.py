#!/usr/bin/env python3
"""Add cause/action/outcome tags to all entries in patterns.yaml.

Strategy: Parse YAML with PyYAML, add tags dict to each entry, then
rebuild the file preserving comments by doing text-level insertion.
"""

import yaml
import re

TAGS = {
    "sp_001": {"cause": "WSL path format incompatible with Windows dumpbin.exe", "action": "convert paths via wslpath -w before passing to Windows tools", "outcome": "DLL analysis works from WSL without manual path editing"},
    "sp_002": {"cause": "Japanese characters in file paths break PowerShell DLL operations", "action": "copy DLL to temp ASCII-path directory before testing", "outcome": "PowerShell tests pass without path encoding errors"},
    "sp_003": {"cause": "disassembly-to-source restoration has multiple subtle mismatch points", "action": "compare calling conventions, function pointer tables, compression, API signatures", "outcome": "systematic verification catches discrepancies that spot-checks miss"},
    "sp_004": {"cause": "restored C++ source diverges from original DLL behavior in multiple ways", "action": "manage fixes by B-x/C-x IDs, update header+cpp+DEF+CMakeLists simultaneously", "outcome": "restored DLL matches original logic for dispatch, RLE, and palette"},
    "sp_005": {"cause": "SPI dispatcher DLL needs crash protection without breaking C++ objects", "action": "SEH wrappers per export + GetProcAddress function table + /EHa option", "outcome": "crash-safe DLL with separate entry points (no ICF folding)"},
    "sp_006": {"cause": "MSVC C2712 when __try/__except coexists with C++ destructors in same function", "action": "separate SEH into wrapper function, keep C++ objects in Impl function", "outcome": "compiles cleanly with SEH protection and C++ objects both working"},
    "sp_007": {"cause": "x86 cross-compile from x64 host fails on mspdb*.dll dependency", "action": "use HostX64/x86 toolchain, add both x86 and x64 to PATH", "outcome": "32-bit builds succeed with dumpbin and other tools still available"},
    "sp_008": {"cause": "MSVC ICF merges GetPicture/GetPreview into single entry point", "action": "/OPT:NOICF linker flag + differentiated Impl functions", "outcome": "separate RVAs confirmed via dumpbin /EXPORTS"},
    "sp_009": {"cause": "TUI apps have render-to-input-ready gap causing send-keys race conditions", "action": "prompt detection + 2-3s stabilization delay before send-keys", "outcome": "send-keys reliability improved for tmux-based automation"},
    "sp_010": {"cause": "Node.js epoll event loop always shows do_epoll_wait in /proc/wchan", "action": "switch from process-based to screen-output-based detection (capture-pane)", "outcome": "reliable idle/busy detection for Node.js CLI apps"},
    "sp_011": {"cause": "fire-and-forget send-keys occasionally not received by target pane", "action": "send-keys + sleep 3 + capture-pane verification + retry up to 3x", "outcome": "fire-and-verify delivery with confirmed activity in target"},
    "sp_012": {"cause": "equal task count but unequal effort caused worker imbalance", "action": "estimate total lines/files/complexity per worker, split heavy tasks", "outcome": "balanced completion times across workers"},
    "sp_013": {"cause": "FortiGate syslog uses key=value format needing structured parsing", "action": "regex parse + classify by type/subtype + output matching API dict format", "outcome": "drop-in compatible structured data from syslog messages"},
    "sp_014": {"cause": "unit tests pass individually but modules fail at integration boundaries", "action": "Phase 1.5 integration smoke tests by non-author worker tracing full pipeline", "outcome": "interface mismatches caught before cross-review phase"},
    "sp_015": {"cause": "nested YAML config causes KeyError chains and consumer guessing", "action": "flat keys only for config files; accessor module if nesting needed", "outcome": "greppable config, immediate KeyError on typo, no nesting bugs"},
    "sp_016": {"cause": "accent colors serving same UI role missed during color migration", "action": "grep all unique hex/rgba, classify into palette families, map every color explicitly", "outcome": "complete color migration with no leftover off-palette colors"},
    "sp_017": {"cause": "inline style attributes bypassed CSS variable-focused color search", "action": "separate grep for hardcoded hex in style= attributes after fixing :root vars", "outcome": "all color references found including inline styles"},
    "sp_018": {"cause": "undefined CSS custom property makes entire property IACVT (invisible)", "action": "grep var(-- usage, cross-reference against :root definitions", "outcome": "missing vars identified, borders and colors restored"},
    "sp_019": {"cause": "single analysis has blind spots; two independent analyses complement each other", "action": "4-section comparison (agree/disagree/new/gaps) with winner per point", "outcome": "revised priority stack with higher confidence from convergence signals"},
    "sp_020": {"cause": "synthesis documents can misattribute, omit, or reframe findings subtly", "action": "source attribution + omission pattern + framing bias + implementation readiness checks", "outcome": "honest evaluation of synthesis quality and actionability"},
    "sp_021": {"cause": "[[ ]] && action exits with code 1 when condition false under set -e", "action": "replace with if/then/fi pattern or append || true", "outcome": "script survives false conditions under strict bash mode"},
    "sp_022": {"cause": "watcher writing to monitored namespace creates TOCTOU race conditions", "action": "enforce hard boundary: watcher detects+notifies, only agents write responses", "outcome": "no false completion claims from watcher authoring"},
    "sp_023": {"cause": "code changes to running daemon not effective until restart", "action": "kill old process, verify gone, restart, verify PID timestamp > file mtime", "outcome": "confirmed new code is running after fix deployment"},
    "sp_024": {"cause": "nominal RPD != effective capacity due to internal request multipliers", "action": "calculate effective_capacity with pessimistic budgeting and multiplier factor", "outcome": "accurate rate budget prevents correlated agent failures"},
    "sp_025": {"cause": "risk analyses contain unsubstantiated quantitative claims presented as facts", "action": "ask where base numbers come from: measured, estimated, or assumed", "outcome": "false precision flagged, assumed numbers labeled as illustrative"},
    "sp_026": {"cause": "same-level-as-failure fixes don't prevent recurrence of violations", "action": "include L3 (code) enforcement + L2.5 (self-check) as supplement", "outcome": "structural enforcement that doesn't rely on violator's judgment"},
    "sp_027": {"cause": "cooperation mandates in debate format structurally converge to TIE", "action": "distinguish adversarial vs mutual-evaluation purpose before format choice", "outcome": "correct format selected per evaluation purpose"},
    "sp_028": {"cause": "Discord bots have multiple attack surfaces (auth, input, subprocess, files, tokens)", "action": "6-point checklist: auth per handler, input sanitize, list-args, file lock, audit log, token grep", "outcome": "comprehensive security posture for command-driven bots"},
    "sp_029": {"cause": "small pixel targets look thin without anti-aliasing", "action": "render at 4x resolution then LANCZOS downscale, increase font 10-15% and double borders", "outcome": "visually crisp small images matching reference quality"},
    "sp_030": {"cause": "ActiveReports .rpx schema undocumented, guessing causes format errors", "action": "use designer-generated template as schema reference, match exact XML structure", "outcome": "valid .rpx files that load in AR18 designer"},
    "sp_031": {"cause": "boatrace odds embedded in results API, not a separate endpoint", "action": "fetch results endpoint, extract payout.trifecta, divide by 100", "outcome": "correct odds data from Boatrace Open API"},
    "sp_032": {"cause": "UPDATE without combination in WHERE hits all bets in race", "action": "always include combination in WHERE clause for record_result updates", "outcome": "only target bet record updated, no collateral damage"},
    "fp_001": {"cause": "SEH __try added directly to functions containing C++ destructors", "action": "attempted inline SEH in 9 export functions with std::string/vector", "outcome": "C2712 compile error in 9 locations"},
    "fp_002": {"cause": "config structure implicit in YAML, no schema check, consumers guess nesting", "action": "awareness hints given but no structural enforcement", "outcome": "config mismatch recurred 3 times despite warnings"},
    "fp_003": {"cause": "tier treated as flat label, copy-paste query without adjusting WHERE", "action": "JOIN with only tier/category as match key for compound conditions", "outcome": "cartesian products or 0% match rate for mismatched categories"},
    "fp_004": {"cause": "all unit tests used self-consistent fixtures, no cross-module verification", "action": "78 tests passed against own mocks, zero integration tests", "outcome": "product broken at all 6 module boundaries despite passing tests"},
    "fp_005": {"cause": "optional regex [Ss]? makes S suffix optional, base model matches variant pattern", "action": "used [Ss]? for model names where base and S-variant are distinct products", "outcome": "iPhone 6 misclassified as 6S, iPhone 5 as 5S"},
    "fp_006": {"cause": "developer used file unlink (nuclear option) instead of targeted table cleanup", "action": "DB file deleted on every run to reset transient data", "outcome": "persistent tables (price_history, scrape_history) destroyed each run"},
    "fp_007": {"cause": "custom .col-N classes collide with Bootstrap column utility names", "action": "custom CSS grid using col-2/col-3 naming alongside Bootstrap 5", "outcome": "containers compressed to 16.67%/25% by Bootstrap width rules"},
    "fp_008": {"cause": "no single schema owner, each module creates own CREATE TABLE with different columns", "action": "two modules independently define bets table with incompatible schemas", "outcome": "first-mover wins, second module INSERT fails on missing columns"},
    "fp_009": {"cause": "stray closing tag causes HTML5 parser to early-close container", "action": "CSS overflow fix applied but HTML structure bug was true root cause", "outcome": "CSS containment ineffective because content rendered outside container"},
    "fp_010": {"cause": "main.py author only registered their own router, missed other workers' routers", "action": "multi-worker parallel FastAPI implementation without router registration contract", "outcome": "incomplete API with missing route prefixes"},
    "fp_011": {"cause": "interface contract specified response shapes but not form field names", "action": "template and router authors independently chose different field names", "outcome": "silent data loss on every POST due to field name mismatch"},
    "wa_001": {"cause": "Playwright chromium needs libasound.so.2, unavailable on WSL without sudo", "action": "dpkg-deb -x to extract from .deb, set LD_PRELOAD", "outcome": "Playwright runs on WSL without root access"},
    "wa_002": {"cause": "LightGBM needs libgomp.so.1, unavailable on WSL without sudo", "action": "apt-get download + dpkg-deb -x + LD_PRELOAD injection", "outcome": "LightGBM runs on WSL without root access"},
}

def process(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # First, remove any existing tags blocks (from partial previous run)
    # Match: "    tags:\n      cause: ...\n      action: ...\n      outcome: ...\n"
    content = re.sub(
        r'(\n)(    tags:\n      cause: "[^"]*"\n      action: "[^"]*"\n      outcome: "[^"]*"\n)',
        '',
        content
    )

    # Now insert tags for each pattern ID
    for pat_id, tags in TAGS.items():
        # Find the id line and then the last field before next entry or section
        # Pattern: find "  - id: {pat_id}\n" then collect lines until next "  - id:" or section header
        pattern = re.compile(
            rf'(  - id: {re.escape(pat_id)}\n'  # id line
            rf'(?:    \w.*\n)*?)'                 # all indented field lines (non-greedy)
            rf'(    \w[^\n]*\n)'                  # last field line before boundary
            rf'(?=  - id:|\n  - id:|[a-z_]+:|\Z)',  # lookahead: next entry, section, or EOF
            re.MULTILINE
        )

        def replacer(m):
            prefix = m.group(1)
            last_field = m.group(2)
            tag_block = (
                f'    tags:\n'
                f'      cause: "{tags["cause"]}"\n'
                f'      action: "{tags["action"]}"\n'
                f'      outcome: "{tags["outcome"]}"\n'
            )
            return prefix + last_field + tag_block

        new_content = pattern.sub(replacer, content)
        if new_content == content:
            print(f"WARNING: Could not insert tags for {pat_id}")
        content = new_content

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

    # Verify
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    total = 0
    tagged = 0
    missing = []
    for section in ['success_patterns', 'failure_patterns', 'workaround_patterns']:
        for entry in data.get(section, []):
            total += 1
            if 'tags' in entry:
                tagged += 1
                for field in ['cause', 'action', 'outcome']:
                    if field not in entry['tags']:
                        missing.append(f"{entry['id']}: missing tags.{field}")
            else:
                missing.append(f"{entry['id']}: no tags field")

    print(f"Total entries: {total}")
    print(f"Tagged: {tagged}")
    if missing:
        print(f"MISSING ({len(missing)}):")
        for m in missing:
            print(f"  {m}")
        return False
    else:
        print("ALL entries have complete tags (cause/action/outcome)")
        return True

if __name__ == '__main__':
    process('memory/patterns.yaml')
