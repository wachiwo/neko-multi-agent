#!/usr/bin/env python3
"""Generate tbody v8: multiple SOLD TO rows per parent, with SOLD TO2/3 data."""

rows = [
    # (type, no, cd, name, date, po, ref, shipto, amount, sales, packing, link,
    #  sold_to_list: [(sold1, sold2, sold3, addr1, addr2, addr3, country, tel, fax)],
    #  meisai_list: [(inv_no, terms, payment, mno, desc, qty, uprice, amt2)])
    {
        "parent": ("PROFORMA", "39-O1-0001", "A00000", "International Tobacco Machinery Poland", "2025/01/01", "PO-2025-001", "REF-001", "XXXX株式会社", "999,999", "はまこむ　たろう", True, "053_海外入力_プロフォーマ.html"),
        "sold_to": [
            ("International Tobacco Machinery Poland Sp. z o.o.", "Radom Branch Office", "", "Radom", "ul. Andreja Stanikowskiego 2", "26-600 Poland", "ポーランド", "+48 48 364-8800", "+48 48 364-8801"),
            ("International Tobacco Machinery Poland Sp. z o.o.", "Warsaw Head Office", "Procurement Div.", "Warsaw", "ul. Marszalkowska 100", "00-001 Poland", "ポーランド", "+48 22 111-2222", "+48 22 111-2223"),
        ],
        "meisai": [
            ("39-O1-00001-0001-1", "F.O.B.YOKOHAMA", "T/T 30 days", "1", "Stainless Steel Belt DW1773-25-50-1850 15-7PH 0.25t×50w×1850L", "12 PCS", "US$", "999,999 US$"),
        ],
    },
    {
        "parent": ("COMMERCIAL", "39-O1-0002", "A00001", "SEIKO MANUFACTURING (Singapore)", "2025/01/02", "PO-2025-002", "REF-002", "XXXX株式会社", "1,250,000", "はまこむ　たろう", False, "053_海外入力_コマーシャル.html"),
        "sold_to": [
            ("SEIKO MANUFACTURING (Singapore) Pte. Ltd.", "Movement Manufacturing Division", "", "10 Tuas South Street 5", "Singapore 637082", "", "Singapore", "+65-6861-1234", "+65-6861-5678"),
        ],
        "meisai": [
            ("39-O1-00002-0001-1", "C&amp;F SINGAPORE", "T/T 60 days", "1", "Precision Spring Assembly PS-2200 SUS304 0.3t×30w×500L", "50 PCS", "25,000 US$", "1,250,000 US$"),
        ],
    },
    {
        "parent": ("COMMERCIAL", "39-O1-0003", "A00002", "ABC Manufacturing Co., Ltd.", "2025/01/03", "PO-2025-003", "REF-003", "XXXX株式会社", "780,000", "はまこむ　たろう", True, "053_海外入力_コマーシャル.html"),
        "sold_to": [
            ("ABC Manufacturing Co., Ltd.", "Quality Control Dept.", "", "123 Sukhumvit Road", "Bangkok 10110", "Thailand", "タイ", "+66-2-123-4567", "+66-2-123-4568"),
            ("ABC Manufacturing Co., Ltd.", "", "", "456 Rama IV Road", "Bangkok 10500", "Thailand", "タイ", "+66-2-987-6543", "+66-2-987-6544"),
            ("ABC Trading (HK) Ltd.", "Import Division", "", "Unit 1205, Tower A", "Kowloon Bay, Hong Kong", "", "香港", "+852-2345-6789", "+852-2345-6780"),
        ],
        "meisai": [
            ("39-O1-00003-0001-1", "FOB YOKOHAMA", "L/C at sight", "1", "Conveyor Belt CB-500 SUS316 0.5t×100w×3000L", "5 PCS", "156,000 US$", "780,000 US$"),
        ],
    },
    {
        "parent": ("COMMERCIAL", "39-O1-0004", "A00003", "DEF Industrial Corp.", "2025/01/04", "PO-2025-004", "REF-004", "XXXX株式会社", "2,100,000", "はまこむ　たろう", False, "053_海外入力_コマーシャル.html"),
        "sold_to": [
            ("DEF Industrial Corp.", "Engineering Dept.", "", "No. 88 Zhongshan Rd", "Taipei 10451", "Taiwan", "台湾", "+886-2-2345-6789", "+886-2-2345-6780"),
        ],
        "meisai": [
            ("39-O1-00004-0001-1", "CIF KEELUNG", "T/T 45 days", "1", "Heat Resistant Belt HR-900 Inconel625 0.15t×40w×2000L", "20 PCS", "105,000 US$", "2,100,000 US$"),
        ],
    },
    {
        "parent": ("COMMERCIAL", "39-O1-0005", "A00004", "GHI Technologies Inc.", "2025/01/05", "PO-2025-005", "REF-005", "XXXX株式会社", "560,000", "はまこむ　たろう", False, "053_海外入力_コマーシャル.html"),
        "sold_to": [
            ("GHI Technologies Inc.", "R&amp;D Center", "", "1234 Innovation Drive", "San Jose, CA 95134", "USA", "アメリカ", "+1-408-555-0100", "+1-408-555-0101"),
            ("GHI Technologies Inc.", "Manufacturing Plant", "", "5678 Factory Road", "Austin, TX 78759", "USA", "アメリカ", "+1-512-555-0200", "+1-512-555-0201"),
        ],
        "meisai": [
            ("39-O1-00005-0001-1", "FOB YOKOHAMA", "T/T 30 days", "1", "Etching Mesh EM-100 SUS304 0.08t×200w×1000L", "100 PCS", "5,600 US$", "560,000 US$"),
        ],
    },
    {
        "parent": ("PACKING LIST", "39-O1-0006", "A00000", "International Tobacco Machinery Poland", "2025/02/10", "PO-2025-006", "REF-006", "JKL Trading Co.", "1,250,000", "出河　太郎", True, "053_海外入力_パッキング.html"),
        "sold_to": [
            ("International Tobacco Machinery Poland Sp. z o.o.", "Logistics Dept.", "", "Radom", "ul. Andreja Stanikowskiego 2", "26-600 Poland", "ポーランド", "+48 48 364-8800", "+48 48 364-8801"),
        ],
        "meisai": [
            ("39-O1-00006-0001-1", "FOB YOKOHAMA", "T/T 30 days", "1", "Stainless Steel Belt DW1773-25-50-1850 15-7PH 0.25t×50w×1850L", "15 PCS", "83,333 US$", "1,250,000 US$"),
        ],
    },
    {
        "parent": ("PROFORMA", "39-O1-0007", "A00005", "MNO Precision Engineering Pte Ltd", "2025/02/15", "PO-2025-007", "REF-007", "PQR Industries Ltd.", "2,450,000", "佐藤　花子", False, "053_海外入力_プロフォーマ.html"),
        "sold_to": [
            ("MNO Precision Engineering Pte Ltd", "", "", "25 Jurong West St 42", "Singapore 649064", "", "シンガポール", "+65-6500-1234", "+65-6500-1235"),
        ],
        "meisai": [
            ("39-O1-00007-0001-1", "CIF SINGAPORE", "T/T 60 days", "1", "Ultra-thin Belt UT-300 SUS301 0.02t×25w×1500L", "200 PCS", "12,250 US$", "2,450,000 US$"),
        ],
    },
    {
        "parent": ("COMMERCIAL", "39-O1-0008", "A00002", "ABC Manufacturing Co., Ltd.", "2025/03/01", "PO-2025-008", "REF-008", "STU Corporation", "780,000", "はまこむ　たろう", True, "053_海外入力_コマーシャル.html"),
        "sold_to": [
            ("ABC Manufacturing Co., Ltd.", "", "", "456 Rama IV Road", "Bangkok 10500", "Thailand", "タイ", "+66-2-987-6543", "+66-2-987-6544"),
        ],
        "meisai": [
            ("39-O1-00008-0001-1", "FOB YOKOHAMA", "L/C at sight", "1", "Filter Mesh FM-800 SUS316L 0.1t×150w×2000L", "30 PCS", "26,000 US$", "780,000 US$"),
        ],
    },
    {
        "parent": ("PROFORMA", "39-O1-0009", "A00006", "VWX Automotive Parts GmbH", "2025/03/20", "PO-2025-009", "REF-009", "YZA Technik AG", "3,100,000", "出河　太郎", False, "053_海外入力_プロフォーマ.html"),
        "sold_to": [
            ("VWX Automotive Parts GmbH", "Einkauf Abteilung", "", "Industriestr. 55", "70565 Stuttgart", "Germany", "ドイツ", "+49-711-123-4567", "+49-711-123-4568"),
            ("VWX Automotive Parts GmbH", "Werk München", "Qualitätssicherung", "Münchener Str. 200", "80331 München", "Germany", "ドイツ", "+49-89-456-7890", "+49-89-456-7891"),
        ],
        "meisai": [
            ("39-O1-00009-0001-1", "CIF HAMBURG", "T/T 90 days", "1", "Precision Shim PS-400 SUS631 0.05t×20w×500L", "500 PCS", "6,200 US$", "3,100,000 US$"),
        ],
    },
    {
        "parent": ("COMMERCIAL", "39-O1-0010", "A00001", "SEIKO MANUFACTURING (Singapore)", "2025/04/05", "PO-2025-010", "REF-010", "BCD Electronics Co.", "560,000", "佐藤　花子", False, "053_海外入力_コマーシャル.html"),
        "sold_to": [
            ("SEIKO MANUFACTURING (Singapore) Pte. Ltd.", "", "", "10 Tuas South Street 5", "Singapore 637082", "", "シンガポール", "+65-6861-1234", "+65-6861-5678"),
        ],
        "meisai": [
            ("39-O1-00010-0001-1", "C&amp;F SINGAPORE", "T/T 60 days", "1", "Spring Steel Strip SS-150 SK5 0.3t×30w×1000L", "80 PCS", "7,000 US$", "560,000 US$"),
        ],
    },
    {
        "parent": ("PACKING LIST", "39-O1-0011", "A00003", "DEF Industrial Corp.", "2025/04/18", "PO-2025-011", "REF-011", "EFG Systems Inc.", "1,890,000", "はまこむ　たろう", True, "053_海外入力_パッキング.html"),
        "sold_to": [
            ("DEF Industrial Corp.", "Warehouse Dept.", "", "No. 88 Zhongshan Rd", "Taipei 10451", "Taiwan", "台湾", "+886-2-2345-6789", "+886-2-2345-6780"),
            ("DEF Industrial Corp.", "Kaohsiung Factory", "Shipping Section", "No. 200 Chenggong Rd", "Kaohsiung 80661", "Taiwan", "台湾", "+886-7-333-4444", "+886-7-333-4445"),
        ],
        "meisai": [
            ("39-O1-00011-0001-1", "CIF KEELUNG", "T/T 45 days", "1", "Conveyor Belt CB-700 SUS316 0.8t×120w×5000L", "3 PCS", "630,000 US$", "1,890,000 US$"),
        ],
    },
    {
        "parent": ("COMMERCIAL", "39-O1-0012", "A00007", "HIJ Metal Works S.A.", "2025/05/02", "PO-2025-012", "REF-012", "KLM Logistics S.r.l.", "4,200,000", "出河　太郎", False, "053_海外入力_コマーシャル.html"),
        "sold_to": [
            ("HIJ Metal Works S.A.", "", "", "Av. Corrientes 1234", "Buenos Aires C1043", "Argentina", "アルゼンチン", "+54-11-4567-8901", "+54-11-4567-8902"),
        ],
        "meisai": [
            ("39-O1-00012-0001-1", "FOB YOKOHAMA", "T/T 30 days", "1", "Wide Belt WB-2000 SUS304 0.5t×500w×10000L", "2 PCS", "2,100,000 US$", "4,200,000 US$"),
        ],
    },
    {
        "parent": ("PROFORMA", "39-O1-0013", "A00004", "GHI Technologies Inc.", "2025/05/15", "PO-2025-013", "REF-013", "NOP Semiconductor Ltd.", "920,000", "佐藤　花子", True, "053_海外入力_プロフォーマ.html"),
        "sold_to": [
            ("GHI Technologies Inc.", "Advanced Materials Lab", "", "5678 Tech Parkway", "Austin, TX 78759", "USA", "アメリカ", "+1-512-555-0200", "+1-512-555-0201"),
        ],
        "meisai": [
            ("39-O1-00013-0001-1", "CIF LOS ANGELES", "T/T 30 days", "1", "Etching Mesh EM-200 SUS316 0.05t×300w×1500L", "40 PCS", "23,000 US$", "920,000 US$"),
        ],
    },
    {
        "parent": ("COMMERCIAL", "39-O1-0014", "A00005", "MNO Precision Engineering Pte Ltd", "2025/06/01", "PO-2025-014", "REF-014", "QRS Chemical Corp.", "1,550,000", "はまこむ　たろう", False, "053_海外入力_コマーシャル.html"),
        "sold_to": [
            ("MNO Precision Engineering Pte Ltd", "Production Dept.", "", "25 Jurong West St 42", "Singapore 649064", "", "シンガポール", "+65-6500-1234", "+65-6500-1235"),
            ("MNO Precision Engineering Pte Ltd", "R&amp;D Division", "", "30 Boon Lay Way", "Singapore 609964", "", "シンガポール", "+65-6600-7890", "+65-6600-7891"),
            ("MNO Trading (Malaysia) Sdn Bhd", "Penang Office", "", "Lot 88 Bayan Lepas FIZ", "11900 Penang", "Malaysia", "マレーシア", "+60-4-888-9999", "+60-4-888-9990"),
        ],
        "meisai": [
            ("39-O1-00014-0001-1", "CIF SINGAPORE", "T/T 60 days", "1", "Precision Spring Wire PW-100 SUS302 0.2mm×500m", "300 COIL", "5,167 US$", "1,550,000 US$"),
        ],
    },
    {
        "parent": ("PACKING LIST", "39-O1-0015", "A00006", "VWX Automotive Parts GmbH", "2025/06/20", "PO-2025-015", "REF-015", "TUV Motors GmbH", "5,300,000", "出河　太郎", True, "053_海外入力_パッキング.html"),
        "sold_to": [
            ("VWX Automotive Parts GmbH", "Versand Abteilung", "", "Industriestr. 55", "70565 Stuttgart", "Germany", "ドイツ", "+49-711-123-4567", "+49-711-123-4568"),
        ],
        "meisai": [
            ("39-O1-00015-0001-1", "CIF HAMBURG", "T/T 90 days", "1", "Automotive Shim Set AS-500 SUS631 0.03-0.1t×Various", "1000 SET", "5,300 US$", "5,300,000 US$"),
        ],
    },
]

