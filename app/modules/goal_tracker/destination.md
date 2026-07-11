# Goal Tracker Destination

## Purpose

Goal Tracker should mature into the personal goals workspace for Ansiversa: a place to define outcomes, break them into measurable checkpoints, record progress, and review what needs attention.

## Destination Status

Approved v1.0

## Final Product Vision

Goal Tracker should become Ansiversa's personal goal evidence system: a calm place to turn broad intentions into goals, milestones, and check-ins that show progress over time without becoming enterprise OKR software, guilt-based habit tracking, or automated coaching.

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

## Target Users

- Individuals setting personal, learning, career, finance, health-adjacent, or project goals.
- Students and self-learners working toward exams, courses, or skill milestones.
- Professionals, freelancers, and founders who need lightweight visibility without enterprise OKR overhead.
- Users who already track tasks or habits but need a higher-level goal layer.
- Coaches, mentors, or managers who discuss progress without needing team administration features.

## Core User Problems

- Goals become stale when they are vague, too large, or disconnected from daily behavior.
- Users need progress evidence without maintaining a heavy project management system.
- Reminder overload, streak guilt, and over-gamification can reduce trust.
- Users need to distinguish goals, milestones, check-ins, tasks, and habits.
- AI goal breakdown can help only when the user remains in control of the plan and meaning.

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

## Weekly Return Value

Users return weekly to update progress, log check-ins, review blocked or high-priority goals, adjust milestones, and decide which goals need attention before motivation fades.

## Success Criteria

- Users can capture a goal quickly before momentum is lost.
- Check-ins take seconds and preserve useful progress history.
- Dashboards make attention needs visible without guilt-based messaging.
- Goal, milestone, and check-in concepts remain clear.
- Future AI, reminders, and cross-app context remain opt-in and reviewable.

## Current V1 Position

V1 is Workflow Ready with owner-scoped goals, milestones, check-ins, dashboard summaries, and protected frontend workflow routes. It does not yet include reminders, recurring plans, exports, collaboration, automation, or AI-assisted review.

## Future Enhancements

- Goal templates and recurring milestones.
- Calendar and reminder integration.
- Richer trend visualizations.
- Cross-app goal context after governance review.
- AI-assisted goal review with visible assumptions and user approval.

## Non Goals

- Do not become enterprise OKR administration.
- Do not make health, financial, legal, employment, or performance guarantees.
- Do not punish missed check-ins through guilt-heavy streak mechanics.
- Do not automate goal meaning or next actions without user approval.
- Do not directly own task, project, fitness, meal, or finance records from other apps.

## Guiding Principles

- The user owns the goal, progress meaning, and next action.
- Progress feedback should be concrete, calm, and revisable.
- Templates, reminders, and AI should reduce setup friction, not remove user control.
- Cross-app context should support review without creating hidden coupling.

## Governance Notes

Astra: Approved on 2026-07-05.
