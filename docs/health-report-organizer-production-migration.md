# Health Report Organizer Production Migration

## App

Health Report Organizer

## Slug

`health-report-organizer`

## Date

2026-07-11

## Scope

Ran the production-configured isolated database migration for App #061 Health Report Organizer.

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
HEALTH_REPORT_ORGANIZER_DATABASE_URL=libsql://health-report-organizer-ansiversa.aws-ap-south-1.turso.io
```

SQLAlchemy reported the driver as:

```text
sqlite+libsql
```

## Alembic Verification

Command:

```bash
.venv/bin/python -m alembic -c health-report-organizer_alembic.ini upgrade head
.venv/bin/python -m alembic -c health-report-organizer_alembic.ini current
```

Result:

```text
20260711_0001_health_report_organizer (head)
```

Version table:

```text
health_report_organizer_alembic_version
```

Recorded revision:

```text
20260711_0001_health_report_organizer
```

## Managed Tables

All expected module-owned tables are present:

```text
HealthReportAttachments
HealthReportCategories
HealthReportFacilities
HealthReportNotes
HealthReports
```

## Starting Row Counts

The production module database starts empty:

```text
HealthReportAttachments = 0
HealthReportCategories  = 0
HealthReportFacilities  = 0
HealthReportNotes       = 0
HealthReports           = 0
```

## Index Verification

Verified indexes:

```text
HealthReportAttachments_userId_reportId_updatedAt_idx
HealthReportAttachments_userId_status_updatedAt_idx
ix_HealthReportAttachments_reportId
ix_HealthReportAttachments_userId

HealthReportCategories_userId_status_updatedAt_idx
ix_HealthReportCategories_userId

HealthReportFacilities_userId_status_updatedAt_idx
ix_HealthReportFacilities_userId

HealthReportNotes_userId_category_noteDate_idx
HealthReportNotes_userId_reportId_noteDate_idx
ix_HealthReportNotes_reportId
ix_HealthReportNotes_userId

HealthReports_userId_categoryId_reportDate_idx
HealthReports_userId_facilityId_reportDate_idx
HealthReports_userId_reportDate_idx
HealthReports_userId_status_reportDate_idx
ix_HealthReports_categoryId
ix_HealthReports_facilityId
ix_HealthReports_userId
```

## Status

Production database migration is complete and ready for manual Astra/Partner verification.

Health Report Organizer remains Workflow Ready only.
