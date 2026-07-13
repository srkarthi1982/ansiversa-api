# Subscription Manager Destination

## Document Status

Approved for Live promotion on 2026-07-13 after Astra review, Partner approval, production migration verification, and manual browser verification.

## Destination Status

Approved v1.0

## Destination

Subscription Manager should mature into a private subscription-control workspace for people who want visibility over recurring services before they are surprised by renewals or fragmented monthly spend.

The destination is always `100 / 100`. The current approved Journey Progress is `20 / 100`.

## Product Identity

Subscription Manager is for:

- Individuals tracking recurring personal subscriptions.
- Families reviewing shared household services.
- Freelancers and small business owners tracking software and service renewals.
- Users replacing scattered notes, spreadsheets, and memory-based renewal tracking.

It is not a payment processor, bank connection tool, card-management product, automatic cancellation service, receipt parser, inbox scanner, tax tool, or foreign-exchange calculator.

## Mature Workflow

The mature product may expand from:

```text
Subscriptions
→ Categories
→ Renewals
→ Insights
```

Toward:

```text
Subscriptions
→ Categories
→ Renewal Calendar
→ Renewal Decisions
→ Shared Household View
→ Documents
→ Alerts
→ Spending Plans
→ Insights
```

Only approved future scope should be implemented.

## Journey Progress

Current Position: 20 / 100

Current Journey Progress: 20 / 100

V1 establishes the manual record foundation across Subscriptions, Categories, Renewals, and Insights while intentionally deferring payment collection, bank/card connections, automatic cancellation, inbox scanning, receipt ingestion, provider integrations, reminder delivery, imports, exports, and shared household roles.

## Destination Capabilities

Potential future capabilities:

- Renewal calendar view.
- Reminder scheduling.
- Shared household grouping.
- Cancellation checklist notes.
- Document attachment references.
- CSV import/export.
- Trial-end review workflow.
- Price-change history.
- Budget targets by category.
- Audit trail.
- Role-aware shared access.

## Current V1 Boundary

V1 includes:

- Subscription CRUD.
- Category CRUD.
- Manual renewal CRUD.
- Duplicate subscription action.
- Pause/cancel status actions.
- Currency-separated spending summaries.
- Operational insights from stored records.

V1 excludes:

- Payment collection.
- Bank or card connections.
- Automatic third-party cancellation.
- Email inbox scanning.
- Receipt ingestion.
- Foreign-exchange conversion.
- Provider API integrations.
- Tax or accounting advice.

## Governance Notes

Astra: Approved on 2026-07-13.

Partner: Approved Subscription Manager live promotion after manual workflow verification.

Codex: Ran production-configured isolated database migration, verified schema/indexes/foreign keys, synced overview metadata, and prepared live promotion metadata.
