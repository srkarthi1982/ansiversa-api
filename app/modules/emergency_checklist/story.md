# Emergency Checklist Story

## Purpose

Emergency Checklist is App #100 (`emergency-checklist`). It helps authenticated users prepare reusable private checklists before emergencies happen.

## Workflow

Users create categories, create checklists, add checklist items, mark items complete, reset a checklist for another review, archive stale checklists, and restore archived records when needed.

## User Journey

The overview Explore CTA enters `/emergency-checklist/checklists`. Protected workflow routes cover checklists, checklist detail, and categories.

## Database Design

The module owns an isolated database configured through `EMERGENCY_CHECKLIST_DATABASE_URL`.

- `ChecklistCategories`: owner-scoped category records with unique user/name protection and deterministic sort order.
- `EmergencyChecklists`: owner-scoped reusable checklists with optional category, description, archive state, and timestamp indexes.
- `ChecklistItems`: child checklist items with deterministic sort order, notes, and completion state.

## API Design

The router is mounted at `/api/v1/emergency-checklist`.

- `GET /dashboard`
- `GET/POST /checklists`
- `GET/PUT/DELETE /checklists/{checklist_id}`
- `POST /checklists/{checklist_id}/archive`
- `POST /checklists/{checklist_id}/restore`
- `POST /checklists/{checklist_id}/reset`
- `POST /checklists/{checklist_id}/complete`
- `POST/PUT/DELETE /checklists/{checklist_id}/items`
- `GET/POST/PUT/DELETE /categories`

List responses are lightweight summaries. Detail responses include checklist items for viewing and editing.

## Shared Components Used

Frontend uses `AvAppOverviewPage`, `AvAuthenticatedPageState`, `AvPageHeader`, `AvFormDrawer`, `AvRecordActions`, `AvPagination`, shared API client, generated OpenAPI types, and Zustand lifecycle helpers.

## Performance Considerations

Indexes cover owner/category, archive filtering, updated sorting, and item sort/completion lookups. Payloads separate list summaries from detail item payloads.

## Current Status

Emergency Checklist is Workflow Ready / Level 3 candidate, `comingSoon`, version `null`. Production-configured migration `20260716_0012_emergency_checklist` is applied and verified for the isolated database. Authenticated browser E2E, Karthik manual acceptance, destination approval, and live promotion remain pending.

## Known Limitations

No templates, reminders, sharing, exports, external APIs, AI advice, live alerts, medical guidance, or emergency-response functions are included.

## Future Enhancements

Approved templates, review reminders, household collaboration, and export/print views may be considered after Partner/Astra approval.

## Current Implementation

Archived checklists are read-only until restored, including update, item mutation, archive, and hard-delete operations. Completion percentage is calculated from completed items over total items. Reset marks every item incomplete. Owner isolation is enforced for categories, checklists, and item mutations through the parent checklist.
