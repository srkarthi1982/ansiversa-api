# Smart Textbook Scanner Backend Story

## Purpose

Smart Textbook Scanner gives authenticated users a persistent workflow for
capturing textbook scan projects, organizing pages, extracting notes, and
reviewing study material. The backend owns scans, pages, extracted notes, and
review metrics for the live scanner workflow.

## Workflow

The API supports a Scans -> Pages -> Extracted Notes -> Review workflow. Scans
are the parent records. Pages belong to scans and store page text plus
extraction status. Extracted notes belong to a scan and page. Dashboard and
review endpoints summarize scan progress and recent extracted notes.

## User Journey

A user creates a scan with subject, source, and goal, adds textbook pages,
updates page text or status after extraction, creates extracted notes from a
page, and opens review to inspect extraction rate, active/reviewed scans, total
pages, and recent notes.

## Database Design

Smart Textbook Scanner uses an isolated mini-app database with three tables:

* `TextbookScans`
* `TextbookPages`
* `ExtractedNotes`

`TextbookScans` is owner-scoped. `TextbookPages` belongs to a scan and repeats
owner scope for user list queries. `ExtractedNotes` belongs to both scan and
page so review/history can navigate from notes back to source pages. Deleting a
scan cascades its pages and notes.

## API Design

The router is mounted at `/api/v1/smart-textbook-scanner`. Dashboard returns
scans, page summaries, notes, and review metrics. Page detail is separate from
page list data so long page text is loaded only when needed. Scan and page
create/update schemas are separate, and note creation validates the selected
scan/page relationship.

## Shared Components Used

The backend follows the shared Ansiversa FastAPI module pattern: isolated
database session, SQLAlchemy models, Pydantic schemas, thin routes,
service-owned logic, current-user auth, and owner-scoped access checks.

## Performance Considerations

The main query patterns are owner-scoped scan lists, page lists by owner and
scan, page detail navigation, note history, status counts, and recent-note
ordering. Owner and parent foreign-key columns are indexed. Page text, key
points, and summaries are not indexed.

## Current Status

The backend implementation is approved live at version `1.0.0`. The parent
Apps catalog stores Smart Textbook Scanner as `active` with
`launchStatus = live`.

## Known Limitations

V1 stores scan structure, page text, and extracted notes. It does not provide
file uploads, OCR processing, image storage, or automated note extraction.

## Future Enhancements

Future versions may add OCR ingestion, file uploads, image storage, concept
linking, exports, and AI-assisted extraction.

## Current Implementation

Current version: `1.0.0`

Implemented:

* Owner-scoped textbook scans
* Textbook pages with extraction status
* Extracted notes linked to scan and page
* Dashboard and review aggregate responses
* Scan and page create, update, and delete support
* Extracted note creation workflow
* Current-state story documentation
