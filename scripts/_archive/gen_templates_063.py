#!/usr/bin/env python3
"""Generate all Jinja2 templates + CSS for shiire-hantei web app (cmd_063)."""
import os

OUT = "outputs/shiire-hantei/app"
TEMPLATES = os.path.join(OUT, "templates")
STATIC = os.path.join(OUT, "static")

os.makedirs(TEMPLATES, exist_ok=True)
os.makedirs(STATIC, exist_ok=True)

# ============================================================
# base.html
# ============================================================
BASE_HTML = r'''<!DOCTYPE html>
<html lang="ja" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}仕入れ判定{% endblock %} | 仕入れ判定</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>tailwind.config={darkMode:'class'}</script>
  <link rel="stylesheet" href="{{ url_for('static', path='style.css') }}">
</head>
<body class="bg-gray-900 text-gray-100 min-h-screen flex flex-col">
  <!-- Tab Navigation: bottom on mobile, top on desktop -->
  <nav class="fixed bottom-0 left-0 right-0 z-50 bg-gray-800 border-t border-gray-700 md:static md:border-t-0 md:border-b">
    <ul class="flex justify-around md:justify-center md:gap-1 py-1 md:py-2 px-1">
      {% set tabs = [
        ("/", "dashboard", "ダッシュボード", "📊"),
        ("/candidates", "candidates", "仕入れ候補", "🛒"),
        ("/ng", "ng", "NG商品", "🚫"),
        ("/calculator", "calculator", "利益計算", "🔢"),
        ("/settings", "settings", "設定", "⚙️")
      ] %}
      {% for href, name, label, icon in tabs %}
      <li>
        <a href="{{ href }}"
           class="flex flex-col md:flex-row items-center gap-0.5 md:gap-2 px-2 md:px-4 py-1.5 md:py-2 rounded-lg text-xs md:text-sm transition-colors
                  {% if active_tab == name %}bg-emerald-600 text-white{% else %}text-gray-400 hover:text-gray-100 hover:bg-gray-700{% endif %}">
          <span class="text-lg md:text-base">{{ icon }}</span>
          <span>{{ label }}</span>
        </a>
      </li>
      {% endfor %}
    </ul>
  </nav>

  <!-- Main content -->
  <main class="flex-1 px-4 py-4 pb-20 md:pb-4 max-w-6xl mx-auto w-full">
    {% block content %}{% endblock %}
  </main>
</body>
</html>'''

# ============================================================
# dashboard.html
# ============================================================
DASHBOARD_HTML = r'''{% extends "base.html" %}
{% set active_tab = "dashboard" %}
{% block title %}ダッシュボード{% endblock %}
{% block content %}
<h1 class="text-xl font-bold mb-4">ダッシュボード</h1>

<!-- Stats cards -->
<div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
  <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
    <p class="text-gray-400 text-xs">全商品数</p>
    <p class="text-2xl font-bold">{{ stats.total | default(0) }}</p>
  </div>
  <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
    <p class="text-gray-400 text-xs">仕入れ候補</p>
    <p class="text-2xl font-bold text-emerald-400">{{ stats.candidates | default(0) }}</p>
  </div>
  <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
    <p class="text-gray-400 text-xs">NG商品</p>
    <p class="text-2xl font-bold text-red-400">{{ stats.ng | default(0) }}</p>
  </div>
  <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
    <p class="text-gray-400 text-xs">仕入れ済み</p>
    <p class="text-2xl font-bold text-blue-400">{{ stats.purchased | default(0) }}</p>
  </div>
</div>

<!-- Top profitable items -->
<h2 class="text-lg font-semibold mb-3">利益上位</h2>
{% if top_items %}
<div class="overflow-x-auto">
  <table class="w-full text-sm">
    <thead class="bg-gray-800 text-gray-400">
      <tr>
        <th class="px-3 py-2 text-left">商品名</th>
        <th class="px-3 py-2 text-right">仕入値</th>
        <th class="px-3 py-2 text-right">最大利益</th>
        <th class="px-3 py-2 text-left">プラットフォーム</th>
      </tr>
    </thead>
    <tbody class="divide-y divide-gray-700">
      {% for item in top_items %}
      <tr class="hover:bg-gray-800/50">
        <td class="px-3 py-2">
          <a href="/candidates/{{ item.id }}" class="text-emerald-400 hover:underline">{{ item.title | truncate(40) }}</a>
        </td>
        <td class="px-3 py-2 text-right">¥{{ "{:,}".format(item.price) }}</td>
        <td class="px-3 py-2 text-right font-bold {{ 'text-emerald-400' if item.best_profit > 0 else 'text-red-400' }}">
          ¥{{ "{:,}".format(item.best_profit) }}
        </td>
        <td class="px-3 py-2">{{ item.best_platform_label }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% else %}
<p class="text-gray-500">データがありません。スクレイプを実行してください。</p>
{% endif %}

<div class="mt-6">
  <form method="post" action="/api/scrape">
    <button type="submit" class="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-lg text-sm transition-colors">
      手動スクレイプ実行
    </button>
  </form>
</div>
{% endblock %}'''

