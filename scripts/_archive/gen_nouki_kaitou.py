#!/usr/bin/env python3
"""Generate 天龍納期回答一覧.html from the existing file (preserving sidebar + CSS) and replacing content."""

import re
import sys

TARGET = "/mnt/g/共有ドライブ/[PJ]ディムコ/01_再構築プロジェクト/90_personal/degawa/003_プロトタイプ完成new/納期回答一覧.html"

# Read the existing file to preserve sidebar and CSS
with open(TARGET, "r", encoding="utf-8") as f:
    original = f.read()

# Extract everything up to and including <main class="main-content">
# and everything from the closing </main> tag onward (scripts)
head_match = re.search(r'(.*?<main class="main-content">)', original, re.DOTALL)
if not head_match:
    print("ERROR: Could not find <main> tag", file=sys.stderr)
    sys.exit(1)

head_part = head_match.group(1)

# Find everything from </main> to end
tail_match = re.search(r'(</main>.*)', original, re.DOTALL)
if not tail_match:
    print("ERROR: Could not find </main> tag", file=sys.stderr)
    sys.exit(1)

tail_part = tail_match.group(1)

# Build the new content section
content = """
<div class="content">
<div class="container"><div class="header">
<h1>天龍納期回答一覧</h1>
</div>
<!-- アクションボタン -->
<div class="action-buttons">
<button class="btn" onclick="alert('検索を実行します')">🔍 検索</button>
<button class="btn" id="btnClear">クリア</button>
</div>
<!-- 検索条件セクション -->
<div class="section-header">検索条件</div>
<div class="search-form">
<div class="search-form-row">
<div class="search-form-field">
<label>受注日</label>
<div class="date-range">
<input style="width: 160px" type="date" value=""/>
<span>～</span>
<input style="width: 160px" type="date" value=""/>
</div>
</div>
<div class="search-form-field">
<label>担当者</label>
<select style="flex: 1; border: 2px solid var(--border-color); padding: 8px 12px; font-size: 13px; border-radius: 6px;">
<option value="">選択してください</option>
<option>木下</option>
<option>佐藤</option>
<option>鈴木</option>
</select>
</div>
</div>
<div class="search-form-row">
<div class="search-form-field">
<label>エンドユーザ</label>
<select style="flex: 1; border: 2px solid var(--border-color); padding: 8px 12px; font-size: 13px; border-radius: 6px;">
<option value="">選択してください</option>
<option>㈱安川電機</option>
<option>㈱ノリタケカンパニーリミテド</option>
</select>
</div>
<div class="search-form-field">
<label>取引先</label>
<select style="flex: 1; border: 2px solid var(--border-color); padding: 8px 12px; font-size: 13px; border-radius: 6px;">
<option value="">選択してください</option>
<option>㈱日伝 北九州</option>
<option>㈱ノリタケカンパニーリミテド</option>
</select>
</div>
</div>
<div class="search-form-row">
<div class="search-form-field">
<label>送付先</label>
<select style="flex: 1; border: 2px solid var(--border-color); padding: 8px 12px; font-size: 13px; border-radius: 6px;">
<option value="">選択してください</option>
<option>㈱日伝 北九州</option>
<option>㈱ノリタケカンパニーリミテド</option>
</select>
</div>
<div class="search-form-field">
<label>希望納期</label>
<div class="date-range">
<input style="width: 160px" type="date" value=""/>
<span>～</span>
<input style="width: 160px" type="date" value=""/>
</div>
</div>
</div>
<div class="search-form-row">
<div class="search-form-field">
<label>回答納期</label>
<div class="date-range">
<input style="width: 160px" type="date" value=""/>
<span>～</span>
<input style="width: 160px" type="date" value=""/>
</div>
</div>
<div class="search-form-field">
<label>送付先種類</label>
<select style="flex: 1; border: 2px solid var(--border-color); padding: 8px 12px; font-size: 13px; border-radius: 6px;">
<option value="">選択してください</option>
<option>本社</option>
<option>直送</option>
</select>
</div>
</div>
<div class="search-form-row">
<div class="search-form-field">
<label>ステータス</label>
<select style="flex: 1; border: 2px solid var(--border-color); padding: 8px 12px; font-size: 13px; border-radius: 6px;">
<option value="">全て</option>
<option>未回答</option>
<option>回答済</option>
</select>
</div>
</div>
</div>
<!-- 納期回答グリッド -->
<div class="table-container">
<table class="data-table">
<thead>
<tr>
<th rowspan="2" style="width: 60px;">発注書<br>照会</th>
<th rowspan="2" style="width: 60px;">納期<br>回答</th>
<th colspan="9" style="border-bottom: 2px solid rgba(255,255,255,0.3);">発注情報</th>
<th rowspan="2">担当者</th>
<th rowspan="2">備考</th>
<th colspan="4" style="border-bottom: 2px solid rgba(255,255,255,0.3);">納期</th>
<th colspan="1" style="border-bottom: 2px solid rgba(255,255,255,0.3);">その他</th>
<th rowspan="2">エンドユーザ</th>
<th rowspan="2">取引先</th>
<th rowspan="2">送付先<br>(直送先)</th>
</tr>
<tr>
<th>ステータス</th>
<th>注文No</th>
<th>連番</th>
<th>受注日</th>
<th>内容・サイズ</th>
<th>本数</th>
<th>ロットNo</th>
<th>単価</th>
<th>価格</th>
<th>希望納期</th>
<th>回答納期</th>
<th>発送日</th>
<th>検収日</th>
<th>送付先種類</th>
</tr>
</thead>
<tbody>
"""

