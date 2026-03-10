#!/usr/bin/env python3
"""Rebuild 043_得意先売上一覧表.html main content to match Excel spec.
Task: subtask_142_001 (cmd_142)
Changes: 8 items — see queue/oyabun_to_kashira.yaml for spec details.
"""

import pathlib

FILE = pathlib.Path("/mnt/g/共有ドライブ/[PJ]ディムコ/01_再構築プロジェクト/90_personal/degawa/003_プロトタイプ完成new/043_得意先売上一覧表.html")

# Read original
content = FILE.read_text(encoding='utf-8')
lines = content.split('\n')

# --- Find key line indices (0-based) ---
main_start = next(i for i, l in enumerate(lines) if 'class="main-content"' in l)
first_script = next(i for i, l in enumerate(lines) if i > main_start and '<script>' in l)
# app-container close is between main-content end and first script
# Find it by scanning backwards from first_script
app_close = None
for i in range(first_script - 1, main_start, -1):
    if lines[i].strip() == '</div>':
        app_close = i
        break

print(f"main_start={main_start}, app_close={app_close}, first_script={first_script}")
print(f"Replacing lines {main_start+1} through {app_close} (file line numbers)")

# Find second <script> block start (sidebar JS — DO NOT TOUCH)
second_script = None
for i in range(first_script + 1, len(lines)):
    if '<script>' in lines[i]:
        second_script = i
        break

# Find first </script> (end of first script block)
first_script_end = next(i for i, l in enumerate(lines) if i > first_script and '</script>' in l)
print(f"first_script={first_script}, first_script_end={first_script_end}, second_script={second_script}")

# --- New CSS to insert before 960px media query ---
NEW_CSS = """\
    /* Header/detail row styles for grouped table */
    .header-row { background-color: #EBF3FA !important; font-weight: 600; cursor: pointer; }
    .header-row:hover { background-color: #d4e5f5 !important; }
    .header-row td { border-bottom: 2px solid #B0C4DE; }
    .detail-row { background-color: #fff; }
    .detail-row td { font-size: 12px; color: #555; padding: 8px 6px; }
    .btn-expand { background: #004B87; color: white; border: none; border-radius: 3px; width: 26px; height: 26px; cursor: pointer; font-size: 14px; line-height: 1; transition: transform 0.2s; }
    .btn-expand.expanded { transform: rotate(90deg); }
    .btn-expand:hover { background: #003366; }
    .expand-cell { text-align: center !important; width: 40px; }
    .footer-row { background-color: #f0f4f8 !important; }
    .footer-row td { border-top: 2px solid #004B87; }
    .thead-detail th { background: #336699 !important; font-size: 12px !important; padding: 8px 6px !important; font-weight: 500 !important; }
    .sort-btn { background: none; border: none; color: white; cursor: pointer; font-size: 14px; padding: 2px 4px; }
    .sort-btn:hover { opacity: 0.7; }
"""

