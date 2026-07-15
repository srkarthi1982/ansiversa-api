# Doctor Visit Tracker Story

## Purpose

Doctor Visit Tracker gives authenticated users a private workspace for doctor appointments and visit history.

## Workflow

Users manage specialties and visit records. Visits include doctor, clinic, date, time, status, reason, notes, medications, follow-up date, cost, insurance notes, and personal notes.

## Database Design

The module owns an isolated database configured by `DOCTOR_VISIT_TRACKER_DATABASE_URL` with `DoctorSpecialties` and `DoctorVisits` tables. The version table is `doctor_visit_tracker_alembic_version`.

## API Design

The API is mounted at `/api/v1/doctor-visit-tracker` and provides dashboard, insights, specialty CRUD, visit CRUD, archive/restore, search, filters, and sorting.

## Safety Boundary

The app stores user-entered personal records only. It does not diagnose conditions, recommend treatments, prescribe medication, replace professional advice, or support emergencies.

## Current Status

Approved live at version `1.0.0` after Astra review, Partner approval, production-configured isolated database migration verification, production Apps row promotion, overview metadata sync, and manual browser workflow verification. Destination metadata is synced at `20 / 100`, status `approved`, reviewed on `2026-07-15`.

## Current Implementation

The production catalog row is `active` / `live` / `1.0.0`.
