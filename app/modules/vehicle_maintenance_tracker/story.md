# Vehicle Maintenance Tracker Story

## Purpose

Vehicle Maintenance Tracker exists to help authenticated Ansiversa users keep private vehicle upkeep records, service history, reminder dates, odometer values, and maintenance costs in one protected workspace. The module is a recordkeeping and planning tool, not a diagnostic system, repair marketplace, or legal compliance engine.

## Workflow

The workflow starts at `/vehicle-maintenance-tracker/vehicles` and continues through `/vehicle-maintenance-tracker/maintenance`, `/vehicle-maintenance-tracker/reminders`, and `/vehicle-maintenance-tracker/insights`.

Users create vehicle profiles, record completed maintenance, create upkeep reminders, mark reminders completed locally, and review cost, reminder, service-frequency, and monthly activity insights.

## User Journey

An authenticated user creates a vehicle with name, make, model, year, plate, VIN, odometer, fuel type, status, and notes. The user records service history with service date, category, odometer, provider, cost, next due signals, and notes. The user creates reminders for oil changes, tire rotations, inspections, insurance renewals, registration renewals, and general service, then marks them completed when handled outside the app.

## Database Design

The backend uses an isolated Vehicle Maintenance Tracker database configured by `VEHICLE_MAINTENANCE_TRACKER_DATABASE_URL`. Tables are:

- `VehicleMaintenanceVehicles`
- `VehicleMaintenanceRecords`
- `VehicleMaintenanceReminders`

Indexes are based on current query paths: owner lists, status filters, vehicle foreign-key lookups, service date ordering, reminder due dates, reminder type/status review, and updated-at sorting. Large text fields such as notes are not indexed.

## API Design

The router is mounted at `/api/v1/vehicle-maintenance-tracker`. It exposes protected owner-scoped endpoints for vehicles, maintenance records, reminders, duplicate vehicle, and complete reminder actions. Dashboard responses return lightweight summaries and deterministic insight fields. Detail endpoints return complete editable fields. Update schemas are separate from create schemas and do not accept create-only `vehicleId` reassignment for maintenance records or reminders.

## Shared Components Used

The frontend uses the Ansiversa shell, `AvOverview`, `AvPageHeader`, `AvAuthenticatedPageState`, `AvCardEmptyState`, `AvInlineFeedback`, `AvPagination`, `AvFormDrawer`, `AvRecordActions`, shared confirmation dialogs, typed API services, and a module-local Zustand store.

## Performance Considerations

List and dashboard responses return summary fields only. Notes are represented by previews in list views and loaded fully from detail endpoints for edit flows. Indexes cover owner-scoped vehicle, date, status, and reminder access patterns without speculative text search.

## Current Status

Approved live at version `1.0.0`. Vehicle Maintenance Tracker is implemented as an active `live` mini app with protected frontend workflow routes, isolated backend persistence, production migration verification, overview Explore routing to `/vehicle-maintenance-tracker/vehicles`, and destination metadata `24 / 100`.

## Known Limitations

The current implementation does not provide mechanic booking, live diagnostics, telematics, OBD integration, repair estimates from providers, parts inventory, insurance processing, legal compliance automation, notifications, or official renewal submission. All records are user-entered upkeep references.

## Future Enhancements

Future approved versions may add reminder notifications, recurring service templates, document attachments, calendar export, cross-app expense links, richer maintenance intervals, and governed AI summaries of user-entered service patterns. Any integrations with diagnostics, insurance, official registrations, or service providers require separate Partner/Astra approval.

## Current Implementation

The implementation includes isolated SQLAlchemy models, Alembic migration `20260712_0001_vehicle_maintenance_tracker`, protected owner-scoped routes, repository/service separation, Pydantic request and response schemas, overview metadata, generated OpenAPI compatibility, and React workflow pages for Vehicles, Maintenance, Reminders, and Insights. The parent Apps catalog stores Vehicle Maintenance Tracker as `active` with `launchStatus = live`, `version = 1.0.0`, and destination metadata `24 / 100`.
