#!/usr/bin/env python3
"""Verify generated templates for shiire-hantei cmd_063."""
import os

templates_dir = "outputs/shiire-hantei/app/templates"
static_dir = "outputs/shiire-hantei/app/static"

errors = []
warnings = []

expected = {
    templates_dir: ["base.html", "dashboard.html", "candidates.html",
                    "candidate_detail.html", "ng.html", "calculator.html", "settings.html"],
    static_dir: ["style.css"]
}

for d, files in expected.items():
    for f in files:
        path = os.path.join(d, f)
        if not os.path.exists(path):
            errors.append(f"MISSING: {path}")
            continue
        with open(path) as fh:
            content = fh.read()
        lines = content.count("\n") + 1
        if len(content.strip()) == 0:
            errors.append(f"EMPTY: {path}")
            continue

        # Templates must extend base (except base.html itself and CSS)
        if f not in ("base.html", "style.css"):
            if 'extends "base.html"' not in content:
                errors.append(f"NO EXTENDS: {path}")
            if "block content" not in content:
                errors.append(f"NO BLOCK CONTENT: {path}")
            if "active_tab" not in content:
                warnings.append(f"NO ACTIVE_TAB: {path}")

        # base.html checks
        if f == "base.html":
            for check, label in [
                ("tailwindcss", "TAILWIND CDN"),
                ("viewport", "VIEWPORT META"),
                ('"dark"', "DARK MODE CLASS"),
                ("bg-gray-900", "DARK BG"),
                ("fixed bottom-0", "MOBILE BOTTOM NAV"),
                ("md:static", "DESKTOP TOP NAV"),
            ]:
                if check not in content:
                    errors.append(f"NO {label}: {path}")

        print(f"  OK: {path} ({lines} lines)")

# F1 fix: status transition form in detail page
detail_path = os.path.join(templates_dir, "candidate_detail.html")
with open(detail_path) as fh:
    detail = fh.read()
    if "/status" not in detail:
        errors.append("F1 FIX MISSING: No status transition form in candidate_detail.html")
    if "ng_reason" not in detail:
        errors.append("NG REASON MISSING: No ng_reason field in candidate_detail.html")

# Calculator interface contract
calc_path = os.path.join(templates_dir, "calculator.html")
with open(calc_path) as fh:
    calc = fh.read()
    if "model_key" not in calc:
        errors.append("CALC: missing model_key reference")
    if "buying_price" not in calc:
        errors.append("CALC: missing buying_price reference")

# Settings filter keys must match filter_engine.py conditions
settings_path = os.path.join(templates_dir, "settings.html")
with open(settings_path) as fh:
    settings = fh.read()
    for key in ["screen_crack", "battery_bad", "degradation", "unverified"]:
        if key not in settings:
            warnings.append(f"SETTINGS: missing filter key {key}")

# Tables must have overflow-x-auto for mobile
for f in ["dashboard.html", "candidates.html", "candidate_detail.html", "ng.html", "calculator.html"]:
    path = os.path.join(templates_dir, f)
    with open(path) as fh:
        content = fh.read()
        if "<table" in content and "overflow-x-auto" not in content:
            warnings.append(f"NO OVERFLOW-X-AUTO ON TABLE: {f}")

# 5 tab coverage check
with open(os.path.join(templates_dir, "base.html")) as fh:
    base = fh.read()
    for tab in ["dashboard", "candidates", "ng", "calculator", "settings"]:
        if tab not in base:
            errors.append(f"TAB MISSING IN NAV: {tab}")

print()
if errors:
    print(f"ERRORS ({len(errors)}):")
    for e in errors:
        print(f"  !! {e}")
else:
    print("NO ERRORS")

if warnings:
    print(f"WARNINGS ({len(warnings)}):")
    for w in warnings:
        print(f"  ?? {w}")
else:
    print("NO WARNINGS")

print(f"\nVERDICT: {'FAIL' if errors else 'PASS'}")
