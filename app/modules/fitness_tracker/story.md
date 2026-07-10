# Fitness Tracker Story

## Purpose

Fitness Tracker gives authenticated users a non-clinical workspace for creating repeatable fitness activities, logging completed sessions, and reviewing recent activity.

## Workflow

The protected workflow starts at `/fitness-tracker/activities`. Users create activities, add logs under those activities, and review summary signals on Insights.

## User Journey

A user creates an activity such as a walk, gym session, mobility routine, sport, or other activity. The user records completed sessions with date, duration, intensity, effort, optional distance, and notes. Insights summarize total activity, weekly minutes, recent logs, and activity mix.

## Database Design

Fitness Tracker uses an isolated database configured by `FITNESS_TRACKER_DATABASE_URL`. The module owns `FitnessActivities` and `FitnessLogs`. Every table stores `userId` for owner scoping. Logs belong to activities and are deleted with their parent activity.

## API Design

The router is mounted at `/api/v1/fitness-tracker`. It exposes protected dashboard, activity CRUD, and log CRUD endpoints. Dashboard and list responses return lightweight summaries and previews. Detail endpoints return full editable fields. Log update schemas intentionally exclude create-only `activityId`, so editing a log does not support parent activity reassignment.

## Shared Components Used

The backend follows the established FastAPI mini-app pattern: isolated `db.py`, thin `router.py`, compatibility `routes.py`, SQLAlchemy models, Pydantic schemas, repository helpers, service-owned business logic, current-user dependencies, and generated OpenAPI contracts.

## Performance Considerations

Indexes cover owner-scoped lists, activity type filters, parent activity lookups, log dates, and updated-at ordering. Large text notes are not indexed. List responses use previews and counts instead of full notes.

## Current Status

Workflow Ready Draft. The backend has protected owner-scoped APIs, isolated migration `20260710_0001`, dashboard summaries, activity CRUD, log CRUD, lightweight/detail response separation, and generated frontend API contracts. The app has not been promoted live.

## Known Limitations

V1 does not include wearable sync, calorie estimates, health metrics, medical advice, workout prescription, AI coaching, recurring reminders, exports, collaboration, or cross-app automation. All activity records are manually entered.

## Future Enhancements

Future versions may add trend charts, exports, recurring activity reminders, and approved cross-app summaries. AI-assisted review requires separate governance and must not make medical or outcome-guarantee claims.

## Current Implementation

Fitness Tracker is a DB-backed mini-app module with owner-scoped CRUD APIs, isolated migration files, lightweight response schemas, dashboard summary calculation, and protected frontend routes for Activities, Logs, and Insights. The parent Apps catalog remains `active` with `launchStatus = comingSoon` and version `null` until review and promotion approval.
