#!/usr/bin/env python3
"""Generate issue_list_w1.md for cmd_037 subtask_037_001."""

output_path = "/mnt/c/tools/neko-multi-agent/outputs/dimco-html-review/issue_list_w1.md"

content = r"""# Visual/Layout Audit — Worker1 (11 files)

Generated: cmd_037 subtask_037_001

---

## company-dashboard.html

| # | Issue | CSS Selector / Line | Severity | Description |
|---|-------|---------------------|----------|-------------|
| 1 | Broken `@keyframes lift-in` syntax | company-dashboard.css L145-151 | High | Missing closing `}` in `@keyframes lift-in` — `from` block never closes before `to`. All subsequent rules (checkbox, .text-purple) become part of broken keyframe and are non-functional. |
| 2 | `.tab` fixed `min-width: 120px` | company-dashboard.css L69 | Medium | 6 tabs × 120px = ~780px minimum. `.tabs` container has no `flex-wrap` or `overflow-x: auto` — tabs overflow on narrow viewports. |
| 3 | `.info-wrap` 2-col grid no stacking | company-dashboard.css L34-38 | Medium | `grid-template-columns: 1fr 1fr` with no `@media` breakpoint. Info tables squeeze instead of stacking on narrow screens. |
| 4 | `.info-grid th` fixed `width: 120px` | company-dashboard.css L29 | Low | Hard-coded th width leaves little room for td content on narrow screens. |
| 5 | Table in `.table-wrap` has no `min-width` | company-dashboard.css L87-98 | Low | `overflow-x: auto` on wrapper is good but table has no `min-width` — columns compress instead of triggering scroll for multi-column tabs. |

---

## company-search.html

| # | Issue | CSS Selector / Line | Severity | Description |
|---|-------|---------------------|----------|-------------|
| 1 | `.page` fixed `max-width: 1100px` | company-search.css L3 | High | Same pattern already fixed in company-dashboard.css. This file still has the old value — content won't use full width on wide monitors. |
| 2 | Broken `@keyframes lift-in` syntax | company-search.css L208-214 | High | Same missing-brace issue as company-dashboard. All CSS rules after L208 corrupted. |
| 3 | Broken `@keyframes row-in` syntax | company-search.css L216-222 | High | Second broken keyframe compounds parse error from #2. |
| 4 | Duplicated JavaScript block | HTML L379-538 | High | Entire `<script>` block duplicated (inside `<main>` and after `</main>`). `const` redeclaration errors crash all JS — search/filter/clear non-functional. |
| 5 | Global `button` style override | company-search.css L102-129 | Medium | Bare `button` selector overrides all buttons globally including sidebar hamburger. |
| 6 | `.form-grid` 4-col no collapse | company-search.css L36-40 | Medium | `grid-template-columns: 120px 1fr 120px 1fr` — no responsive breakpoint, inputs become unusable on narrow screens. |
| 7 | `.period-grid` 5-col no collapse | company-search.css L88-93 | Medium | `grid-template-columns: 24px 90px 1fr 40px 1fr` — no breakpoint for narrow screens. |
| 8 | `max-height: 320px` + 2 scrollbars | company-search.css L141,149 | Medium | Table has `min-width: 900px` + container `max-height: 320px` — both scrollbars appear simultaneously, poor UX. |
| 9 | `.page` border color mismatch | company-search.css L7 | Low | Uses `#d6e3f7` instead of theme `--border` (`#c8d6e5`). |

---

## 作業予定一覧.html

| # | Issue | CSS Selector / Line | Severity | Description |
|---|-------|---------------------|----------|-------------|
| 1 | `.calendar-detail-layout` fixed 420px panel | 作業予定一覧.css L93 | High | `grid-template-columns: 1fr 420px` — detail panel is exactly 420px. No `@media` to stack on narrow/tablet screens. Calendar cells compress to unusable widths below ~900px. |
| 2 | No `overflow-x` on `.calendar-grid` | 作業予定一覧.css L136-139 | Medium | 7-column grid with `white-space: nowrap` count badges — will overflow cells on narrow screens with no scroll mechanism. |
| 3 | Calendar cells `min-height: 90px` | 作業予定一覧.css L162 | Medium | Forces tall layout that doesn't adapt to narrow screens. Combined with 420px panel, creates very large fixed layout. |
| 4 | `.detail-panel max-height` clips on short viewports | 作業予定一覧.css L234 | Medium | `calc(100vh - 300px)` yields only ~468px on 768px height — nested scroll conflicts with page scroll. |
| 5 | `.container` max-width: 1800px (dead CSS) | 作業予定一覧.css L5 | Low | HTML uses `.container-fluid`, never `.container`. Rule never applies. |

---

## 作業予定表.html

| # | Issue | CSS Selector / Line | Severity | Description |
|---|-------|---------------------|----------|-------------|
| 1 | 10 sticky cols with hardcoded `left` px offsets | 作業予定表.css L181-219 | High | Combined fixed-column width is 868px before day columns. On screens < ~1000px (after sidebar), fixed columns fill viewport — no day columns visible without scrolling. If any column content overflows its assigned width, columns overlap because `left` positions are hardcoded. |
| 2 | `white-space: nowrap` on all cells | 作業予定表.css L151 | Medium | Long company names exceeding 140px (e.g., "(株)デンソーウェーブ") overflow cell boundaries. Fixed `left` offsets don't adjust — causes text overlap. |
| 3 | `.schedule-table width: max-content` | 作業予定表.css L141 | Medium | Table can never shrink below ~1860px (868px fixed + 31 × 32px day cols). Extensive horizontal scrolling required on normal screens. |
| 4 | Fixed-col z-index border artifacts | 作業予定表.css L170-179 | Medium | `thead th.fixed-col` z-index: 3, non-fixed `thead th` z-index: 2 — day-column headers slide under fixed headers during scroll, borders may disappear at boundary. |
| 5 | `.search-row` flex items no breakpoint | 作業予定表.css L34-39 | Medium | `flex-wrap: wrap` is set but no `@media` — 5 search fields + button may wrap awkwardly at medium widths. |
| 6 | `.sub-header` bg overridden by `bg-navy !important` | 作業予定表.css L164-168 | Low | `var(--primary-blue-light)` never applies because `thead.bg-navy` uses `!important` — both header rows appear same dark navy, no differentiation. |
| 7 | Detail sub-tables inline widths total ~950px | HTML L331-431 | Low | Fixed pixel widths in inline styles prevent column adaptation. `.detail-table-wrap` overflow-x: auto provides scrolling. |

---

## 個人営業管理.html

| # | Issue | CSS Selector / Line | Severity | Description |
|---|-------|---------------------|----------|-------------|
| 1 | `overflow-x:hidden` on main content column | HTML L109 inline | Medium | Silently clips horizontal overflow instead of scrolling. If table data exceeds viewport width, right side is invisibly cut off. |
| 2 | 通期 tab table 14 columns no `min-width` | HTML L399-475 | High | 14 columns (name + 12 months + total) with no `min-width` on table — columns shrink to unreadable widths before scroll kicks in. |
| 3 | Table header color conflict (3-way) | style.css L73,86 vs 個人営業管理.css L105-117 | Medium | `thead.bg-navy th !important` (#001f3f) overrides page CSS `.header-row-2 th` (#0070C0). Intended two-tone header becomes uniform dark navy. |
| 4 | No responsive breakpoints | 個人営業管理.css (entire file) | Medium | Zero `@media` queries. `.tabs` and period select layout won't reflow on mobile. |
| 5 | `transform: scale(1.01)` on row hover | 個人営業管理.css L147-152 | Low | Causes rows to pop out and overlap adjacent rows — borders shift during hover. |
| 6 | `.container` max-width: 1800px (dead CSS) | 個人営業管理.css L2 | Low | HTML uses `.container-fluid`. Rule never applies. |

---

## 入庫.html

| # | Issue | CSS Selector / Line | Severity | Description |
|---|-------|---------------------|----------|-------------|
| 1 | `.form-row` 2-col grid no responsive breakpoint | 入庫.css L60 | High | `grid-template-columns: 1fr 1fr` with `label min-width: 150px` — no `@media` to collapse to single column. Unusable on mobile. |
| 2 | Inline fixed-width inputs | HTML L176,182,188,192,198 | Medium | Multiple `style="width: 160px"` / `180px` / `250px` override flex:1 — won't shrink on narrow screens, overflow grid cells. |
| 3 | `thead.bg-navy th` overrides page header color | style.css L73 vs 入庫.css L120 | Medium | `!important` forces #001f3f instead of intended var(--primary-blue) (#005DA8). |
| 4 | Attachment section heavy inline styles | HTML L267-309 | Medium | Entire section built with inline styles — not responsive-aware, maintenance difficult. |
| 5 | Registration button padding inconsistency | HTML L339 | Medium | Inline `padding: 12px 60px` overrides CSS class `padding: 10px 24px` — size mismatch with other .btn elements. |
| 6 | `.container` max-width: 1400px (dead CSS) | 入庫.css L4 | Low | HTML uses `.container-fluid`. |

---

## 入庫一覧.html

| # | Issue | CSS Selector / Line | Severity | Description |
|---|-------|---------------------|----------|-------------|
| 1 | 16-column table ~1860px with inline fixed th widths | HTML L258-274 | High | Total column widths sum to ~1860px in inline styles. Even at full 1920px screen (minus sidebar), requires horizontal scrolling. Columns can't adapt. |
| 2 | `.search-form-row` 2-col no responsive breakpoint | 入庫一覧.css L35 | High | `grid-template-columns: 1fr 1fr` — 7 rows of search fields compressed on narrow screens, no `@media` to stack. |
| 3 | Date range row no flex-wrap | HTML L213-247 | Medium | Two date inputs + separator + 3 date buttons + label in single flex row — overflow or compress on narrow screens. |
| 4 | `thead.bg-navy th` overrides page header color | style.css L73 vs 入庫一覧.css L142 | Medium | Same `!important` override pattern. |
| 5 | Asymmetric date input widths | HTML L217,219 | Low | First date input has `width: 160px`, second has no width — visual misalignment in range pair. |
| 6 | `.container` max-width: 1800px (dead CSS) | 入庫一覧.css L4 | Low | HTML uses `.container-fluid`. |

---

## 出荷.html

| # | Issue | CSS Selector / Line | Severity | Description |
|---|-------|---------------------|----------|-------------|
| 1 | Duplicate action buttons | HTML L132-135 + L139-142 | High | TWO sets of 登録/画面クリア buttons rendered with different styles (Bootstrap outline vs CSS gradient). Clearly a bug — one set should be removed. |
| 2 | `.form-row` 2-col no responsive breakpoint | 出荷.css L60 | High | Same as 入庫.html — no `@media`, unusable on narrow screens. |
| 3 | `thead.bg-navy th` overrides header color | style.css L73 vs 出荷.css L132 | Medium | Same pattern. Both 出荷履歴 and 同梱書類 tables affected. |
| 4 | 出荷日 asymmetric width | HTML L207 | Medium | `style="width: 160px"` on 出荷日 input but not on 出荷予定日 in same row — visual mismatch. |
| 5 | `.container` max-width: 1400px (dead CSS) | 出荷.css L4 | Low | HTML uses `.container-fluid`. |

---

## 出荷一覧.html

| # | Issue | CSS Selector / Line | Severity | Description |
|---|-------|---------------------|----------|-------------|
| 1 | Duplicate action buttons | HTML L132-137 + L141-146 | Medium | Two sets of 検索/画面クリア/新規登録/出力 buttons — Bootstrap set + CSS gradient set. |
| 2 | `.btn` overrides Bootstrap `.btn` | 出荷一覧.css L19-30 | Medium | Page CSS redefines `.btn` globally — Bootstrap `btn-outline-secondary` buttons lose intended styling. |
| 3 | `.search-form-row` no responsive breakpoint | 出荷一覧.css L35 + L74 | Medium | 2-col grid + `label min-width: 120px` — overflow below ~900px. Zero `@media` queries in file. |
| 4 | `wide-table` class undefined | HTML L282 | Low | Class referenced but no CSS rule defines it. Dead class. |
| 5 | `.container` max-width: 1800px (dead CSS) | 出荷一覧.css L4 | Low | HTML uses `.container-fluid`. |

---

## 受注一覧.html

| # | Issue | CSS Selector / Line | Severity | Description |
|---|-------|---------------------|----------|-------------|
| 1 | **Unclosed `@media` query** | 受注一覧.css L358 | High | `@media (max-width: 1400px) {` never closed. All rules after L358 — `.approval-status`, checkbox styling, `.text-purple` — are trapped inside media query. On screens > 1400px: approval badges unstyled, purple checkboxes disappear. |
| 2 | Duplicate action buttons | HTML L132-138 + L144-150 | Medium | Two sets of 検索/画面クリア/新規(国内)/新規(海外)/出力 buttons. |
| 3 | `.btn` overrides Bootstrap `.btn` | 受注一覧.css L36-53 | Medium | Same global `.btn` override pattern. |
| 4 | Generic `table { min-width: 1200px }` | 受注一覧.css L174 | Medium | Applies to ALL tables including nested child/grandchild tables — forces horizontal scrolling everywhere. |
| 5 | `overflow-x: hidden` on main content | HTML L109 inline | Medium | Silently clips horizontal overflow. Tables inside scroll wrappers mitigate, but content outside wrappers is clipped. |
| 6 | `wide-table` class undefined | HTML L402,457,500 | Low | Class referenced but no CSS rule defines it. |
| 7 | Empty form fields as spacers in grid | HTML L229-231 etc. | Low | Empty `.form-field` entries become visible empty rows when `@media` stacks to 1 column. |
| 8 | `.container` max-width: 1800px (dead CSS) | 受注一覧.css L3 | Low | HTML uses `.container-fluid`. |

---

## 受注画面.html

| # | Issue | CSS Selector / Line | Severity | Description |
|---|-------|---------------------|----------|-------------|
| 1 | `table td:first-child` forced blue bg on ALL tables | 受注画面.css L483-488 | High | Every table's first data column becomes blue header-style (white text on #005DA8). Affects payment-table, child-table, process-table, search dialog — data cells look like headers. |
| 2 | `.child-table th` color mismatch | 受注画面.css L96-97 | High | `color: var(--primary-blue-dark)` (#001f3f dark navy) on `background: #005DA8` — dark text on blue instead of white-on-blue used everywhere else. |
| 3 | Zero `@media` breakpoints (most complex page) | 受注画面.css (entire file) | High | Multiple 2-column layouts (`.flex-container`, `.two-column`) won't stack. Page unusable below ~1000px. |
| 4 | `table td:last-child` border-right removed | 受注画面.css L514-516 | Medium | Inconsistent borders — last cell missing right border on all tables. |
| 5 | `.payment-info { max-width: 1000px }` | 受注画面.css L1-5 | Medium | Fixed max-width while rest of page is fluid — visual width mismatch. |
| 6 | Duplicate `.payment-table` definitions | 受注画面.css L16-51 vs L257-284 | Medium | Second block overrides first — sticky header functionality lost. |
| 7 | `.label-cell` 140px vs `.table-row .th` 120px | 受注画面.css L307-317 vs L424-431 | Medium | 20px label misalignment between top section and card sections. |
| 8 | Input border `#1a7cc7` vs other pages' `var(--border-color)` | 受注画面.css L331 | Medium | Prominent blue input borders differ from other pages' gray borders — cross-page inconsistency. |
| 9 | Dialog fixed widths (500px, 700px) | HTML L849, L871 inline | Medium | No `max-width: 90vw` fallback — dialogs overflow on narrow viewports. |
| 10 | `.enclosed-docs-label .th` dark text on blue bg | 受注画面.css L806-808 | Medium | `color: var(--primary-blue-dark)` on blue background — hard to read. |
| 11 | `colspan` attribute on `<div>` elements | HTML L328,331,411,414 | Low | `colspan` has no effect on `<div>` — divs won't span as intended. |

---

## Cross-Cutting Issues (All 11 Files)

| Issue | Files Affected | Severity |
|-------|---------------|----------|
| **No `@media` responsive breakpoints** — 2-col grids, flex layouts, tabs break on mobile | All 11 (受注一覧 has one broken) | High |
| **`thead.bg-navy th !important`** overrides page-level header colors to dark navy | 個人営業管理, 入庫, 入庫一覧, 出荷, 出荷一覧, 受注一覧, 受注画面, 作業予定表 | Medium |
| **`.container` max-width (dead CSS)** — HTML uses `.container-fluid` everywhere | 作業予定一覧, 個人営業管理, 入庫, 入庫一覧, 出荷, 出荷一覧, 受注一覧 | Low |
| **Duplicate action buttons** — Bootstrap set + custom CSS gradient set | 出荷, 出荷一覧, 受注一覧 | Medium-High |
| **Broken `@keyframes` syntax** — missing closing braces corrupt subsequent rules | company-dashboard, company-search | High |
| **Duplicated JS block** in company-search.html crashes all page JS | company-search | High |
| **`--pink-primary/dark/darker` variable naming** — all are blue values | All (via style.css) | Low |
| **Checkbox purple circle (#6a1b9a) duplicated** in each page CSS + style.css | All 11 | Low |

---

## Clean Files

None — all 11 files have at least one issue.
"""

with open(output_path, "w", encoding="utf-8") as f:
    f.write(content.strip() + "\n")

# Verify
with open(output_path, "r", encoding="utf-8") as f:
    lines = f.readlines()
print(f"Written: {output_path}")
print(f"Lines: {len(lines)}")
print(f"Size: {len(''.join(lines))} bytes")
