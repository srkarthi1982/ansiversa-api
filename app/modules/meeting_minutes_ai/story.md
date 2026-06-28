# Meeting Minutes AI Backend Story

## Purpose

Meeting Minutes AI owns the persistent records that turn meeting context into notes, action items, and reviewable summaries. The backend exists to keep meeting follow-up owner-scoped, editable, and split into purpose-built records instead of one large unstructured document.

## Workflow

The backend supports a Meetings -> Notes -> Action Items -> Summaries workflow. Meetings are the parent records. Notes and transcripts, action items, and summaries belong to a meeting and are protected by owner-scoped service logic.

## User Journey

An authenticated user creates a meeting, records participants and context, adds notes or transcript text, tracks action items with owners and due dates, and creates a summary with decisions and risks. The dashboard returns meeting records, previews of long notes and summaries, action items, and counts for open actions, reviewed meetings, and transcripts.

## Database Design

The module uses four persistent tables:

* `MeetingMinutesMeetings` stores the meeting title, date, participants, context, and status.
* `MeetingMinutesNotes` stores note or transcript content under a meeting.
* `MeetingMinutesActionItems` stores follow-up title, owner, due date, and status under a meeting.
* `MeetingMinutesSummaries` stores summary text, decisions, and risks under a meeting.

`ownerId` indexes support user-owned dashboard and list queries. `meetingId` indexes support parent-child navigation for notes, action items, and summaries. Long note, transcript, summary, decision, and risk fields are not indexed because V1 does not provide text search.

## API Design

The router exposes `/api/v1/meeting-minutes-ai/dashboard`, meeting CRUD, note create/detail/update/delete, action item CRUD, and summary create/detail/update/delete routes. Dashboard responses use `contentPreview`, `summaryPreview`, `decisionsPreview`, and `risksPreview` for long fields. Detail endpoints return complete note and summary content only when the frontend opens the corresponding workflow.

## Shared Components Used

The module uses the shared FastAPI module pattern: isolated database dependency, SQLAlchemy models, Pydantic schemas, thin routes, service-owned business logic, current-user authentication, owner-scoped access checks, and generated OpenAPI contracts for the frontend.

## Performance Considerations

The API separates list previews from full detail records so large notes, transcripts, and summaries do not inflate the dashboard payload. Indexes match owner list queries, meeting-child lookups, and dashboard status counts. The module avoids speculative full-text indexes until the product explicitly introduces meeting search.

## Current Status

The backend implementation is live at version `1.0.0`. The parent Apps catalog stores Meeting Minutes AI as `active` with `launchStatus = live`.

## Known Limitations

V1 stores structured meeting records and manually entered notes, action items, and summaries. It does not include live transcription, audio ingestion, speaker diarization, calendar import, external task sync, or automated AI summary generation from recordings.

## Future Enhancements

Future versions may add transcript imports, AI-assisted summaries, calendar and conferencing integrations, action item export, attendee tagging, search, and project management sync.

## Current Implementation

Current version: `1.0.0`

Implemented:

* Isolated Meeting Minutes AI backend module
* `MeetingMinutesMeetings` persistence
* `MeetingMinutesNotes` persistence
* `MeetingMinutesActionItems` persistence
* `MeetingMinutesSummaries` persistence
* Dashboard route with preview responses and counters
* Meeting CRUD routes
* Note create, detail, update, and delete routes
* Action item CRUD routes
* Summary create, detail, update, and delete routes
* Owner-scoped service access
* Query-pattern indexes for owner and meeting lookups
* Current-state story documentation
