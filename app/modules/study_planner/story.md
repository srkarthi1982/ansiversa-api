# Study Planner Backend Story

## Purpose

Study Planner gives authenticated users a persistent study planning workflow
around plans, actionable tasks, and dated study logs. The backend owns the
study records so progress can be reviewed across sessions and summarized for
the app dashboard.

## Workflow

The API supports a Plans -> Tasks -> Logs -> Review workflow. Plans define the
subject, goal, date range, and current status. Tasks belong to plans and carry
priority, due date, and completion status. Logs record dated study effort and
can optionally link to a specific task. Review and dashboard endpoints aggregate
the same records into progress metrics.

## User Journey

A user creates a study plan, adds tasks under that plan, records study sessions
with minutes and reflections, and opens the review view to understand completed
tasks, active plans, total minutes, completion rate, and recent logs.

## Database Design

Study Planner uses an isolated mini-app database with three tables:

* `StudyPlans`
* `StudyPlanTasks`
* `StudyLogs`

`StudyPlans` is owner-scoped with `ownerId` and stores the long-lived planning
record. `StudyPlanTasks` belongs to a plan and repeats `ownerId` for efficient
owner-scoped list queries. `StudyLogs` belongs to a plan, can optionally belong
to a task, and records historical study effort. Deleting a plan cascades its
tasks and logs.

## API Design

The router is mounted at `/api/v1/study-planner`. Dashboard returns the current
plans, tasks, logs, and review summary in one lightweight startup payload.
Dedicated list endpoints also exist for plans, tasks, logs, and review. Create
and update schemas are separate so task and plan updates do not resend
create-only parent fields unless the endpoint explicitly supports them.

Service logic validates that tasks and logs belong to the authenticated owner.
Review responses return aggregate counts and recent logs rather than raw
database records beyond what the frontend needs.

## Shared Components Used

The backend follows the shared Ansiversa FastAPI module pattern: isolated
database session, SQLAlchemy models, Pydantic schemas, thin routes,
service-owned logic, current-user auth, and owner-scoped access checks.

## Performance Considerations

The main query patterns are owner-scoped plan lists, owner-scoped task/log
lists, parent plan lookups, status filters, and recent-log ordering. Owner and
parent foreign-key columns are indexed. Large goal, notes, and reflection text
are not indexed.

## Current Status

The backend implementation is approved live at version `1.0.0`. The parent
Apps catalog stores Study Planner as `active` with `launchStatus = live`.

## Known Limitations

V1 does not schedule calendar events, send reminders, rebalance workload, or
sync with external learning systems. Logs are historical records and are created
rather than edited in the current API.

## Future Enhancements

Future versions may add reminders, calendar export, smarter workload planning,
subject analytics, and deeper links to Course Tracker or Quiz performance.

## Current Implementation

Current version: `1.0.0`

Implemented:

* Owner-scoped study plans
* Plan tasks with priority and status
* Historical study logs
* Dashboard and review aggregate responses
* Create, update, and delete support for plans and tasks
* Current-state story documentation
