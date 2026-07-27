# ASTRA-VAL-001 — Certified Fail-Closed Integration Verification

Status: Certified / Approved.

## Purpose and architecture

ASTRA-VAL-001 is a local/test-only validation package under `validation/astra_val_001`. It imports certified Astra components, but application startup never imports it. A single deterministic runner serves pytest and a thin CLI.

The harness proves the current certified truth:

```text
authoritative configuration disabled
→ Governance Kernel FAIL_CLOSED
→ intent invalid
→ planning non-actionable/governance-blocked
→ read authorization unavailable
```

`successful_path_available` is always `false`; `unavailability_reason` is always `certified_governance_disabled_fail_closed`. This is a verified invariant, not a failed scenario.

## Result and output contract

`AstraValidationScenarioResult` is immutable and bounded. It records scenario identity/group, expected and actual outcomes, pass state, structural stage statuses, evidence/lifecycle results, the successful-path invariant, and fixed operational boundary states. It contains no conversation content, user/tenant/app records, credentials, prompts, provider payloads, hidden reasoning, SQL, or database results.

Text and stable, key-sorted JSON are representations of the same result. Reports go only to stdout; errors go to stderr. No report is persisted or tracked.

## Evidence verification

The integrated scenario resolves every returned intent and plan evidence reference against the in-memory Evidence Sink. The capacity-failure scenario proves no successful conversation operation is released when evidence append cannot complete. Evidence remains bounded metadata from certified components.

## Lifecycle and health

Runtime starts through its certified lifecycle. Previously obtained interfaces fail after shutdown. Read-authorization health remains degraded because the certified registry and authority issuers are unavailable; direct engine health is stopped after shutdown.

## Permanent boundaries

Every result fixes:

```text
database_connection_state  not_authorized
sql_execution_state        not_authorized
data_retrieval_state       not_performed
data_mutation_state        prohibited
schema_mutation_state      prohibited
production_read_state      not_approved
production_state           unchanged
```

There is no governance monkeypatch, configuration override, private-registry mutation, fabricated downstream object, successful fixture authority, API, route, frontend, database, SQL, ORM, provider, model, prompt, Tool Executor, deployment, or production integration.

## CLI contract

```text
python -m validation.astra_val_001.cli --list
python -m validation.astra_val_001.cli --scenario certified_default_fail_closed
python -m validation.astra_val_001.cli --scenario certified_default_fail_closed --format json
python -m validation.astra_val_001.cli --all --format text
```

Exit codes: `0` expectations passed, `1` expectation failed, `2` invalid CLI use, `3` setup failure.

Successful non-production governance evaluation requires a separately designed and authorized authority phase. It is not part of ASTRA-VAL-001.
