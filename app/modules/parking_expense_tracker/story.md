# Parking Expense Tracker Story

## Purpose

Parking Expense Tracker helps authenticated Ansiversa users keep private records of recurring parking spend. It focuses on expenses, reusable locations, vehicles, payment methods, and monthly cost visibility. It is not a parking reservation marketplace, payment processor, receipt forwarding system, reimbursement approval workflow, or official tax/compliance product.

## Workflow

The overview Explore CTA enters `/parking-expense-tracker/expenses`. The protected workflow routes are:

- `/parking-expense-tracker/expenses`
- `/parking-expense-tracker/locations`
- `/parking-expense-tracker/insights`

## User Journey

Users create parking locations for repeated places such as office buildings, malls, airports, street parking, and other destinations. They then create parking expenses with date, start time, end time, calculated or entered duration, amount, currency, payment method, vehicle, purpose, and notes. Expenses can be searched, filtered by vehicle, payment method, and date range, edited, and deleted with confirmation. Insights summarize spending by month, payment method, and location.

## Database Design

The backend uses an isolated Parking Expense Tracker database configured by `PARKING_EXPENSE_TRACKER_DATABASE_URL`.

Tables:

- `ParkingExpenseLocations`
- `ParkingExpenseEntries`

Locations are owner-scoped long-lived records. Entries are owner-scoped expense records that belong to one location. Deleting a location cascades its parking expenses because expenses without their location lose required context.

Indexes cover owner list queries, updated sorting, location lookups, date sorting, payment-method filters, vehicle filters, and location search patterns. No text or speculative search indexes are added.

## API Design

The router is mounted at `/api/v1/parking-expense-tracker`. It exposes protected owner-scoped endpoints for dashboard summary, locations, and parking expenses. List endpoints return lightweight summary fields with notes previews. Detail endpoints return full notes for edit drawers. Expense update payloads intentionally exclude create-only `locationId` reassignment.

## Shared Components Used

The frontend implementation uses the established Ansiversa shell and shared components:

- `AvAppOverviewPage`
- `AvAuthenticatedPageState`
- `AvPageHeader`
- `AvCardEmptyState`
- `AvInlineFeedback`
- `AvPagination`
- `AvFormDrawer`
- `AvRecordActions`
- Shared confirmation dialog
- Zustand store helpers

## Performance Considerations

Dashboard payloads remain bounded to summary data. Expense notes are previewed in list responses and loaded fully only through detail endpoints. Aggregations are deterministic and computed from owner-scoped records. Indexes are aligned to the filters and ordering the UI exposes.

## Current Status

Workflow Ready. Parking Expense Tracker is implemented as an active `comingSoon` mini app with protected frontend workflow routes, isolated backend persistence, local migration verification, overview Explore routing to `/parking-expense-tracker/expenses`, and no live promotion.

## Known Limitations

The current implementation does not provide parking reservations, live availability, payments, receipt import, receipt forwarding, OCR, reimbursement approvals, tax filing guidance, GPS detection, or accounting integrations. All records are user-entered references.

## Future Enhancements

Future approved versions may add receipt attachments, export packs, recurring parking passes, commute summaries, cross-app expense links, calendar context, reimbursement report preparation, and governed import workflows after Partner/Astra review.

## Current Implementation

The implementation includes isolated SQLAlchemy models, Alembic migration `20260712_0001_parking_expense_tracker`, protected owner-scoped routes, repository/service separation, Pydantic request and response schemas, overview metadata, generated OpenAPI compatibility, and React workflow pages for Parking Expenses, Parking Locations, and Insights. The parent Apps catalog keeps Parking Expense Tracker as `active` with `launchStatus = comingSoon` and `version = null`.
