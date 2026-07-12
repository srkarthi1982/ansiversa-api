# VAT Assistant UAE Story

## Purpose

VAT Assistant UAE gives UAE businesses a private workspace for organizing VAT registrations, user-entered VAT returns, VAT transactions, filing statuses, and estimate-only insights. The module exists to support preparation and review, not to provide tax, legal, accounting, audit, filing, or compliance advice.

## Workflow

The overview Explore CTA enters `/vat-assistant-uae/registrations`. Protected workflow routes are:

- `/vat-assistant-uae/registrations`
- `/vat-assistant-uae/returns`
- `/vat-assistant-uae/transactions`
- `/vat-assistant-uae/insights`

## User Journey

Users create a VAT registration for a business, add VAT return records for periods, record transactions with user-entered VAT rates and VAT amounts, then review estimate-only summaries by period and rate. The app keeps the official filing boundary visible so users verify requirements through the UAE Federal Tax Authority, EmaraTax, and qualified professionals.

## Database Design

The module uses an isolated database configured by `VAT_ASSISTANT_UAE_DATABASE_URL`. It owns:

- `VATRegistrations`
- `VATReturns`
- `VATTransactions`

Records are owner-scoped by `userId`. Returns and transactions reference registrations through `registrationId`; transactions may optionally reference a return through `returnId`. SQLAlchemy relationships use cascade delete from registration to returns and transactions. Indexes support owner lists, status/type filters, registration lookups, filing due dates, VAT period filters, transaction type/rate filters, transaction dates, and updated-at sorting.

## API Design

The router is mounted at `/api/v1/vat-assistant-uae`. It exposes protected endpoints for dashboard summary, registration CRUD and duplicate, return CRUD and duplicate, and transaction CRUD and duplicate. List responses return lightweight summaries and previews. Detail responses return full notes for edit drawers. Return and transaction update payloads intentionally exclude create-only `registrationId`.

## Shared Components Used

The frontend uses the Ansiversa protected workspace pattern with shared page headers, stat grids, empty states, inline feedback, pagination, confirm dialogs, record actions, and form drawers.

## Performance Considerations

The first release keeps payloads compact, avoids document storage, and groups dashboard calculations from owner-scoped lists. Indexes are aligned with user-facing filters and dashboard queries rather than speculative search.

## Current Status

Workflow Ready. VAT Assistant UAE remains `active` / `comingSoon` with version `null`; destination metadata remains null. A read-only remote-state audit confirmed the production-configured isolated database was accidentally migrated early to Alembic head `20260712_0001_vat_assistant_uae` with empty starting tables. It is not promoted to Live.

## Known Limitations

- No official FTA filing or EmaraTax submission.
- No VAT advice, eligibility determination, or compliance guarantee.
- No document attachments.
- No adviser collaboration.
- No currency conversion or FX normalization.
- VAT outputs are estimate-only and depend on user-entered records.

## Future Enhancements

- Document attachments.
- Exportable VAT schedules.
- Adviser review workflow.
- Audit trail.
- Multi-entity grouping.
- Official-reference links.
- Optional import workflows after governance review.

## Current Implementation

The backend implements isolated SQLAlchemy models, Alembic migration `20260712_0001_vat_assistant_uae`, schemas, repository/service layer, owner isolation, stable operation IDs, dashboard summaries, and overview metadata. The app preserves clear product safety boundaries across documentation, API summaries, and frontend copy.