I = '                    '

lines = []
lines.append(f'{I}<tbody>')

for i, row in enumerate(rows):
    p = row["parent"]
    (typ, no, cd, name, date, po, ref, shipto, amount, sales, packing, link) = p
    n = i + 1
    pk = '<span class="packing-badge">○</span>' if packing else ''

    lines.append(f'{I}<!-- Row {n} -->')
    lines.append(
        f'{I}<tr data-row-id="{n}">'
        f'<td class="expand-icon-cell" onclick="toggleSoldTo({n})"><span class="expand-icon" id="icon-sold-{n}">▷</span></td>'
        f'<td><div class="action-cell"><button class="action-btn" onclick="location.href=\'{link}?no={no}\'">編集</button><button class="action-btn ref">参照</button></div></td>'
        f'<td>{typ}</td><td>{no}</td><td>{cd}</td><td class="text-left">{name}</td>'
        f'<td>{date}</td><td>{po}</td><td>{ref}</td><td class="text-left">{shipto}</td>'
        f'<td class="text-right">{amount}</td><td>{sales}</td><td>{pk}</td></tr>'
    )

    # Child: colspan=13 → child table (SOLD TO)
    lines.append(f'{I}<tr><td colspan="13" style="padding:0;">')
    lines.append(f'{I}  <div class="child-table-container" id="child-sold-{n}">')
    lines.append(f'{I}    <table class="child-table">')
    lines.append(f'{I}      <thead><tr>'
        f'<th style="width:30px;"></th>'
        f'<th>SOLD TO1</th><th>SOLD TO2</th><th>SOLD TO3</th>'
        f'<th>ADDRESS1</th><th>ADDRESS2</th><th>ADDRESS3</th>'
        f'<th>COUNTRY</th><th>TEL</th><th>FAX</th>'
        f'</tr></thead>')
    lines.append(f'{I}      <tbody>')

    for j, st in enumerate(row["sold_to"]):
        (sold1, sold2, sold3, addr1, addr2, addr3, country, tel, fax) = st
        sid = j + 1
        lines.append(
            f'{I}        <tr data-sold-id="{n}-{sid}">'
            f'<td class="expand-icon-cell" onclick="toggleMeisai({n},{sid})"><span class="expand-icon" id="icon-meisai-{n}-{sid}">▷</span></td>'
            f'<td class="text-left">{sold1}</td><td class="text-left">{sold2}</td><td class="text-left">{sold3}</td>'
            f'<td class="text-left">{addr1}</td><td class="text-left">{addr2}</td><td class="text-left">{addr3}</td>'
            f'<td>{country}</td><td>{tel}</td><td>{fax}</td></tr>'
        )

        # Grandchild: INVOICE/明細
        lines.append(f'{I}        <tr><td colspan="10" style="padding:0;">')
        lines.append(f'{I}          <div class="grandchild-table-container" id="grandchild-meisai-{n}-{sid}">')
        lines.append(f'{I}            <table class="grandchild-table">')
        lines.append(f'{I}              <thead><tr>'
            f'<th>INVOICE NO</th><th>TERMS</th><th>TERMS OF PAYMENT</th>'
            f'<th>NO</th><th>DESCRIPTION</th>'
            f'<th>QUANTITY</th><th>UNIT PRICE</th><th>AMOUNT</th>'
            f'</tr></thead>')
        lines.append(f'{I}              <tbody>')
        for m in row["meisai"]:
            (inv_no, terms, payment, mno, desc, qty, uprice, amt2) = m
            lines.append(
                f'{I}                <tr>'
                f'<td>{inv_no}</td><td>{terms}</td><td>{payment}</td>'
                f'<td>{mno}</td><td class="text-left">{desc}</td>'
                f'<td class="text-right">{qty}</td><td class="text-right">{uprice}</td><td class="text-right">{amt2}</td></tr>'
            )
        lines.append(f'{I}              </tbody>')
        lines.append(f'{I}            </table>')
        lines.append(f'{I}          </div>')
        lines.append(f'{I}        </td></tr>')

    lines.append(f'{I}      </tbody>')
    lines.append(f'{I}    </table>')
    lines.append(f'{I}  </div>')
    lines.append(f'{I}</td></tr>')
    lines.append('')

lines.append(f'{I}</tbody>')

print('\n'.join(lines))
