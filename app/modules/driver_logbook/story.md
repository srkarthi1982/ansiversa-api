# Driver Logbook Story

## Purpose

Driver Logbook helps users keep a personal record of driving trips and vehicle use. It is a private record-keeping tool, not an official or regulatory driving logbook.

## Workflow

Users add vehicles, record driving trips, filter and review trip history, archive old trips, and open insights for distance, purpose, vehicle, and monthly summaries.

## User Journey

The user opens `/driver-logbook/trips`, creates or selects a vehicle, records a trip with date, time, odometer readings, purpose, route notes, and distance, then reviews dashboard metrics and insights.

## Database Design

The module owns an isolated database configured by `DRIVER_LOGBOOK_DATABASE_URL`.

Tables:

- `DriverVehicles`
- `DriverTrips`

The Alembic version table is `driver_logbook_alembic_version`.

## API Design

The API prefix is `/api/v1/driver-logbook`.

Routes cover dashboard, insights, vehicle CRUD, vehicle archive/restore, trip CRUD, trip archive/restore, search, filtering, sorting, and pagination.

## Shared Components Used

The frontend uses the shared authenticated page wrapper, API client, store helpers, overview page, cards, and app shell routing.

## Performance Considerations

Indexes cover owner-scoped vehicle lookup, archive filters, vehicle names, updated timestamps, trip owner, vehicle, date, purpose, archive state, creation date, distance, and odometer readings.

## Current Status

Workflow Ready for manual verification. No live promotion has been performed.

## Known Limitations

V1 has manual entry only, no GPS, no navigation, no official compliance calculations, no fleet features, and no regulatory certification.

## Future Enhancements

Possible future improvements include CSV export, trip templates, printable personal summaries, and optional receipt/attachment support after approval.

## Current Implementation

The implementation provides owner-scoped vehicles and trips, FastAPI endpoints, SQLAlchemy models, Pydantic schemas, Alembic migration, React routes, typed API integration, Zustand state, and readiness documentation.
