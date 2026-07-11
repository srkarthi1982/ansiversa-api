# Rent a Car Production Migration

## App

Rent a Car

## Slug

`rent-a-car`

## Date

2026-07-11

## Scope

Ran the production-configured isolated database migration for App #063 Rent a Car.

No live promotion was performed.

The parent Apps row remains:

```text
status = active
launchStatus = comingSoon
version = null
```

## Database Configuration

The migration used the configured module database URL:

```text
RENT_A_CAR_DATABASE_URL=libsql://rent-a-car-ansiversa.aws-ap-south-1.turso.io
```

SQLAlchemy reported the driver as:

```text
sqlite+libsql
```

## Alembic Verification

Command:

```bash
PYTHONPATH=. .venv/bin/python -m alembic -c rent-a-car_alembic.ini upgrade head
PYTHONPATH=. .venv/bin/python -m alembic -c rent-a-car_alembic.ini current
```

Result:

```text
20260711_0001_rent_a_car (head)
```

Version table:

```text
rent_a_car_alembic_version
```

Recorded revision:

```text
20260711_0001_rent_a_car
```

## Managed Tables

All expected module-owned tables are present:

```text
RentACarBookings
RentACarSearches
RentACarVehicleOptions
```

## Starting Row Counts

The production module database starts empty:

```text
RentACarBookings       = 0
RentACarSearches       = 0
RentACarVehicleOptions = 0
```

## Foreign Key Verification

Verified foreign keys:

```text
RentACarVehicleOptions.searchId -> RentACarSearches
RentACarBookings.searchId -> RentACarSearches
RentACarBookings.vehicleOptionId -> RentACarVehicleOptions
```

## Index Verification

Verified indexes:

```text
RentACarBookings_userId_cancellationDeadline_idx
RentACarBookings_userId_searchId_bookingDate_idx
RentACarBookings_userId_status_bookingDate_idx
ix_RentACarBookings_searchId
ix_RentACarBookings_userId
ix_RentACarBookings_vehicleOptionId

RentACarSearches_userId_status_pickupAt_idx
RentACarSearches_userId_updatedAt_idx
ix_RentACarSearches_userId

RentACarVehicleOptions_userId_availability_updatedAt_idx
RentACarVehicleOptions_userId_class_updatedAt_idx
RentACarVehicleOptions_userId_provider_updatedAt_idx
RentACarVehicleOptions_userId_searchId_updatedAt_idx
ix_RentACarVehicleOptions_searchId
ix_RentACarVehicleOptions_userId
```

## Status

Production database migration is complete and ready for manual Astra/Partner verification.

Rent a Car remains Workflow Ready only.
