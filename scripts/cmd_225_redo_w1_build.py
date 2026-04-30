#!/usr/bin/env python3
"""cmd_225_redo W1 layout section builder.

Reads degawa source files (literal MUST、推測禁止) and outputs a self-contained section file:
- HTML literal copy from sample_登録.html L382-413 (sidebar) + L416-435 (header) + L437 main wrapper
- CSS inline copy: zdo_drawer_menu.css + style.css + responsive-common.css
- JS inline copy: zdo_drawer_menu.js
- 8 PNGs base64 inlined (menu/contact_page/description/edit_calendar/group/manage_accounts/person_add/settings)
- .part-label showroom 化
"""
import base64
from pathlib import Path

DEGAWA_DIR = Path("/mnt/g/共有ドライブ/[PJ]ディムコ/01_再構築プロジェクト/90_personal/degawa/007_部品一覧")
OUT = Path("/mnt/c/tools/neko-multi-agent/outputs/dimco-prototype/cmd_225_redo/w1_layout_section.html")


def base64_png(name: str) -> str:
    p = DEGAWA_DIR / "assets" / name
    data = p.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:image/png;base64,{b64}"


def read_text(p: Path) -> str:
    # responsive-common.css のコメントは cp932 で書かれているが CSS 本体は ASCII range で問題ないため utf-8 with errors='replace' で読む
    try:
        return p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return p.read_text(encoding="utf-8", errors="replace")


