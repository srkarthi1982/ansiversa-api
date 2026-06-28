# Concept Explainer Backend Story

## Purpose

Concept Explainer gives authenticated users a persistent way to break a topic
into explanation steps and self-check questions. The backend owns the concept
structure, ordered explanation records, check records, and review status so the
learning workflow can be reopened and refined over time.

## Workflow

The API supports a Concepts -> Steps -> Checks -> Review workflow. A concept is
the parent record. Steps explain the concept in ordered parts. Checks capture
questions and expected answers. The review endpoint marks a concept as reviewed
and records the review timestamp.

## User Journey

A user creates a concept with a title, topic, and optional description. From
concept detail, the user adds explanation steps and check questions, edits or
deletes saved records, and marks the concept reviewed after studying it.

## Database Design

Concept Explainer uses an isolated mini-app database with four tables:

* `Concepts`
* `ConceptSteps`
* `ConceptChecks`
* `ConceptJobs`

`Concepts` is owner-scoped with `userId` and stores review state. Steps and
checks belong to a concept through `conceptId` and keep explicit `position`
values for ordered display. Jobs are reserved for concept-related background
work. Deleting a concept cascades its child records.

## API Design

The router is mounted at `/api/v1/concept-explainer`. Concept list responses
return summary fields and counts. Concept detail returns the selected concept,
steps, and checks. Step and check mutations use dedicated child endpoints, while
the review endpoint updates concept status without requiring the frontend to
send a full concept update payload.

Create and update DTOs are separate, trim text, enforce field lengths, and
forbid unexpected fields. Service functions validate owner access before
returning or mutating parent and child records.

## Shared Components Used

The backend follows the shared Ansiversa FastAPI module pattern: isolated
database session, SQLAlchemy models, Pydantic schemas, thin routes,
service-owned logic, current-user auth, and owner-scoped access checks.

## Performance Considerations

The main query patterns are owner-scoped concept lists, concept detail
navigation, and parent-child lookups for steps and checks. The database indexes
`userId` on concepts and `conceptId` on child tables. Large explanation and
answer text is not indexed.

## Current Status

The backend implementation is approved live at version `1.0.0`. The parent
Apps catalog stores Concept Explainer as `active` with `launchStatus = live`.

## Known Limitations

V1 stores manually authored concepts, steps, and checks. It does not generate
explanations automatically, schedule spaced review, or map concepts into a full
curriculum.

## Future Enhancements

Future versions may add AI explanation drafts, adaptive checks, spaced review,
topic collections, and links to course or study-planner workflows.

## Current Implementation

Current version: `1.0.0`

Implemented:

* Owner-scoped concepts
* Ordered explanation steps
* Ordered self-check questions
* Concept reviewed status
* Create, update, and delete support for long-lived records
* Current-state story documentation
