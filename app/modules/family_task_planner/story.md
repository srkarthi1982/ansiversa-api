# Family Task Planner Story

## Purpose

Family Task Planner helps households organize daily responsibilities in one shared workflow. It is designed for family coordination, not project management, so the core objects are tasks, family members, and everyday categories.

## Workflow

The module supports Dashboard, Tasks, Family Members, Categories, Calendar, and Insights views. Users create household tasks, assign them to family members, group them by category, track due dates, mark work complete or reopened, duplicate repeatable tasks, and review upcoming work by date.

## User Journey

A user starts from the dashboard to see today, upcoming, recently completed, and workload summaries. They add family members and categories first when useful, then create tasks with title, description, assignee, category, priority, due date, recurring option, status, and notes. The calendar groups pending dated tasks by day, and insights summarize completion and workload patterns.

## Database Design

The app owns an isolated database configured by `FAMILY_TASK_PLANNER_DATABASE_URL`.

Persistent tables:

* `FamilyTaskMembers`
* `FamilyTaskCategories`
* `FamilyTasks`

Every table stores `userId`, timestamps, and app-owned fields only. Tasks reference members and categories through nullable foreign keys so unassigned or uncategorized household work remains valid.

## API Design

The API is exposed under `/api/v1/family-task-planner`.

Endpoints provide dashboard data, CRUD for tasks, members, and categories, plus task duplicate, complete, and reopen actions. List and dashboard responses use lightweight summary models with preview fields. Detail endpoints return full editable content for drawers.

## Shared Components Used

The frontend uses the Ansiversa authenticated page state, overview page, page header, cards, empty states, feedback stack, confirmation dialog, pagination, record actions, and form drawer patterns.

## Performance Considerations

The API keeps list payloads lightweight and uses indexes for owner-scoped lists, status and due-date filtering, member/category lookups, updated ordering, and completion history. The calendar is a simple grouped list and does not use a heavy calendar library.

## Current Status

Approved Live. The app is promoted to `active` / `live` with version `1.0.0` after Astra/Partner approval, production database migration, manual workflow verification, overview CTA sync, destination metadata sync, and parent Apps row promotion.

## Known Limitations

The current workflow is local to the Ansiversa account. It does not include push notifications, reminders, messaging, AI, payments, external calendar sync, email, SMS, or wearable integrations.

## Future Enhancements

Future approved versions may add richer recurring task generation, household-level sharing, reminders, and deeper workload recommendations after Partner and Astra approval.

## Current Implementation

The backend module lives in `app/modules/family_task_planner`. The frontend module lives in `src/modules/family-task-planner`. The isolated migration lives under `migrations/family-task-planner`. The parent Apps catalog stores Family Task Planner as `active` with `launchStatus = live`, `version = 1.0.0`, and destination metadata `30 / 100`.
