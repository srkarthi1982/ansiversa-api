# Goal Tracker Story

## Purpose

Goal Tracker gives authenticated users a focused workspace for creating long-lived goals, breaking them into milestones, and recording dated progress check-ins.

## Workflow

The protected workflow starts at `/goal-tracker/goals`. Users create and edit goals, duplicate useful goal structures, delete goals they no longer need, add milestones, record check-ins, and review progress signals.

## User Journey

A user creates a goal with category, priority, status, target date, and progress. The user adds milestones as checkpoints and logs check-ins with progress, mood, and notes. Review screens summarize active, paused, completed, high-priority, and recently checked-in goals.

## Database Design

Goal Tracker uses an isolated database configured by `GOAL_TRACKER_DATABASE_URL`. The module owns `GoalTrackerGoals`, `GoalTrackerMilestones`, and `GoalTrackerCheckIns`. Every table stores `userId` for owner scoping. Milestones and check-ins belong to goals and are deleted with their parent goal.

## API Design

The router is mounted at `/api/v1/goal-tracker`. It exposes protected dashboard, goal CRUD, goal duplicate, milestone CRUD, and check-in CRUD endpoints. Dashboard and list responses return lightweight summaries. Detail endpoints return full editable fields. Milestone and check-in update schemas intentionally exclude create-only `goalId`.

## Shared Components Used

The backend follows the established FastAPI mini-app pattern: isolated `db.py`, thin `router.py`, compatibility `routes.py`, SQLAlchemy models, Pydantic schemas, repository helpers, service-owned business logic, current-user dependencies, and generated OpenAPI contracts.

## Performance Considerations

Indexes cover owner-scoped goal lists, status/priority/category filters, target dates, milestone lookups by goal, and check-in history by goal/date. Large text fields are not indexed. List responses use previews and counts instead of full descriptions and notes.

## Current Status

Approved Live at version 1.0.0 after Astra/Partner approval, production Apps row promotion, destination metadata sync, isolated Goal Tracker database migration, manual workflow verification, and duplicate icon contrast polish. The backend has protected owner-scoped APIs, isolated migration `20260705_0001_goal_tracker`, dashboard summaries, goal CRUD/duplicate/delete, milestone CRUD, check-in CRUD, lightweight/detail response separation, and generated frontend API contracts.

## Known Limitations

V1 does not include reminders, recurring goals, calendar sync, collaboration, automated progress scoring, AI coaching, exports, or cross-app goal recommendations. Progress is manually entered by the user.

## Future Enhancements

Future versions may add recurring milestones, reminders, goal templates, calendar integration, richer progress charts, cross-app goal suggestions, and AI-assisted review after governance approval.

## Current Implementation

Goal Tracker is a DB-backed mini-app module with owner-scoped CRUD APIs, isolated migration files, lightweight response schemas, dashboard summary calculation, and approved live routing. The parent Apps catalog stores Goal Tracker as `active` with `launchStatus = live` and version `1.0.0`.
