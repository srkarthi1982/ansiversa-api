# Medicine Reminder Story

## Purpose

Medicine Reminder gives authenticated users a private workspace for organizing medicines, defining reminder schedules, logging dose outcomes, and keeping notes related to medication routines.

## Workflow

The protected workflow starts at `/medicine-reminder/medicines`. Users create medicines, add schedules, record dose logs, review history, and capture notes. The overview CTA routes into the first real workflow route rather than back to the overview.

## User Journey

A user creates a medicine with dosage, form, purpose, instructions, prescriber, active dates, status, and refill reminder information. The user adds one or more schedules with time, frequency, dose amount, and instructions. Each day, the user records whether a dose was taken, missed, skipped, or late. Notes capture side effects, doctor questions, refill comments, and general observations.

## Database Design

Medicine Reminder uses an isolated database configured by `MEDICINE_REMINDER_DATABASE_URL`. The module owns `MedicineReminderMedicines`, `MedicineReminderSchedules`, `MedicineReminderDoseLogs`, and `MedicineReminderNotes`. Every table stores `userId` for owner scoping. Schedules, dose logs, and notes belong to medicines and are deleted with the parent medicine.

## API Design

The router is mounted at `/api/v1/medicine-reminder`. It exposes protected dashboard, medicine CRUD, schedule CRUD, dose-log CRUD, and note CRUD endpoints. Dashboard and list responses use lightweight summaries and previews. Detail endpoints return full editable fields. Schedule, dose-log, and note update schemas intentionally exclude create-only parent IDs.

## Shared Components Used

The backend follows the established FastAPI mini-app pattern: isolated `db.py`, thin `router.py`, compatibility `routes.py`, SQLAlchemy models, Pydantic schemas, repository helpers, service-owned business logic, current-user dependencies, and generated OpenAPI contracts.

## Performance Considerations

Indexes cover owner-scoped medicine lists, status sorting, refill reminders, schedule lookups by medicine/time, active schedule filters, dose history by medicine/status/date, and medicine notes by category/date. Large text fields are not indexed. List responses use previews and counts instead of full instructions, notes, and bodies.

## Current Status

Workflow Ready V1. The backend has protected owner-scoped APIs, isolated migration `20260711_0001_medicine_reminder`, dashboard summaries, medicine CRUD/delete, schedule CRUD/delete, dose-log CRUD/delete, note CRUD/delete, lightweight/detail response separation, and knowledge lifecycle documents. The app remains `comingSoon` with `version = null` until Astra/Partner approval.

## Known Limitations

V1 does not send actual notifications, calculate clinical adherence scores, provide drug-interaction checks, provide dosage guidance, support caregiver sharing, export reports, or integrate with pharmacies, calendars, or health systems.

## Future Enhancements

Future versions may add notification delivery, refill quantity automation, exports for doctor visits, caregiver sharing, Today view improvements, and AI-assisted setup or review after governance approval.

## Current Implementation

Medicine Reminder is a DB-backed mini-app module with owner-scoped CRUD APIs, isolated migration files, lightweight response schemas, dashboard summary calculation, and Workflow Ready backend routing. The parent Apps catalog remains unchanged as `active` / `comingSoon` / `version = null`.
