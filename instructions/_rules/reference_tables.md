# Reference Tables

## Language Naming Convention Quick Reference

| Language | Classes / Types | Methods / Functions | Variables | Constants |
|----------|----------------|--------------------|-----------|-----------|
| C# | PascalCase | PascalCase | camelCase | UPPER_SNAKE or PascalCase |
| PHP | PascalCase | camelCase | $camelCase | UPPER_SNAKE |
| HTML/CSS | — | — | kebab-case (classes/ids) | — |
| SCSS | — | kebab-case (mixins) | $kebab-case | $UPPER_SNAKE |
| C/C++ | PascalCase | snake_case or camelCase | snake_case | UPPER_SNAKE |
| JavaScript/TS | PascalCase | camelCase | camelCase | UPPER_SNAKE |
| Python | PascalCase | snake_case | snake_case | UPPER_SNAKE |

Always defer to the project's existing conventions.

## Flat Config Rule (Mandatory for New Projects)

Config YAML files MUST use **flat keys only (no nesting)** for new projects. Flat keys are greppable, raise `KeyError` immediately on typo, and eliminate `.get().get()` chains.

| Pattern | Example | Allowed? |
|---------|---------|----------|
| Flat key | `db_path: "data/app.db"` | Yes |
| 1-level nest | `database:\n  path: "data/app.db"` | No (for new projects) |
| Accessor module | `config_schema.get_db_path(settings)` | Yes (if nesting needed) |

- If nesting is truly needed, create a `config_schema.py` accessor module. No direct `config['key']['subkey']` access.
- Applies to **new projects only**. Do not refactor existing config files.
- Self-check: `grep -E "config\[|settings\.get|settings\[" ` in your code before submitting.

## Hypothesis Challenge Rule (Bug Diagnosis)

When diagnosing bugs, workers MUST list at least 2 alternative hypotheses before committing to one.

### Procedure
1. Receive bug report with initial hypothesis
2. Before investigating, list alternatives: What else could cause this symptom? Is the hypothesis testable?
3. Document your differential diagnosis in the report
4. Test hypotheses in order of likelihood
5. VERIFY THE OUTCOME (symptom resolved), not just the ACTION (change applied)
