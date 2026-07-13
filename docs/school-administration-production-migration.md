# School Administration Production Migration

## App

School Administration

## Slug

`school-administration`

## Date

2026-07-13

## Scope

Ran the production-configured isolated database migration for App #070 School Administration.

No live promotion was performed.

The parent Apps row remains:

```text
status = active
launchStatus = comingSoon
version = null
destination metadata = null
```

## Database Configuration

The migration used the configured module database URL:

```text
SCHOOL_ADMINISTRATION_DATABASE_URL=libsql://school-administration-ansiversa.aws-ap-south-1.turso.io
```

SQLAlchemy reported the driver as:

```text
sqlite+libsql
```

## Alembic Verification

Command:

```bash
PYTHONPATH=. .venv/bin/alembic -c school-administration_alembic.ini upgrade head
PYTHONPATH=. .venv/bin/alembic -c school-administration_alembic.ini current
```

Result:

```text
20260713_0001_school_administration (head)
```

Version table:

```text
school_administration_alembic_version
```

Recorded revision:

```text
20260713_0001_school_administration
```

## Managed Tables

All expected module-owned tables are present:

```text
SchoolAttendance
SchoolClasses
SchoolEnrollments
SchoolStudents
```

## Starting Row Counts

The production module database starts empty:

```text
SchoolAttendance   = 0
SchoolClasses      = 0
SchoolEnrollments  = 0
SchoolStudents     = 0
```

## Foreign Key Verification

Verified foreign keys:

```text
SchoolEnrollments.classId -> SchoolClasses
SchoolEnrollments.studentId -> SchoolStudents
SchoolAttendance.classId -> SchoolClasses
SchoolAttendance.studentId -> SchoolStudents
```

## Unique Constraint Verification

Verified unique constraints:

```text
SchoolStudents_userId_admissionNumber_key
SchoolEnrollments_userId_classId_studentId_status_key
SchoolAttendance_userId_classId_studentId_date_key
```

## Index Verification

Verified indexes:

```text
SchoolStudents_userId_createdAt_idx
SchoolStudents_userId_status_updatedAt_idx
ix_SchoolStudents_userId

SchoolClasses_userId_updatedAt_idx
SchoolClasses_userId_year_status_idx
ix_SchoolClasses_userId

SchoolEnrollments_userId_classId_status_idx
SchoolEnrollments_userId_studentId_status_idx
ix_SchoolEnrollments_classId
ix_SchoolEnrollments_studentId
ix_SchoolEnrollments_userId

SchoolAttendance_userId_classId_date_status_idx
SchoolAttendance_userId_date_idx
SchoolAttendance_userId_studentId_date_idx
ix_SchoolAttendance_classId
ix_SchoolAttendance_studentId
ix_SchoolAttendance_userId
```

## Status

Production database migration is complete and ready for manual Astra/Partner verification.

School Administration remains Workflow Ready only.
