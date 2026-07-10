# Meal Planner Story

## Purpose

Meal Planner gives authenticated users a practical workspace for saving reusable recipes, creating weekly meal plans, and scheduling meals on a calendar.

## Workflow

The protected backend workflow is mounted at `/api/v1/meal-planner`. Users manage recipes, create meal plans, and add meal plan entries that connect a plan, date, meal type, and optional recipe.

## User Journey

A user creates recipes with ingredients, instructions, serving size, and timing. The user creates a meal plan for a week, then schedules entries for breakfast, lunch, dinner, or snacks. Entries may reference a saved recipe or use a custom meal title when the meal does not need a full recipe record.

## Database Design

Meal Planner uses an isolated database configured by `MEAL_PLANNER_DATABASE_URL`. The module owns `Recipes`, `MealPlans`, and `MealPlanEntries`. Every table stores `userId` for owner scoping. Meal plan entries belong to meal plans and are deleted with their parent plan. Recipe deletion clears recipe references from entries before deleting the recipe so a meal plan can keep custom entry context without owning a deleted recipe.

## API Design

The router exposes protected dashboard, recipe CRUD, meal plan CRUD, and meal plan entry CRUD endpoints. List endpoints support pagination, search, filtering, sorting, and lightweight summaries. Detail endpoints return full editable fields. Entry update payloads intentionally exclude create-only `mealPlanId`; entries cannot be reassigned to another plan through the update API. Entry create and update requests require either a saved recipe reference or a non-empty custom title.

## Shared Components Used

The backend follows the established FastAPI mini-app pattern: isolated `db.py`, thin `router.py`, compatibility `routes.py`, SQLAlchemy models, Pydantic schemas, repository helpers, service-owned business logic, current-user dependencies, and generated OpenAPI contracts.

## Performance Considerations

Indexes cover owner-scoped list queries, updated-at ordering, weekly plan dates, entry dates, plan lookups, and recipe lookups. Large text fields such as ingredients, instructions, and notes are not indexed. Dashboard metrics use dedicated count queries, and dashboard/list responses return previews and counts instead of full recipe bodies.

## Current Status

Approved Live at version 1.0.0 after Astra/Partner approval, production Apps row promotion, destination metadata sync, legacy production schema repair, FK repair, and manual workflow verification. The backend has protected owner-scoped APIs, isolated migrations through `20260710_0004`, dashboard summaries, CRUD endpoints for all planned tables, lightweight/detail response separation, and generated frontend API contracts.

## Known Limitations

V1 does not include grocery list generation, nutrition calculations, pantry inventory, shopping integrations, recipe import from websites, AI-generated meal plans, reminders, collaboration, exports, or cross-app recommendations.

## Future Enhancements

Future versions may add grocery lists, pantry-aware planning, dietary preference profiles, recipe import, calendar reminders, nutrition summaries, exports, and governed AI-assisted meal suggestions after Partner/Astra approval.

## Current Implementation

Meal Planner is a DB-backed mini-app module with owner-scoped CRUD APIs, isolated migration files, lightweight response schemas, dashboard summary calculation, and protected frontend workflow routes. The parent Apps catalog stores Meal Planner as `active` with `launchStatus = live` and version `1.0.0`.
