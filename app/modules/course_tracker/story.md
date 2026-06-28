# Course Tracker Backend Story

## Purpose

Course Tracker gives authenticated users a persistent way to track courses,
course modules, and study progress logs. The backend owns the course structure
and progress history so the app can summarize completion and learning effort
without relying on browser state.

## Workflow

The API supports a Courses -> Modules -> Progress Logs -> Review workflow.
Courses are the parent records. Modules break a course into ordered units.
Progress logs record dated study effort and can optionally reference a module.
Dashboard and review endpoints summarize the current course state.

## User Journey

A user creates a course with provider, category, goal, dates, and status. The
user adds modules, records progress logs with minutes and reflections, and
opens the review view to inspect active courses, completed courses, module
completion, total minutes, completion rate, and recent progress.

## Database Design

Course Tracker uses an isolated mini-app database with three tables:

* `Courses`
* `CourseModules`
* `CourseProgressLogs`

`Courses` is owner-scoped with `ownerId`. `CourseModules` belongs to a course
and stores sequence and status. `CourseProgressLogs` belongs to a course, can
optionally belong to a module, and records historical progress. Owner IDs are
duplicated on child records for efficient user-scoped dashboard and list
queries. Deleting a course cascades its modules and logs.

## API Design

The router is mounted at `/api/v1/course-tracker`. Dashboard returns courses,
modules, progress logs, and review metrics for the frontend startup state.
Dedicated endpoints support course and module CRUD, progress-log creation, list
views, and review summaries. Create and update DTOs are separate, so update
payloads do not blindly resubmit create-only parent IDs.

Service logic validates owner access and parent-child relationships before
mutating modules or logs.

## Shared Components Used

The backend follows the shared Ansiversa FastAPI module pattern: isolated
database session, SQLAlchemy models, Pydantic schemas, thin routes,
service-owned logic, current-user auth, and owner-scoped access checks.

## Performance Considerations

The main query patterns are owner-scoped course lists, owner-scoped module/log
lists, parent course lookups, status filters, sequence ordering, and recent-log
ordering. Owner and parent foreign-key columns are indexed. Goal, notes,
summary, and reflection text are not indexed.

## Current Status

The backend implementation is approved live at version `1.0.0`. The parent
Apps catalog stores Course Tracker as `active` with `launchStatus = live`.

## Known Limitations

V1 does not import data from learning management systems, calculate grades, or
sync assignments from external course providers. Progress logs are created as
historical records.

## Future Enhancements

Future versions may add LMS imports, due-date reminders, richer analytics,
grade tracking, and Study Planner integration.

## Current Implementation

Current version: `1.0.0`

Implemented:

* Owner-scoped courses
* Ordered course modules
* Historical progress logs
* Dashboard and review aggregate responses
* Create, update, and delete support for courses and modules
* Current-state story documentation
