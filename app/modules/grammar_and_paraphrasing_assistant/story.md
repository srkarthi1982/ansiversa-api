# Grammar and Paraphrasing Assistant

## Purpose

Grammar and Paraphrasing Assistant gives authenticated Ansiversa users a focused workspace for saving source text, running lightweight grammar/paraphrase passes, and reviewing generated results.

## Workflow

Users create a grammar project, edit the original text, run a correction or paraphrase action with an optional tone, review the latest result, and revisit job history.

## User Journey

The user starts from the public overview, signs in for workflow pages, creates a project, opens the editor, generates a placeholder V1 result, compares original/corrected/paraphrased text, and returns later through Projects, Results, or History.

## Database Design

The module owns an isolated `GRAMMAR_AND_PARAPHRASING_ASSISTANT_DATABASE_URL` database. Tables are `GrammarProjects`, `GrammarResults`, and `GrammarJobs`. Project records are long-lived and editable. Results are generated records. Jobs preserve the workflow timeline. Owner and parent indexes support current list, detail, result, and history navigation paths without indexing large text fields.

## API Design

The router is mounted at `/api/v1/grammar-and-paraphrasing-assistant`. It exposes protected dashboard, project CRUD, project run, result list/detail, and history list endpoints. List and dashboard payloads use previews and counters; detail endpoints return full text only when the editor or result view needs it.

## Shared Components Used

The frontend uses the shared authenticated page state, page header, stat grid, empty state, inline feedback, form drawer, cards, confirmation dialog, and record actions.

## Performance Considerations

Dashboard and list endpoints do not return full source, corrected, or paraphrased text. The V1 generation step is deterministic and local, with no external AI provider, NLP package, export library, or heavy dependency.

## Current Status

Approved Live. App #042 is promoted to `active` / `live` with version `1.0.0` after Astra/Partner review, production database migration, parent catalog promotion, and overview metadata sync.

## Known Limitations

V1 placeholder generation only normalizes spacing, capitalization, punctuation, and tone-framed paraphrase text. It is not a real grammar engine or AI provider integration.

## Future Enhancements

Future versions may add AI provider-backed correction, richer tone controls, diff highlighting, reusable style presets, export, and deeper readability diagnostics after review.

## Current Implementation

The backend uses SQLAlchemy models, Pydantic schemas, a repository/service split, protected FastAPI routes, and an isolated Alembic migration at revision `20260702_0001`. The frontend consumes generated API types through a module service and Zustand store.