# ============================================================
# candidates.html
# ============================================================
CANDIDATES_HTML = r'''{% extends "base.html" %}
{% set active_tab = "candidates" %}
{% block title %}仕入れ候補{% endblock %}
{% block content %}
<h1 class="text-xl font-bold mb-4">仕入れ候補</h1>

{% if listings %}
<div class="overflow-x-auto">
  <table class="w-full text-sm">
    <thead class="bg-gray-800 text-gray-400">
      <tr>
        <th class="px-3 py-2 text-left">商品名</th>
        <th class="px-3 py-2 text-left">機種</th>
        <th class="px-3 py-2 text-right">価格</th>
        <th class="px-3 py-2 text-right">最大利益</th>
        <th class="px-3 py-2 text-center">ステータス</th>
      </tr>
    </thead>
    <tbody class="divide-y divide-gray-700">
      {% for item in listings %}
      <tr class="hover:bg-gray-800/50">
        <td class="px-3 py-2">
          <a href="/candidates/{{ item.id }}" class="text-emerald-400 hover:underline">{{ item.title | truncate(50) }}</a>
        </td>
        <td class="px-3 py-2">{{ item.model_key or "-" }}</td>
        <td class="px-3 py-2 text-right">¥{{ "{:,}".format(item.price) }}</td>
        <td class="px-3 py-2 text-right font-bold {{ 'text-emerald-400' if item.best_profit is defined and item.best_profit > 0 else 'text-red-400' }}">
          {% if item.best_profit is defined %}¥{{ "{:,}".format(item.best_profit) }}{% else %}-{% endif %}
        </td>
        <td class="px-3 py-2 text-center">
          {% if item.status == 'candidate' %}
            <span class="bg-emerald-900 text-emerald-300 text-xs px-2 py-0.5 rounded">候補</span>
          {% elif item.status == 'purchased' %}
            <span class="bg-blue-900 text-blue-300 text-xs px-2 py-0.5 rounded">仕入済</span>
          {% elif item.status == 'sold' %}
            <span class="bg-purple-900 text-purple-300 text-xs px-2 py-0.5 rounded">販売済</span>
          {% endif %}
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% else %}
<p class="text-gray-500">仕入れ候補がありません。</p>
{% endif %}
{% endblock %}'''

