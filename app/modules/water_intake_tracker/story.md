# Water Intake Tracker Story

## Purpose

Water Intake Tracker helps authenticated users keep a private hydration record. It focuses on manual water intake logging, personal goals, and practical summaries.

## Workflow

Users set a daily goal, add water entries, edit or delete corrections, search/filter history, and review dashboard and insight summaries.

## Database Design

The module owns an isolated database configured by `WATER_INTAKE_TRACKER_DATABASE_URL`.

- `WaterGoals` stores one owner-scoped daily goal and preferred unit.
- `WaterEntries` stores owner-scoped intake records with date, time, amount, unit, drink type, and notes.

The version table is `water_intake_tracker_alembic_version`.

## API Design

The API is mounted at `/api/v1/water-intake-tracker` and provides dashboard, insights, goal read/update, drink type listing, entry CRUD, paginated entry search/filter/sort, and summary endpoints.

## Current Status

The V1 workflow is ready for manual verification. The app remains `comingSoon` with `version = null` and has not been promoted live.

## Known Limitations

No reminders, wearable integrations, health recommendations, or medical guidance are included in V1.

## Future Enhancements

Potential future work may include reminders, quick-add presets, exports, and optional cross-app wellness summaries after governance review.
