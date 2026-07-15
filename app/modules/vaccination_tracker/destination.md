# Vaccination Tracker Destination

## Product Vision

Vaccination Tracker is a private personal organizer for vaccination profiles, vaccine labels, dose records, and upcoming due dates.

## Core Workflows

- Create and manage profiles for people or dependents.
- Use default or custom vaccine type labels.
- Record completed, scheduled, skipped, and cancelled vaccination records.
- Track dose number, total doses, completion percentage, next due date, and series-complete status.
- Search, filter, sort, archive, restore, and review vaccination history.

## Medical Limitations

The app does not recommend vaccines, diagnose conditions, replace professional care, guarantee immunity, generate official certificates, provide emergency support, or alter schedules without professional guidance.

## Acceptance Criteria

Protected owner-scoped CRUD for profiles, vaccine types, and records; duplicate dose prevention; date/dose/cost validation; dashboard and insights; overview CTA `/vaccination-tracker/records`; production migration verified; app remains comingSoon/version null.

## Manual Verification Checklist

Verify profile CRUD, vaccine type CRUD, record CRUD, duplicate-dose blocking, invalid dose/cost validation, due today/week/overdue calculations, insights, archive/restore, persistence, responsive layout, keyboard controls, owner isolation, and no medical advice wording.

## Current Readiness

Workflow Ready after implementation and production migration. Manual verification is required before any live promotion.
