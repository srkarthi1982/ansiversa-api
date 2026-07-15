# Symptom Journal Story

## Purpose

Symptom Journal exists so users can keep structured personal records of health observations over time. It is a memory and organization tool, not a medical decision system.

## Workflow

Users create categories, add symptom entries, review recent and recurring observations, archive or restore entries, and delete records when needed.

## User Journey

The user opens `/symptom-journal/entries`, records date, time, title, category, severity, duration, body location, mood, optional temperature, triggers, relief methods, notes, and follow-up notes, then reviews summaries in Insights.

## Database Design

The module owns an isolated database configured by `SYMPTOM_JOURNAL_DATABASE_URL`.

Tables:

- `SymptomCategories`
- `SymptomEntries`

The Alembic version table is `symptom_journal_alembic_version`.

## API Design

The API prefix is `/api/v1/symptom-journal`.

Routes cover dashboard, insights, category CRUD, entry CRUD, archive, restore, delete, and paginated entry search/filter/sort.

## Shared Components Used

The frontend uses the shared authenticated page wrapper, API client, store helpers, overview page, cards, inputs, and app shell routing.

## Performance Considerations

Indexes cover owner queries, category filtering, date sorting, severity filters, archive filters, title scans, body-location filters, created dates, and updated dates.

## Current Status

Approved live at version `1.0.0` after Astra review, Partner approval, production-configured isolated database migration verification, backend database-authentication fix verification, production Apps row promotion, overview metadata sync, and manual browser workflow verification. Destination metadata is synced at `20 / 100`, status `approved`, reviewed on `2026-07-15`.

## Known Limitations

V1 has no exports, attachments, sharing, AI summaries, clinical integrations, reminders, or emergency support.

## Future Enhancements

Possible future improvements include export, print-friendly appointment summaries, optional reminders, and richer charts after approval.

## Current Implementation

The production catalog row is `active` / `live` / `1.0.0`. The implementation provides owner-scoped FastAPI endpoints, SQLAlchemy models, Pydantic validation, default categories, Alembic migration, React routes, typed API integration, Zustand state, and readiness documentation.
