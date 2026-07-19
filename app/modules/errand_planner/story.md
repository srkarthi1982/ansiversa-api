# Errand Planner Story

## Purpose

Errand Planner is App #098 (`errand-planner`). It helps authenticated users organize personal errands with categories, priorities, due dates, locations, estimates, notes, status tracking, archive behavior, search, filters, pagination, and dashboard metrics.

## Workflow

The shared overview enters `/errand-planner/errands`. Protected workflow routes provide an errand list, errand detail page, and category management. Users create categories, create errands, edit saved records, complete or reopen errands, archive completed errands, restore archived errands, delete records through shared confirmations, and filter the list by status, category, priority, overdue, due today, due soon, and due date range.

## User Journey

A user creates categories such as Grocery, Pharmacy, Bank, School, Home, Vehicle, Business, or Other. The user adds errands with title, optional description, category, priority, due date, estimated minutes, location, status, and notes. The dashboard summarizes pending, in-progress, completed, overdue, due-today, due-soon, archived, and cancelled records. Completed errands can be archived; archived errands are read-only until restored.

## Database Design

The isolated database uses `ERRAND_PLANNER_DATABASE_URL` and custom version table `errand_planner_alembic_version`.

Tables:

- `ErrandCategories`: owner-scoped category records with unique user/name protection, color, sort order, and timestamps.
- `Errands`: owner-scoped errand records with category foreign key, priority, due date, estimate, location, status, notes, timestamps, and completion timestamp.

Indexes cover user/status, user/due date, user/priority, user/category, user/updated date, and category sort query patterns.

## API Design

Routes live under `/api/v1/errand-planner`.

- `GET /dashboard`
- `GET /errands`
- `POST /errands`
- `GET /errands/{id}`
- `PUT /errands/{id}`
- `DELETE /errands/{id}`
- `POST /errands/{id}/complete`
- `POST /errands/{id}/reopen`
- `POST /errands/{id}/archive`
- `POST /errands/{id}/restore`
- `GET /categories`
- `POST /categories`
- `PUT /categories/{id}`
- `DELETE /categories/{id}`

List and dashboard responses stay lightweight. Detail responses return the complete record needed for viewing and editing. Every operation resolves owner-scoped records and never trusts client-provided user identity.

## Shared Components Used

The frontend uses generated API types, the shared typed API client, Zustand, `AvAppOverviewPage`, `AvAuthenticatedPageState`, `AvPageHeader`, `AvFormDrawer`, `AvRecordActions`, `AvConfirmDialog`, `AvPagination`, `AvInlineFeedback`, shared cards, and empty states.

## Performance Considerations

The list endpoint returns only fields displayed by the list UI. Dashboard returns counts and recent summaries only. Filters and pagination limit list payload size. Indexes are aligned to owner-scoped list, status, due date, priority, category, and updated-at query patterns.

## Current Status

Errand Planner is Approved Live at version `1.0.0` after authenticated E2E, Astra review, Partner manual verification, production-configured isolated migration verification, destination metadata sync, overview metadata sync, and parent Apps row promotion.

## Known Limitations

- No reminders or push notifications.
- No maps, GPS, route optimization, delivery tracking, or calendar sync.
- No AI assistant.
- No household sharing.
- No recurring errands.

## Future Enhancements

- Approved reminder integration through shared platform notifications.
- Recurring errands or templates.
- Optional household collaboration if approved.
- Better category color controls.
- Calendar export only if the platform approves that boundary.

## Current Implementation

The implementation provides protected CRUD for errands and categories, lightweight list summaries with detail-only description and notes loaded from the detail endpoint, combined list filters, deterministic ordering, overdue/due-today/due-soon flags, status actions, archive/restore behavior, archived restore-only protection, duplicate category protection, category delete protection, generated OpenAPI contracts, service tests, and shared frontend drawer/delete patterns.
