# ASTRA-APP-001 Subscription Manager Governed Read Capability

## Purpose

Create a production-quality, app-owned, read-only capability foundation that allows deterministic retrieval of authenticated-user Subscription Manager data through fixed named capabilities.

## Ownership Boundary

Astra asks for a named capability.

Subscription Manager owns the read adapter, repository access, owner enforcement, field selection, aggregation, limits, currency semantics, date semantics, sensitivity classification, and returned structured result.

Astra does not own Subscription Manager SQL, ORM queries, database credentials, calculations, or data-access rules.

## Capability Catalog

- `subscription.count_all`
- `subscription.count_active`
- `subscription.list_active`
- `subscription.highest_cost`
- `subscription.total_recurring_cost`
- `subscription.monthly_cost_estimate`
- `subscription.renewing_this_month`
- `subscription.renewing_within_days`
- `subscription.overdue_renewals`
- `subscription.group_by_category`

All capabilities are fixed at version `1.0.0`, app-owned by `subscription_manager`, and bounded to a maximum result limit of 50.

## Request Contract

The request contract is metadata only. It requires:

- capability ID and version
- app identity `subscription_manager`
- request reference
- requested maximum result count
- authorization reference
- declared purpose
- timezone-aware observed timestamp
- allowed parameters only
- optional plan reference

Caller-supplied user IDs are rejected. Ownership must come from the authenticated backend user object.

## App-Owned Read Grant Contract

The certified Astra `authorized_metadata_only` reference is not treated as permission to retrieve data.

Actual app read execution requires a `SubscriptionAstraReadGrant` issued by the private Subscription Manager grant issuer. The grant binds:

- exact authenticated user identity
- capability ID and version
- app scope
- request reference
- exact permitted parameters
- maximum result count
- purpose
- issuance and expiry
- corresponding Astra authorization metadata reference
- production state `not_approved`

The adapter rejects caller-created, copied, reconstructed, modified, foreign, expired, reused, or principal-mismatched grants. A grant is consumed during execution and cannot be used again.

Grant expiry is validated against the actual execution timestamp, not the request's historical observed timestamp. Production execution uses an app-owned UTC clock. Production code has no deterministic clock factory, trusted test-clock registry, or caller-selectable execution timestamp. Focused tests patch the private app-owned clock inside the isolated test process. Execution before grant issuance, before request observation, exactly at expiry, after expiry, with an ordinary caller timestamp override, or with a naive app-clock timestamp is rejected before repository access.

## Result Contract

Every result includes:

- capability ID and version
- status
- result kind
- bounded records
- deterministic summary
- calculation basis
- record and returned counts
- truncation flag
- reason codes
- observed timestamp
- app scope
- user scope state
- authorization state
- production authorization state

Results never return ORM objects, sessions, credentials, raw SQL, stack traces, deleted rows, or unrestricted metadata.

## Read-Only Enforcement

The adapter uses only existing owner-scoped list repository behavior. It exposes no create, update, delete, duplicate, pause, cancel, commit, flush, merge, DDL, SQL, or arbitrary filter surface.

A mutation-surface scan is available through `mutation_surface_report()`.

## Currency And Cost Semantics

Totals are grouped by currency. The adapter does not perform FX conversion and does not silently combine currencies.

`subscription.highest_cost` returns `highest_cost_by_currency` and chooses one deterministic highest-cost subscription inside each currency only. It does not compare numeric values across currencies.

`subscription.total_recurring_cost` returns raw recurring commitments grouped by currency and billing frequency. Incompatible frequencies are not added together.

`subscription.monthly_cost_estimate` returns normalized monthly and annual estimates grouped by currency.

Monthly normalization follows current Subscription Manager service semantics:

- weekly: `amount * 52 / 12`
- monthly: `amount`
- quarterly: `amount / 3`
- semiannual: `amount / 6`
- annual: `amount / 12`
- custom: `amount`

Amounts are rounded to two decimal places using decimal half-up rounding in the read result.

## Renewal Semantics

Renewal windows use an injected timezone-aware `observed_at` timestamp. The adapter parses the ISO date prefix of `next_billing_date`.

`renewing_this_month` returns active subscriptions with renewal dates on or after `observed_at.date()` in the same month.

`renewing_within_days` includes the observed date through the inclusive end date. Exactly 30 days is included when `days = 30`; 31 days is excluded.

`overdue_renewals` returns active subscriptions with parsed renewal dates before `observed_at.date()`.

Missing or invalid renewal dates are excluded from date-window lists.

## Privacy Model

The only user scope accepted by the adapter is the authenticated backend user. Each repository result is verified so `record.owner_id == authenticated_user.id` before any structured answer is released.

## Threat Model

Rejected surfaces:

- unauthenticated owner
- caller-supplied user ID
- foreign app scope
- caller-created or copied read grant
- reconstructed or tampered read grant
- foreign read grant issuer
- caller-supplied execution clock or timestamp
- reused read grant
- principal mismatch between grant metadata and authenticated user
- unsupported capability
- unsupported parameter
- duplicate parameter
- excessive limit
- stale or expired authorization
- expired app-owned read grant
- execution before grant issuance or request observation
- naive execution timestamp
- grant execution exactly at or after expiry
- disabled or non-authorized authorization state
- raw SQL
- arbitrary table, column, predicate, expression, aggregation, or sort field
- mutation methods

## Evidence Integration Status

No certified app-read evidence type exists for ASTRA-APP-001. The adapter remains app-owned and observational. It does not write fabricated evidence into the Astra Evidence Sink.

## Runtime Integration Status

Full certified Runtime read execution is unavailable because ASTRA-READ-EXEC-001 is not authorized and no certified read executor exists. The app capability is ready for future connection through a separately approved executor that consumes certified read authorization decisions.

## Validation

Focused tests:

```text
.venv/bin/python -m pytest tests/test_subscription_manager_astra_read_capabilities.py -q
```

Local scenarios:

```text
.venv/bin/python -m validation.astra_app_001.cli --list
.venv/bin/python -m validation.astra_app_001.cli --scenario count_active
.venv/bin/python -m validation.astra_app_001.cli --scenario renewals_next_30_days --format json
.venv/bin/python -m validation.astra_app_001.cli --all --format text
```
