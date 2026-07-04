# Project Tracker

## Purpose

Project Tracker supports a lightweight DB-backed workflow for organizing user-owned project records and tasks inside Ansiversa. V1 gives users a persistent planning workspace without collaboration infrastructure, notifications, calendar sync, file storage, or enterprise project-management features.

## Workflow

The frontend provides a public overview and protected Projects, Tasks, and Insights routes. Users create projects, add project tasks, update saved records, delete records, and review persisted progress signals from a protected dashboard endpoint.

## User Journey

Users start at `/project-tracker`, continue to `/project-tracker/projects`, create a project, then add tasks from `/project-tracker/tasks`. Insights summarizes backend project and task records so users can review active projects, completed projects, blocked tasks, overdue tasks, and upcoming due dates.

## Database Design

The app uses an isolated `PROJECT_TRACKER_DATABASE_URL` database. Tables are `ProjectTrackerProjects` and `ProjectTrackerTasks`. Every record includes `ownerId` and optional `platformId`. Tasks use an indexed `projectId` foreign key. Query-pattern indexes support owner-scoped list ordering, status filters, priority filters, due-date review, and parent task lookups without indexing large text fields.

## API Design

Protected `/api/v1/project-tracker` endpoints provide dashboard, project CRUD, and task CRUD. List and dashboard endpoints return lightweight summary models with `notesPreview`. Detail endpoints return complete notes for edit drawers. Create and update DTOs are separate; task update does not accept `projectId`, so parent reassignment is not supported in V1.

## Shared Components Used

The frontend uses the shared Ansiversa shell, authenticated page state, page header, form drawer, empty state, feedback stack, stat grid, record actions, and card patterns.

## Performance Considerations

V1 keeps API payloads small with summary/detail response separation and indexes the user-facing query patterns: owner lists, updated sorting, status/priority filters, due-date review, and parent task lookups. It avoids project-management SDKs, background jobs, notification libraries, chart libraries, calendar integrations, file storage, and new dependencies.

## Current Status

Workflow ready for Astra review as the next development candidate after 50 live apps. Project Tracker remains `comingSoon` with `version = null`. It may become the 51st developed app, but its canonical roadmap identity remains the Project Tracker catalog item 49, not canonical App #051.

## Known Limitations

V1 does not support team collaboration, comments, attachments, recurring tasks, calendar sync, project templates, time tracking, notifications, Kanban boards, Gantt charts, import/export, or backend audit history beyond current project/task timestamps.

## Future Enhancements

Future versions may add approved import/export, templates, recurring task helpers, optional calendar handoff, cloud synchronization, collaboration, or AI summaries after privacy, architecture, and governance review.

## Current Implementation

The backend owns the Project Tracker database, SQLAlchemy models, Alembic migration, protected API routes, response schemas, and owner-scoped service logic. The module is registered under `/api/v1/project-tracker` and remains separate from catalog promotion.
