# Lesson Builder Backend Story

## Purpose

Lesson Builder gives authenticated users a persistent lesson-authoring workflow
for creating lesson plans, arranging lesson sections, and publishing a finished
lesson. The backend owns the lesson and section records so drafts can be edited
until publish and protected afterward.

## Workflow

The API supports a Lessons -> Sections -> Reorder -> Publish workflow. A lesson
plan stores the subject, audience, duration, objective, and publish status.
Sections belong to the lesson, carry a section type, and are ordered by
position. Reorder updates the section sequence. Publish marks the lesson as
published and records `publishedAt`.

## User Journey

A user creates a lesson draft, opens it in the workspace, adds objective,
instruction, activity, assessment, or resource sections, reorders sections, and
publishes the lesson when the structure is ready.

## Database Design

Lesson Builder uses an isolated mini-app database with two tables:

* `LessonPlans`
* `LessonSections`

`LessonPlans` is owner-scoped with `userId` and stores lesson metadata plus
status. `LessonSections` belongs to a lesson through `lessonId`, stores the
section type and content, and keeps explicit `position` values for ordering.
Deleting a lesson cascades its sections.

## API Design

The router is mounted at `/api/v1/lesson-builder`. Lesson list responses return
lesson summaries with section counts. Lesson detail returns the selected lesson
and ordered sections. Section creation uses the lesson route context rather than
accepting a parent ID in the body. Section reorder accepts the ordered section
ID list for the selected lesson.

Published lessons are treated as locked content by service logic: after publish,
lesson updates, section mutations, reorder operations, and repeat publish calls
are rejected so the published lesson remains stable.

## Shared Components Used

The backend follows the shared Ansiversa FastAPI module pattern: isolated
database session, SQLAlchemy models, Pydantic schemas, thin routes,
service-owned logic, current-user auth, and owner-scoped access checks.

## Performance Considerations

The main query patterns are owner-scoped lesson lists, lesson detail navigation,
section lookup by parent, and section ordering. User and parent foreign-key
columns are indexed. Lesson objectives and section content are large text fields
and are not indexed.

## Current Status

The backend implementation is approved live at version `1.0.0`. The parent
Apps catalog stores Lesson Builder as `active` with `launchStatus = live`.

## Known Limitations

V1 does not include collaborative editing, attachments, classroom delivery, or
export formats. Published lessons are locked rather than versioned.

## Future Enhancements

Future versions may add lesson templates, export formats, collaboration,
versioned publishing, and Course Tracker integration.

## Current Implementation

Current version: `1.0.0`

Implemented:

* Owner-scoped lesson plans
* Ordered lesson sections
* Section reorder workflow
* Publish workflow with locked published lessons
* Lesson and section create, update, and delete support before publish
* Current-state story documentation
