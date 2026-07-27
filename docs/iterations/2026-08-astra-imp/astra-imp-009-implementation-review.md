# ASTRA-IMP-009 Implementation Review

Status: implemented; pending Astra source review. Production is unchanged and not approved.

| Boundary | Enforcement |
|---|---|
| Meaning | declared bounded signal only; never raw-text inference |
| Conversation | current, fresh, owned, same runtime, eligible lifecycle |
| Capability | governed Discovery result, exact ID match, available status |
| Governance | deterministic mapping; fail closed invalid |
| Planning | eligibility boolean only; no planning operation |
| Authority | execution always not authorized; production not approved |
| Evidence | governance then intent evidence before release |
| Health | structural dependencies only; unbound is degraded |

Focused tests cover registration/shutdown, deterministic resolution, immutable contracts, current-turn/stale/foreign rejection, ambiguity, unsupported signals, governance mapping, planning-eligibility boundary, evidence failure, health, and prohibited fields. No Tool Registry or executable handler is imported.

## Validation record

- Focused intent plus Runtime: 41 passed.
- Intent/Planning/Runtime/Conversation/Discovery: 120 passed.
- IMP-001 through IMP-009 selection: 205 passed and 29 subtests passed; two pre-existing isolated legacy audit-mock import-order failures remain.
- Compileall, `git diff --check`, forbidden-surface scan, and frozen-parent verification passed.
- Ruff and Black are unavailable in the repository virtual environment.
- Database-backed full repository and Assistant regressions remain unavailable because `libsql_experimental` is missing.
