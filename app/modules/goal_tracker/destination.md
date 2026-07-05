# Goal Tracker Destination

## Purpose

Goal Tracker should mature into the personal goals workspace for Ansiversa: a place to define outcomes, break them into measurable checkpoints, record progress, and review what needs attention.

## Destination Status

Approved v1.0

## Journey Progress

Current Position: 34 / 100
Destination: 100 / 100
Remaining Journey: 66 / 100

This estimate describes product maturity, not feature completion. Goal Tracker
has a useful DB-backed Workflow Ready V1 with goal CRUD, duplicate/delete,
milestones, check-ins, dashboard summaries, filters, owner-scoped persistence,
overview routing, production database migration, and manual QA verification.
The remaining journey includes templates, recurring plans, reminders after
governance, richer trends, exports, and careful governance for AI or cross-app
recommendations.

## Mature Product Direction

The mature product should help users convert intentions into maintained goals with clear progress evidence. It should stay practical, owner-scoped, and reviewable rather than becoming an automated coaching system without user control.

## Core Capabilities

- Create, edit, duplicate, archive, and delete goals.
- Add milestones under each goal.
- Record dated progress check-ins.
- Review active, paused, completed, and high-priority goals.
- Preserve user notes and progress history.
- Keep list responses lightweight and detail views complete.

## Trust Boundaries

Goal Tracker stores user-authored personal planning data. AI suggestions, reminders, notifications, and cross-app recommendations must remain opt-in and reviewable. The app should not make health, financial, legal, or employment claims from goal content.

## Ecosystem Fit

Goal Tracker can later connect with Wellness and Goal Planner, Task Prioritizer, Project Tracker, Fitness Tracker, Meal Planner, Savings Goal Planner, and Career Planner, but those integrations should happen through approved APIs rather than direct database ownership.

## Current V1 Position

V1 is Workflow Ready with owner-scoped goals, milestones, check-ins, dashboard summaries, and protected frontend workflow routes. It does not yet include reminders, recurring plans, exports, collaboration, automation, or AI-assisted review.

## Future Enhancements

- Goal templates and recurring milestones.
- Calendar and reminder integration.
- Richer trend visualizations.
- Cross-app goal context after governance review.
- AI-assisted goal review with visible assumptions and user approval.

## Governance Notes

Astra: Approved on 2026-07-05.
