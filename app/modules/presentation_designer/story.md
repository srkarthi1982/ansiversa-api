# Presentation Designer Backend Story

## Purpose

Presentation Designer stores owner-scoped presentation workspaces, ordered
slides, reusable assets, and review activity for the Presentation Designer mini
app.

## Workflow

The backend supports a protected workflow from projects to slides, assets, and
review. Users create a presentation project, add ordered slides, collect
project-level assets, and log review, export, or presentation activity.

## User Journey

A signed-in user opens the app, creates a presentation project for an audience,
adds slides in order, stores reusable visual or text assets, and records review
events as the deck moves from draft to review to ready.

## Database Design

The isolated Presentation Designer database contains:

* `PresentationProjects`
* `PresentationSlides`
* `PresentationAssets`
* `PresentationReviewHistory`

Every table has an `ownerId` column. Slides and assets belong to projects.
Review history entries can reference a project or stand alone as general deck
activity.

## API Design

The module is mounted at `/api/v1/presentation-designer`. Dashboard responses
return lightweight summaries for projects, slides, assets, and review history.
Detail endpoints return full editable project, slide, or asset records. Long
slide body text, speaker notes, asset descriptions, and source text are excluded
from dashboard and list responses.

## Shared Components Used

The backend follows shared Ansiversa patterns for FastAPI routers, Pydantic
request and response schemas, SQLAlchemy models, isolated session management,
and owner-scoped service functions.

## Performance Considerations

The dashboard uses summary responses and avoids large text fields. Phase-1
indexes support owner-updated project lists, project-status filters,
project-slide ordering, project-asset ordering, asset type filtering, and
project review timelines.

## Current Status

The backend is workflow ready for protected local review. The app remains
`active`, `comingSoon`, and has no version value.

## Known Limitations

The backend stores presentation planning data, slide text, asset references, and
review activity. It does not render slide files, export PowerPoint or PDF
artifacts, store binary uploads, or run production migration promotion.

## Future Enhancements

Future versions can add template libraries, generated slide previews, export
rendering, richer asset handling, presenter notes tooling, and approval
workflows.

## Current Implementation

The implementation includes isolated SQLAlchemy models, an isolated database
session, an isolated Alembic configuration, initial migration, CRUD routes for
projects/slides/assets/review history, dashboard summaries, detail responses
for editable records, owner checks for every record, and overview metadata for
the Presentation Designer mini app.