# ============================================================
# candidate_detail.html
# ============================================================
CANDIDATE_DETAIL_HTML = r'''{% extends "base.html" %}
{% set active_tab = "candidates" %}
{% block title %}{{ listing.title | truncate(30) }}{% endblock %}
{% block content %}
<a href="/candidates" class="text-gray-400 hover:text-gray-200 text-sm mb-4 inline-block">&larr; 一覧に戻る</a>

<!-- Listing info card -->
<div class="bg-gray-800 rounded-lg p-4 border border-gray-700 mb-6">
  <h1 class="text-lg font-bold mb-2">{{ listing.title }}</h1>
  <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
    <div><span class="text-gray-400">機種:</span> {{ listing.model_key or "不明" }}</div>
    <div><span class="text-gray-400">価格:</span> ¥{{ "{:,}".format(listing.price) }}</div>
    <div><span class="text-gray-400">修理種別:</span> {{ listing.repair_type }}</div>
    <div><span class="text-gray-400">ステータス:</span>
      {% if listing.status == 'candidate' %}
        <span class="text-emerald-400">候補</span>
      {% elif listing.status == 'purchased' %}
        <span class="text-blue-400">仕入済</span>
      {% elif listing.status == 'sold' %}
        <span class="text-purple-400">販売済</span>
      {% elif listing.status == 'ng' %}
        <span class="text-red-400">NG</span>
      {% endif %}
    </div>
  </div>
  {% if listing.url %}
  <a href="{{ listing.url }}" target="_blank" rel="noopener" class="text-emerald-400 hover:underline text-sm mt-2 inline-block">オークションページを開く &rarr;</a>
  {% endif %}
</div>

<!-- 4-platform profit comparison -->
<h2 class="text-lg font-semibold mb-3">プラットフォーム別利益比較</h2>
{% if profits %}
<div class="overflow-x-auto mb-6">
  <table class="w-full text-sm">
    <thead class="bg-gray-800 text-gray-400">
      <tr>
        <th class="px-3 py-2 text-left">プラットフォーム</th>
        <th class="px-3 py-2 text-right">売値</th>
        <th class="px-3 py-2 text-right">手数料</th>
        <th class="px-3 py-2 text-right">パーツ代</th>
        <th class="px-3 py-2 text-right">送料</th>
        <th class="px-3 py-2 text-right">粗利</th>
      </tr>
    </thead>
    <tbody class="divide-y divide-gray-700">
      {% for p in profits %}
      <tr class="hover:bg-gray-800/50">
        <td class="px-3 py-2 font-medium">{{ platforms[p.platform].label if p.platform in platforms else p.platform }}</td>
        <td class="px-3 py-2 text-right">¥{{ "{:,}".format(p.selling_price) }}</td>
        <td class="px-3 py-2 text-right">¥{{ "{:,}".format(p.fee) }}</td>
        <td class="px-3 py-2 text-right">¥{{ "{:,}".format(p.parts_cost) }}</td>
        <td class="px-3 py-2 text-right">¥{{ "{:,}".format(p.shipping) }}</td>
        <td class="px-3 py-2 text-right font-bold {{ 'text-emerald-400' if p.gross_profit > 0 else 'text-red-400' }}">
          ¥{{ "{:,}".format(p.gross_profit) }}
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% else %}
<p class="text-gray-500 mb-6">利益計算データがありません。</p>
{% endif %}

<!-- Status change form (F1 fix) -->
<h2 class="text-lg font-semibold mb-3">ステータス変更</h2>
<form method="post" action="/candidates/{{ listing.id }}/status" class="bg-gray-800 rounded-lg p-4 border border-gray-700">
  <div class="flex flex-col md:flex-row gap-3">
    <div class="flex-1">
      <label for="status" class="block text-sm text-gray-400 mb-1">ステータス</label>
      <select name="status" id="status"
              class="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm text-gray-100 focus:outline-none focus:border-emerald-500"
              onchange="document.getElementById('ng-reason-group').style.display = this.value === 'ng' ? 'block' : 'none'">
        <option value="candidate" {% if listing.status == 'candidate' %}selected{% endif %}>候補</option>
        <option value="purchased" {% if listing.status == 'purchased' %}selected{% endif %}>仕入済</option>
        <option value="sold" {% if listing.status == 'sold' %}selected{% endif %}>販売済</option>
        <option value="ng" {% if listing.status == 'ng' %}selected{% endif %}>NG</option>
      </select>
    </div>
    <div id="ng-reason-group" class="flex-1 {{ '' if listing.status == 'ng' else 'hidden' }}">
      <label for="ng_reason" class="block text-sm text-gray-400 mb-1">NG理由</label>
      <textarea name="ng_reason" id="ng_reason" rows="2"
                class="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm text-gray-100 focus:outline-none focus:border-emerald-500"
                placeholder="NG理由を入力...">{{ listing.ng_reason or "" }}</textarea>
    </div>
    <div class="flex items-end">
      <button type="submit" class="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded text-sm transition-colors">
        更新
      </button>
    </div>
  </div>
</form>
{% endblock %}'''

