# Vaccination Tracker Story

## Purpose

Vaccination Tracker helps authenticated users organize vaccination records for themselves and family members. It is a record-keeping tool, not a medical decision system.

## User Journeys

A parent creates child profiles and records completed childhood doses. An adult records annual and travel-related vaccines after a clinic visit. A family reviews upcoming and overdue doses before contacting a qualified provider. A user records provider, manufacturer, batch, and reference details from clinic paperwork.

## Database Design

The module owns an isolated database configured by `VACCINATION_TRACKER_DATABASE_URL` with `VaccinationProfiles`, `VaccineTypes`, and `VaccinationRecords`. The version table is `vaccination_tracker_alembic_version`.

## API Design

The API is mounted at `/api/v1/vaccination-tracker` and provides dashboard, insights, profile CRUD/archive/restore, vaccine type CRUD, and record CRUD/archive/restore/search/filter/sort/pagination.

## Current Status

The V1 workflow is ready for manual verification. The app remains `comingSoon` with `version = null` and has not been promoted live.

## Known Limitations

No attachment uploads, official certificate generation, medical recommendations, clinical schedule generation, or external integrations are included in V1.
