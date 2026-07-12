# Trip Cost Calculator Story

## Purpose

Trip Cost Calculator helps authenticated Ansiversa users estimate, record, compare, and analyze trip costs. It complements the Mobility & Travel suite by turning trips, travelers, distance, and category expenses into a private cost review workspace.

## Workflow

The overview Explore CTA enters `/trip-cost-calculator/trips`. The protected workflow routes are:

- `/trip-cost-calculator/trips`
- `/trip-cost-calculator/expenses`
- `/trip-cost-calculator/comparison`
- `/trip-cost-calculator/insights`

## User Journey

Users create trips with route, dates, travelers, optional vehicle, distance, currency, and notes. They add cost items for fuel, parking, tolls, accommodation, food, transport, tickets, shopping, and miscellaneous expenses. Comparison shows total cost by trip, cost per traveler, cost per kilometer, category breakdowns, and highest or lowest expense categories. Insights summarize overall activity and monthly spending.

## Database Design

The backend uses an isolated Trip Cost Calculator database configured by `TRIP_COST_CALCULATOR_DATABASE_URL`.

Tables:

- `TripCostTrips`
- `TripCostExpenses`

Trips are owner-scoped long-lived records. Expenses are owner-scoped cost items that belong to one trip. Deleting a trip cascades its cost items because expenses require trip context. Indexes cover owner list queries, updated sorting, trip lookups, date filters, category filters, and destination review.

## API Design

The router is mounted at `/api/v1/trip-cost-calculator`. It exposes protected owner-scoped endpoints for dashboard summary, trips, duplicate trip, and cost items. List endpoints return lightweight summary fields with notes previews. Detail endpoints return full notes for edit drawers. Expense update payloads intentionally exclude create-only `tripId` reassignment.

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

Dashboard payloads stay bounded to trip and cost summaries. Notes are previewed in list responses and loaded fully only through detail endpoints. Aggregations are deterministic and computed from owner-scoped records. Indexes are aligned to the filters and ordering exposed by the UI.

## Current Status

Approved Live. Trip Cost Calculator is promoted to `active` / `live` at version `1.0.0` after Astra/Partner approval, browser workflow verification, production Apps row promotion, destination metadata sync, local and production-configured migration verification, and overview Explore routing to `/trip-cost-calculator/trips`.

## Known Limitations

The current implementation does not provide live booking prices, map routing, fuel-price feeds, currency conversion, split payments, receipt OCR, reimbursement workflows, tax guidance, or accounting integrations. Monetary insights aggregate entered amounts as-is by stored currency.

## Future Enhancements

Future approved versions may add estimate templates, exports, receipt attachments, recurring trip presets, cross-app links to parking or car-pool records, optional currency normalization, and governed import workflows.

## Current Implementation

The implementation includes isolated SQLAlchemy models, Alembic migration `20260712_0001_trip_cost_calculator`, protected owner-scoped routes, repository/service separation, Pydantic request and response schemas, overview metadata, generated OpenAPI compatibility, and React workflow pages for Trips, Cost Items, Comparison, and Insights. The production-configured isolated database has been migrated to head with the expected tables, indexes, foreign key, empty starting row counts, and module Alembic version table. The parent Apps catalog keeps Trip Cost Calculator as `active` with `launchStatus = live`, `version = 1.0.0`, and approved destination metadata `22 / 100`.
