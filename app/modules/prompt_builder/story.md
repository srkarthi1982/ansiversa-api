# Prompt Builder Backend Story

## Purpose

Prompt Builder gives each authenticated user an owner-scoped backend for creating, organizing, reusing, categorizing, and versioning AI prompts. The module keeps prompt projects, prompt records, reusable templates, and prompt history in an isolated mini-app database so the parent platform remains responsible only for shared shell concerns.

## Workflow

Users create prompt projects, add editable prompts to those projects, save reusable templates, and record history events for prompt revisions, testing, usage, and versioning. The backend exposes a dashboard endpoint for lightweight workspace initialization and dedicated CRUD endpoints for each long-lived record type.

## User Journey

A signed-in user opens `/prompt-builder/projects`, creates a project for a prompt category or workspace, adds prompts under that project, saves reusable templates, and logs history as prompts are edited or used. Detail endpoints provide the full editable body only when a drawer or detail workflow needs it.

## Database Design

Prompt Builder owns four isolated tables:

* `PromptProjects` stores project title, category, status, goal, notes, ownership, platform reference, and timestamps.
* `PromptLibrary` stores editable prompts tied to a project, including category, model target, status, prompt text, context text, output format, tags, ownership, platform reference, and timestamps.
* `PromptTemplates` stores reusable template text and usage notes tied to a project.
* `PromptHistory` stores prompt-level revision, testing, usage, versioning, and archive events.

Indexes are based on the current query patterns: owner-scoped dashboard/list reads, updated-at ordering, parent lookups, status filters, and prompt history timelines.

## API Design

The API mounts at `/api/v1/prompt-builder`. Dashboard and list endpoints return summary response models with preview fields. Detail endpoints return complete editable records. Create and update DTOs are separate, and update DTOs do not accept create-only parent IDs such as `projectId` or `promptId`.

Ownership is validated in the service layer for every project, prompt, template, and history operation. Child records must belong to a parent owned by the current user before they can be created, read, updated, or deleted.

## Shared Components Used

The backend follows the established Ansiversa mini-app module structure: `models.py`, `schemas.py`, `repository.py`, `service.py`, `router.py`, `dependencies.py`, `db.py`, `constants.py`, `routes.py`, and an isolated Alembic migration tree.

## Performance Considerations

The dashboard endpoint composes lightweight lists and preview text instead of returning full prompt bodies. Full prompt text, context, output format, template text, notes, and revision notes are limited to detail responses. Indexes avoid large text fields and focus on owner, parent, status, ordering, and timeline access.

## Current Status

Prompt Builder App #039 backend V1 foundation is implemented and remains `comingSoon`. The local isolated migration is available for verification. No production migration has been run, and the app is not promoted live.

## Known Limitations

The backend stores prompt records and workflow history but does not generate prompts with an AI model. Prompt testing results are represented as history events rather than a separate execution-results table.

## Future Enhancements

Future versions can add prompt execution, saved variables, prompt scoring, import/export, template sharing, and AI-assisted prompt refinement after the V1 workflow is reviewed and approved.

## Current Implementation

The current implementation consists of isolated SQLAlchemy models, Pydantic request/response schemas, repository helpers, service-layer ownership validation, FastAPI routes, app configuration, content overview metadata, and a dedicated Alembic migration under `migrations/prompt-builder`.