# Sample data from task YAML
rows = [
    {"status": "回答済", "order_no": "T12345-S1-1234", "seq": 1, "order_date": "2019/08/02",
     "content": "0.20t×13t×619.6L<br>材質：SUS304-H", "qty": 10, "lot_no": "",
     "unit_price": "7,500", "price": "75,000", "person": "木下", "note": "",
     "delivery_desired": "2019/08/02", "delivery_answer": "", "ship_date": "", "inspect_date": "",
     "delivery_type": "本社", "end_user": "㈱安川電機", "customer": "㈱日伝 北九州", "ship_to": "㈱日伝 北九州"},
    {"status": "回答済", "order_no": "T12345-S1-1234", "seq": 2, "order_date": "2019/08/02",
     "content": "0.10t×7.5t×450.3L<br>材質：SUS304-H", "qty": 6, "lot_no": "",
     "unit_price": "7,500", "price": "45,000", "person": "木下", "note": "",
     "delivery_desired": "2019/08/02", "delivery_answer": "", "ship_date": "", "inspect_date": "",
     "delivery_type": "本社", "end_user": "㈱安川電機", "customer": "㈱日伝 北九州", "ship_to": "㈱日伝 北九州"},
    {"status": "未回答", "order_no": "T12345-S1-1234", "seq": 3, "order_date": "2019/08/02",
     "content": "0.10t×7.5t×275.4L<br>材質：SUS304-H", "qty": 6, "lot_no": "",
     "unit_price": "7,500", "price": "45,000", "person": "木下", "note": "",
     "delivery_desired": "2019/08/02", "delivery_answer": "", "ship_date": "", "inspect_date": "",
     "delivery_type": "本社", "end_user": "㈱安川電機", "customer": "㈱日伝 北九州", "ship_to": "㈱日伝 北九州"},
    {"status": "未回答", "order_no": "T99999-S1-9999", "seq": 1, "order_date": "2019/04/24",
     "content": "0.70t×60t×4320L<br>材質：SUS304-H", "qty": 30, "lot_no": "",
     "unit_price": "3,000", "price": "90,000", "person": "木下", "note": "",
     "delivery_desired": "2019/05/27", "delivery_answer": "", "ship_date": "", "inspect_date": "",
     "delivery_type": "直送", "end_user": "㈱ノリタケカンパニーリミテド", "customer": "㈱ノリタケカンパニーリミテド", "ship_to": "㈱ノリタケカンパニーリミテド"},
    {"status": "未回答", "order_no": "T99999-S1-9999", "seq": 2, "order_date": "2019/04/24",
     "content": "端面加工", "qty": 30, "lot_no": "T19-2R",
     "unit_price": "800", "price": "24,000", "person": "木下", "note": "",
     "delivery_desired": "2019/05/27", "delivery_answer": "", "ship_date": "", "inspect_date": "",
     "delivery_type": "直送", "end_user": "㈱ノリタケカンパニーリミテド", "customer": "㈱ノリタケカンパニーリミテド", "ship_to": "㈱ノリタケカンパニーリミテド"},
    {"status": "未回答", "order_no": "T99999-S1-9999", "seq": 3, "order_date": "2019/04/24",
     "content": "梱包・送料一式", "qty": 1, "lot_no": "",
     "unit_price": "10,930", "price": "10,930", "person": "木下", "note": "",
     "delivery_desired": "2019/05/27", "delivery_answer": "", "ship_date": "", "inspect_date": "",
     "delivery_type": "直送", "end_user": "㈱ノリタケカンパニーリミテド", "customer": "㈱ノリタケカンパニーリミテド", "ship_to": "㈱ノリタケカンパニーリミテド"},
]

