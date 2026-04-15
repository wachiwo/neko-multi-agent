#!/usr/bin/env python3
"""
fix_167_001_html.py — Apply all review fixes (HTML portion) to 詳細入力フォーム.html
Fixes: H01(17 @bind), H02, M01, M02, M03, M04, M05, M10, L02, L05
"""
import re

path = "/mnt/g/共有ドライブ/[PJ]ディムコ/01_再構築プロジェクト/90_personal/degawa/007_部品一覧/詳細入力フォーム.html"

with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

original = c
changes = 0
warnings = []

def rep1(old, new, label=""):
    global c, changes
    if old not in c:
        warnings.append(f"NOT FOUND [{label}]: {repr(old[:80])}")
        return False
    c = c.replace(old, new, 1)
    changes += 1
    return True

def rep_all(old, new, label=""):
    global c, changes
    count = c.count(old)
    if count == 0:
        warnings.append(f"NOT FOUND [{label}]: {repr(old[:80])}")
        return 0
    c = c.replace(old, new)
    changes += count
    return count

# ============================================================
# L02: Move inline grid-template-columns:1fr to CSS class
# ============================================================
n = rep_all(
    'class="detail-form-grid" style="grid-template-columns: 1fr;"',
    'class="detail-form-grid detail-form-grid-single"',
    "L02"
)
print(f"L02: {n} inline styles -> .detail-form-grid-single")

# ============================================================
# L05: Remove redundant aria-label from checklist items
# ============================================================
for label_text in ['納品書', '請求書', '検査成績書', 'ミルシート', 'SDS']:
    rep1(f' aria-label="{label_text}"', '', f"L05-{label_text}")
print("L05: Removed 5 redundant aria-labels from checklist items")

# ============================================================
# H01: Add @bind annotations to 17 inputs
# ============================================================
for for_val, prop in [
    ('yuubin', 'Customer.PostalCode'),
    ('todofuken', 'Customer.Prefecture'),
    ('shikuchoson', 'Customer.City'),
    ('banchi', 'Customer.Address'),
    ('bldg', 'Customer.Building'),
    ('tel', 'Customer.Phone'),
    ('keitai', 'Customer.Mobile'),
    ('fax', 'Customer.Fax'),
    ('email', 'Customer.Email'),
    ('shiharai-houhou', 'TradeCondition.PaymentMethod'),
    ('shimebi', 'TradeCondition.ClosingDate'),
    ('shiharai-tsuki', 'TradeCondition.PaymentMonth'),
    ('shiharai-bi', 'TradeCondition.PaymentDay'),
    ('shiharai-kijitsu', 'TradeCondition.PaymentDueDate'),
]:
    rep1(f'<label for="{for_val}">',
         f'<!-- Blazor: @bind="Model.{prop}" -->\n<label for="{for_val}">',
         f"H01-{for_val}")

for chk_id, prop in [
    ('chk-shitei', 'TradeCondition.DesignatedSlip'),
    ('chk-seikyusho', 'TradeCondition.DymcoInvoice'),
    ('chk-shinki', 'TradeCondition.IsNew'),
]:
    rep1(f'<input class="form-check-input" type="checkbox" id="{chk_id}"',
         f'<!-- Blazor: @bind="Model.{prop}" -->\n<input class="form-check-input" type="checkbox" id="{chk_id}"',
         f"H01-{chk_id}")
print("H01: Added 17 @bind annotations")

# ============================================================
# M02: Move Blazor comments to ABOVE elements, split combined
# ============================================================
rep1(
    '<button class="btn btn-primary btn-sm ms-1" onclick="handleCopyLink()">\n<!-- Blazor: @onclick="HandleCopyLink" -->\n<i class="bi bi-link-45deg"></i> 見積紐付\n</button>',
    '<!-- Blazor: @onclick="HandleCopyLink" -->\n<button class="btn btn-primary btn-sm ms-1" onclick="handleCopyLink()">\n<i class="bi bi-link-45deg"></i> 見積紐付\n</button>',
    "M02-copylink")

rep1(
    '<!-- Blazor: @onclick="HandleSave" / HandleDelete / HandleExport / HandleClose -->\n<div class="detail-action-buttons">\n<button class="btn btn-primary" onclick="handleSave()">',
    '<div class="detail-action-buttons">\n<!-- Blazor: @onclick="HandleSave" -->\n<button class="btn btn-primary" onclick="handleSave()">',
    "M02-save")
rep1('<button class="btn btn-outline-danger" onclick="handleDelete()">',
     '<!-- Blazor: @onclick="HandleDelete" -->\n<button class="btn btn-outline-danger" onclick="handleDelete()">',
     "M02-delete")
rep1('<button class="btn btn-outline-secondary" onclick="handleExport()">',
     '<!-- Blazor: @onclick="HandleExport" -->\n<button class="btn btn-outline-secondary" onclick="handleExport()">',
     "M02-export")
rep1('<button class="btn btn-outline-secondary" onclick="handleClose()">',
     '<!-- Blazor: @onclick="HandleClose" -->\n<button class="btn btn-outline-secondary" onclick="handleClose()">',
     "M02-close")
print("M02: Moved/split Blazor comments")

# ============================================================
# M03: Arrow key navigation annotation
# ============================================================
rep1('<div class="detail-tab-list" role="tablist"',
     '<!-- Blazor: @onkeydown for ArrowLeft/Right/Home/End navigation -->\n<div class="detail-tab-list" role="tablist"',
     "M03")
