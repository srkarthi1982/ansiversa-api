# Car Pool Production Migration

## App

Car Pool

## Slug

`car-pool`

## Date

2026-07-12

## Scope

Ran the production-configured isolated database migration for App #064 Car Pool.

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
CAR_POOL_DATABASE_URL=libsql://car-pool-ansiversa.aws-ap-south-1.turso.io
```

SQLAlchemy reported the driver as:

```text
sqlite+libsql
```

## Alembic Verification

Command:

```bash
PYTHONPATH=. .venv/bin/python -m alembic -c car-pool_alembic.ini upgrade head
PYTHONPATH=. .venv/bin/python -m alembic -c car-pool_alembic.ini current
```

Result:

```text
20260712_0001_car_pool (head)
```

Version table:

```text
car_pool_alembic_version
```

Recorded revision:

```text
20260712_0001_car_pool
```

## Managed Tables

All expected module-owned tables are present:

```text
CarPoolPassengers
CarPoolRequests
CarPoolRides
```

## Starting Row Counts

The production module database starts empty:

```text
CarPoolPassengers = 0
CarPoolRequests   = 0
CarPoolRides      = 0
```

## Foreign Key Verification

Verified foreign keys:

```text
CarPoolPassengers.rideId -> CarPoolRides
CarPoolRequests.rideId -> CarPoolRides
```

## Index Verification

Verified indexes:

```text
CarPoolPassengers_userId_rideId_joinedAt_idx
CarPoolPassengers_userId_status_joinedAt_idx
ix_CarPoolPassengers_rideId
ix_CarPoolPassengers_userId

CarPoolRequests_userId_rideId_requestedAt_idx
CarPoolRequests_userId_status_requestedAt_idx
ix_CarPoolRequests_rideId
ix_CarPoolRequests_userId

CarPoolRides_userId_origin_destination_idx
CarPoolRides_userId_status_departureAt_idx
CarPoolRides_userId_updatedAt_idx
ix_CarPoolRides_userId
```

## Status

Production database migration is complete and ready for manual Astra/Partner verification.

Car Pool remains Workflow Ready only.
