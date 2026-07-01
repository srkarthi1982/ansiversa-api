# AI Translator and Tone Fixer Backend Story

## Purpose

AI Translator and Tone Fixer gives each authenticated user an owner-scoped backend for creating, organizing, reusing, and reviewing AI translations and tone fixes. The module keeps translation projects, translation records, reusable templates, and translation history in an isolated mini-app database so the parent platform remains responsible only for shared shell concerns.

## Workflow

Users create translation projects, add editable translations to those projects, save reusable templates, and record history events for translation creation, translation, tone fixing, review, export, and archiving. The backend exposes a dashboard endpoint for lightweight workspace initialization and dedicated CRUD endpoints for each long-lived record type.

## User Journey

A signed-in user opens `/ai-translator-and-tone-fixer/projects`, creates a project for a language pair and tone, adds translations under that project, saves reusable templates, and logs history as translations are reviewed or exported. Detail endpoints provide the full editable body only when a drawer or detail workflow needs it.

## Database Design

AI Translator and Tone Fixer owns four isolated tables:

* `TranslationProjects` stores project title, source language, target language, tone, status, goal, notes, ownership, platform reference, and timestamps.
* `Translations` stores editable translations tied to a project, including source language, target language, tone, status, source text, translated text, notes, ownership, platform reference, and timestamps.
* `TranslationTemplates` stores reusable template text, usage notes, language pair, tone, ownership, platform reference, and timestamps tied to a project.
* `TranslationHistory` stores translation-level creation, translation, tone-fix, review, export, and archive events.

Indexes are based on the current query patterns: owner-scoped dashboard/list reads, updated-at ordering, parent lookups, status filters, and translation history timelines.

## API Design

The API mounts at `/api/v1/ai-translator-and-tone-fixer`. Dashboard and list endpoints return summary response models with preview fields. Detail endpoints return complete editable records. Create and update DTOs are separate, and update DTOs do not accept create-only parent IDs such as `projectId` or `translationId`.

Ownership is validated in the service layer for every project, translation, template, and history operation. Child records must belong to a parent owned by the current user before they can be created, read, updated, or deleted.

## Shared Components Used

The backend follows the established Ansiversa mini-app module structure: `models.py`, `schemas.py`, `repository.py`, `service.py`, `router.py`, `dependencies.py`, `db.py`, `constants.py`, `routes.py`, and an isolated Alembic migration tree.

## Performance Considerations

The dashboard endpoint composes lightweight lists and preview text instead of returning full translation bodies. Full source text, translated text, template text, notes, and revision notes are limited to detail responses. Indexes avoid large text fields and focus on owner, parent, status, ordering, and timeline access.

## Current Status

AI Translator and Tone Fixer App #041 backend V1 foundation is approved live at version `1.0.0` after Astra review, manual QA, production DB migration verification, and Partner approval. The production isolated database is verified at revision `20260701_0001`, and the parent Apps catalog stores the app as `active` with `launchStatus = live`.

## Known Limitations

The backend stores translation records and workflow history but does not generate translations with an AI model. Translation and tone-fix results are represented as user-authored records and history events rather than a separate execution-results table.

## Future Enhancements

Future versions can add translation execution, saved variables, translation scoring, import/export, template sharing, and AI-assisted translation refinement after the V1 workflow is reviewed and approved.

## Current Implementation

The current implementation consists of isolated SQLAlchemy models, Pydantic request/response schemas, repository helpers, service-layer ownership validation, FastAPI routes, app configuration, content overview metadata, and a dedicated Alembic migration under `migrations/ai-translator-and-tone-fixer`.