# ============================================================
# ng.html
# ============================================================
NG_HTML = r'''{% extends "base.html" %}
{% set active_tab = "ng" %}
{% block title %}NG商品{% endblock %}
{% block content %}
<h1 class="text-xl font-bold mb-4">NG商品</h1>

{% if listings %}
<div class="overflow-x-auto">
  <table class="w-full text-sm">
    <thead class="bg-gray-800 text-gray-400">
      <tr>
        <th class="px-3 py-2 text-left">商品名</th>
        <th class="px-3 py-2 text-left">機種</th>
        <th class="px-3 py-2 text-right">価格</th>
        <th class="px-3 py-2 text-left">NG理由</th>
      </tr>
    </thead>
    <tbody class="divide-y divide-gray-700">
      {% for item in listings %}
      <tr class="hover:bg-gray-800/50">
        <td class="px-3 py-2">{{ item.title | truncate(50) }}</td>
        <td class="px-3 py-2">{{ item.model_key or "-" }}</td>
        <td class="px-3 py-2 text-right">¥{{ "{:,}".format(item.price) }}</td>
        <td class="px-3 py-2 text-red-400">{{ item.ng_reason or "理由なし" }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% else %}
<p class="text-gray-500">NG商品はありません。</p>
{% endif %}
{% endblock %}'''

# ============================================================
# calculator.html
# ============================================================
CALCULATOR_HTML = r'''{% extends "base.html" %}
{% set active_tab = "calculator" %}
{% block title %}利益計算{% endblock %}
{% block content %}
<h1 class="text-xl font-bold mb-4">利益計算シミュレーター</h1>

<form method="post" action="/calculator" class="bg-gray-800 rounded-lg p-4 border border-gray-700 mb-6">
  <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
    <div>
      <label for="model_key" class="block text-sm text-gray-400 mb-1">機種</label>
      <select name="model_key" id="model_key"
              class="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm text-gray-100 focus:outline-none focus:border-emerald-500">
        <option value="">-- 選択 --</option>
        {% for key, model in models.items() %}
        <option value="{{ key }}" {% if request.form and request.form.get('model_key') == key %}selected{% endif %}>
          {{ model.name }}
        </option>
        {% endfor %}
      </select>
    </div>
    <div>
      <label for="buying_price" class="block text-sm text-gray-400 mb-1">仕入れ価格 (円)</label>
      <input type="number" name="buying_price" id="buying_price" min="0" step="100"
             value="{{ request.form.get('buying_price', '') if request.form else '' }}"
             class="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm text-gray-100 focus:outline-none focus:border-emerald-500"
             placeholder="例: 5000" required>
    </div>
    <div>
      <label class="block text-sm text-gray-400 mb-1">修理タイプ</label>
      <div class="flex gap-4 mt-2">
        <label class="flex items-center gap-1.5 text-sm">
          <input type="checkbox" name="repair_screen" value="1"
                 {% if request.form and request.form.get('repair_screen') %}checked{% endif %}
                 class="rounded bg-gray-700 border-gray-600 text-emerald-500 focus:ring-emerald-500">
          画面修理
        </label>
        <label class="flex items-center gap-1.5 text-sm">
          <input type="checkbox" name="repair_battery" value="1"
                 {% if request.form and request.form.get('repair_battery') %}checked{% endif %}
                 class="rounded bg-gray-700 border-gray-600 text-emerald-500 focus:ring-emerald-500">
          バッテリー交換
        </label>
      </div>
    </div>
  </div>
  <div class="mt-4">
    <button type="submit" class="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-2 rounded-lg text-sm transition-colors">
      計算する
    </button>
  </div>
</form>

<!-- Results table -->
{% if results %}
<h2 class="text-lg font-semibold mb-3">計算結果</h2>
<div class="overflow-x-auto">
  <table class="w-full text-sm">
    <thead class="bg-gray-800 text-gray-400">
      <tr>
        <th class="px-3 py-2 text-left">プラットフォーム</th>
        <th class="px-3 py-2 text-right">想定売値</th>
        <th class="px-3 py-2 text-right">仕入値</th>
        <th class="px-3 py-2 text-right">パーツ代</th>
        <th class="px-3 py-2 text-right">手数料</th>
        <th class="px-3 py-2 text-right">送料</th>
        <th class="px-3 py-2 text-right">粗利</th>
      </tr>
    </thead>
    <tbody class="divide-y divide-gray-700">
      {% for r in results %}
      <tr class="hover:bg-gray-800/50">
        <td class="px-3 py-2 font-medium">{{ r.label }}</td>
        <td class="px-3 py-2 text-right">¥{{ "{:,}".format(r.selling_price) }}</td>
        <td class="px-3 py-2 text-right">¥{{ "{:,}".format(r.buying_price) }}</td>
        <td class="px-3 py-2 text-right">¥{{ "{:,}".format(r.parts_cost) }}</td>
        <td class="px-3 py-2 text-right">¥{{ "{:,}".format(r.fee) }}</td>
        <td class="px-3 py-2 text-right">¥{{ "{:,}".format(r.shipping) }}</td>
        <td class="px-3 py-2 text-right font-bold {{ 'text-emerald-400' if r.gross_profit > 0 else 'text-red-400' }}">
          ¥{{ "{:,}".format(r.gross_profit) }}
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% endif %}
{% endblock %}'''

