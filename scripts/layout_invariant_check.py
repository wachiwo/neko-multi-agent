#!/usr/bin/env python3
# ruff: noqa: W605
r"""Semantic Layout Invariant Checker (cmd_184_3layer_defense Day 0, layer 3).

# ============================================================================
# USAGE (originator: W4, committed: cmd_184_layout_invariant_tooling)
# ============================================================================
#
# 前提:
#   pip install playwright pyyaml && python3 -m playwright install chromium
#   (WSL では libasound.so.2 が必要、先頭で自動 LD_PRELOAD 解決)
#
# 単一ファイル検査:
#   python3 scripts/layout_invariant_check.py \
#     --target-file /mnt/i/.../new/052_受注画面\(受注明細\).html \
#     --expected scripts/expected_縦.yaml \
#     --output-dir outputs/dimco-prototype/<cmd_id>/layout_check/
#
# ディレクトリ一括検査 (全 *.html):
#   python3 scripts/layout_invariant_check.py \
#     --target-dir /mnt/i/.../new/ \
#     --expected scripts/expected_縦.yaml \
#     --output-dir outputs/dimco-prototype/<cmd_id>/layout_check/ \
#     --viewport 1200
#
# 出力:
#   layout_invariants_<filename>.json  - ファイル単位詳細 (rules_evaluated / fails 構造化)
#   layout_invariants_summary.md        - バッチ全体サマリ (テーブル + FAIL 詳細)
#
# 終了コード:
#   0: HIGH severity 失敗なし
#   1: 1 ファイル以上で HIGH 失敗あり
#   2: 依存 (playwright/pyyaml) 未インストール
#
# expected YAML の書き方:
#   scripts/expected_縦.yaml を参照 (vertical form-label 向けの 11 rules)。
#     rule_type: computed_style | geometric | existence | conditional
#                | click_test | width_ratio_check | viewport_overflow_check
#     severity:  high | medium | low
#   サンプリング禁止系 (click_test) は click_policy: all 必須。
#
# 代表的な検出対象 (cmd_184 系の事故から由来):
#   - form-field が flex-direction:row に戻っていないか (rollback_003_w4)
#   - data-component=CollapsibleSection に .collapsible-header 実装あるか (rollback)
#   - .form-field align-items:stretch で子要素が過剰伸長していないか (stretch_fix)
#   - button 幅が親の 50% を超えていないか (form_field_stretch)
#   - 1200/800/600 viewport 全件 overflow ゼロか (phase_a_pivot)
#   - 折りたたみ全件 (サンプリング禁止) bidirectional toggle 成功か (052_pattern_b)
#
# 参考実装バージョン:
#   originator W4 / v5 (cmd_184_hotfix5_typography_unify 以降の expected_縦.yaml 11 rules
#   に対応)。過去 cmd_184_052_pattern_b_fix/post_w1 は pre-v5 (8 rules) だが JSON schema
#   は互換 (追加 rule は差分として現れるのみ)。
# ============================================================================

cmd_184_brainstorm Q5 提案の本実装。subtask_184_rollback_003_w4 で「overflow=0 だが横並び /
折りたたみ機能削除」を実機検出した経験を汎用化したツール。

  CLI:
    python3 layout_invariant_check.py \
      --target-dir <new/> | --target-file <path>... \
      --expected scripts/expected_縦.yaml \
      --output-dir outputs/dimco-prototype/cmd_184_3layer_defense/layout_check/ \
      [--viewport 1200] [--html-report]

  期待値 YAML スキーマ:
    version: "1.0"
    form_label: "vertical | horizontal | other"
    rules:
      - id: <unique>
        rule_type: computed_style | geometric | existence | conditional
        selector: <CSS selector>      # rule_type != conditional のとき必須
        if_selector_exists: <CSS>     # rule_type == conditional
        then_check:
          selector: <CSS>
          min_count: <int>
        expect:
          computed_style: { property: value | range }
          geometric: { vertical_stacking: true | horizontal_stacking: true }
          existence: { min_count: 1, max_count: null }
        severity: high | medium | low
        diag: <human readable>
        sample_limit: 20            # 各ルールで最大何要素まで詳細チェックするか

  出力:
    - layout_invariants_<file>.json (ファイル単位、FAIL detail)
    - layout_invariants_summary.md  (バッチ全体サマリ)

経験的根拠 (subtask_184_rollback_003_w4 検証で実証):
  - form-field flex-direction:row が overflow=0 でも検出可能
  - label-input 幾何 (label.bottom <= input.top) で縦/横並びを機械判定可能
  - data-component='CollapsibleSection' あるのに .collapsible-header が無い
    (= 折りたたみ機能削除事故) を conditional rule で防止
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote

# ---------- libasound (WSL Playwright) workaround ----------
LIBASOUND_PATHS = [
    "/tmp/libasound/usr/lib/x86_64-linux-gnu/libasound.so.2",
    "/tmp/libasound_extract/usr/lib/x86_64-linux-gnu/libasound.so.2",
]
if not os.environ.get("LD_PRELOAD"):
    for p in LIBASOUND_PATHS:
        if os.path.exists(p):
            os.environ["LD_PRELOAD"] = p
            break

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("ERROR: playwright not installed. pip install playwright && python3 -m playwright install chromium", file=sys.stderr)
    sys.exit(2)

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml not installed. pip install pyyaml", file=sys.stderr)
    sys.exit(2)


# ====================================================================
# Rule evaluators
# ====================================================================

def _rgb_in_range(rgb_str: str, r_range, g_range, b_range) -> bool:
    """'rgb(0, 93, 168)' or 'rgba(...)' を parse して range 内か判定。"""
    m = re.search(r"rgba?\((\d+)[,\s]+(\d+)[,\s]+(\d+)", rgb_str)
    if not m:
        return False
    r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
    return r_range[0] <= r <= r_range[1] and g_range[0] <= g <= g_range[1] and b_range[0] <= b <= b_range[1]


def _check_computed_style(actual: dict, expect: dict) -> tuple[bool, str | None]:
    """expect dict: { propName: literalValue } or { propName_rgb_range: {...} }
       or { propName_regex: ... } or { propName_forbidden: [values] }
       (cmd_184_form_field_stretch_fix: _forbidden suffix で value の禁止 list を指定可能)
    """
    for key, want in expect.items():
        if key.endswith("_rgb_range"):
            prop = key[: -len("_rgb_range")]
            actual_val = actual.get(prop, "")
            if not _rgb_in_range(actual_val, want.get("r", [0, 255]), want.get("g", [0, 255]), want.get("b", [0, 255])):
                return False, f"{prop}={actual_val} not in rgb range {want}"
        elif key.endswith("_regex"):
            prop = key[: -len("_regex")]
            actual_val = actual.get(prop, "")
            if not re.search(want, str(actual_val)):
                return False, f"{prop}={actual_val} does not match /{want}/"
        elif key.endswith("_forbidden"):
            # ★ cmd_184_form_field_stretch_fix ★ 禁止 value list
            prop = key[: -len("_forbidden")]
            actual_val = actual.get(prop, "")
            forbid = want if isinstance(want, list) else [want]
            if actual_val in forbid:
                return False, f"{prop}={actual_val} is in FORBIDDEN list {forbid}"
        elif isinstance(want, list):
            actual_val = actual.get(key)
            if actual_val not in want:
                return False, f"{key}={actual_val} not in {want}"
        else:
            actual_val = actual.get(key)
            if actual_val != want:
                return False, f"{key}={actual_val!r} expected {want!r}"
    return True, None


def _check_geometric(geom: dict, expect: dict) -> tuple[bool, str | None]:
    """expect: { vertical_stacking: true | horizontal_stacking: true | label_above_input: true }"""
    for key, want in expect.items():
        if key in ("vertical_stacking", "label_above_input"):
            actual = geom.get("vertical")
            if want and not actual:
                return False, f"label is NOT above input (label.bottom={geom.get('label_bottom')}, input.top={geom.get('input_top')})"
            if not want and actual:
                return False, "vertical stacking detected when expected NOT vertical"
        elif key == "horizontal_stacking":
            actual = geom.get("horizontal")
            if want and not actual:
                return False, "label is NOT to the left of input"
            if not want and actual:
                return False, "horizontal stacking detected when expected NOT horizontal"
    return True, None


# ====================================================================
# Per-file analysis
# ====================================================================

def _evaluate_click_test(page, rule: dict) -> dict:
    """click_test rule: click each matched element and verify state change.

    ★cmd_184_052_pattern_b_fix 経緯★:
      subtask_184_revive_002_w4 でサンプリング 3/3 を「成功」と報告したが、
      実は 11 個中 3 個しか検査しておらず、残り 8 個のうち 3 個が FAIL していた。
      ★サンプリング検査は禁止★ — all policy (全件) を必須化。

    rule structure:
      rule_type: click_test
      selector: ".collapsible-header"
      click_policy: all          # all (required) | sample (deprecated, error)
      required_pass_ratio: 1.0   # 1.0 = 100% all must pass; <1.0 partial allowed (rarely)
      verify:                    # どう「toggle 成功」を判定するか
        strategy: display_toggle | class_toggle | section_class_toggle
        # display_toggle: nextElementSibling の computed display が block→none→block 変化
        # class_toggle: nextElementSibling の classList に 'collapsed' が追加/除去される
        # section_class_toggle: closest('.section') の classList に 'collapsed' が追加/除去される
      severity: high
      diag: ...
    """
    rid = rule.get("id", "<no-id>")
    severity = rule.get("severity", "medium")
    diag = rule.get("diag", "")
    selector = rule["selector"]
    policy = rule.get("click_policy", "all")
    required_ratio = float(rule.get("required_pass_ratio", 1.0))
    verify = rule.get("verify", {})
    strategy = verify.get("strategy", "auto")  # auto tries multiple strategies
    if policy != "all":
        return {"rule_id": rid, "severity": severity, "diag": diag, "passed": False,
                "fails": [{"reason": f"click_policy='{policy}' is not allowed — must be 'all' (サンプリング検査は禁止)"}],
                "note": "policy_violation"}

    total = page.evaluate("(s) => document.querySelectorAll(s).length", selector)
    if total == 0:
        return {"rule_id": rid, "severity": severity, "diag": diag, "passed": True,
                "fails": [], "note": f"no target elements (0) — click_test N/A"}

    results = []  # per-element
    for idx in range(total):
        try:
            # take snapshot of strategy signals BEFORE click
            before = page.evaluate(
                """(args) => {
                  const {selector, idx, strategy} = args;
                  const el = document.querySelectorAll(selector)[idx];
                  if (!el) return null;
                  const next = el.nextElementSibling;
                  const parentSection = el.closest('.section');
                  const title_text = el.textContent.trim().slice(0, 40);
                  return {
                    idx,
                    text: title_text,
                    next_display: next ? getComputedStyle(next).display : null,
                    next_has_collapsed: next ? next.classList.contains('collapsed') : null,
                    section_has_collapsed: parentSection ? parentSection.classList.contains('collapsed') : null,
                  };
                }""", {"selector": selector, "idx": idx, "strategy": strategy})

            if before is None:
                results.append({"idx": idx, "passed": False, "reason": "element disappeared before click"})
                continue

            # click (locator 経由で全件安全アクセス)
            loc = page.locator(selector).nth(idx)
            try:
                loc.scroll_into_view_if_needed(timeout=3000)
            except Exception:
                pass  # scroll failure は click 試行まで継続
            loc.click(timeout=3000, force=True)
            page.wait_for_timeout(150)

            after = page.evaluate(
                """(args) => {
                  const {selector, idx} = args;
                  const el = document.querySelectorAll(selector)[idx];
                  if (!el) return null;
                  const next = el.nextElementSibling;
                  const parentSection = el.closest('.section');
                  return {
                    idx,
                    next_display: next ? getComputedStyle(next).display : null,
                    next_has_collapsed: next ? next.classList.contains('collapsed') : null,
                    section_has_collapsed: parentSection ? parentSection.classList.contains('collapsed') : null,
                  };
                }""", {"selector": selector, "idx": idx})

            # decide toggle pass (1st click): ANY of the signals changed
            signals_changed = []
            if before["next_display"] != after["next_display"]:
                signals_changed.append(f"display {before['next_display']}→{after['next_display']}")
            if before["next_has_collapsed"] != after["next_has_collapsed"]:
                signals_changed.append(f"next.collapsed {before['next_has_collapsed']}→{after['next_has_collapsed']}")
            if before["section_has_collapsed"] != after["section_has_collapsed"]:
                signals_changed.append(f"section.collapsed {before['section_has_collapsed']}→{after['section_has_collapsed']}")

            first_click_changed = len(signals_changed) > 0

            # click back (bidirectional test: 2nd click should restore state)
            restored = False
            restore_signals = []
            try:
                loc2 = page.locator(selector).nth(idx)
                loc2.click(timeout=2000, force=True)
                page.wait_for_timeout(120)
                restored_state = page.evaluate(
                    """(args) => {
                      const {selector, idx} = args;
                      const el = document.querySelectorAll(selector)[idx];
                      if (!el) return null;
                      const next = el.nextElementSibling;
                      const parentSection = el.closest('.section');
                      return {
                        next_display: next ? getComputedStyle(next).display : null,
                        next_has_collapsed: next ? next.classList.contains('collapsed') : null,
                        section_has_collapsed: parentSection ? parentSection.classList.contains('collapsed') : null,
                      };
                    }""", {"selector": selector, "idx": idx})
                if restored_state is not None:
                    # restored state should match the BEFORE state (bidirectional toggle)
                    restored = (
                        restored_state["next_display"] == before["next_display"] and
                        restored_state["next_has_collapsed"] == before["next_has_collapsed"] and
                        restored_state["section_has_collapsed"] == before["section_has_collapsed"]
                    )
                    if after["next_display"] != restored_state["next_display"]:
                        restore_signals.append(f"display {after['next_display']}→{restored_state['next_display']}")
            except Exception as e:
                restore_signals.append(f"restore click error: {str(e)[:100]}")

            # ★ BOTH clicks must change state to pass (bidirectional toggle required)
            toggled = first_click_changed and restored

            reason = None
            if not first_click_changed:
                reason = "1st click no state change (folding broken)"
            elif not restored:
                reason = "2nd click did not restore state (bidirectional toggle broken)"

            results.append({
                "idx": idx,
                "text": before.get("text"),
                "passed": toggled,
                "first_click_signals": signals_changed,
                "restore_signals": restore_signals,
                "before_display": before["next_display"],
                "after_display": after["next_display"],
                "first_click_changed": first_click_changed,
                "restored": restored,
                "reason": reason,
            })
        except Exception as e:
            results.append({"idx": idx, "passed": False, "reason": f"click error: {str(e)[:120]}"})

    pass_count = sum(1 for r in results if r["passed"])
    fail_count = total - pass_count
    ratio = pass_count / total if total else 0.0

    fails = []
    if ratio < required_ratio:
        for r in results:
            if not r["passed"]:
                fails.append(r)

    # ★ 分母明示必須 (pass/total 形式) ★
    note = f"click_pass={pass_count}/{total} ratio={ratio:.2f} required>={required_ratio}"

    return {"rule_id": rid, "severity": severity, "diag": diag,
            "passed": ratio >= required_ratio,
            "fails": fails, "note": note,
            "click_results": results, "pass_count": pass_count, "total_count": total,
            "ratio": ratio}


def evaluate_rule(page, rule: dict) -> dict:
    """Evaluate one rule against the loaded page. Returns {rule_id, passed, fails: [...], note}"""
    rid = rule.get("id", "<no-id>")
    severity = rule.get("severity", "medium")
    diag = rule.get("diag", "")
    rule_type = rule.get("rule_type", "computed_style")
    sample_limit = rule.get("sample_limit", 20)

    fails: list[dict] = []
    note: str = ""

    if rule_type == "click_test":
        return _evaluate_click_test(page, rule)

    if rule_type == "width_ratio_check":
        # ★cmd_184_form_field_stretch_fix★
        # 要素の width / 親の width 比率を機械判定 (button の過剰伸長検出)
        # rule:
        #   selector: ".form-field button"
        #   max_width_ratio_to_parent: 0.5
        #   min_parent_width_px: 200   # この幅未満の親は skip (wrap div など false positive 回避)
        #   compare_to_ancestor: ".form-field"  # 省略時は parentElement
        sel = rule["selector"]
        max_ratio = float(rule.get("max_width_ratio_to_parent", 0.5))
        min_parent_w = float(rule.get("min_parent_width_px", 0))
        ancestor_sel = rule.get("compare_to_ancestor")  # None → parentElement
        sample_limit = rule.get("sample_limit", 20)
        data = page.evaluate(
            """({selector, limit, ancestorSel}) => {
              const els = Array.from(document.querySelectorAll(selector)).slice(0, limit);
              return els.map((el, idx) => {
                const b = el.getBoundingClientRect();
                const ref = ancestorSel ? el.closest(ancestorSel) : el.parentElement;
                const pb = ref ? ref.getBoundingClientRect() : null;
                const text = (el.textContent || '').trim().slice(0, 30);
                return {
                  idx,
                  text,
                  el_width: b.width,
                  ref_width: pb ? pb.width : null,
                  ratio: (pb && pb.width > 0) ? (b.width / pb.width) : null,
                };
              });
            }""",
            {"selector": sel, "limit": sample_limit, "ancestorSel": ancestor_sel},
        )
        fails = []
        skipped = 0
        for item in data:
            if item["ratio"] is None:
                continue
            if item["ref_width"] is not None and item["ref_width"] < min_parent_w:
                skipped += 1
                continue  # too-small parent: skip to avoid false positive on tight wrappers
            if item["ratio"] > max_ratio:
                ref_label = f"ancestor({ancestor_sel})" if ancestor_sel else "parent"
                fails.append({
                    "selector": sel, "element_idx": item["idx"],
                    "reasons": [f"width ratio {item['ratio']:.2f} > max {max_ratio} (el={item['el_width']:.0f}px {ref_label}={item['ref_width']:.0f}px text='{item['text']}')"],
                })
        evaluated = len(data) - skipped
        note = f"evaluated={evaluated}/{len(data)} (skipped small-parent={skipped}) over_ratio={len(fails)} max_ratio={max_ratio}"
        return {"rule_id": rid, "severity": severity, "diag": diag, "passed": len(fails) == 0,
                "fails": fails, "note": note,
                "pass_count": evaluated - len(fails), "total_count": evaluated}

    if rule_type == "conditional":
        if_sel = rule["if_selector_exists"]
        then = rule["then_check"]
        if_count = page.evaluate("(s) => document.querySelectorAll(s).length", if_sel)
        if if_count >= 1:
            then_count = page.evaluate("(s) => document.querySelectorAll(s).length", then["selector"])
            min_count = then.get("min_count", 1)
            if then_count < min_count:
                fails.append({
                    "trigger": f"{if_sel} count={if_count}",
                    "then_selector": then["selector"],
                    "actual_count": then_count,
                    "expected_min": min_count,
                    "reason": f"{if_sel} が {if_count} 個存在するが {then['selector']} が {then_count} 個 (期待 >={min_count})",
                })
            note = f"if-trigger:{if_count} then-actual:{then_count}"
        else:
            note = "if-condition not met (skipped)"
    elif rule_type == "existence":
        sel = rule["selector"]
        cnt = page.evaluate("(s) => document.querySelectorAll(s).length", sel)
        expect = rule.get("expect", {}).get("existence", {})
        min_c = expect.get("min_count")
        max_c = expect.get("max_count")
        if min_c is not None and cnt < min_c:
            fails.append({"selector": sel, "actual_count": cnt, "expected_min": min_c, "reason": f"count={cnt} < min={min_c}"})
        if max_c is not None and cnt > max_c:
            fails.append({"selector": sel, "actual_count": cnt, "expected_max": max_c, "reason": f"count={cnt} > max={max_c}"})
        note = f"count={cnt}"
    else:
        # computed_style or geometric (per-element)
        sel = rule["selector"]
        expect = rule.get("expect", {})
        cs_expect = expect.get("computed_style")
        geom_expect = expect.get("geometric")
        # gather data
        data = page.evaluate(
            """({selector, limit, needComputedStyle, needGeometric}) => {
              const els = Array.from(document.querySelectorAll(selector)).slice(0, limit);
              return els.map((el, idx) => {
                const out = {idx};
                if (needComputedStyle) {
                  const cs = getComputedStyle(el);
                  out.computed = {
                    display: cs.display,
                    flexDirection: cs.flexDirection,
                    gridTemplateColumns: cs.gridTemplateColumns,
                    backgroundColor: cs.backgroundColor,
                    color: cs.color,
                    position: cs.position,
                  };
                }
                if (needGeometric) {
                  const label = el.querySelector('label');
                  const input = el.querySelector('input, select, textarea');
                  if (label && input) {
                    const lb = label.getBoundingClientRect();
                    const ib = input.getBoundingClientRect();
                    out.geom = {
                      label_bottom: lb.bottom, label_right: lb.right, label_top: lb.top, label_left: lb.left,
                      input_top: ib.top, input_left: ib.left, input_bottom: ib.bottom, input_right: ib.right,
                      vertical: lb.bottom <= ib.top + 2,
                      horizontal: lb.right <= ib.left + 2 && Math.abs(lb.top - ib.top) < 10,
                    };
                  } else {
                    out.geom = null;
                  }
                }
                return out;
              });
            }""",
            {"selector": sel, "limit": sample_limit, "needComputedStyle": cs_expect is not None, "needGeometric": geom_expect is not None},
        )
        for item in data:
            fail_reasons = []
            if cs_expect is not None and "computed" in item:
                ok, reason = _check_computed_style(item["computed"], cs_expect)
                if not ok:
                    fail_reasons.append(reason)
            if geom_expect is not None:
                if item.get("geom") is None:
                    if geom_expect:
                        fail_reasons.append("no label/input pair found")
                else:
                    ok, reason = _check_geometric(item["geom"], geom_expect)
                    if not ok:
                        fail_reasons.append(reason)
            if fail_reasons:
                fails.append({
                    "selector": sel, "element_idx": item["idx"], "reasons": fail_reasons,
                    "computed": item.get("computed"), "geom": item.get("geom"),
                })
        note = f"sampled={len(data)}"

    return {"rule_id": rid, "severity": severity, "diag": diag, "passed": len(fails) == 0, "fails": fails, "note": note}


def _eval_viewport_overflow_check(browser, file_url: str, rule: dict) -> dict:
    """★cmd_184_phase_a_pivot★ multi-viewport overflow detection.

    rule:
      rule_type: viewport_overflow_check
      viewports: [1200, 800, 600]   # 100% / 150% / 200% 相当
      target_selectors: ["input", "button", "label", ".form-field"]
      severity: high
      diag: ...

    Detects: (1) horizontal scroll on body / docElement, (2) target elements right > viewport width
    Required: ALL viewports + ALL selectors PASS (zero overflow)
    """
    rid = rule.get("id", "<no-id>")
    severity = rule.get("severity", "high")
    diag = rule.get("diag", "")
    viewports = rule.get("viewports", [1200])
    selectors = rule.get("target_selectors", ["input", "button", "label", ".form-field"])
    sample_limit = rule.get("sample_limit", 50)
    fails: list[dict] = []
    per_viewport_results = []

    for vw in viewports:
        ctx = browser.new_context(viewport={"width": vw, "height": 1080})
        page = ctx.new_page()
        try:
            page.goto(file_url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(400)
        except Exception as e:
            ctx.close()
            fails.append({"viewport": vw, "type": "load_error", "reason": str(e)[:120]})
            continue

        body_data = page.evaluate("""() => ({
          docScrollW: document.documentElement.scrollWidth,
          bodyScrollW: document.body.scrollWidth,
          viewportW: window.innerWidth,
        })""")
        # check 1: horizontal scroll
        h_scroll = body_data["docScrollW"] > body_data["viewportW"] + 1
        if h_scroll:
            fails.append({
                "viewport": vw, "type": "horizontal_scroll",
                "doc_scrollW": body_data["docScrollW"], "viewport_w": body_data["viewportW"],
                "reason": f"document.scrollWidth ({body_data['docScrollW']}) > viewport ({body_data['viewportW']})",
            })
        # check 2: per-selector overflow
        sel_results = {}
        for sel in selectors:
            items = page.evaluate(
                """({sel, limit, vp}) => {
                  return Array.from(document.querySelectorAll(sel)).slice(0, limit).map((el, idx) => {
                    const r = el.getBoundingClientRect();
                    const text = (el.textContent||'').trim().slice(0, 30);
                    return {
                      idx, text,
                      right: r.right, left: r.left,
                      width: r.width,
                      overflow_right: r.right > vp + 1,
                      overflow_left: r.left < -1,
                    };
                  });
                }""",
                {"sel": sel, "limit": sample_limit, "vp": body_data["viewportW"]},
            )
            over_count = sum(1 for it in items if it["overflow_right"] or it["overflow_left"])
            sel_results[sel] = {"checked": len(items), "overflow_count": over_count}
            for it in items:
                if it["overflow_right"] or it["overflow_left"]:
                    fails.append({
                        "viewport": vw, "type": "element_overflow", "selector": sel,
                        "element_idx": it["idx"], "element_right": it["right"], "element_left": it["left"],
                        "element_width": it["width"], "viewport_w": body_data["viewportW"],
                        "text": it["text"],
                        "reason": (
                            f"right={it['right']:.0f}px > viewport={body_data['viewportW']}px"
                            if it["overflow_right"] else
                            f"left={it['left']:.0f}px < 0"
                        ),
                    })
        per_viewport_results.append({
            "viewport": vw,
            "doc_scrollW": body_data["docScrollW"],
            "viewport_w": body_data["viewportW"],
            "horizontal_scroll": h_scroll,
            "per_selector": sel_results,
        })
        ctx.close()

    total_viewports = len(viewports)
    failed_viewports = len(set(f["viewport"] for f in fails))
    pass_viewports = total_viewports - failed_viewports
    # ★ 分母明示 N/M ★
    note = f"vp_pass={pass_viewports}/{total_viewports} fails={len(fails)}"
    return {
        "rule_id": rid, "severity": severity, "diag": diag,
        "passed": len(fails) == 0,
        "fails": fails, "note": note,
        "pass_count": pass_viewports, "total_count": total_viewports,
        "per_viewport_results": per_viewport_results,
    }


def analyze_file(html_path: Path, rules: list[dict], viewport_width: int) -> dict:
    file_url = "file://" + quote(str(html_path.resolve()), safe="/:")
    result: dict[str, Any] = {
        "file": str(html_path),
        "filename": html_path.name,
        "viewport_width": viewport_width,
        "console_errors": [],
        "rules_evaluated": [],
        "rules_failed": 0,
        "rules_passed": 0,
        "high_severity_failures": 0,
    }
    # Separate viewport_overflow_check rules (need multi-viewport context)
    vp_rules = [r for r in rules if r.get("rule_type") == "viewport_overflow_check"]
    other_rules = [r for r in rules if r.get("rule_type") != "viewport_overflow_check"]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # main loop: single-viewport rules
        ctx = browser.new_context(viewport={"width": viewport_width, "height": 1080})
        page = ctx.new_page()
        page.on("pageerror", lambda exc: result["console_errors"].append(str(exc)))
        page.on("console", lambda msg: result["console_errors"].append(msg.text) if msg.type == "error" else None)
        try:
            page.goto(file_url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(500)
        except Exception as e:
            result["load_error"] = str(e)
            ctx.close(); browser.close()
            return result
        for rule in other_rules:
            try:
                ev = evaluate_rule(page, rule)
                result["rules_evaluated"].append(ev)
                if ev["passed"]:
                    result["rules_passed"] += 1
                else:
                    result["rules_failed"] += 1
                    if ev["severity"] == "high":
                        result["high_severity_failures"] += 1
            except Exception as e:
                result["rules_evaluated"].append({"rule_id": rule.get("id"), "error": str(e)[:200]})
        ctx.close()

        # viewport_overflow_check rules: separate multi-viewport context
        for rule in vp_rules:
            try:
                ev = _eval_viewport_overflow_check(browser, file_url, rule)
                result["rules_evaluated"].append(ev)
                if ev["passed"]:
                    result["rules_passed"] += 1
                else:
                    result["rules_failed"] += 1
                    if ev["severity"] == "high":
                        result["high_severity_failures"] += 1
            except Exception as e:
                result["rules_evaluated"].append({"rule_id": rule.get("id"), "error": str(e)[:200]})

        browser.close()
    return result


# ====================================================================
# Reports
# ====================================================================

def write_summary_md(results: list[dict], output_dir: Path, expected_path: Path) -> Path:
    md_path = output_dir / "layout_invariants_summary.md"
    total = len(results)
    high_fail = sum(1 for r in results if r.get("high_severity_failures", 0) > 0)
    any_fail = sum(1 for r in results if r.get("rules_failed", 0) > 0)
    lines = [
        f"# Layout Invariant Check — Summary",
        "",
        f"- Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"- Expected YAML: `{expected_path.name}`",
        f"- Files scanned: **{total}**",
        f"- Files with HIGH severity failures: **{high_fail}**",
        f"- Files with ANY failures: **{any_fail}**",
        "",
        "## File Results Table",
        "",
        "| File | High FAIL | Any FAIL | Console Err | Verdict |",
        "|---|---:|---:|---:|:---:|",
    ]
    for r in results:
        verdict = "FAIL_HIGH" if r.get("high_severity_failures", 0) else ("FAIL_LOW" if r.get("rules_failed", 0) else "PASS")
        emoji = {"FAIL_HIGH": "❌", "FAIL_LOW": "⚠️", "PASS": "✅"}[verdict]
        lines.append(f"| `{r['filename']}` | {r.get('high_severity_failures',0)} | {r.get('rules_failed',0)} | {len(r.get('console_errors',[]))} | {emoji} {verdict} |")
    lines.append("")
    # Detail per file with failures
    for r in results:
        if r.get("rules_failed", 0) == 0:
            continue
        lines.append(f"## {r['filename']} — failure detail")
        lines.append("")
        for ev in r["rules_evaluated"]:
            if ev.get("error"):
                lines.append(f"- ❗ rule `{ev.get('rule_id')}` errored: {ev['error']}")
                continue
            if ev.get("passed"):
                continue
            sev_icon = {"high": "❌", "medium": "⚠️", "low": "ℹ️"}.get(ev.get("severity", "medium"), "⚠️")
            # click_test は分母明示必須 (★cmd_184_052_pattern_b_fix 再発防止★)
            if "pass_count" in ev and "total_count" in ev:
                lines.append(f"- {sev_icon} **{ev['rule_id']}** ({ev.get('severity')}): click_pass=**{ev['pass_count']}/{ev['total_count']}** ratio={ev.get('ratio',0):.2f}")
            else:
                lines.append(f"- {sev_icon} **{ev['rule_id']}** ({ev.get('severity')}): {ev.get('diag','')}")
            for f in ev["fails"][:10]:
                if "selector" in f and "element_idx" in f:
                    lines.append(f"  - `{f['selector']}` element[{f['element_idx']}]: {'; '.join(f.get('reasons', []))}")
                elif "trigger" in f:
                    lines.append(f"  - {f['reason']}")
                elif "selector" in f:
                    lines.append(f"  - `{f['selector']}`: {f['reason']}")
                elif "idx" in f and "reason" in f:
                    t = f.get("text") or f"[{f['idx']}]"
                    lines.append(f"  - `element[{f['idx']}]` '{t[:30]}': {f.get('reason','unknown')}")
            if len(ev["fails"]) > 10:
                lines.append(f"  - ...and {len(ev['fails']) - 10} more")
        lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path


def write_per_file_json(result: dict, output_dir: Path) -> Path:
    safe_name = result["filename"].replace("/", "_")
    p = output_dir / f"layout_invariants_{safe_name}.json"
    p.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    return p


# ====================================================================
# Main
# ====================================================================

def collect_targets(args) -> list[Path]:
    targets: list[Path] = []
    if args.target_dir:
        d = Path(args.target_dir)
        targets.extend(sorted(d.glob("*.html")))
    if args.target_file:
        for f in args.target_file:
            targets.append(Path(f))
    return [t for t in targets if t.exists()]


def main():
    ap = argparse.ArgumentParser(description="Semantic Layout Invariant Checker (cmd_184_3layer_defense layer 3)")
    ap.add_argument("--target-dir", help="Directory containing *.html")
    ap.add_argument("--target-file", action="append", help="Single HTML file (can be repeated)")
    ap.add_argument("--expected", required=True, help="Expected YAML")
    ap.add_argument("--output-dir", required=True, help="Output directory for JSON/MD")
    ap.add_argument("--viewport", type=int, default=1200, help="Viewport width (default 1200)")
    args = ap.parse_args()

    expected_path = Path(args.expected)
    if not expected_path.exists():
        print(f"ERROR: --expected not found: {expected_path}", file=sys.stderr)
        sys.exit(1)
    spec = yaml.safe_load(expected_path.read_text(encoding="utf-8")) or {}
    rules = spec.get("rules", [])
    if not rules:
        print(f"ERROR: no rules in {expected_path}", file=sys.stderr)
        sys.exit(1)

    targets = collect_targets(args)
    if not targets:
        print("ERROR: no target HTML found. Use --target-dir or --target-file", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[layout_invariant_check] expected={expected_path.name} rules={len(rules)} targets={len(targets)} viewport={args.viewport}")
    results = []
    for i, t in enumerate(targets, 1):
        print(f"  [{i}/{len(targets)}] {t.name}", flush=True)
        try:
            r = analyze_file(t, rules, args.viewport)
            results.append(r)
            json_p = write_per_file_json(r, out_dir)
            verdict = "FAIL_HIGH" if r.get("high_severity_failures", 0) else ("FAIL_LOW" if r.get("rules_failed", 0) else "PASS")
            print(f"    → {verdict} (high={r.get('high_severity_failures',0)} fail={r.get('rules_failed',0)} consoleErr={len(r.get('console_errors',[]))})", flush=True)
        except Exception as e:
            print(f"    ERROR: {e}", file=sys.stderr)

    md_p = write_summary_md(results, out_dir, expected_path)
    print(f"[done] summary: {md_p}")
    print(f"       per-file JSON: {out_dir}")

    # exit code 1 if any HIGH failure
    if any(r.get("high_severity_failures", 0) > 0 for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
