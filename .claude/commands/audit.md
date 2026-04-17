---
description: Run neko system audit (skills + self-audit orphan/dup/dead rules)
---

# /audit

猫システムの棚卸しを一括実行する。

## 実行内容

1. `scripts/audit-skills.sh` を実行して `logs/audit_skills_YYYY-MM-DD.md` を生成
2. `instructions/_rules/self_audit.md` の checklist を参照しながら:
   - orphan scripts 検出
   - rule duplication check
   - dead rules 検出
   - policy bloat (800 行超) 検出
3. 結果を `logs/audit_YYYY-MM-DD.md` にまとめる
4. 親分に「action_items (自動実行可) と escalate (goshujinsama 承認必要)」を報告

## 使い方

```
/audit
```

## 注意

- 低リスク action (0 reference orphan 削除等) は親分自走可
- 高リスク action (policy file split / skill archive) は goshujinsama エスカレ