for row in rows:
    status_class = "status-answered" if row["status"] == "回答済" else "status-pending"
    content += f"""<tr>
<td><button class="action-btn">照会</button></td>
<td><button class="action-btn">回答</button></td>
<td><span class="status-badge {status_class}">{row["status"]}</span></td>
<td>{row["order_no"]}</td>
<td style="text-align: center;">{row["seq"]}</td>
<td>{row["order_date"]}</td>
<td style="text-align: left; white-space: normal; min-width: 200px;">{row["content"]}</td>
<td style="text-align: right;">{row["qty"]}</td>
<td>{row["lot_no"]}</td>
<td style="text-align: right;">{row["unit_price"]}</td>
<td style="text-align: right;">{row["price"]}</td>
<td>{row["person"]}</td>
<td>{row["note"]}</td>
<td>{row["delivery_desired"]}</td>
<td>{row["delivery_answer"]}</td>
<td>{row["ship_date"]}</td>
<td>{row["inspect_date"]}</td>
<td>{row["delivery_type"]}</td>
<td style="text-align: left;">{row["end_user"]}</td>
<td style="text-align: left;">{row["customer"]}</td>
<td style="text-align: left;">{row["ship_to"]}</td>
</tr>
"""

content += """</tbody>
</table>
</div>
</div>
<script>
        // クリアボタン
        document.getElementById('btnClear').addEventListener('click', function() {
            if (confirm('画面をクリアしますか？')) {
                document.querySelectorAll('.search-form input[type="text"], .search-form input[type="date"]').forEach(function(input) {
                    input.value = '';
                });
                document.querySelectorAll('.search-form select').forEach(function(select) {
                    select.selectedIndex = 0;
                });
            }
        });

        // グリッド行クリック
        document.querySelectorAll('.data-table tbody tr').forEach(function(row) {
            row.style.cursor = 'pointer';
        });
    </script>
</div>
"""

# Combine
output = head_part + "\n" + content + "\n" + tail_part

# Fix the title in header
output = output.replace("<title>天龍納期回答一覧</title>", "<title>天龍納期回答一覧</title>")

# Write the output
with open(TARGET, "w", encoding="utf-8") as f:
    f.write(output)

# Count lines
line_count = output.count("\n") + 1
print(f"SUCCESS: Wrote {line_count} lines to {TARGET}")
