# AI Notes Summarizer Backend Story

## Purpose

AI Notes Summarizer lets authenticated users save long note documents and
produce structured summaries they can revisit later. The backend owns source
documents, generated summary records, and summary job records so the frontend
can keep list screens lightweight while still offering full document detail.

## Workflow

The API supports a Documents -> Summaries -> History -> Detail workflow. A user
creates a document from pasted source text, requests a summary for that
document, sees summaries in history, and opens document detail to review the
source text, generated summaries, and job records.

## User Journey

A user creates a notes document with a title and source text. The backend saves
the full source content, creates a deterministic summary record when requested,
and returns summary metadata for history. When the user opens a document, the
detail endpoint returns the document, its summaries, and associated jobs.

## Database Design

AI Notes Summarizer uses an isolated mini-app database with three tables:

* `NotesDocuments`
* `NoteSummaries`
* `SummaryJobs`

`NotesDocuments` stores owner-scoped source material. `NoteSummaries` stores
generated summary content, key points, action items, and length metadata linked
to a document. `SummaryJobs` records job status and input/output context for
summary generation. Source text and summary text remain text fields and are not
used as indexing targets.

## API Design

The router is mounted at `/api/v1/ai-notes-summarizer`. Document list responses
return IDs, titles, summary counts, and timestamps only. Document detail returns
the full source text, summaries, and jobs. Summary list responses are separate
from document lists so history can show generated output without loading every
source document.

Create and update DTOs are separate, trim user text, enforce source length, and
forbid unexpected fields. All data is owner-scoped through `ownerId`.

## Shared Components Used

The backend follows the shared Ansiversa FastAPI module pattern: isolated
database session, SQLAlchemy models, Pydantic schemas, thin routes,
service-owned logic, current-user auth, and owner-scoped access checks.

## Performance Considerations

The primary query patterns are owner document lists, owner summary history,
document detail navigation, and document-to-summary lookup. The database indexes
owner fields and parent foreign keys. Large source and summary bodies are only
returned when the frontend needs the detail payload.

## Current Status

The backend implementation is approved live at version `1.0.0`. The parent
Apps catalog stores AI Notes Summarizer as `active` with `launchStatus = live`.

## Known Limitations

V1 persists note documents and summary output, but it does not provide
multi-document synthesis, citation extraction, collaboration, or external file
ingestion.

## Future Enhancements

Future versions may add batch summarization, uploaded documents, richer insight
types, exports, and Research Assistant integration.

## Current Implementation

Current version: `1.0.0`

Implemented:

* Owner-scoped note documents
* Document create, update, delete, list, and detail APIs
* Summary creation and summary history APIs
* Summary job records
* Lightweight list/detail response separation
* Current-state story documentation
