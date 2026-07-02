# Creative Title Generator

## Purpose

Creative Title Generator gives authenticated Ansiversa users a focused workspace for saving title briefs, generating lightweight placeholder title options, and reviewing previous generation history.

## Workflow

Users create a title project with a topic, audience, and language, open the generator, choose generation type and style, generate title options, review scored results, and revisit previous generations through History.

## User Journey

The user starts from the public overview, signs in for workflow pages, creates a project, opens the generator, produces a small list of V1 title ideas, reviews the generated titles with placeholder scores, and returns later through Projects, Results, or History.

## Database Design

The module owns an isolated `CREATIVE_TITLE_GENERATOR_DATABASE_URL` database. Tables are `TitleProjects`, `GeneratedTitles`, and `TitleJobs`. Projects are long-lived editable briefs. Generated titles are immutable output records. Jobs preserve the generation timeline. Owner, parent, status, and created/updated indexes support current list, detail, result, and history navigation paths without indexing large text fields.

## API Design

The router is mounted at `/api/v1/creative-title-generator`. It exposes protected dashboard, project CRUD, project generation, generated title list/detail, and history list endpoints. List and dashboard payloads use previews and counters. Detail endpoints return the full project topic only when the editor or title detail view needs it.

## Shared Components Used

The frontend uses the shared authenticated page state, page header, stat grid, empty state, inline feedback, form drawer, cards, confirmation dialog, and record actions.

## Performance Considerations

Dashboard and list endpoints do not return full project topic text unless a screen needs it. The V1 title generation step is deterministic and local, with no external AI provider, NLP package, export library, or heavy dependency.

## Current Status

Approved Live. App #043 is promoted to `active` / `live` with version `1.0.0` after Astra/Partner review, production database migration to revision `20260702_0002`, parent catalog promotion, and overview metadata sync.

## Known Limitations

V1 placeholder generation uses deterministic templates based on project topic, audience, generation type, style, and optional keywords. It is not a real AI title engine.

## Future Enhancements

Future versions may add AI provider-backed generation, richer title scoring, reusable brief presets, favorite-title selection, A/B title variants, and deeper SEO diagnostics after review.

## Current Implementation

The backend uses SQLAlchemy models, Pydantic schemas, a repository/service split, protected FastAPI routes, and an isolated Alembic migration. The frontend consumes generated API types through a module service and Zustand store.
