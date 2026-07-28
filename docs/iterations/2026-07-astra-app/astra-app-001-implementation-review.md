# ASTRA-APP-001 Implementation Review

## Implementation Summary

ASTRA-APP-001 adds `app.modules.subscription_manager.astra_read_capabilities` as the Subscription Manager-owned read adapter for governed Astra questions.

The adapter provides fixed, versioned capabilities for counts, active lists, highest normalized cost by currency, raw recurring totals by currency and frequency, monthly estimates by currency, renewal windows, overdue renewals, and category grouping.

The correction pass adds an app-owned exact-object read grant. Certified Astra `authorized_metadata_only` references are retained only as supporting metadata; they do not authorize repository retrieval by themselves.

## Files

- `app/modules/subscription_manager/astra_read_capabilities.py`
- `tests/test_subscription_manager_astra_read_capabilities.py`
- `validation/astra_app_001/cli.py`
- `validation/astra_app_001/runner.py`
- `docs/iterations/2026-07-astra-app/00-iteration-overview.md`
- `docs/iterations/2026-07-astra-app/tasks/astra-app-001-subscription-manager-governed-read-capability.md`
- `docs/iterations/2026-07-astra-app/astra-app-001-implementation-review.md`
- `docs/iterations/2026-07-astra-app/astra-app-001-requirement-traceability.md`
- `app/modules/subscription_manager/story.md`
- `AGENTS.md`

## Boundaries Preserved

- No frontend changes.
- No API route changes.
- No database schema changes.
- No migrations.
- No provider or model invocation.
- No generalized tool executor.
- No raw SQL or generated SQL.
- No mutation path.
- No production activation.

## Authority Boundary

`SubscriptionAstraReadRequest` carries caller-supplied metadata and supporting Astra authorization metadata.

`SubscriptionAstraReadGrant` is the app-owned execution authority. It is issued only by the Subscription Manager grant issuer, validates by exact object identity, binds to the authenticated user and request shape, expires, and is consumed on execution.

Execution validates grants against an authoritative execution timestamp from the app-owned UTC clock. Production code has no deterministic clock factory, trusted test-clock registry, or caller-selectable execution timestamp. Deterministic local tests patch the private app-owned clock inside the isolated test process. Direct requests, caller-created grants, copied grants, reconstructed grants, tampered grants, foreign issuers, expired grants, execution before issuance, naive app-clock timestamps, reused grants, ordinary timestamp overrides, and principal mismatches are rejected before repository reads.

## Runtime Integration Reachability

The certified Runtime cannot currently execute the app-owned read adapter without a separately authorized read executor. ASTRA-APP-001 does not bypass this. The app adapter can be called by focused tests and local validation only.

## Evidence Integration

No app-read evidence sink type is certified. The implementation does not write fabricated evidence. Evidence integration remains pending a future certified evidence contract.

## Known Review Items

- Subscription Manager is App #071. Earlier ASTRA-APP-001 authorization text used App #063 by mistake; ASTRA-APP-001 docs now use App #071 without catalog or production metadata changes.
- `SubscriptionManagerSubscriptions.nextBillingDate` is stored as a string. The adapter uses deterministic ISO-prefix parsing and excludes invalid or missing dates from renewal windows.
- Subscription Manager has no archive flag. Deleted records are absent by existing delete behavior.

## Validation Snapshot

Focused ASTRA-APP-001 tests passed:

```text
20 passed
```

Local validation CLI scenarios passed:

```text
30 scenarios reported passed
```
