# Car Pool Story

## Purpose

Car Pool exists to help authenticated Ansiversa users organize shared ride plans, local trip participation, passenger requests, and simple activity insights in one protected workspace. The module supports coordination memory; it is not a live rideshare marketplace.

## Workflow

The workflow starts at `/car-pool/rides` and continues through `/car-pool/my-trips`, `/car-pool/requests`, and `/car-pool/insights`.

Users create ride records, join saved rides as local trips, leave trips when needed, create and review passenger requests, and use insights to understand seats, completed trips, cancellations, and weekly activity.

## User Journey

An authenticated user creates a ride with origin, destination, departure time, meeting point, vehicle details, seats, optional price reference, recurrence, status, and notes. The user can edit, duplicate, delete, search, filter, and paginate ride records. The user can join a ride locally, review upcoming and past trip records, leave a trip, and manage requests through pending, approved, and rejected states.

## Database Design

The backend uses an isolated Car Pool database configured by `CAR_POOL_DATABASE_URL`. Tables are:

- `CarPoolRides`
- `CarPoolPassengers`
- `CarPoolRequests`

Indexes are based on current query paths: owner lists, status filters, departure ordering, parent ride lookups, request status review, and updated-at sorting. Large text fields such as notes and messages are not indexed.

## API Design

The router is mounted at `/api/v1/car-pool`. It exposes protected owner-scoped endpoints for rides, passengers, requests, duplicate ride, join/leave trip, and approve/reject request actions. Dashboard responses return lightweight summaries and deterministic insight fields. Detail endpoints return complete editable fields. Update schemas are separate from create schemas and do not accept create-only `rideId` for passenger or request reassignment.

## Shared Components Used

The frontend uses the Ansiversa shell, `AvOverview`, `AvPageHeader`, `AvAuthenticatedPageState`, `AvCardEmptyState`, `AvInlineFeedback`, `AvPagination`, `AvFormDrawer`, `AvRecordActions`, shared confirmation dialogs, typed API services, and a module-local Zustand store.

## Performance Considerations

List and dashboard responses return summary fields only. Notes and request messages are represented by previews in list views and loaded fully from detail endpoints for edit flows. Indexes cover owner-scoped date/status access patterns without speculative text search.

## Current Status

Workflow Ready. Car Pool is implemented as an active `comingSoon` mini app with protected frontend workflow routes, isolated backend persistence, local migration verification, overview Explore routing to `/car-pool/rides`, and no live promotion.

## Known Limitations

The current implementation does not provide live rider matching, driver verification, identity checks, payments, chat, route tracking, maps, notifications, insurance logic, emergency support, or public ride discovery. All ride, trip, and request records are user-entered local coordination records.

## Future Enhancements

Future approved versions may add reminder support, recurring ride improvements, trusted-group sharing, map-assisted route context, calendar integration, notification workflows, export, and governed AI assistance for summarizing repeated ride patterns. Any live matching, payment, safety, or verification feature requires separate Partner/Astra approval.

## Current Implementation

The implementation includes isolated SQLAlchemy models, Alembic migration `20260712_0001_car_pool`, protected owner-scoped routes, repository/service separation, Pydantic request and response schemas, overview metadata, generated OpenAPI compatibility, and React workflow pages for Rides, My Trips, Requests, and Insights. The parent Apps catalog keeps Car Pool as `active` with `launchStatus = comingSoon` and `version = null`.
