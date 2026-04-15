#!/usr/bin/env python3
"""Generate the new tbody for 053_海外取引一覧.html with 2-level expandable detail rows."""

# Data for 15 rows
rows = [
    # (type, no, cd, name, date, po, ref, shipto, amount, sales, packing, link,
    #  sold1, sold2, sold3, addr1, addr2, addr3, country_jp, tel, fax,
    #  inv_no, terms, payment, meisai_no, desc, qty, uprice, amt2)
    ("PROFORMA", "39-O1-0001", "A00000", "International Tobacco Machinery Poland", "2025/01/01", "PO-2025-001", "REF-001", "XXXX株式会社", "999,999", "はまこむ　たろう", True, "053_海外入力_プロフォーマ.html",
     "International Tobacco Machinery Poland Sp. z o.o.", "", "", "Radom", "ul. Andreja Stanikowskiego 2", "26-600 Poland", "ポーランド", "+48 48 364-8800", "+48 48 364-8801",
     "39-O1-00001-0001-1", "F.O.B.YOKOHAMA", "T/T 30 days", "1", "Stainless Steel Belt DW1773-25-50-1850 15-7PH 0.25t×50w×1850L", "12 PCS", "US$", "999,999 US$"),
    ("COMMERCIAL", "39-O1-0002", "A00001", "SEIKO MANUFACTURING (Singapore)", "2025/01/02", "PO-2025-002", "REF-002", "XXXX株式会社", "1,250,000", "はまこむ　たろう", False, "053_海外入力_コマーシャル.html",
     "SEIKO MANUFACTURING (Singapore) Pte. Ltd.", "Movement Manufacturing Division", "", "10 Tuas South Street 5", "Singapore 637082", "", "Singapore", "+65-6861-1234", "+65-6861-5678",
     "39-O1-00002-0001-1", "C&amp;F SINGAPORE", "T/T 60 days", "1", "Precision Spring Assembly PS-2200 SUS304 0.3t×30w×500L", "50 PCS", "25,000 US$", "1,250,000 US$"),
    ("COMMERCIAL", "39-O1-0003", "A00002", "ABC Manufacturing Co., Ltd.", "2025/01/03", "PO-2025-003", "REF-003", "XXXX株式会社", "780,000", "はまこむ　たろう", True, "053_海外入力_コマーシャル.html",
     "ABC Manufacturing Co., Ltd.", "Quality Control Dept.", "", "123 Sukhumvit Road", "Bangkok 10110", "Thailand", "タイ", "+66-2-123-4567", "+66-2-123-4568",
     "39-O1-00003-0001-1", "FOB YOKOHAMA", "L/C at sight", "1", "Conveyor Belt CB-500 SUS316 0.5t×100w×3000L", "5 PCS", "156,000 US$", "780,000 US$"),
    ("COMMERCIAL", "39-O1-0004", "A00003", "DEF Industrial Corp.", "2025/01/04", "PO-2025-004", "REF-004", "XXXX株式会社", "2,100,000", "はまこむ　たろう", False, "053_海外入力_コマーシャル.html",
     "DEF Industrial Corp.", "", "", "No. 88 Zhongshan Rd", "Taipei 10451", "Taiwan", "台湾", "+886-2-2345-6789", "+886-2-2345-6780",
     "39-O1-00004-0001-1", "CIF KEELUNG", "T/T 45 days", "1", "Heat Resistant Belt HR-900 Inconel625 0.15t×40w×2000L", "20 PCS", "105,000 US$", "2,100,000 US$"),
    ("COMMERCIAL", "39-O1-0005", "A00004", "GHI Technologies Inc.", "2025/01/05", "PO-2025-005", "REF-005", "XXXX株式会社", "560,000", "はまこむ　たろう", False, "053_海外入力_コマーシャル.html",
     "GHI Technologies Inc.", "R&amp;D Center", "", "1234 Innovation Drive", "San Jose, CA 95134", "USA", "アメリカ", "+1-408-555-0100", "+1-408-555-0101",
     "39-O1-00005-0001-1", "FOB YOKOHAMA", "T/T 30 days", "1", "Etching Mesh EM-100 SUS304 0.08t×200w×1000L", "100 PCS", "5,600 US$", "560,000 US$"),
    ("PACKING LIST", "39-O1-0006", "A00000", "International Tobacco Machinery Poland", "2025/02/10", "PO-2025-006", "REF-006", "JKL Trading Co.", "1,250,000", "出河　太郎", True, "053_海外入力_パッキング.html",
     "International Tobacco Machinery Poland Sp. z o.o.", "Logistics Dept.", "", "Radom", "ul. Andreja Stanikowskiego 2", "26-600 Poland", "ポーランド", "+48 48 364-8800", "+48 48 364-8801",
     "39-O1-00006-0001-1", "FOB YOKOHAMA", "T/T 30 days", "1", "Stainless Steel Belt DW1773-25-50-1850 15-7PH 0.25t×50w×1850L", "15 PCS", "83,333 US$", "1,250,000 US$"),
    ("PROFORMA", "39-O1-0007", "A00005", "MNO Precision Engineering Pte Ltd", "2025/02/15", "PO-2025-007", "REF-007", "PQR Industries Ltd.", "2,450,000", "佐藤　花子", False, "053_海外入力_プロフォーマ.html",
     "MNO Precision Engineering Pte Ltd", "", "", "25 Jurong West St 42", "Singapore 649064", "", "シンガポール", "+65-6500-1234", "+65-6500-1235",
     "39-O1-00007-0001-1", "CIF SINGAPORE", "T/T 60 days", "1", "Ultra-thin Belt UT-300 SUS301 0.02t×25w×1500L", "200 PCS", "12,250 US$", "2,450,000 US$"),
    ("COMMERCIAL", "39-O1-0008", "A00002", "ABC Manufacturing Co., Ltd.", "2025/03/01", "PO-2025-008", "REF-008", "STU Corporation", "780,000", "はまこむ　たろう", True, "053_海外入力_コマーシャル.html",
     "ABC Manufacturing Co., Ltd.", "", "", "456 Rama IV Road", "Bangkok 10500", "Thailand", "タイ", "+66-2-987-6543", "+66-2-987-6544",
     "39-O1-00008-0001-1", "FOB YOKOHAMA", "L/C at sight", "1", "Filter Mesh FM-800 SUS316L 0.1t×150w×2000L", "30 PCS", "26,000 US$", "780,000 US$"),
    ("PROFORMA", "39-O1-0009", "A00006", "VWX Automotive Parts GmbH", "2025/03/20", "PO-2025-009", "REF-009", "YZA Technik AG", "3,100,000", "出河　太郎", False, "053_海外入力_プロフォーマ.html",
     "VWX Automotive Parts GmbH", "Einkauf Abteilung", "", "Industriestr. 55", "70565 Stuttgart", "Germany", "ドイツ", "+49-711-123-4567", "+49-711-123-4568",
     "39-O1-00009-0001-1", "CIF HAMBURG", "T/T 90 days", "1", "Precision Shim PS-400 SUS631 0.05t×20w×500L", "500 PCS", "6,200 US$", "3,100,000 US$"),
    ("COMMERCIAL", "39-O1-0010", "A00001", "SEIKO MANUFACTURING (Singapore)", "2025/04/05", "PO-2025-010", "REF-010", "BCD Electronics Co.", "560,000", "佐藤　花子", False, "053_海外入力_コマーシャル.html",
     "SEIKO MANUFACTURING (Singapore) Pte. Ltd.", "", "", "10 Tuas South Street 5", "Singapore 637082", "", "シンガポール", "+65-6861-1234", "+65-6861-5678",
     "39-O1-00010-0001-1", "C&amp;F SINGAPORE", "T/T 60 days", "1", "Spring Steel Strip SS-150 SK5 0.3t×30w×1000L", "80 PCS", "7,000 US$", "560,000 US$"),
    ("PACKING LIST", "39-O1-0011", "A00003", "DEF Industrial Corp.", "2025/04/18", "PO-2025-011", "REF-011", "EFG Systems Inc.", "1,890,000", "はまこむ　たろう", True, "053_海外入力_パッキング.html",
     "DEF Industrial Corp.", "Warehouse Dept.", "", "No. 88 Zhongshan Rd", "Taipei 10451", "Taiwan", "台湾", "+886-2-2345-6789", "+886-2-2345-6780",
     "39-O1-00011-0001-1", "CIF KEELUNG", "T/T 45 days", "1", "Conveyor Belt CB-700 SUS316 0.8t×120w×5000L", "3 PCS", "630,000 US$", "1,890,000 US$"),
    ("COMMERCIAL", "39-O1-0012", "A00007", "HIJ Metal Works S.A.", "2025/05/02", "PO-2025-012", "REF-012", "KLM Logistics S.r.l.", "4,200,000", "出河　太郎", False, "053_海外入力_コマーシャル.html",
     "HIJ Metal Works S.A.", "", "", "Av. Corrientes 1234", "Buenos Aires C1043", "Argentina", "アルゼンチン", "+54-11-4567-8901", "+54-11-4567-8902",
     "39-O1-00012-0001-1", "FOB YOKOHAMA", "T/T 30 days", "1", "Wide Belt WB-2000 SUS304 0.5t×500w×10000L", "2 PCS", "2,100,000 US$", "4,200,000 US$"),
    ("PROFORMA", "39-O1-0013", "A00004", "GHI Technologies Inc.", "2025/05/15", "PO-2025-013", "REF-013", "NOP Semiconductor Ltd.", "920,000", "佐藤　花子", True, "053_海外入力_プロフォーマ.html",
     "GHI Technologies Inc.", "Advanced Materials Lab", "", "5678 Tech Parkway", "Austin, TX 78759", "USA", "アメリカ", "+1-512-555-0200", "+1-512-555-0201",
     "39-O1-00013-0001-1", "CIF LOS ANGELES", "T/T 30 days", "1", "Etching Mesh EM-200 SUS316 0.05t×300w×1500L", "40 PCS", "23,000 US$", "920,000 US$"),
    ("COMMERCIAL", "39-O1-0014", "A00005", "MNO Precision Engineering Pte Ltd", "2025/06/01", "PO-2025-014", "REF-014", "QRS Chemical Corp.", "1,550,000", "はまこむ　たろう", False, "053_海外入力_コマーシャル.html",
     "MNO Precision Engineering Pte Ltd", "Production Dept.", "", "25 Jurong West St 42", "Singapore 649064", "", "シンガポール", "+65-6500-1234", "+65-6500-1235",
     "39-O1-00014-0001-1", "CIF SINGAPORE", "T/T 60 days", "1", "Precision Spring Wire PW-100 SUS302 0.2mm×500m", "300 COIL", "5,167 US$", "1,550,000 US$"),
    ("PACKING LIST", "39-O1-0015", "A00006", "VWX Automotive Parts GmbH", "2025/06/20", "PO-2025-015", "REF-015", "TUV Motors GmbH", "5,300,000", "出河　太郎", True, "053_海外入力_パッキング.html",
     "VWX Automotive Parts GmbH", "Versand Abteilung", "", "Industriestr. 55", "70565 Stuttgart", "Germany", "ドイツ", "+49-711-123-4567", "+49-711-123-4568",
     "39-O1-00015-0001-1", "CIF HAMBURG", "T/T 90 days", "1", "Automotive Shim Set AS-500 SUS631 0.03-0.1t×Various", "1000 SET", "5,300 US$", "5,300,000 US$"),
]

