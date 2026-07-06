# Meal Planner Destination

## Purpose

Meal Planner should mature into the personal and household food planning workspace for Ansiversa: a place to keep reusable recipes, plan a week, review scheduled meals, and eventually connect meal planning with grocery and wellness workflows.

## Destination Status

Workflow Ready V1

## Journey Progress

Current Position: 28 / 100
Destination: 100 / 100
Remaining Journey: 72 / 100

This estimate describes product maturity, not feature completion. Meal Planner has a useful DB-backed Workflow Ready V1 with recipe CRUD, meal plan CRUD, calendar entry CRUD, dashboard summaries, owner-scoped persistence, protected routes, and overview routing. The remaining journey includes grocery lists, pantry support, recipe import, nutrition context, reminders after governance, exports, and careful governance for AI or cross-app recommendations.

## Mature Product Direction

The mature product should help users reduce everyday meal decision fatigue while preserving flexibility. It should stay practical, privacy-aware, and user-authored rather than becoming a prescriptive diet, health, or nutrition authority.

## Core Capabilities

- Create, edit, and delete reusable recipes.
- Create, edit, archive, and delete weekly meal plans.
- Add, edit, and delete dated meal plan entries.
- Schedule breakfast, lunch, dinner, and snacks.
- Use saved recipes or custom meal titles.
- Review lightweight summaries and full editable details.
- Keep user-owned planning data isolated by account.

## Trust Boundaries

Meal Planner stores user-authored food planning data. V1 does not make medical, diet, allergy, nutrition, or weight-loss recommendations. Future nutrition, AI, grocery, health, or wellness integrations must be opt-in, reviewable, and clearly separated from professional advice.

## Ecosystem Fit

Meal Planner can later connect with Wellness and Goal Planner, Goal Tracker, Fitness Tracker, Expense Tracker, Shopping/Grocery workflows, and Family Task Planner, but those integrations should happen through approved APIs rather than direct database ownership.

## Current V1 Position

V1 is Workflow Ready with owner-scoped recipes, meal plans, calendar entries, dashboard summaries, protected frontend workflow routes, generated API types, and an isolated migration. It does not yet include grocery lists, pantry inventory, shopping integrations, nutrition analysis, reminders, collaboration, exports, or AI-assisted planning.

## Future Enhancements

- Grocery list generation from planned meals.
- Pantry and staple tracking.
- Recipe import and duplicate detection.
- Dietary preference profiles.
- Nutrition summaries with clear non-medical boundaries.
- Calendar reminders and exports.
- Cross-app household planning after governance review.
- AI-assisted meal suggestions with visible assumptions and user approval.

## Governance Notes

Astra: Workflow Ready implementation prepared on 2026-07-06. No live promotion has been performed.
