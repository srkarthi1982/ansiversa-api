# Interview Scheduler

## Purpose

Interview Scheduler helps users plan interview schedules, track interview rounds, and manage calendar events.

## Workflow

The V1 workflow moves through schedules, rounds, and calendar events. Schedules hold the candidate and role context. Rounds describe each interview step. Calendar events keep timing and reminders visible. Interview history remains backend-ready for a future workflow but is not exposed in V1.

## User Journey

A signed-in user creates an interview schedule, adds one or more interview rounds, and places events on the calendar.

## Database Design

The app uses an isolated `INTERVIEW_SCHEDULER_DATABASE_URL` database. Tables are `InterviewSchedules`, `InterviewRounds`, `InterviewCalendarEvents`, and `InterviewHistory`. Every record includes `ownerId` and `platformId`. Child records use indexed foreign keys for schedule and round relationships.

## API Design

The module is mounted at `/api/v1/interview-scheduler`. Dashboard and list endpoints return lightweight summaries. Detail endpoints return complete editable records. Create and update DTOs are separate. Service operations validate ownership and parent-child relationships before writes.

## Shared Components Used

The backend follows shared FastAPI routing, auth dependency, SQLAlchemy session timing, Pydantic schema, and isolated Alembic migration patterns used by Ansiversa mini apps.

## Performance Considerations

Phase-1 indexes cover owner-scoped lists, schedule-linked rounds, calendar date ordering, status filters, priority filters, and future history timeline lookups. Long text fields are excluded from text indexes.

## Current Status

The backend V1 foundation is approved live at version `1.0.0`. The parent Apps catalog stores Interview Scheduler as `active` with `launchStatus = live`.

## Known Limitations

The backend stores manual scheduling records only. It does not send external calendar invites, email reminders, or AI-generated interview preparation.

## Future Enhancements

Future versions may add calendar integrations, notification reminders, interview preparation prompts, candidate pipeline analytics, and exportable schedule summaries.

## Current Implementation

Current implementation includes isolated database configuration, models, schemas, service functions, authenticated routes, migration files, overview metadata, production Apps row promotion, and module story documentation.