def main():
    # base64 PNGs
    icons = {}
    for name in ["menu.png", "contact_page.png", "description.png", "edit_calendar.png",
                 "group.png", "manage_accounts.png", "person_add.png", "settings.png"]:
        icons[name] = base64_png(name)

    # CSS files (literal copy)
    zdo_css = read_text(DEGAWA_DIR / "assets" / "zdo_drawer_menu.css")
    style_css = read_text(DEGAWA_DIR / "assets" / "style.css")
    # responsive-common.css は cp932 コメント問題で utf-8 read に失敗するので bytes 経由で読み、ASCII 範囲外を ? に
    rc_bytes = (DEGAWA_DIR / "assets" / "responsive-common.css").read_bytes()
    try:
        rc_css = rc_bytes.decode("cp932")
    except UnicodeDecodeError:
        rc_css = rc_bytes.decode("utf-8", errors="replace")

    # JS file (literal copy)
    zdo_js = read_text(DEGAWA_DIR / "assets" / "zdo_drawer_menu.js")

    # HTML sidebar literal (sample_登録.html L382-413、L412-413 は閉じ div)
    sample_lines = read_text(DEGAWA_DIR / "sample_登録.html").splitlines()
    sidebar_html = "\n".join(sample_lines[381:413])  # L382-413 (0-indexed 381-412 + 413 closing)
    header_html = "\n".join(sample_lines[418:435])   # L419-435

    # Replace assets/ image refs with base64 data URIs
    def swap_img(html: str) -> str:
        for name, b64 in icons.items():
            html = html.replace(f"assets/{name}", b64)
        return html

    sidebar_html = swap_img(sidebar_html)
    header_html = swap_img(header_html)

    section = f"""<!-- ====================================================================== -->
<!-- ★W1 SECTION (cmd_225_redo)★ — レイアウト系 (sidebar + header + footer audit + app-container) -->
<!-- ====================================================================== -->
<!--
  parent_cmd: cmd_225_redo subtask_225_redo_w1_layout
  worker: 1号猫 (worker1)
  作成日時: 2026-04-30T22:30
  ご主人様 trigger: 18:30 真意確定『worker 推測 SSOT (016/049/027) 採用禁止、degawa SSOT 起点 fresh build』
  方針: ★Spec Drafting Rule 1: degawa literal copy + line ref MUST、推測禁止★

  本 file の scope (W1 担当):
    1. サイドバー (zdo_drawer_menu.css + zdo_drawer_menu.js literal port、ハンバーガー drawer 開閉、左から slide-in)
    2. ヘッダー (sticky header、ロゴ + ユーザー dropdown)
    3. フッター audit (degawa 全 sample で 0 hit = 不在、DIMCO 同様 page-level footer 不採用)
    4. app-container 構造 (Bootstrap container-fluid + row、左 col-sm-auto sidebar + 右 col-sm main、960px breakpoint で responsive)

  source_files (literal copy reference):
    - sample_登録.html L382-413 (sidebar HTML)
    - sample_登録.html L419-435 (header HTML)
    - assets/zdo_drawer_menu.css (145 lines、サイドバー drawer CSS、Zarigani Design Office MIT license)
    - assets/style.css (769 lines、:root + sidebar + main 領域 + responsive 960px breakpoint)
    - assets/responsive-common.css (123 lines、767.98px breakpoint + scroll-hint utility)
    - assets/zdo_drawer_menu.js (49 lines、jQuery + vanilla JS dual binding)
    - 8 PNGs (menu/contact_page/description/edit_calendar/group/manage_accounts/person_add/settings) → base64 inline

  self-contained:
    - CDN: Bootstrap 5.3.x + Bootstrap Icons + jQuery (kashira 統合時に追加想定、本 section file は依存明記のみ)
    - ローカル CSS 全 inline (zdo_drawer_menu + style + responsive-common 計 1037 lines)
    - JS inline (zdo_drawer_menu.js)
    - 画像 base64 inline (8 PNGs、約 16KB)
    - 外部 file ref 0
-->


<!-- ====================================================================== -->
<!-- ★1. サイドバー (zdo_drawer_menu)★ -->
<!-- canonical: degawa 007_部品一覧/sample_登録.html L382-413 (HTML) + assets/zdo_drawer_menu.css (CSS) + assets/zdo_drawer_menu.js (JS) -->
<!-- 使用ガイド:
       Bootstrap container-fluid > row 内の左カラム (col-sm-auto bg-navy sticky-top)。
       - >960px: 縦アイコン列固定表示 (62px 幅)、ハンバーガー隠れ
       - ≤960px: サイドバー隠れ、ハンバーガー (左上 fixed) + drawer 左から slide-in
       - drawer 開閉: zdo_drawer_button.click → zdo_drawer_nav_wrapper.open class toggle
       - body scroll lock (drawer 開時)
       使用 file: degawa 全 sample で同 pattern。
-->
<!-- ====================================================================== -->

<div class="part-label">サイドバー (zdo_drawer_menu) — degawa SSOT</div>
<div class="part-demo-area">

{sidebar_html}

</div>


<!-- ====================================================================== -->
<!-- ★2. ヘッダー (sticky)★ -->
<!-- canonical: degawa 007_部品一覧/sample_登録.html L419-435 -->
<!-- 使用ガイド:
       右カラム (col-sm bg-maincolor) の最上段、background var(--primary-blue) で page タイトル + ユーザー dropdown。
       - position: sticky (style.css L714-717 で flex-shrink:0 + z-index:50)
       - logo + h3 (画面タイトル)、右側 user-info dropdown
       - 960px 以下では padding-left:50px で hamburger ボタン分の余白確保 (style.css L765-767)
-->
<!-- ====================================================================== -->

<div class="part-label">ヘッダー (sticky、ロゴ + dropdown) — degawa SSOT</div>
<div class="part-demo-area">

<div class="col-sm p-0 bg-maincolor" style="min-height: 200px;">

{header_html}

<main class="p-3" style="min-height: 100px;">
<p style="color: var(--text-gray); margin: 0;">main 領域 (page content がここに配置される)</p>
</main>

</div>

</div>


<!-- ====================================================================== -->
<!-- ★3. フッター — audit 結果: degawa 全 sample で 0 hit (page-level footer 不在)★ -->
<!-- audit method:
       - grep '<footer' degawa/007_部品一覧/*.html → 0 hit
       - grep 'class="footer"' degawa/007_部品一覧/*.html → 0 hit
     結論: ★degawa SSOT は page-level footer pattern 不採用★、catalog 採用時は省略 + audit finding として記載
-->
<!-- ====================================================================== -->

<div class="part-label">フッター — degawa 不在 (audit finding)</div>
<div class="part-demo-area">
<p style="color: var(--text-gray); font-style: italic; margin: 0;">degawa SSOT で page-level footer 不在 (DIMCO 既存 file も同様)。catalog では本 finding を documentation 化、独自 footer 追加禁止。</p>
</div>


<!-- ====================================================================== -->
<!-- ★4. app-container 構造 (full layout sample)★ -->
<!-- canonical: degawa 007_部品一覧/sample_登録.html L379-1042 (Bootstrap container-fluid + row + col-sm-auto sidebar + col-sm main wrap) -->
<!-- 使用ガイド:
       - <div class="container-fluid"><div class="row"> = 全画面 wrapper
       - 左 col-sm-auto bg-navy sticky-top (62px sidebar、≤960px で 0 px)
       - 右 col-sm bg-maincolor (flex column、header sticky + main scroll)
       - main 内 .table-responsive で table はみ出し防止
-->
<!-- ====================================================================== -->

<div class="part-label">app-container 構造 (Bootstrap container-fluid + row 2 col layout) — degawa SSOT</div>
<div class="part-demo-area">
<pre style="background: #f8f9fa; padding: 12px; border-radius: 6px; overflow-x: auto; font-size: 12px; margin: 0;"><code>&lt;body&gt;
  &lt;div class="container-fluid"&gt;
    &lt;div class="row"&gt;
      &lt;!-- 左サイドバー --&gt;
      &lt;div class="col-sm-auto bg-navy sticky-top"&gt;
        &lt;!-- zdo_drawer_menu HTML (Section 1) --&gt;
      &lt;/div&gt;
      &lt;!-- 右メインカラム --&gt;
      &lt;div class="col-sm p-0 min-vh-100 bg-maincolor"&gt;
        &lt;header&gt;...&lt;/header&gt;  &lt;!-- sticky header (Section 2) --&gt;
        &lt;main class="p-3"&gt;...&lt;/main&gt;  &lt;!-- page content --&gt;
      &lt;/div&gt;
    &lt;/div&gt;
  &lt;/div&gt;
&lt;/body&gt;</code></pre>
</div>


<!-- ====================================================================== -->
<!-- ★W1 LAYOUT SECTION 全 CSS (literal port)★ -->
<!-- 含まれる CSS:
       1. zdo_drawer_menu.css 全文 (145 lines、Zarigani Design Office)
       2. style.css 全文 (769 lines、:root canonical + sidebar + main + responsive 960px)
       3. responsive-common.css 全文 (123 lines、767.98px breakpoint + utilities)
     注: cp932 で書かれた responsive-common.css のコメントは utf-8 で読み込み困難、
         本 inline 版では cp932 → utf-8 変換または ? で代替表示 (CSS rule 自体は ASCII で問題なし)
-->
<style>
/* ===== zdo_drawer_menu.css (degawa assets/zdo_drawer_menu.css 全 145 行 literal copy) ===== */
{zdo_css}

/* ===== style.css (degawa assets/style.css 全 769 行 literal copy、:root canonical + sidebar + main responsive) ===== */
{style_css}

/* ===== responsive-common.css (degawa assets/responsive-common.css 全 123 行 literal copy、cp932 コメントは ? 化) ===== */
{rc_css}

/* ===== W1 統合担当追加 .part-label / .part-demo-area (showroom 化) ===== */
.part-label {{
    background: var(--primary-blue);
    color: white;
    padding: 8px 16px;
    font-size: 14px;
    font-weight: 600;
    margin-top: 24px;
    margin-bottom: 8px;
    border-radius: 6px 6px 0 0;
    display: inline-block;
}}
.part-demo-area {{
    background: white;
    border: 1px solid var(--border-color);
    border-radius: 0 6px 6px 6px;
    padding: 16px;
    margin-bottom: 24px;
}}
</style>


<!-- ====================================================================== -->
<!-- ★W1 LAYOUT SECTION JS (literal port)★ -->
<!-- zdo_drawer_menu.js 全 49 行 literal copy、jQuery + vanilla JS dual binding -->
<!-- ====================================================================== -->
<script>
/* ===== zdo_drawer_menu.js (degawa assets/zdo_drawer_menu.js 全 49 行 literal copy) ===== */
{zdo_js}
</script>


<!-- ====================================================================== -->
<!-- ★W1 SECTION END (cmd_225_redo)★ -->
<!--
  W1 担当 audit + literal copy 結果サマリ:
    1. サイドバー (zdo_drawer_menu): sample_登録.html L382-413 HTML + zdo_drawer_menu.css 145 行 + zdo_drawer_menu.js 49 行 + 7 PNG icon (base64 inline)
    2. ヘッダー (sticky): sample_登録.html L419-435 HTML + settings.png (base64 inline) + style.css L714-767 (sticky + 960px breakpoint)
    3. フッター: degawa 全 sample 0 hit 確認、audit finding として記載 (独自追加禁止)
    4. app-container 構造: container-fluid > row > 2-col (sidebar + main wrap) Bootstrap pattern documented
  literal copy compliance:
    - Spec Drafting Rule 1 厳守: HTML/CSS/JS 全件 degawa literal copy + line ref 明示
    - 推測禁止: 全 source が degawa 007_部品一覧/ 由来、worker 推測 SSOT (016/049/027) 一切採用なし
    - self-contained: CDN deps (Bootstrap/jQuery/Icons) のみ外部、ローカル CSS/JS/画像 全 inline
  scope_lock 遵守:
    - degawa source file (G drive) touch なし、reference のみ
    - 既存 DIMCO file 全 touch なし
    - shared/ ファイル新規作成なし
    - outputs/cmd_225_redo/w1_layout_section.html 1 file 生成のみ
  Phase 2: kashira (or 他 worker) が 4 worker section を統合 (HTML5 wrapper + CDN link 追加)
-->
<!-- ====================================================================== -->
"""

    OUT.write_text(section, encoding="utf-8")
    line_count = section.count("\n") + 1
    byte_count = len(section.encode("utf-8"))
    print(f"[OK] Wrote {OUT} ({line_count} lines, {byte_count:,} bytes)")
    print(f"  base64 PNGs: {len(icons)} (約 {sum(len(v) for v in icons.values()):,} chars)")


if __name__ == "__main__":
    main()
