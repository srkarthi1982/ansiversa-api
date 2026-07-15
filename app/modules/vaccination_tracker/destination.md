# Vaccination Tracker Destination

## Document Status

Approved for Live promotion on 2026-07-15 after Astra review, Partner approval, production migration verification, production catalog verification, backend authentication fix verification, and manual browser verification.

## Destination Status

Approved v1.0

## Product Vision

Vaccination Tracker is a private personal organizer for vaccination profiles, vaccine labels, dose records, and upcoming due dates.

The destination is always `100 / 100`. The current approved Journey Progress is `20 / 100`.

## Core Workflows

- Create and manage profiles for people or dependents.
- Use default or custom vaccine type labels.
- Record completed, scheduled, skipped, and cancelled vaccination records.
- Track dose number, total doses, completion percentage, next due date, and series-complete status.
- Search, filter, sort, archive, restore, and review vaccination history.

## Medical Limitations

The app does not recommend vaccines, diagnose conditions, replace professional care, guarantee immunity, generate official certificates, provide emergency support, or alter schedules without professional guidance.

## Acceptance Criteria

Protected owner-scoped CRUD for profiles, vaccine types, and records; duplicate dose prevention; date/dose/cost validation; dashboard and insights; overview CTA `/vaccination-tracker/records`; production migration verified; app is `active` / `live` at version `1.0.0`.

## Manual Verification Checklist

Verify profile CRUD, vaccine type CRUD, record CRUD, duplicate-dose blocking, invalid dose/cost validation, due today/week/overdue calculations, insights, archive/restore, persistence, responsive layout, keyboard controls, owner isolation, and no medical advice wording.

## Current Readiness

Approved live after implementation, production migration, backend authentication fix verification, and manual browser verification.

## Journey Progress

Current Position: 20 / 100

Current Journey Progress: 20 / 100

V1 creates the private vaccination record foundation with owner-scoped profiles, vaccine type labels, vaccination record CRUD, archive/restore actions, duplicate dose protection, due-date summaries, insights, production migration, database authentication fix verification, and verified production workflow behavior. Remaining maturity includes reminders, attachment support, exports, and approved cross-app health record summaries without medical recommendation claims.

## Future Direction

- Add reminders only through the approved platform notification layer.
- Add attachment support after privacy and storage review.
- Add exports after product review.
- Consider approved cross-app health record summaries without medical advice or certificate claims.

## Governance Notes

Astra: Approved on 2026-07-15.

Partner: Approved Vaccination Tracker live promotion after owner-review browser verification and backend authentication fix verification.

Codex: Fixed isolated database auth wiring, verified Turso connectivity, smoke-tested dashboard/profiles/vaccines/records/insights API responses, removed temporary smoke-test data, synced overview metadata, promoted the production Apps row, synced destination metadata, and verified production catalog counts.
