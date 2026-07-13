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

Workflow Ready review candidate. The parent Apps catalog must remain `active` / `comingSoon` with version `null` and destination metadata unset until Astra review, Partner approval, and a separate Live promotion task.

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

Subscription Manager V1 is implemented as an owner-scoped FastAPI module with isolated SQLAlchemy models, Alembic migration `20260713_0001_subscription_manager`, generated OpenAPI contracts, overview metadata routing Explore to `/subscription-manager/subscriptions`, and a React workflow under `src/modules/subscription-manager`.
