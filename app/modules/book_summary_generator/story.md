# Book Summary Generator Backend Story

## Purpose

Book Summary Generator helps authenticated users organize books or chapter excerpts, create summary records, add personal notes, and retain summary revision history. The backend keeps this writing data in an isolated mini-app database so book-summary records remain owner-scoped and separate from parent platform data.

## Workflow

The API supports a Books -> Summaries -> Notes -> History workflow. A user saves a book collection record, creates one or more summaries for that book, adds personal notes or highlights to a summary, and records history entries for revisions and review activity.

## User Journey

A signed-in user opens the app, creates a book record with source text or chapter notes, adds a generated or manually written summary, captures observations and highlights, and reviews historical changes as the summary evolves.

## Database Design

The module owns four tables: `BookCollections`, `BookSummaries`, `SummaryNotes`, and `SummaryHistory`. Each table includes `ownerId`, optional `platformId`, `createdAt`, and `updatedAt`. `BookSummaries` belongs to `BookCollections`; `SummaryNotes` and `SummaryHistory` belong to `BookSummaries`.

## API Design

The module is mounted at `/api/v1/book-summary-generator`. Dashboard and list endpoints return lightweight summary responses with previews and counters. Detail endpoints return complete editable records. Create and update DTOs are separate, and update DTOs avoid create-only parent reassignment for summaries, notes, and history.

## Shared Components Used

The backend uses the shared auth dependency for current-user ownership, the shared timing session infrastructure, and the standard FastAPI router/service/repository layering used by current Platform Foundation V1 mini apps.

## Performance Considerations

Summary responses avoid returning large source text, full summaries, key points, note bodies, highlights, descriptions, and revision notes. Phase-1 indexes cover owner-scoped lists, updated sorting, parent lookups, status dashboards, summary type filters, note filters, and history timelines without indexing large text columns.

## Current Status

The backend is implemented as an isolated coming-soon mini-app API. It is ready for local migration, OpenAPI type generation, frontend integration, and review. Production migration and live promotion are intentionally not part of the current status.

## Known Limitations

The current backend stores summary data supplied by the frontend. It does not call an AI model, parse uploaded files, fetch book metadata, or generate summaries automatically.

## Future Enhancements

Future versions may add AI-assisted summary generation, file import, chapter extraction, citation support, exportable reading notes, and integration with other learning mini apps.

## Current Implementation

The module contains explicit models, schemas, repository functions, service ownership checks, protected routes, isolated database configuration, Alembic migration assets, and current story documentation for App #036.