# ============================================================
# settings.html
# ============================================================
SETTINGS_HTML = r'''{% extends "base.html" %}
{% set active_tab = "settings" %}
{% block title %}設定{% endblock %}
{% block content %}
<h1 class="text-xl font-bold mb-4">設定</h1>

<form method="post" action="/settings" class="space-y-6">
  <!-- Filter settings -->
  <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
    <h2 class="text-lg font-semibold mb-3">フィルター設定</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
      <label class="flex items-center gap-2 text-sm">
        <input type="checkbox" name="filter_screen_crack" value="1"
               {% if filters.get('filter_screen_crack', '1') == '1' %}checked{% endif %}
               class="rounded bg-gray-700 border-gray-600 text-emerald-500 focus:ring-emerald-500">
        画面割れを含む
      </label>
      <label class="flex items-center gap-2 text-sm">
        <input type="checkbox" name="filter_battery_bad" value="1"
               {% if filters.get('filter_battery_bad', '1') == '1' %}checked{% endif %}
               class="rounded bg-gray-700 border-gray-600 text-emerald-500 focus:ring-emerald-500">
        バッテリー劣化を含む
      </label>
      <label class="flex items-center gap-2 text-sm">
        <input type="checkbox" name="filter_degradation" value="1"
               {% if filters.get('filter_degradation', '0') == '1' %}checked{% endif %}
               class="rounded bg-gray-700 border-gray-600 text-emerald-500 focus:ring-emerald-500">
        焼き付き/残像を含む
      </label>
      <label class="flex items-center gap-2 text-sm">
        <input type="checkbox" name="filter_unverified" value="1"
               {% if filters.get('filter_unverified', '0') == '1' %}checked{% endif %}
               class="rounded bg-gray-700 border-gray-600 text-emerald-500 focus:ring-emerald-500">
        動作未確認品を含む
      </label>
    </div>
  </div>

  <!-- Platform fee/shipping settings -->
  <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
    <h2 class="text-lg font-semibold mb-3">プラットフォーム設定</h2>
    <div class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="text-gray-400">
          <tr>
            <th class="px-3 py-2 text-left">プラットフォーム</th>
            <th class="px-3 py-2 text-right">手数料率 (%)</th>
            <th class="px-3 py-2 text-right">送料 (円)</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-700">
          {% for key, pf in platforms.items() %}
          <tr>
            <td class="px-3 py-2">{{ pf.label }}</td>
            <td class="px-3 py-2 text-right">
              <input type="number" name="platform_{{ key }}_fee" step="0.1" min="0" max="100"
                     value="{{ (pf.fee_rate * 100) | round(1) }}"
                     class="w-20 bg-gray-700 border border-gray-600 rounded px-2 py-1 text-sm text-gray-100 text-right focus:outline-none focus:border-emerald-500">
            </td>
            <td class="px-3 py-2 text-right">
              <input type="number" name="platform_{{ key }}_shipping" step="10" min="0"
                     value="{{ pf.shipping }}"
                     class="w-24 bg-gray-700 border border-gray-600 rounded px-2 py-1 text-sm text-gray-100 text-right focus:outline-none focus:border-emerald-500">
            </td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  </div>

  <!-- Profit threshold -->
  <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
    <h2 class="text-lg font-semibold mb-3">利益しきい値</h2>
    <div class="flex items-center gap-3">
      <label for="profit_threshold" class="text-sm text-gray-400">最低利益 (円):</label>
      <input type="number" name="profit_threshold" id="profit_threshold" step="100" min="0"
             value="{{ filters.get('profit_threshold', '3000') }}"
             class="w-28 bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm text-gray-100 text-right focus:outline-none focus:border-emerald-500">
    </div>
    <p class="text-xs text-gray-500 mt-1">この金額以下の利益の商品はダッシュボードで強調されません。</p>
  </div>

  <button type="submit" class="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-2 rounded-lg text-sm transition-colors">
    設定を保存
  </button>
</form>
{% endblock %}'''

