# Interview Scheduler

## Purpose

Interview Scheduler helps users plan interview schedules, track interview rounds, manage calendar events, and record completed interview outcomes.

## Workflow

The V1 workflow moves through schedules, rounds, calendar events, and history. Schedules hold the candidate and role context. Rounds describe each interview step. Calendar events keep timing and reminders visible. History records completed interviews, outcomes, summaries, and next steps.

## User Journey

A signed-in user creates an interview schedule, adds one or more interview rounds, places events on the calendar, and records outcomes after interviews are completed.

## Database Design

The app uses an isolated `INTERVIEW_SCHEDULER_DATABASE_URL` database. Tables are `InterviewSchedules`, `InterviewRounds`, `InterviewCalendarEvents`, and `InterviewHistory`. Every record includes `ownerId` and `platformId`. Child records use indexed foreign keys for schedule and round relationships.

## API Design

The module is mounted at `/api/v1/interview-scheduler`. Dashboard and list endpoints return lightweight summaries. Detail endpoints return complete editable records. Create and update DTOs are separate. Service operations validate ownership and parent-child relationships before writes.

## Shared Components Used

The backend follows shared FastAPI routing, auth dependency, SQLAlchemy session timing, Pydantic schema, and isolated Alembic migration patterns used by Ansiversa mini apps.

## Performance Considerations

Phase-1 indexes cover owner-scoped lists, schedule-linked rounds, calendar date ordering, status filters, priority filters, and history timeline lookups. Long text fields are excluded from text indexes.

## Current Status

The backend V1 foundation is implemented and remains `comingSoon`.

## Known Limitations

The backend stores manual scheduling records only. It does not send external calendar invites, email reminders, or AI-generated interview preparation.

## Future Enhancements

Future versions may add calendar integrations, notification reminders, interview preparation prompts, candidate pipeline analytics, and exportable schedule summaries.

## Current Implementation

Current implementation includes isolated database configuration, models, schemas, service functions, authenticated routes, migration files, overview metadata, and module story documentation.