# --- New main-content HTML ---
NEW_MAIN = """\
<div class="main-content" style="flex: 1; padding: 20px; overflow-y: auto;">
<h2 style="margin: 0 0 16px; color: #333; font-size: 20px;">得意先売上一覧表</h2>

<!-- 検索条件 -->
<div style="background: white; border-radius: 8px; padding: 16px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
<h3 style="margin: 0 0 12px; color: #333; font-size: 14px;">検索条件</h3>
<div style="display: flex; flex-wrap: wrap; gap: 12px; align-items: flex-end;">
<div style="display: flex; flex-direction: column;">
<label style="font-weight: 500; color: #004B87; font-size: 14px; margin-bottom: 4px;">売上日</label>
<input type="date" id="sales-date" style="width: 180px; padding: 6px 8px; border: 1px solid #ccc; border-radius: 4px;">
</div>
<button type="button" style="padding: 6px 20px; background: #4a90d9; color: white; border: none; border-radius: 4px; cursor: pointer;">検索</button>
</div>
</div>

<!-- 検索結果テーブル -->
<div style="background: white; border-radius: 8px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
<h3 style="margin: 0; color: #333; font-size: 14px;">検索結果</h3>
<span style="color: #666; font-size: 13px;">3件表示</span>
</div>
<div class="table-container">
<table class="data-table" style="min-width: 900px;">
<thead>
<tr>
<th style="width: 40px;"></th>
<th>得意先CD</th>
<th colspan="3">得意先名</th>
<th>売上額</th>
<th>返金額</th>
<th>合計額</th>
<th style="width: 40px;"><button class="sort-btn">△▽</button></th>
</tr>
<tr class="thead-detail">
<th></th>
<th>商伝番号</th>
<th>部門CD</th>
<th>部門名称</th>
<th>課名称</th>
<th>入金予定日</th>
<th>売上額</th>
<th>返品額</th>
<th>差引合計額</th>
</tr>
</thead>
<tbody>
<!-- Group 1: ｱ00001 株式会社hogehoge -->
<tr class="header-row" data-group="group1">
<td class="expand-cell"><button class="btn-expand" onclick="toggleDetail('group1')">＞</button></td>
<td style="text-align: left;">ｱ00001</td>
<td colspan="3" style="text-align: left;">株式会社hogehoge</td>
<td style="text-align: right;">100,000</td>
<td style="text-align: right;">0</td>
<td style="text-align: right;">100,000</td>
<td></td>
</tr>
<tr class="detail-row group1" style="display: none;">
<td></td>
<td style="text-align: left;">39-S1-0002-01</td>
<td style="text-align: left;">001</td>
<td style="text-align: left;">営業部門</td>
<td style="text-align: left;">営業課</td>
<td style="text-align: center;">2025/01/31</td>
<td style="text-align: right;">20,000</td>
<td style="text-align: right;">0</td>
<td style="text-align: right;">20,000</td>
</tr>
<tr class="detail-row group1" style="display: none;">
<td></td>
<td style="text-align: left;">39-S1-0002-02</td>
<td style="text-align: left;">001</td>
<td style="text-align: left;">営業部門</td>
<td style="text-align: left;">営業課</td>
<td style="text-align: center;">2025/01/31</td>
<td style="text-align: right;">80,000</td>
<td style="text-align: right;">0</td>
<td style="text-align: right;">80,000</td>
</tr>
<!-- Group 2: ｲ00001 株式会社○○ -->
<tr class="header-row" data-group="group2">
<td class="expand-cell"><button class="btn-expand" onclick="toggleDetail('group2')">＞</button></td>
<td style="text-align: left;">ｲ00001</td>
<td colspan="3" style="text-align: left;">株式会社○○</td>
<td style="text-align: right;">10,000</td>
<td style="text-align: right;">0</td>
<td style="text-align: right;">10,000</td>
<td></td>
</tr>
<!-- Group 3: ｳ00001 株式会社■■ -->
<tr class="header-row" data-group="group3">
<td class="expand-cell"><button class="btn-expand" onclick="toggleDetail('group3')">＞</button></td>
<td style="text-align: left;">ｳ00001</td>
<td colspan="3" style="text-align: left;">株式会社■■</td>
<td style="text-align: right;">30,000</td>
<td style="text-align: right;">10,000</td>
<td style="text-align: right;">20,000</td>
<td></td>
</tr>
</tbody>
<tfoot>
<tr class="footer-row">
<td colspan="5" style="text-align: right; font-weight: bold;">総合計</td>
<td style="text-align: right; font-weight: bold;">140,000</td>
<td style="text-align: right; font-weight: bold;">10,000</td>
<td style="text-align: right; font-weight: bold;">130,000</td>
<td></td>
</tr>
</tfoot>
</table>
</div>
</div>

<!-- 出力種類 -->
<div style="background: white; border-radius: 8px; padding: 16px; margin-top: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
<div style="display: flex; align-items: center; gap: 16px; flex-wrap: wrap; justify-content: flex-end;">
<label style="font-weight: 500; color: #004B87; font-size: 14px;">出力種類</label>
<select style="width: 200px; padding: 6px 8px; border: 1px solid #ccc; border-radius: 4px;">
<option>得意先売上一覧表</option>
<option>CSV</option>
</select>
<button type="button" style="padding: 6px 20px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer;">出力</button>
</div>
</div>
</div>"""

