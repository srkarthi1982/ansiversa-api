# ASTRA-IMP-008 Implementation Review

Status: implementation direction approved; source-review corrections applied and pending Astra re-review. Production authorization is not approved; production is unchanged.

The diff adds `planning.py`, focused tests, documentation, and the narrow Runtime Core registration/interface/health extension required by authorization. Certified configuration, governance, evidence, conversation, and discovery behavior is reused without weakening. Frozen constitutional and ASTRA-IR-001 documents are unchanged.

| Check | Pass | Failure |
|---|---|---|
| Runtime | ready owner | reject |
| Conversation | current, owned, same runtime, eligible | reject |
| Authority | owner-issued context | reject |
| Graph | contiguous, unique, backward-only, bounded | reject pre-commit |
| Capability | discovered, available, metadata-only | reject |
| Governance | ALLOW | proposal |
| Governance | non-ALLOW | mapped status, no steps |
| Evidence | appended | release |
| Evidence | failed | no plan/sequence advance |

## Astra source-review corrections

1. Plan-governance evidence is appended through Runtime Core immediately after evaluation and before either allowed or blocked plan preparation. Returned evidence references match stored discovery, plan-governance, and planning records in deterministic order. Governance-evidence or planning-evidence append failure returns no plan and does not advance the successful planning sequence.
2. Conversation structural health begins unbound and degraded. A certified engine is bound only after same-runtime ownership, current snapshot, matching reference, and lifecycle validation. Invalid/foreign dependencies do not satisfy health; stopped runtime health is stopped and payload-free.

No APIs, routes, databases, migrations, providers, keys, prompts, models, Tool Executor, execution bridge, handlers, app mutation, frontend, deployment, production activation, memory, vectors, learning, or ASTRA-IMP-009.

## Validation record

- Focused planning plus Runtime/Conversation/Discovery after corrections: 107 passed.
- IMP-001 through IMP-007 selection with corrected planning suite: 192 passed, 29 subtests passed, with two pre-existing isolated import-order failures in legacy audit mocks.
- Backend compile/import: planning and runtime compile; all `app/modules/astra_ai` compile.
- Assistant/User Context/Tool Registry and full repository suites: unavailable at collection because the existing environment lacks `libsql_experimental`.
- Ruff and Black: unavailable in the repository virtual environment.
- `git diff --check`: passed.
- Unauthorized planning source-surface scan: passed.
- Frozen ASTRA-001 through ASTRA-010 and ASTRA-IR-001 files: unchanged.

Local tests use `APP_ENV=local` because the ignored `.env` has an empty value that certified configuration correctly rejects.
