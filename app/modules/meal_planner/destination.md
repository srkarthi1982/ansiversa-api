# Meal Planner Destination

## Purpose

Meal Planner should mature into the personal and household food planning workspace for Ansiversa: a place to keep reusable recipes, plan a week, review scheduled meals, and eventually connect meal planning with grocery and wellness workflows.

## Destination Status

Approved v1.0

## Final Product Vision

Meal Planner should become Ansiversa's flexible weekly food planning workspace: a private place to keep reusable recipes, schedule meals, adapt plans when life changes, and eventually support grocery or household workflows without becoming a diet, allergy, or nutrition authority.

## Journey Progress

Current Position: 28 / 100
Destination: 100 / 100
Remaining Journey: 72 / 100

This estimate describes product maturity, not feature completion. Meal Planner has an approved DB-backed V1 with recipe CRUD, meal plan CRUD, calendar entry CRUD, dashboard summaries, owner-scoped persistence, protected routes, and overview routing. The remaining journey includes grocery lists, pantry support, recipe import, nutrition context, reminders after governance, exports, and careful governance for AI or cross-app recommendations.

## Mature Product Direction

The mature product should help users reduce everyday meal decision fatigue while preserving flexibility. It should stay practical, privacy-aware, and user-authored rather than becoming a prescriptive diet, health, or nutrition authority.

## Target Users

- Individuals trying to reduce daily meal decisions.
- Families and households coordinating a flexible weekly food plan.
- Busy professionals, students, and budget-conscious users building reusable meal rotations.
- Users with preferences, dislikes, or dietary constraints who need planning structure without medical claims.
- Users who save recipes but need a calendar and future grocery workflow.

## Core User Problems

- Recipes, weekly plans, grocery ideas, and household schedules often live in separate places.
- Users need flexible meals because real-life plans change.
- Grocery lists and ingredient cleanup are high-value but trust-sensitive future work.
- Some users want planning without weight-loss, macro, or diet framing.
- AI meal suggestions can be useful only when assumptions are visible and user-approved.

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

## Weekly Return Value

Users return weekly to choose recipes, fill the meal calendar, adjust changed plans, and prepare future grocery or household decisions from the week ahead.

## Success Criteria

- A user can plan a week without entering a full recipe for every meal.
- Saved recipes and custom meals both remain first-class.
- Calendar entries remain easy to edit when plans change.
- Future grocery or AI features reduce planning effort without hiding assumptions.
- The product avoids diet, allergy, medical, or nutrition authority claims.

## Current V1 Position

V1 is approved live with owner-scoped recipes, meal plans, calendar entries, dashboard summaries, protected frontend workflow routes, generated API types, and isolated production migrations. It does not yet include grocery lists, pantry inventory, shopping integrations, nutrition analysis, reminders, collaboration, exports, or AI-assisted planning.

## Future Enhancements

- Grocery list generation from planned meals.
- Pantry and staple tracking.
- Recipe import and duplicate detection.
- Dietary preference profiles.
- Nutrition summaries with clear non-medical boundaries.
- Calendar reminders and exports.
- Cross-app household planning after governance review.
- AI-assisted meal suggestions with visible assumptions and user approval.

## Non Goals

- Do not present meal plans as diet, medical, allergy, or nutrition advice.
- Do not scrape or import recipe sites without legal and technical approval.
- Do not require every meal entry to be tied to a full recipe.
- Do not store wellness, health, or shopping data owned by other apps.
- Do not generate AI plans without user-reviewed assumptions.

## Guiding Principles

- Planning should stay flexible enough for real households.
- User-authored meals and recipes should remain editable.
- Grocery, pantry, nutrition, and AI features must be opt-in and governed.
- Meal Planner should reduce decision fatigue without becoming prescriptive.

## Governance Notes

Astra: Approved on 2026-07-10.

Partner: Approved Meal Planner live promotion after manual workflow verification.

Codex: Fixed production legacy schema drift, verified production recipes, plans, and calendar workflows, and prepared live promotion metadata.
