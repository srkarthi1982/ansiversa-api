# Social Caption Generator Backend Story

## Purpose

Social Caption Generator gives each authenticated user an owner-scoped backend for organizing social caption work. The module stores campaign-style projects, editable caption records, reusable caption templates, and caption history without mixing this domain data into the shared platform database.

## Workflow

The backend supports a four-part workflow:

1. Projects capture the campaign brief, platform, audience, tone, status, and private notes.
2. Captions belong to projects and store editable caption text, hashtags, calls to action, and review status.
3. Templates belong to projects and store reusable caption structures with usage notes.
4. History records belong to captions and track generation, edit, approval, publishing, and status-change activity.

## User Journey

A user creates a project for a social campaign or post series, adds captions under that project, saves reusable templates for repeated formats, and records key history events as captions are generated or revised. List endpoints return compact summaries for fast workspace screens, while detail endpoints return the complete fields needed by edit drawers.

## Database Design

The module uses an isolated database connection and migration path. Persistent tables are:

- `CaptionProjects`
- `SocialCaptions`
- `CaptionTemplates`
- `CaptionHistory`

Every table includes `ownerId`, optional `platformId`, `createdAt`, and `updatedAt`. `SocialCaptions` and `CaptionTemplates` reference `CaptionProjects`; `CaptionHistory` references `SocialCaptions`. Deletes remove dependent child records inside the service/repository boundary before removing the parent record.

Indexes are limited to Phase-1 query patterns: owner-scoped lists sorted by update time, parent lookups, status/platform dashboard filters, and caption history timeline access. No large text fields are indexed.

## API Design

The module is mounted at `/api/v1/social-caption-generator`.

Available resources:

- `GET /dashboard`
- CRUD `/projects`
- CRUD `/captions`
- CRUD `/templates`
- CRUD `/history`

Create DTOs include required parent IDs where the record is created under a parent. Update DTOs exclude create-only parent IDs, so edits cannot move captions, templates, or history records between parents. Services validate ownership and parent-child relationships before creating, reading, updating, or deleting records.

## Shared Components Used

Backend shared platform services used by this module:

- FastAPI router registration through the platform app.
- Auth dependency through `get_current_user`.
- SQLAlchemy session timing through the shared timing helpers.
- Alembic isolated migration structure used by owner-scoped mini apps.
- Content overview metadata JSON consumed by the platform overview API.

## Performance Considerations

Dashboard and list responses are lightweight and use preview fields instead of full campaign briefs, caption text, template bodies, or revision notes. Detail endpoints return complete editable records only when the frontend opens a record for viewing or editing. Indexes target the current user-facing query paths and avoid speculative text search or blob-style indexing.

## Current Status

The backend is implemented as an active, coming-soon mini-app module. It is ready for local isolated migration, CRUD verification, API type generation, and Astra review. The module is not promoted live by this implementation.

## Known Limitations

The backend stores generated and edited caption content but does not call an AI generation provider directly. History records are manually created by the current workflow. Search, bulk publishing, scheduling, and social network integrations are outside the current implementation.

## Future Enhancements

Future work can add AI caption generation, template-assisted drafting, platform-specific validation, hashtag suggestions, scheduled publishing integrations, analytics feedback, and richer history automation when the product direction is approved.

## Current Implementation

The current implementation consists of isolated SQLAlchemy models, Pydantic request/response schemas, repository helpers, service-layer ownership validation, FastAPI routes, module dependencies, app configuration, content overview metadata, and a dedicated Alembic migration under `migrations/social-caption-generator`.
