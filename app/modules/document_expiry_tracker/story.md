# Document Expiry Tracker Story

## Purpose

Document Expiry Tracker helps authenticated users manage personal document renewal dates in one protected Ansiversa workspace. It exists for personal planning and recordkeeping only. It is not a government renewal service, notification delivery system, OCR scanner, identity vault, or compliance automation product.

## Workflow

Users create document records with title, type, optional number, issuing authority, country, issue date, expiry date, reminder window, notes, and tags. The app calculates the current status from expiry date and archive state. Users can edit, delete, archive, restore, and mark documents renewed by updating issue and expiry dates. Dashboard and insights views summarize current expiry risk.

## User Journey

The first real workflow route is `/document-expiry-tracker/documents`. Users add or review document records there, then open `/expiry-dashboard` to review upcoming windows and `/insights` to understand document distribution and renewal pressure.

## Database Design

The module owns an isolated database configured by `DOCUMENT_EXPIRY_TRACKER_DATABASE_URL`.

The `Documents` table stores owner-scoped personal document metadata:

- `userId`, title, document type, optional document number, issuing authority, and country
- issue date, expiry date, and renewal reminder days
- notes, tags, archive state, renewal count, and last renewed date
- created and updated timestamps

Status is not user-maintained. It is computed from archive state, expiry date, and reminder window. Indexes support owner-scoped list queries, created/updated sorting, expiry review, type filters, country filters, and archived expiry dashboard queries.

## API Design

The router is mounted at `/api/v1/document-expiry-tracker`.

Endpoints:

- `GET /dashboard`
- `GET /documents`
- `POST /documents`
- `GET /documents/{document_id}`
- `PUT /documents/{document_id}`
- `POST /documents/{document_id}/archive`
- `POST /documents/{document_id}/restore`
- `POST /documents/{document_id}/renew`
- `DELETE /documents/{document_id}`

List and dashboard responses return summary fields and note previews. Detail responses include full notes for edit drawers. Update payloads are independent from create payloads and do not include create-only parent IDs.

## Shared Components Used

The frontend uses the shared Ansiversa shell, generated API client, `AvAuthenticatedPageState`, `AvPageHeader`, `AvInlineFeedback`, `AvCardEmptyState`, `AvPagination`, `AvFormDrawer`, `AvRecordActions`, confirmation dialog helpers, shared cards, and Zustand store helpers.

## Performance Considerations

The module stores compact metadata only. Dashboard and list responses avoid large payloads by returning note previews instead of full notes. Full notes load only through detail endpoints before editing. Tags are stored as a small JSON array in a text field, with a capped list length.

## Current Status

Approved live at version `1.0.0`. Catalog status is `active` / `live`, destination metadata is approved at `20 / 100` with `destination_reviewed_at` set to `2026-07-14`, and the production-configured isolated database migration is verified at Alembic head `20260715_0001_document_expiry_tracker`.

## Known Limitations

- No email, SMS, push, calendar, or background notification delivery.
- No OCR, scanning, file upload, or AI extraction.
- No government, insurer, or renewal portal integration.
- Renewal history is intentionally simple: renewal count and last renewed date.
- Tags are lightweight labels, not a full taxonomy.

## Future Enhancements

- Governed reminder delivery after Partner/Astra approval.
- Optional document attachment support after privacy review.
- OCR extraction only after explicit governance approval.
- Richer renewal timeline if users need historical audit detail.
- CSV export for personal review.

## Current Implementation

The backend uses isolated SQLAlchemy models, Alembic migration `20260715_0001_document_expiry_tracker`, owner-scoped protected routes, repository/service separation, Pydantic request and response schemas, deterministic status calculation, archive/restore/renew actions, and overview metadata. The frontend provides Documents, Expiry Dashboard, and Insights routes using app-local services and Zustand state.
