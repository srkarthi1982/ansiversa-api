# Wellness and Goal Planner

## Purpose

Wellness and Goal Planner gives authenticated users a focused workspace for defining wellness areas, setting goals, and recording dated reflections. The module exists to connect long-term wellness intentions with lightweight progress tracking without becoming a medical, therapy, or fitness-prescription product.

## Workflow

The V1 workflow is Goals -> Areas -> Reflections. Goals are the primary entry point because users usually start by deciding what they want to improve. Areas group related goals. Reflections preserve dated context and optional goal links so users can review what happened over time.

## User Journey

A signed-in user creates wellness areas such as rest, movement, nutrition, or mindfulness. The user creates goals with status, priority, progress, optional area, and optional target date. The user records reflections with date, mood, notes, and optional related goal. Deleting an area keeps goals saved with `areaId = null`; deleting a goal keeps reflections saved with `goalId = null`.

## Database Design

The module uses an isolated database configured by `WELLNESS_AND_GOAL_PLANNER_DATABASE_URL` and an isolated Alembic version table, `wellness_and_goal_planner_alembic_version`.

Tables:

- `WellnessAreas`: user-scoped wellness categories with text IDs, `userId`, name, description, optional icon, optional sort order, and timestamps.
- `WellnessGoals`: user-scoped long-lived goals with text IDs, optional `areaId`, `userId`, title, description, target date, status, priority, `progressPercent`, and timestamps.
- `WellnessReflections`: user-scoped dated reflections with text IDs, `userId`, optional `areaId`, optional `goalId`, `entryDate`, reflection body, mood, optional energy level, notes, and creation timestamp.

Indexes support user-scoped lists, area/goal parent lookups, status filtering, target-date review, entry-date filtering, and updated sorting where the table stores update timestamps. Large text fields are not indexed.

## API Design

The API is mounted at `/api/v1/wellness-and-goal-planner` and requires the current authenticated user. Routes remain thin and delegate ownership checks and business rules to `service.py`.

Endpoints include:

- `GET /dashboard`
- CRUD for `/areas`
- CRUD for `/goals`
- CRUD for `/reflections`

List and dashboard responses return lightweight summaries with preview fields. Detail endpoints return complete fields needed by edit drawers. Create and update DTOs are separate and forbid extra fields.

## Shared Components Used

The backend follows the established FastAPI mini-app module structure: isolated `db.py`, thin `router.py`, compatibility `routes.py`, SQLAlchemy models, Pydantic schemas, service-owned logic, current-user dependencies, and generated OpenAPI contracts.

## Performance Considerations

Dashboard payloads include only fields needed by the current V1 screens. Large descriptions, reflection text, and notes are previewed in lists and loaded fully through detail endpoints before editing. Query-pattern indexes cover user-facing owner lists and filters without indexing text/blob columns.

## Current Status

Workflow Ready V1. The module has protected owner-scoped APIs, isolated migration, dashboard summaries, area CRUD, goal CRUD, reflection CRUD, lightweight/detail response separation, and generated frontend API contracts.

## Known Limitations

V1 does not send reminders, integrate calendars, provide medical guidance, generate wellness recommendations with AI, sync wearable data, or calculate health scores. Progress is user-entered.

## Future Enhancements

Future versions may add gentle reminders, richer weekly review summaries, goal templates, streak views, export, and cross-app handoffs after Partner/Astra approval.

## Current Implementation

The module stores user-authored wellness planning records only. It preserves platform boundaries by owning app-specific persistence and APIs while authentication, routing shell, navigation, and global user context remain outside the mini app.
