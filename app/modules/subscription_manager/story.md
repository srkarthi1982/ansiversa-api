# Subscription Manager Story

## Purpose

Subscription Manager is App #071 in Ansiversa. It provides a private workspace for organizing user-entered subscription records, categories, renewal history, and spending summaries.

V1 is intentionally not a payment processor, bank or card connector, automatic cancellation service, inbox scanner, receipt ingestion tool, foreign-exchange calculator, tax tool, or provider-integrated subscription broker.

## Workflow

The protected workflow is:

```text
Overview
→ Subscriptions
→ Categories
→ Renewals
→ Insights
```

The overview Explore CTA enters `/subscription-manager/subscriptions`.

## User Journey

A signed-in user creates categories, then creates subscription records with provider, amount, currency, billing frequency, status, next billing date, payment method notes, auto-renew setting, cancellation notice days, website/reference details, and private notes. The user records renewals manually when a subscription is reviewed, paid, skipped, or cancelled. Insights summarize only records the user entered.

## Database Design

The module owns an isolated database configured by `SUBSCRIPTION_MANAGER_DATABASE_URL`.

Tables:

- `SubscriptionManagerCategories`
- `SubscriptionManagerSubscriptions`
- `SubscriptionManagerRenewals`

Important constraints:

- Unique owner plus category name.
- Unique owner plus subscription provider plus subscription name.
- Unique owner plus subscription plus renewal date.
- Foreign keys from subscriptions to categories and renewals to subscriptions.
- Subscription deletion cascades dependent renewal rows.
- Category deletion is blocked by the service when subscriptions still use the category.

Indexes are based on owner-scoped list, updated-at sorting, category filters, status filters, frequency filters, next billing date review, subscription lookup, renewal date history, and dashboard query patterns.

## API Design

Routes live under `/api/v1/subscription-manager`.

The API provides:

- Dashboard summary endpoint.
- Category CRUD endpoints.
- Subscription CRUD, duplicate, pause, and cancel endpoints.
- Renewal CRUD endpoints.

List and dashboard responses return lightweight summaries and note previews. Detail endpoints return the full editable note fields. Update payloads are separate from create payloads. Category reassignment is supported by subscription update and is verified against the current owner before saving.

All queries are owner-scoped through the authenticated user. The service verifies that category, subscription, and renewal IDs belong to the current owner before linking or mutating records.

## Astra Read Capability Design

Subscription Manager owns an app-local Astra read capability adapter in `astra_read_capabilities.py`. The adapter is read-only, backend-only, and not exposed as an API route or chat surface.

The capability catalog is fixed and versioned. It supports authenticated-user questions for subscription counts, active subscription lists, highest normalized recurring cost grouped by currency, raw recurring totals grouped by currency and billing frequency, monthly estimates grouped by currency, renewal windows, overdue renewals, and category grouping.

The adapter reuses Subscription Manager ownership and calculation semantics. Certified Astra read-authorization metadata is supporting metadata only; repository reads require an app-owned, exact-object Subscription Manager read grant issued by the module's private grant issuer. Records are loaded through the owner-scoped repository using the authenticated backend user, then rechecked so every returned subscription has `owner_id` equal to the authenticated user ID. Caller-supplied user IDs, caller-created grants, copied grants, tampered grants, reused grants, arbitrary SQL, arbitrary filters, unsupported parameters, excessive result limits, stale authorization references, foreign app scopes, and mutation surfaces are rejected.

Currency totals are grouped by currency code and never converted. Highest-cost answers choose one deterministic record within each currency instead of comparing numeric amounts across currencies. Raw recurring totals preserve billing-frequency buckets, while monthly estimates use the app's documented normalization. Renewal windows use an injected observed timestamp and deterministic ISO-date parsing of `next_billing_date`. Missing or invalid renewal dates are excluded from renewal-window answers.

## Shared Components Used

The frontend uses established Ansiversa shared components:

- `AvAppOverviewPage`
- `AvAuthenticatedPageState`
- `AvPageHeader`
- `AvCardEmptyState`
- `AvInlineFeedback`
- `AvPagination`
- `AvRecordActions`
- `AvFormDrawer`
- `useAvConfirmDialog`

State is managed through a module-local Zustand store.

## Performance Considerations

The dashboard payload seeds the V1 workflow with summary arrays and aggregate insight data. Large note fields are kept out of list responses by returning previews. Detail endpoints are used before edit drawers populate full records. Currency totals are separated by currency code instead of converted, avoiding inaccurate exchange-rate assumptions.

## Current Status

Approved live at version `1.0.0`. The parent Apps catalog stores Subscription Manager as `active` / `live` with destination progress `20 / 100`, destination status `approved`, and destination reviewed date `2026-07-13`. The production-configured isolated database migration is verified at Alembic head `20260713_0001_subscription_manager`.

## Known Limitations

- No payment processing.
- No bank or card connections.
- No automatic cancellation.
- No inbox scanning or receipt ingestion.
- No foreign-exchange conversion.
- No provider integrations.
- No shared household roles.
- No reminder delivery.
- No imports, exports, or attachments.

## Future Enhancements

Potential future directions include renewal calendars, reminder scheduling, shared household views, cancellation checklist notes, attachment references, CSV import/export, trial-end review flows, price-change history, category budgets, audit trail, and role-aware shared access.

## Current Implementation

Subscription Manager V1 is implemented as an owner-scoped FastAPI module with isolated SQLAlchemy models, Alembic migration `20260713_0001_subscription_manager`, generated OpenAPI contracts, overview metadata routing Explore to `/subscription-manager/subscriptions`, a React workflow under `src/modules/subscription-manager`, and an app-owned ASTRA-APP-001 read-only capability adapter for local governed validation.
