# Corporate Tax UAE Story

## Purpose

Corporate Tax UAE gives UAE businesses a private workspace for organizing corporate-tax-related periods, user-entered adjustments, obligations, assumptions, and estimate-only insights. The module exists to support preparation and review, not to provide tax, legal, accounting, audit, filing, or compliance advice.

## Workflow

The overview Explore CTA enters `/corporate-tax-uae/tax-periods`. Protected workflow routes are:

- `/corporate-tax-uae/tax-periods`
- `/corporate-tax-uae/adjustments`
- `/corporate-tax-uae/obligations`
- `/corporate-tax-uae/insights`

## User Journey

Users create tax periods for an entity and financial year, add user-entered taxable-income adjustments, track obligations and deadlines, then review estimate-only insights. Each calculation shows its basis and assumptions so users can verify records with the UAE Federal Tax Authority and qualified professionals.

## Database Design

The module uses an isolated database configured by `CORPORATE_TAX_UAE_DATABASE_URL`. It owns:

- `CorporateTaxPeriods`
- `CorporateTaxAdjustments`
- `CorporateTaxObligations`

Records are owner-scoped by `userId`. Adjustments and obligations reference periods through `periodId` and use cascade delete behavior through SQLAlchemy relationships. Indexes support owner lists, status/year filters, period lookups, category/status filters, due-date queries, and updated-at sorting.

## API Design

The router is mounted at `/api/v1/corporate-tax-uae`. It exposes protected endpoints for dashboard summary, period CRUD, duplicate period, adjustment CRUD, obligation CRUD, and local mark-completed. List responses return lightweight summaries and previews. Detail responses return full notes/explanations for edit drawers. Adjustment and obligation update payloads intentionally exclude create-only `periodId`.

## Shared Components Used

The frontend uses the Ansiversa protected workspace pattern with shared page headers, stat grids, empty states, inline feedback, pagination, confirm dialogs, record actions, and Zustand state.

## Performance Considerations

The first release keeps payloads compact, avoids large document storage, and groups dashboard calculations from owner-scoped lists. Indexes are aligned with user-facing filters and dashboard queries rather than speculative search.

## Current Status

Workflow Ready. Corporate Tax UAE remains `active` / `comingSoon` with version `null`. It is not promoted to Live.

## Known Limitations

- No filing, FTA integration, or official submission workflow.
- No document attachments.
- No adviser collaboration.
- No currency conversion or FX normalization.
- Tax outputs are estimates only and depend on user-entered records and assumptions.

## Future Enhancements

- Document attachments.
- Exportable schedules.
- Adviser collaboration.
- Audit trail.
- Multi-entity management.
- Configurable assumption library.
- Official-reference links.

## Current Implementation

The backend implements isolated SQLAlchemy models, Alembic migration, schemas, repository/service layer, owner isolation, stable operation IDs, defensive estimate calculations, and overview metadata. The app preserves clear product safety boundaries across documentation, API summaries, and frontend copy.
