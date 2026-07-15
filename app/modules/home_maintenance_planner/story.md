# Home Maintenance Planner Story

## Purpose

Home Maintenance Planner gives authenticated users a private workspace for household maintenance planning. It organizes recurring and one-time work by area, category, due date, priority, provider details, notes, and optional cost records.

## Workflow

Users create areas and categories, then create maintenance tasks. Tasks can be searched, filtered, sorted, edited, completed, reopened, archived, restored, and deleted. Completing a recurring task records completion history and advances the same task to the next due date.

## User Journey

A family tracks air-conditioner servicing before summer. A homeowner schedules water-tank cleaning. A renter records appliance maintenance and provider reference numbers. A villa resident keeps garden and exterior work visible. A user reviews overdue tasks and cost totals in insights.

## Database Design

The module owns an isolated database configured by `HOME_MAINTENANCE_PLANNER_DATABASE_URL`.

Tables:

- `MaintenanceAreas`
- `MaintenanceCategories`
- `MaintenanceTasks`
- `MaintenanceTaskCompletions`

The Alembic version table is `home_maintenance_planner_alembic_version`.

## API Design

The API is mounted at `/api/v1/home-maintenance-planner` and provides dashboard, insights, area CRUD, category CRUD, task CRUD, complete, reopen, archive, restore, search, filters, sorting, and recurrence calculations.

## Shared Components Used

The frontend uses the shared authenticated page state, overview page, feedback, drawer, confirmation dialog, empty state, stat grid, and generated API client conventions.

## Performance Considerations

List responses return task summaries. Detail endpoints return the full editable task. Lookup lists include task counts. Dashboard and insights return compact aggregates.

## Current Status

Approved live at version `1.0.0` after Astra review, Partner approval, production-configured isolated database migration verification, production Apps row promotion, overview metadata sync, and manual browser workflow verification. Destination metadata is synced at `20 / 100`, status `approved`, reviewed on `2026-07-15`.

## Known Limitations

The app does not send notifications, upload invoices, diagnose home issues, dispatch contractors, certify safety, or provide regulatory compliance guidance. V2 UI polish should replace native browser delete confirmations with shared `AvConfirmDialog` and move create/edit flows into shared drawers for platform consistency.

## Future Enhancements

Future approved versions may add calendar export, safer attachment handling, shared household collaboration, or cross-app dashboard summaries through approved APIs.

## Current Implementation

The current implementation is an owner-scoped FastAPI, SQLAlchemy, Alembic, React, TypeScript, and Zustand workflow designed for manual planning and record keeping. The production catalog row is `active` / `live` / `1.0.0`.
