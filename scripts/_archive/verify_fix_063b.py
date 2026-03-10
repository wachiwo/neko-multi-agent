#!/usr/bin/env python3
"""Verify all 6 fixes in calculator.py and settings.py."""
import ast

CALC = "outputs/shiire-hantei/app/routers/calculator.py"
SETTINGS = "outputs/shiire-hantei/app/routers/settings.py"
TEMPLATE_CALC = "outputs/shiire-hantei/app/templates/calculator.html"
TEMPLATE_SETTINGS = "outputs/shiire-hantei/app/templates/settings.html"

errors = []
passes = []

calc_code = open(CALC).read()
settings_code = open(SETTINGS).read()
calc_template = open(TEMPLATE_CALC).read()
settings_template = open(TEMPLATE_SETTINGS).read()

# Syntax check
try:
    ast.parse(calc_code)
    ast.parse(settings_code)
    passes.append("B1: Both files parse successfully")
except SyntaxError as e:
    errors.append(f"B1: Syntax error: {e}")

# Fix 1: calculator.py form field alignment
if "selling_price: int = Form" in calc_code:
    errors.append("Fix1: selling_price still a Form param (should derive from model)")
else:
    passes.append("Fix1: selling_price removed from Form params")

if "repair_screen" in calc_code and "repair_battery" in calc_code:
    passes.append("Fix1: repair_screen/repair_battery checkboxes accepted")
else:
    errors.append("Fix1: Missing repair_screen/repair_battery Form params")

if "market_price" in calc_code:
    passes.append("Fix1: selling_price derived from market_price")
else:
    errors.append("Fix1: market_price not used to derive selling_price")

if "repair_type" not in calc_code.split("Form")[0].split("def calculator_post")[-1] or 'repair_type: str = Form' not in calc_code:
    passes.append("Fix1: repair_type no longer a Form param")
else:
    errors.append("Fix1: repair_type still a direct Form param")

# Fix 2: settings.py field name alignment with template
# Template sends: profit_threshold, filter_screen_crack, filter_battery_bad, platform_{key}_fee
if '"profit_threshold"' in settings_code and "min_profit_threshold" not in settings_code:
    passes.append("Fix2: profit_threshold field name matches template")
else:
    errors.append("Fix2: profit_threshold field name still mismatched")

if "filter_screen_crack" in settings_code:
    passes.append("Fix2: filter_screen_crack key present")
else:
    errors.append("Fix2: filter_screen_crack key missing")

if "filter_battery_bad" in settings_code:
    passes.append("Fix2: filter_battery_bad key present")
else:
    errors.append("Fix2: filter_battery_bad key missing")

if "exclude_no_battery" in settings_code or "exclude_water_damage" in settings_code:
    errors.append("Fix2: Old exclude_* keys still present")
else:
    passes.append("Fix2: Old exclude_* keys removed")

if "platform_{platform_key}_fee" in settings_code or 'f"platform_{platform_key}_fee"' in settings_code:
    passes.append("Fix2: Platform fee field names match template (platform_{key}_fee)")
else:
    errors.append("Fix2: Platform fee field names still mismatched")

if "fee_rate_{platform_key}" in settings_code or 'f"fee_rate_{platform_key}"' in settings_code:
    errors.append("Fix2: Old fee_rate_{key} pattern still present")
else:
    passes.append("Fix2: Old fee_rate_{key} pattern removed")

# Fix 3: Connection leak — should use try/finally/close instead of with
if "finally:" in settings_code and "db.close()" in settings_code:
    passes.append("Fix3: try/finally/db.close() pattern used")
else:
    errors.append("Fix3: Connection leak not fixed (missing try/finally/close)")

if "with get_db() as db:" in settings_code:
    errors.append("Fix3: Old 'with get_db() as db:' still present")
else:
    passes.append("Fix3: Old 'with get_db()' pattern removed")

# Fix 4: Input validation
if "try:" in settings_code and "except" in settings_code and ("ValueError" in settings_code or "TypeError" in settings_code):
    passes.append("Fix4: Input validation with try/except present")
else:
    errors.append("Fix4: No input validation found")

# Fix 5: Use shared config loader
if "from app.config import load_models" in calc_code:
    passes.append("Fix5: calculator uses shared config.load_models()")
else:
    errors.append("Fix5: calculator still uses local _load_models()")

if "def _load_models" in calc_code:
    errors.append("Fix5: calculator still has local _load_models definition")
else:
    passes.append("Fix5: local _load_models removed from calculator")

if "from app.config import load_models" in settings_code:
    passes.append("Fix5: settings uses shared config.load_models()")
else:
    errors.append("Fix5: settings still uses local _load_models()")

if "def _load_models" in settings_code:
    errors.append("Fix5: settings still has local _load_models definition")
else:
    passes.append("Fix5: local _load_models removed from settings")

# Fix 6: Use app.state.templates
if "request.app.state.templates" in calc_code:
    passes.append("Fix6: calculator uses app.state.templates")
else:
    errors.append("Fix6: calculator not using app.state.templates")

if "request.app.state.templates" in settings_code:
    passes.append("Fix6: settings uses app.state.templates (or no TemplateResponse)")
elif "TemplateResponse" not in settings_code:
    passes.append("Fix6: settings has no TemplateResponse (uses redirect) — N/A for POST")
else:
    errors.append("Fix6: settings not using app.state.templates")

if "templates = Jinja2Templates" in calc_code:
    errors.append("Fix6: calculator still creates own Jinja2Templates instance")
else:
    passes.append("Fix6: no local Jinja2Templates in calculator")

if "templates = Jinja2Templates" in settings_code:
    errors.append("Fix6: settings still creates own Jinja2Templates instance")
else:
    passes.append("Fix6: no local Jinja2Templates in settings")

# Print results
print(f"PASS ({len(passes)}):")
for p in passes:
    print(f"  + {p}")
print()
if errors:
    print(f"FAIL ({len(errors)}):")
    for e in errors:
        print(f"  !! {e}")
else:
    print("FAIL (0): None")

print(f"\nVERDICT: {'FAIL' if errors else 'ALL 6 FIXES VERIFIED'}")