# ============================================================
# style.css
# ============================================================
STYLE_CSS = r'''/* shiire-hantei custom overrides — on top of TailwindCSS */

/* Smooth scrolling */
html { scroll-behavior: smooth; }

/* Mobile-first table fixes */
@media (max-width: 767px) {
  table { font-size: 0.8125rem; }
  th, td { padding: 0.375rem 0.5rem; }
}

/* Custom scrollbar for dark theme */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #1f2937; }
::-webkit-scrollbar-thumb { background: #4b5563; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #6b7280; }

/* Form focus glow */
input:focus, select:focus, textarea:focus {
  box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.3);
}

/* Tab nav safe area for bottom nav on iPhone */
@supports (padding-bottom: env(safe-area-inset-bottom)) {
  nav.fixed.bottom-0 {
    padding-bottom: env(safe-area-inset-bottom);
  }
}

/* Profit color utility (fallback if Tailwind classes fail to purge) */
.profit-positive { color: #34d399; }
.profit-negative { color: #f87171; }
'''

# ============================================================
# Write all files
# ============================================================
files = {
    os.path.join(TEMPLATES, "base.html"): BASE_HTML,
    os.path.join(TEMPLATES, "dashboard.html"): DASHBOARD_HTML,
    os.path.join(TEMPLATES, "candidates.html"): CANDIDATES_HTML,
    os.path.join(TEMPLATES, "candidate_detail.html"): CANDIDATE_DETAIL_HTML,
    os.path.join(TEMPLATES, "ng.html"): NG_HTML,
    os.path.join(TEMPLATES, "calculator.html"): CALCULATOR_HTML,
    os.path.join(TEMPLATES, "settings.html"): SETTINGS_HTML,
    os.path.join(STATIC, "style.css"): STYLE_CSS,
}

total_lines = 0
for path, content in files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.lstrip("\n"))
    lines = content.count("\n")
    total_lines += lines
    print(f"  OK: {path} ({lines} lines)")

print(f"\nTotal: {len(files)} files, {total_lines} lines written")