print("M03: Arrow key nav annotation added")

# ============================================================
# H02: Panel-2 annotation
# ============================================================
rep1('<div class="detail-tab-panel" id="panel-2"',
     '<!-- Blazor: Panel2は実装時ActiveDetailテンプレート共用。Panel1のアノテーション参照 -->\n<div class="detail-tab-panel" id="panel-2"',
     "H02")
print("H02: Panel-2 annotation added")

# ============================================================
# M04: Add tabindex="-1" to readonly inputs
# ============================================================
n = rep_all(' readonly value=', ' readonly tabindex="-1" value=', "M04")
print(f"M04: tabindex=-1 added to {n} readonly inputs")

# ============================================================
# M05: Add row numbers to detail table cell aria-labels
# ============================================================
rep1('<!-- Blazor: @foreach (var line in ActiveDetail.LineItems) { -->\n<tbody>',
     '<!-- Blazor: @foreach (var line in ActiveDetail.LineItems) { -->\n'
     '<!-- Blazor: aria-label属性は行番号付き例: aria-label="@($"行{line.LineNumber}: 商品名称")" -->\n<tbody>',
     "M05-annotation")

def add_row_numbers_to_tbody(match):
    tbody = match.group(0)
    parts = re.split(r'(<tr>)', tbody)
    result = ''
    row_num = 0
    for part in parts:
        if part == '<tr>':
            row_num += 1
            result += part
        elif row_num > 0:
            def replace_label(m):
                label = m.group(1)
                if '明細行' in label:
                    return m.group(0)
                return f'aria-label="行{row_num}: {label}"'
            part = re.sub(r'aria-label="([^"]+)"', replace_label, part)
            result += part
        else:
            result += part
    return result

c = re.sub(r'<tbody>.*?</tbody>', add_row_numbers_to_tbody, c, flags=re.DOTALL)
print("M05: Row numbers added to aria-labels in detail tables")

# ============================================================
# M01: Dynamic ARIA annotations for delete buttons
# (AFTER M05 to avoid regex conflict with comment content)
# ============================================================
for onclick_args in ['(1, 1)', '(1, 2)', '(2, 1)']:
    rep1(
        f'<button class="btn btn-outline-danger btn-sm" onclick="handleDeleteLine{onclick_args}"',
        f'<!-- Blazor: aria-label="@($"明細行{{line.LineNumber}}を削除")" -->\n<button class="btn btn-outline-danger btn-sm" onclick="handleDeleteLine{onclick_args}"',
        f"M01-{onclick_args}")
print("M01: 3 dynamic ARIA annotations added")

# ============================================================
# M10: Change div wrappers to <section>
# ============================================================
n = rep_all('<div class="card mb-3">', '<section class="card mb-3">', "M10-open")
print(f"M10: {n} opening <div> -> <section>")

rep1('\n</div>\n\n<!-- ===== 取引条件セクション',
     '\n</section>\n\n<!-- ===== 取引条件セクション', "M10-close-tokuisaki")
rep1('\n</div>\n\n<!-- ===== 受注備考等セクション',
     '\n</section>\n\n<!-- ===== 受注備考等セクション', "M10-close-torihiki")
rep1('\n</div>\n\n<!-- ===== 明細タブセクション',
     '\n</section>\n\n<!-- ===== 明細タブセクション', "M10-close-bikou")
rep1('\n</div>\n\n</main>',
     '\n</section>\n\n</main>', "M10-close-meisai")
print("M10: 4 closing </div> -> </section>")

# ============================================================
# Verification
# ============================================================
checks = [
    ('@bind="Model.Customer.PostalCode"', "H01"),
    ('@bind="Model.TradeCondition.PaymentMethod"', "H01"),
    ('@bind="Model.TradeCondition.IsNew"', "H01-checkbox"),
    ('Panel2は実装時ActiveDetail', "H02"),
    ('明細行{line.LineNumber}を削除', "M01"),
    ('@onclick="HandleSave" -->', "M02-split"),
    ('@onclick="HandleClose" -->', "M02-split"),
    ('ArrowLeft/Right/Home/End', "M03"),
    ('tabindex="-1"', "M04"),
    ('aria-label="行1: 商品名称"', "M05-row1"),
    ('aria-label="行2: 商品名称"', "M05-row2"),
    ('detail-form-grid-single"', "L02"),
    ('<section class="card mb-3">', "M10-open"),
    ('</section>\n\n<!-- ===== 取引条件', "M10-close"),
    ('</section>\n\n</main>', "M10-close-last"),
]

pass_count = 0
for pattern, label in checks:
    if pattern in c:
        pass_count += 1
    else:
        print(f"  VERIFY FAIL: {label} — '{pattern[:50]}' not found")

# Count section balance
section_opens = c.count('<section ')
section_closes = c.count('</section>')

print(f"\n=== Results ===")
print(f"Changes applied: {changes}")
print(f"Verification: {pass_count}/{len(checks)} passed")
print(f"Section balance: {section_opens} open, {section_closes} close {'OK' if section_opens == section_closes else 'MISMATCH!'}")
if warnings:
    print(f"Warnings ({len(warnings)}):")
    for w in warnings:
        print(f"  {w}")

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

print(f"File written ({len(c)} chars)")
