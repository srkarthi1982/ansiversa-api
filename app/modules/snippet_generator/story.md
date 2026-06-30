# Snippet Generator Backend Story

## Purpose

Snippet Generator gives each authenticated user an owner-scoped backend for creating, organizing, categorizing, reusing, and managing reusable text or code snippets. The module keeps snippet projects, snippet records, reusable categories, and snippet history in an isolated mini-app database so the parent platform remains focused on shared shell concerns.

## Workflow

Users create snippet projects, define reusable categories inside those projects, add editable snippets, and record history events for revisions, usage, copying, versioning, and archiving. The backend exposes a dashboard endpoint for lightweight workspace initialization and dedicated CRUD endpoints for each long-lived record type.

## User Journey

A signed-in user opens `/snippet-generator/projects`, creates a project for a language or snippet workspace, adds categories, stores snippets under the project, and logs history as snippets are edited or reused. Detail endpoints provide full snippet text only when an edit drawer or detail workflow needs it.

## Database Design

Snippet Generator owns four isolated tables:

* `SnippetProjects` stores project title, language, status, goal, notes, ownership, platform reference, and timestamps.
* `SnippetCategories` stores reusable category names, color hints, descriptions, ownership, project ownership, platform reference, and timestamps.
* `SnippetLibrary` stores editable snippets tied to a project and optional category, including language, status, description, snippet text, usage notes, tags, ownership, platform reference, and timestamps.
* `SnippetHistory` stores snippet-level creation, edit, copy, usage, versioning, and archive events.

Indexes are based on the current query patterns: owner-scoped dashboard/list reads, updated-at ordering, project lookups, category lookups, status filters, and snippet history timelines.

## API Design

The API mounts at `/api/v1/snippet-generator`. Dashboard and list endpoints return summary response models with preview fields. Detail endpoints return complete editable records. Create and update DTOs are separate, and update DTOs do not accept create-only parent IDs such as `projectId`, `categoryId`, or `snippetId`.

Ownership is validated in the service layer for every project, category, snippet, and history operation. Child records must belong to a parent owned by the current user before they can be created, read, updated, or deleted.

## Shared Components Used

The backend follows the established Ansiversa mini-app module structure: `models.py`, `schemas.py`, `repository.py`, `service.py`, `router.py`, `dependencies.py`, `db.py`, `constants.py`, `routes.py`, and an isolated Alembic migration tree.

## Performance Considerations

The dashboard endpoint composes lightweight lists and preview text instead of returning full snippet bodies. Full snippet text, usage notes, project notes, category descriptions, and revision notes are limited to detail responses. Indexes avoid large text fields and focus on owner, parent, category, status, ordering, and timeline access.

## Current Status

Snippet Generator App #040 backend V1 foundation is implemented and remains `comingSoon`. The production isolated database has been migrated to revision `20260630_0001` and verified for schema, indexes, CRUD behavior, overview metadata, and catalog status. The app is not promoted live.

## Known Limitations

The backend stores snippets and workflow history but does not generate snippets with an AI model. Category deletion clears category assignments from snippets instead of deleting the snippets.

## Future Enhancements

Future versions can add snippet generation, syntax highlighting metadata, import/export, snippet search, favorites, and shared team libraries after the V1 workflow is reviewed and approved.

## Current Implementation

The current implementation consists of isolated SQLAlchemy models, Pydantic request/response schemas, repository helpers, service-layer ownership validation, FastAPI routes, app configuration, content overview metadata, and a dedicated Alembic migration under `migrations/snippet-generator`.
