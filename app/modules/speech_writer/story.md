# Speech Writer Backend Story

## Purpose

Speech Writer gives each authenticated user an owner-scoped backend for planning, drafting, editing, and reviewing speeches. The module stores event-oriented projects, editable speech drafts, reusable templates, and revision or delivery history without mixing this domain data into the shared platform database.

## Workflow

1. Projects capture the occasion, event date, audience, tone, purpose, status, and private notes.
2. Speeches belong to projects and store speaker, duration, key message, draft text, and readiness status.
3. Templates belong to projects and preserve reusable speech structures for similar occasions.
4. History records belong to speeches and track drafting, editing, review, delivery, and status-change activity.

## User Journey

A user creates a project for an event or speaking need, adds one or more speech drafts under that project, saves reusable templates, and records history as the speech is drafted, reviewed, or delivered. List and dashboard endpoints return compact summaries for scanning, while detail endpoints return complete editable fields only when the frontend opens a record.

## Database Design

The module owns four persistent tables:

- `SpeechProjects`
- `Speeches`
- `SpeechTemplates`
- `SpeechHistory`

Every table includes `ownerId`, optional `platformId`, `createdAt`, and `updatedAt`. `Speeches` and `SpeechTemplates` reference `SpeechProjects`; `SpeechHistory` references `Speeches`. Deletes remove dependent child records inside the service/repository boundary before removing parent records.

Indexes are limited to Phase-1 query patterns: owner-scoped lists sorted by update time, parent lookups, status filters, event-date review, and speech history timeline access. Large text fields such as purpose, key message, speech text, template text, and revision notes are not indexed.

## API Design

The module is mounted at `/api/v1/speech-writer`.

Routes:

- GET `/dashboard`
- CRUD `/projects`
- CRUD `/speeches`
- CRUD `/templates`
- CRUD `/history`

Dashboard and list responses use summary schemas with preview fields. Detail endpoints return full editable records. Create DTOs include required parent IDs where a child record is created under a parent. Update DTOs exclude create-only parent IDs, so edits cannot move speeches, templates, or history records between parents. Services validate ownership and parent-child relationships before creating, reading, updating, or deleting records.

## Shared Components Used

Backend shared platform services used by this module:

- FastAPI router registration through the platform app.
- Authenticated current-user dependency from the auth module.
- SQLAlchemy session and engine timing helpers.
- Pydantic schemas with generated OpenAPI contracts.
- Content overview metadata JSON consumed by the platform overview API.

## Performance Considerations

Dashboard and list responses are lightweight and use preview fields instead of full purpose text, speech text, template bodies, or revision notes. Detail endpoints return complete editable records only when needed. Indexes target the current user-facing query paths and avoid speculative full-text search.

## Current Status

Speech Writer App #038 backend V1 foundation is approved live at version `1.0.0`. The parent Apps catalog stores Speech Writer as `active` with `launchStatus = live`, and the production isolated database migration has been applied and verified.

## Known Limitations

The backend stores user-authored speech records and templates but does not generate speech text with AI, export speeches, or automate revision history. History records are manually created by the workflow.

## Future Enhancements

Future versions may add AI-assisted drafting, outline generation, delivery rehearsal notes, export/download support, template-assisted generation, richer revision automation, and speech-readiness review scoring after Partner/Astra approval.

## Current Implementation

The current implementation consists of isolated SQLAlchemy models, Pydantic request/response schemas, repository helpers, service-layer ownership validation, FastAPI routes, module dependencies, app configuration, content overview metadata, and a dedicated Alembic migration under `migrations/speech-writer`.
