# Vehicle Document Tracker Story

## Purpose

Vehicle Document Tracker gives users a focused personal workspace for vehicle paperwork metadata and renewal awareness. The app exists because vehicle registrations, insurance, inspections, warranties, and related references often live across emails, folders, and memory.

## Workflow

Users create vehicles, define or reuse document types, add document records, and review expiry and renewal dates. The workflow is metadata-only and intentionally avoids file upload, OCR, government records, insurance portals, and legal-compliance promises.

## User Journey

1. Add a vehicle with registration details and notes.
2. Confirm the default document types or create a custom type.
3. Add document records with issue, expiry, reminder, authority, status, and notes.
4. Search, filter, sort, archive, restore, or delete records.
5. Review insights for upcoming renewals, expired documents, and recently updated records.

## Database Design

The module owns an isolated database configured by `VEHICLE_DOCUMENT_TRACKER_DATABASE_URL`. Tables are `VehicleDocumentsVehicles`, `VehicleDocumentTypes`, and `VehicleDocuments`. Alembic uses `vehicle_document_tracker_alembic_version`.

## API Design

The API prefix is `/api/v1/vehicle-document-tracker`. Protected endpoints cover vehicles, document types, documents, dashboard, and insights. Every record is owner-scoped by `userId`; system document types are shared read-only defaults while custom types are user-owned.

## Shared Components Used

The frontend uses the standard protected workflow wrapper, generated API types, Zustand store lifecycle, Ansiversa cards, feedback states, empty states, and overview metadata rendering.

## Performance Considerations

List responses return the fields visible in the workflow. Detail endpoints support record editing. Indexes cover owner lists, vehicle/type filters, status, archive filters, expiry/reminder dates, document numbers, and update sorting.

## Current Status

Workflow Ready and queued for manual verification. The app remains `active / comingSoon / version null`. No live promotion has been performed.

## Known Limitations

V1 stores document metadata only. It does not store uploaded files, scan documents, verify legal status, renew documents, or connect to government or insurance systems.

## Future Enhancements

Future versions may add secure document vault integration, notification delivery, export tools, richer household sharing, and stronger date-review workflows after Partner approval.

## Current Implementation

The current implementation includes full CRUD for vehicles, document types, and document records, date validation, owner isolation, archive/restore behavior, search/filter/sort, dashboard summaries, insights, metadata, and production migration readiness.
