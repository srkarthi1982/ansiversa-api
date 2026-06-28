# Research Assistant Backend Story

## Purpose

Research Assistant gives authenticated users a persistent place to organize a
research question, collect notes, save references, and move the topic through a
simple research status lifecycle. The backend owns the research data so notes
and references remain available across sessions and devices.

## Workflow

The API supports a Topics -> Notes -> References -> Status workflow. A topic is
the parent record. Notes and references are created under that topic and are
ordered by position. The status endpoint moves the topic through the current
research states: `collecting`, `reviewing`, and `complete`.

## User Journey

A user creates a topic with a title, optional research question, and optional
summary. From topic detail, the user adds notes and references, edits or
deletes those child records, and changes the topic status as the research moves
from collection to review.

## Database Design

Research Assistant uses an isolated mini-app database with four tables:

* `ResearchTopics`
* `ResearchNotes`
* `ResearchReferences`
* `ResearchJobs`

`ResearchTopics` is owner-scoped with `userId`. Notes, references, and jobs
belong to a topic through `topicId`. Topic deletion cascades child records so
orphaned notes and references are not left behind. Large note and reference
body fields stay out of summary intent and are returned from detail workflows.

## API Design

The router is mounted at `/api/v1/research-assistant`. Topic list responses
return topic summaries with note and reference counts. Topic detail returns the
selected topic plus its notes and references. Create and update DTOs are
separate, trim user text, and forbid unexpected fields.

Child mutations use dedicated note and reference endpoints. The service layer
verifies ownership through the parent topic before returning, updating, or
deleting child records.

## Shared Components Used

The backend follows the shared Ansiversa FastAPI module pattern: isolated
database session, SQLAlchemy models, Pydantic schemas, thin routes,
service-owned logic, current-user auth, and owner-scoped access checks.

## Performance Considerations

The persistent query pattern is owner-scoped topic listing, topic detail
navigation, and parent-child lookup for notes and references. The database
indexes `userId` on topics and `topicId` on child tables. Large text fields are
not indexed.

## Current Status

The backend implementation is approved live at version `1.0.0`. The parent
Apps catalog stores Research Assistant as `active` with `launchStatus = live`.

## Known Limitations

V1 stores manually entered research material. It does not crawl sources,
generate citations, run external research jobs, or synthesize long-form reports.

## Future Enhancements

Future versions may add citation formatting, source import, AI synthesis,
research job execution, and handoff into note summarization or writing modules.

## Current Implementation

Current version: `1.0.0`

Implemented:

* Owner-scoped research topics
* Topic notes and references
* Topic status updates
* Topic detail response with child records
* Create, update, and delete support for long-lived records
* Current-state story documentation
