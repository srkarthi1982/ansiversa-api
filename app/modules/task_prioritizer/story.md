# Task Prioritizer

## Purpose

Task Prioritizer supports a DB-backed local workflow for deciding which user-owned tasks should receive attention first. V1 focuses on explicit task signals, local scoring, manual priority override, and review history without AI, collaboration, calendar sync, notifications, or external task integrations.

## Workflow

The frontend provides a public overview and protected Prioritize, Tasks, History, and Insights routes. Users create tasks, edit saved task details, duplicate tasks, delete tasks, assign manual priorities, recalculate local priorities, search and filter the task list, review priority history, and inspect dashboard summary signals.

## User Journey

Users start at `/task-prioritizer`, select Explore, and enter `/task-prioritizer/prioritize`. They create tasks with category, status, due date, effort, impact, urgency, priority, manual override, and notes. The Tasks route supports ongoing record management. History shows changes and priority actions. Insights summarizes open work, urgent work, overdue tasks, manual overrides, average priority score, top tasks, and active rule metadata.

## Database Design

The app uses an isolated `TASK_PRIORITIZER_DATABASE_URL` database. Tables are `TaskPrioritizerTasks`, `TaskPrioritizerTaskPriorities`, `TaskPrioritizerPriorityRules`, and `TaskPrioritizerPriorityHistory`. Every persisted user-facing record includes `ownerId`. Task priorities and history reference tasks by indexed `taskId`; history may preserve deleted-task events with `taskId = null`. Indexes support owner-scoped task lists, updated sorting, category/status filters, priority review, due-date review, task priority history, enabled rule lookup, and timeline history queries without indexing large text fields.

## API Design

Protected `/api/v1/task-prioritizer` endpoints provide dashboard, task CRUD, duplicate, manual priority assignment, priority recalculation, rule CRUD, and history listing. List and dashboard responses return lightweight summaries with `notesPreview`. Detail endpoints return complete task notes for edit drawers. Create and update DTOs are separate and do not require create-only parent IDs because V1 tasks are standalone records.

## Shared Components Used

The frontend uses the shared Ansiversa shell, authenticated page state, page header, form drawer, empty state, feedback stack, stat grid, record actions, confirmation dialog, and card patterns.

## Performance Considerations

V1 keeps API payloads small with summary/detail response separation and owner-scoped query indexes. Priority scoring runs locally in the backend service from stored task inputs and enabled rules. The module avoids AI calls, task-management SDKs, background jobs, notification libraries, chart libraries, calendar integrations, file storage, and new dependencies.

## Current Status

Approved Live at version `1.0.0` after Astra/Partner approval, production Task Prioritizer database migration, parent Apps row promotion, destination metadata sync, overview CTA validation, and Workflow Ready verification. The production isolated database is verified at revision `20260704_0001`.

## Known Limitations

V1 does not support AI prioritization, recurring tasks, team assignments, comments, attachments, calendar sync, reminders, Kanban boards, import/export, external task providers, or cross-app handoffs. Priority rules are exposed through the API and dashboard but do not yet have a dedicated frontend rule-management page.

## Future Enhancements

Future versions may add rule-management UI, richer scoring explanations, import/export, optional reminders, explicit handoff from Project Tracker, calendar handoff, AI-assisted suggestions, or collaboration only after Partner/Astra governance review.

## Current Implementation

The backend owns the Task Prioritizer database, SQLAlchemy models, Alembic migration, protected API routes, response schemas, and owner-scoped service logic. The module is registered under `/api/v1/task-prioritizer`, and the parent Apps catalog keeps Task Prioritizer as `active` with `launchStatus = live` and version `1.0.0`.
