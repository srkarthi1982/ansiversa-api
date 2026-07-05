# Wellness and Goal Planner Destination

## Destination

Wellness and Goal Planner should become a calm personal planning workspace that helps users connect wellness goals, daily or periodic reflection, and progress review without pretending to be a medical or therapeutic authority.

## Product Identity

The mature product answers:

- What wellness areas matter to me right now?
- Which goals am I actively working on?
- What progress have I made?
- What patterns appear in my reflections?

It should remain a planning and reflection tool, not a diagnosis, treatment, coaching, or health-monitoring system.

## Mature Workflow

The intended mature workflow is:

1. Define wellness areas.
2. Create measurable or descriptive goals.
3. Track goal progress.
4. Capture reflections and mood context.
5. Review progress and recurring patterns.
6. Adjust goals as personal priorities change.

## Architecture Direction

The app should stay DB-backed and owner-scoped. Areas, goals, and reflections remain the core records. Future reminder, template, insight, or export features should extend these records without creating a separate wellness platform inside the mini app.

## Integration Boundaries

Possible future handoffs:

- Mood Journal may provide reflection context.
- Fitness Tracker may provide activity context.
- Medicine Reminder and Health Report Organizer may remain separate health/medical utilities.

Wellness and Goal Planner should not absorb medical records, medication schedules, fitness logs, or family task management.

## Data Principles

User-authored descriptions, reflections, and notes are private planning data. List and dashboard views should continue using previews and summaries. Full text should be loaded only when users view or edit a record.

## Journey Progress

Current Journey Progress: 35 / 100

Status: Workflow Ready

Reviewed: 2026-07-05

V1 establishes the core owner-scoped workflow. The remaining journey is about deeper review, habit cadence, reminders, and optional insight layers after approval.
