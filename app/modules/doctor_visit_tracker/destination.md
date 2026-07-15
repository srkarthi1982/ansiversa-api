# Doctor Visit Tracker Destination

Document Status: Approved for Live promotion on 2026-07-15 after Astra review, Partner approval, production migration verification, production catalog verification, and manual browser verification.
Destination Status: approved
Destination Reviewed At: 2026-07-15
Created: 2026-07-15

## Product Vision

Doctor Visit Tracker is a private personal organizer for medical appointments and visit history. It helps users record appointment details, follow-ups, notes, medications mentioned, insurance notes, and costs.

The destination is always `100 / 100`. The current approved Journey Progress is `20 / 100`.

## Core Workflows

Create, edit, archive, restore, delete, search, filter, and sort visits. Manage specialties. Review dashboard and insights.

## Medical Safety Boundary

The app is not medical advice, diagnosis, treatment recommendation, prescription support, or emergency care. User-entered diagnosis notes and medications are personal records only.

## Acceptance Criteria

Protected visit/specialty CRUD, owner isolation, validation, search/filter/sort, dashboard, insights, overview CTA `/doctor-visit-tracker/visits`, production migration verified, and status is `active` / `live` at version `1.0.0`.

## Manual Verification

Manual verification confirmed visit CRUD, specialty CRUD, status workflows, follow-ups, costs, insights, archive/delete actions, persistence, default specialties, dashboard counters, and overview navigation.

## Journey Progress

Current Position: 20 / 100

Current Journey Progress: 20 / 100

V1 creates the private doctor visit record foundation with owner-scoped visits and specialties, default specialty seeding, visit CRUD, specialty CRUD, archive/delete actions, search, filters, sorting, dashboard counters, insights, cost summaries, follow-up summaries, production migration, and verified production workflow behavior. Remaining maturity includes notification reminders through the approved platform layer, calendar export, safer attachment handling, and approved cross-app summaries.

## Future Direction

- Add notification reminders only through the approved platform notification layer.
- Add calendar export after review.
- Add safer attachment handling only after storage governance approval.
- Consider approved cross-app summaries with health-record modules.

## Governance Notes

Astra: Approved on 2026-07-15.

Partner: Approved Doctor Visit Tracker live promotion after owner-review browser verification.

Codex: Ran production-configured isolated database migration, verified schema/indexes/version table, synced overview metadata, promoted the production Apps row, synced destination metadata, and verified production catalog counts.
