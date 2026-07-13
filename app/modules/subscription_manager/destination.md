# Subscription Manager Destination

## Document Status

Draft prepared for App #071 Workflow Ready development. Not approved for Live promotion.

## Destination Status

Draft

## Destination

Subscription Manager should mature into a private subscription-control workspace for people who want visibility over recurring services before they are surprised by renewals or fragmented monthly spend.

The destination is always `100 / 100`. The current Journey Progress is unapproved until Astra review and Partner approval.

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

Current Position: Unapproved

Current Journey Progress: Unapproved

V1 establishes the manual record foundation across Subscriptions, Categories, Renewals, and Insights. Journey Progress must be set only after approval.

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

Astra: Pending review.

Partner: Pending approval.

Codex: Implements Workflow Ready V1 only and must not promote Subscription Manager to Live without approval.