# --- New JS (replace first script block) ---
NEW_JS = """\
<script>
    // 明細行の展開/折りたたみ
    function toggleDetail(groupId) {
        var rows = document.querySelectorAll('.detail-row.' + groupId);
        var btn = document.querySelector('[data-group="' + groupId + '"] .btn-expand');
        if (!rows.length) return;
        var isHidden = rows[0].style.display === 'none';
        rows.forEach(function(row) {
            row.style.display = isHidden ? 'table-row' : 'none';
        });
        if (btn) {
            btn.classList.toggle('expanded', isHidden);
            btn.textContent = isHidden ? '＞' : '＞';
        }
    }

    // ヘッダー行クリックでも展開/折りたたみ
    document.addEventListener('DOMContentLoaded', function() {
        // 売上日の初期値を今日に設定
        var dateInput = document.getElementById('sales-date');
        if (dateInput) {
            var today = new Date().toISOString().split('T')[0];
            dateInput.value = today;
        }

        // ヘッダー行クリックで展開/折りたたみ（ボタン以外の領域）
        document.querySelectorAll('.header-row').forEach(function(row) {
            row.addEventListener('click', function(e) {
                if (e.target.classList.contains('btn-expand')) return;
                var groupId = this.getAttribute('data-group');
                if (groupId) toggleDetail(groupId);
            });
        });
    });
    </script>"""

# === Build the new file ===
new_lines = []

# Part 1: Everything before main-content (lines 0 to main_start-1)
# But we need to insert CSS before the 960px media query
css_insert_marker = '    /* 960px overflow fix (auto-generated) */'
css_inserted = False
for i in range(main_start):
    if not css_inserted and lines[i].strip() == css_insert_marker.strip():
        new_lines.append(NEW_CSS)
        css_inserted = True
    new_lines.append(lines[i])

if not css_inserted:
    # Fallback: insert before </style>
    print("WARNING: Could not find 960px marker, inserting before </style>")
    for idx, l in enumerate(new_lines):
        if '</style>' in l:
            new_lines.insert(idx, NEW_CSS)
            break

# Part 2: New main-content
new_lines.append(NEW_MAIN)

# Part 3: app-container close
new_lines.append('</div>')

# Part 4: Blank lines + new JS + keep second script block onward
new_lines.append('')
new_lines.append('')
new_lines.append(NEW_JS)

# Part 5: Second script block (sidebar JS) through end of file
for i in range(second_script, len(lines)):
    new_lines.append(lines[i])

# Write output
output = '\n'.join(new_lines)
FILE.write_text(output, encoding='utf-8')

# Verify
result_lines = output.split('\n')
print(f"\nOriginal: {len(lines)} lines")
print(f"New: {len(result_lines)} lines")

# Verify key elements present
checks = [
    ('sidebar unchanged', '<aside class="sidebar">' in output),
    ('single date picker', 'id="sales-date"' in output),
    ('no FROM-TO', '～' not in output),
    ('no クリア button', 'クリア' not in output),
    ('no pagination', '前へ' not in output and '次へ' not in output),
    ('combobox (select)', '<select' in output and '得意先売上一覧表</option>' in output),
    ('no radio buttons', 'type="radio"' not in output),
    ('expand button', 'btn-expand' in output and 'toggleDetail' in output),
    ('header cols 7', '得意先CD' in output and '返金額' in output and '合計額' in output),
    ('detail cols 8', '商伝番号' in output and '返品額' in output and '差引合計額' in output),
    ('footer totals', '総合計' in output and '140,000' in output),
    ('sample data', 'ｱ00001' in output and 'ｲ00001' in output and 'ｳ00001' in output),
    ('sort button', '△▽' in output),
    ('sidebar JS preserved', 'menu-category-header' in output),
]

print("\n=== Verification ===")
all_pass = True
for name, result in checks:
    status = "PASS" if result else "FAIL"
    if not result:
        all_pass = False
    print(f"  [{status}] {name}")

print(f"\n{'ALL CHECKS PASSED' if all_pass else 'SOME CHECKS FAILED'}")
