# Expense Tracker Story

## Purpose

Expense Tracker records what a signed-in user spent. The module is intentionally focused on expense tracking, not budgeting, forecasting, or planning.

## Workflow

The backend supports the approved V1 workflow:

```text
Overview
  -> Expenses
  -> Categories
  -> History
  -> Insights
```

Protected API routes sit under `/api/v1/expense-tracker`.

## User Journey

Users create expense records with title, amount, currency, date, payment method, optional category, merchant, and notes. They can edit, delete, duplicate, search, and filter expenses. Categories are user-managed records used to organize spending. History records lifecycle events, and insights summarize the current workspace.

## Database Design

The module uses an isolated database connection configured by `EXPENSE_TRACKER_DATABASE_URL` and an isolated Alembic version table, `expense_tracker_alembic_version`.

Tables:

- `ExpenseTrackerExpenses`
- `ExpenseTrackerCategories`
- `ExpenseTrackerHistory`

Expenses and categories are owner-scoped through `ownerId`. History is also owner-scoped and stores enough denormalized context to remain readable after an expense or category is deleted.

Indexes are based on the V1 query patterns: owner-scoped lists, expense date sorting, category filters, currency filters, payment method filters, and history timelines.

## API Design

The API exposes dashboard, expense, category, and history endpoints. List and dashboard responses return lightweight summary models with note previews. Detail endpoints return full notes for edit drawers.

Update payloads are separate from create payloads. Category deletion detaches expenses instead of deleting spending records.

## Shared Components Used

Backend code follows the existing Ansiversa FastAPI, SQLAlchemy, Alembic, and auth dependency patterns. No shared platform redesign was introduced.

## Performance Considerations

Dashboard data is intentionally small: expenses, categories, recent history, and computed summaries. History is limited to the latest 100 events. Large text fields are previewed outside detail endpoints.

## Current Status

Workflow Ready for App #053 review. The module is not promoted to Live.

## Known Limitations

- No currency conversion or exchange-rate normalization.
- No budgeting, budget limits, alerts, forecasting, or recurring expense automation.
- Category totals group recorded amounts by category and currency context but do not perform financial reconciliation.

## Future Enhancements

- Optional recurring expense templates.
- Export support.
- Currency-aware reporting if approved.
- Attachments or receipt metadata if approved.

## Current Implementation

Expense Tracker is a DB-backed mini-app module with owner-scoped CRUD APIs, isolated migration files, lightweight response schemas, history preservation, and local dashboard summary calculation.