lines = []
lines.append('                <tbody>')

for i, r in enumerate(rows):
    (typ, no, cd, name, date, po, ref, shipto, amount, sales, packing, link,
     sold1, sold2, sold3, addr1, addr2, addr3, country, tel, fax,
     inv_no, terms, payment, mno, desc, qty, uprice, amt2) = r

    num = i + 1
    packing_html = '<span class="packing-badge">○</span>' if packing else ''

    lines.append(f'                    <!-- Row {num} -->')
    # Parent row: 2 expand buttons + data
    lines.append(
        f'                    <tr class="parent-row">'
        f'<td><button class="expand-btn" onclick="toggleDetail1(this)">▷</button></td>'
        f'<td><button class="expand-btn" onclick="toggleDetail2(this)">▷</button></td>'
        f'<td><div class="action-cell"><button class="action-btn" onclick="location.href=\'{link}?no={no}\'">編集</button><button class="action-btn ref">参照</button></div></td>'
        f'<td>{typ}</td><td>{no}</td><td>{cd}</td><td class="text-left">{name}</td>'
        f'<td>{date}</td><td>{po}</td><td>{ref}</td><td class="text-left">{shipto}</td>'
        f'<td class="text-right">{amount}</td><td>{sales}</td><td>{packing_html}</td></tr>'
    )

    # Detail Level 1: SOLD TO (detail-target-1)
    lines.append(
        f'                    <tr class="detail-header detail-target-1">'
        f'<td colspan="3" class="detail-empty"></td>'
        f'<td>SOLD TO1</td><td colspan="2">SOLD TO2</td><td>SOLD TO3</td>'
        f'<td colspan="2">ADDRESS1</td><td>ADDRESS2</td><td>ADDRESS3</td>'
        f'<td>COUNTRY</td><td>TEL</td><td>FAX</td></tr>'
    )
    lines.append(
        f'                    <tr class="detail-row detail-target-1">'
        f'<td colspan="3" class="detail-empty"></td>'
        f'<td class="text-left">{sold1}</td><td colspan="2" class="text-left">{sold2}</td><td class="text-left">{sold3}</td>'
        f'<td colspan="2" class="text-left">{addr1}</td><td class="text-left">{addr2}</td><td class="text-left">{addr3}</td>'
        f'<td>{country}</td><td>{tel}</td><td>{fax}</td></tr>'
    )

    # Detail Level 2: INVOICE / 明細 (detail-target-2)
    lines.append(
        f'                    <tr class="detail-header detail-target-2">'
        f'<td colspan="3" class="detail-empty"></td>'
        f'<td>INVOICE NO</td><td colspan="2">TERMS</td><td colspan="2">TERMS OF PAYMENT</td>'
        f'<td>NO</td><td colspan="2">DESCRIPTION</td>'
        f'<td>QUANTITY</td><td>UNIT PRICE</td><td>AMOUNT</td></tr>'
    )
    lines.append(
        f'                    <tr class="detail-row detail-target-2">'
        f'<td colspan="3" class="detail-empty"></td>'
        f'<td>{inv_no}</td><td colspan="2">{terms}</td><td colspan="2">{payment}</td>'
        f'<td>{mno}</td><td colspan="2" class="text-left">{desc}</td>'
        f'<td class="text-right">{qty}</td><td class="text-right">{uprice}</td><td class="text-right">{amt2}</td></tr>'
    )
    lines.append('')

lines.append('                </tbody>')

print('\n'.join(lines))
