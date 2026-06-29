# Career Planner

## Purpose

Career Planner helps a signed-in user organize career goals, roadmap workstreams, measurable milestones, and review activity in one owner-scoped workflow.

## Workflow

The protected workflow starts at `/career-planner/goals`, where users create the main career outcomes they want to pursue. Roadmaps define focused workstreams for each goal, milestones break a roadmap into ordered checkpoints, and review history records planning, completion, pause, or archive events.

## User Journey

A user creates a career goal, adds one or more roadmaps under that goal, adds milestones under each roadmap, and logs review activity as the plan changes. Goals, roadmaps, milestones, and review entries support saved-record editing. The overview Explore action points directly to the goals page so the editable workflow is the first destination.

## Database Design

Career Planner uses an isolated database configured by `CAREER_PLANNER_DATABASE_URL`. The module owns `CareerGoals`, `CareerRoadmaps`, `CareerMilestones`, and `CareerReviewHistory`. Every table stores `ownerId` so records are scoped to the authenticated user. Roadmaps belong to goals, milestones belong to roadmaps, and review history can optionally reference a goal.

## API Design

The router is mounted at `/api/v1/career-planner`. Dashboard and list responses return lightweight summaries with counts, status, ordering, titles, previews, and timestamps. Detail endpoints return full editable records including notes or summary text. Create DTOs accept parent IDs where needed, and update DTOs omit create-only parent IDs. Review update keeps the original optional goal association fixed and only accepts title, action type, and notes.

## Shared Components Used

The frontend workflow uses `AvAppOverviewPage`, `AvAuthenticatedPageState`, `AvPageHeader`, `AvFormDrawer`, `AvRecordActions`, `AvEmptyState`, `AvInlineFeedback`, `AvStatGrid`, and the shared confirmation dialog.

## Performance Considerations

List responses avoid large text fields. The migration adds Phase-1 indexes for owner/timestamp lookups, parent-child lookups, status filtering, and ordering by `sortOrder`.

## Current Status

Career Planner is approved live at version `1.0.0`. The parent Apps catalog stores Career Planner as `active` with `launchStatus = live`.

## Known Limitations

Career Planner does not generate AI plans, export documents, sync calendars, or publish plans outside the authenticated user's workspace.

## Future Enhancements

Future work can add guided career templates, skill gap suggestions, calendar reminders, export options, and richer progress analytics.

## Current Implementation

The current implementation provides isolated backend models, migration, service ownership checks, protected CRUD APIs, review detail/update endpoints, overview metadata, protected frontend workflow routes, typed API integration, local state management, shared drawers, icon record actions, empty/loading/error/success states, and story documentation.
