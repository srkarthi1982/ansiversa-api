# Health Report Organizer Story

## Purpose

Health Report Organizer gives authenticated users a private workspace for organizing health reports, categories, facilities, attachment metadata, and report-linked notes.

The app is an organizing tool. It does not diagnose, interpret clinical results, recommend treatment, provide emergency guidance, or integrate with provider portals in the current implementation.

## Workflow

The protected workflow starts at `/health-report-organizer/reports`. Users create report records, organize them with categories and facilities, track document attachment metadata, add report notes, and review insights. The overview CTA routes into the first real workflow route rather than back to the overview.

## User Journey

A user creates a health report with title, type, date, optional patient and doctor names, category, facility, review status, priority, and summary. The user can create categories such as Blood Work or Imaging and facilities such as labs, hospitals, clinics, or imaging centers. For each report, the user can record attachment metadata that points to where a document lives and add notes for questions, follow-up, results context, or billing context. Insights summarize report volume, reviewed reports, follow-up records, attachment count, and recent activity.

## Database Design

Health Report Organizer uses an isolated database configured by `HEALTH_REPORT_ORGANIZER_DATABASE_URL`. The module owns `HealthReportCategories`, `HealthReportFacilities`, `HealthReports`, `HealthReportAttachments`, and `HealthReportNotes`. Every table stores `userId` for owner scoping. Reports can reference a category and facility. Attachments and notes belong to reports and are deleted with the parent report.

## API Design

The router is mounted at `/api/v1/health-report-organizer`. It exposes protected dashboard, report CRUD, category CRUD, facility CRUD, attachment CRUD, and note CRUD endpoints. Dashboard and list responses use lightweight summaries and previews. Detail endpoints return full editable fields. Attachment and note update schemas intentionally exclude create-only `reportId` because parent reassignment is not supported for those child records.

## Shared Components Used

The backend follows the established FastAPI mini-app pattern: isolated `db.py`, thin `router.py`, compatibility `routes.py`, SQLAlchemy models, Pydantic schemas, repository helpers, service-owned business logic, current-user dependencies, and generated OpenAPI contracts.

## Performance Considerations

Indexes cover owner-scoped category and facility lists, report timelines, report status filtering, category/facility report lookups, attachment lookups by report/status, and note lookups by report/category/date. Large text fields are not indexed. List responses use previews and counts instead of full summaries, addresses, attachment notes, and note bodies.

## Current Status

Approved Live at version `1.0.0` after Astra/Partner approval, production Apps row promotion, destination metadata sync, isolated production migration verification, and manual workflow verification. The backend has protected owner-scoped APIs, isolated migration `20260711_0001_health_report_organizer`, dashboard summaries, report CRUD/delete, category CRUD/delete, facility CRUD/delete, attachment metadata CRUD/delete, note CRUD/delete, lightweight/detail response separation, and knowledge lifecycle documents.

The parent Apps catalog stores Health Report Organizer as `active` with `launchStatus = live` and version `1.0.0`.

## Known Limitations

V1 does not upload or store medical files, import records from provider portals, sync with Apple Health or Google Health, export appointment packets, support caregiver sharing, provide clinical interpretation, or include AI functionality.

## Future Enhancements

Future versions may add secure file upload after privacy governance, appointment packet exports, richer timelines, family-member support, cross-app health links, and AI-assisted metadata extraction or question preparation after governance approval.

## Current Implementation

Health Report Organizer is a DB-backed mini-app module with owner-scoped CRUD APIs, isolated migration files, lightweight response schemas, dashboard summary calculation, and protected frontend routes for Reports, Categories, Documents, and Insights. The parent Apps catalog is approved live at version `1.0.0`.
