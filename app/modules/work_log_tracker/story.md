# Work Log Tracker Story
## Purpose and workflow
Authenticated users follow `Projects → Log work → Review history` through `/work-log-tracker/logs`, detail, and projects routes.
## Architecture
The isolated `WorkProjects` and `WorkLogs` tables are owner scoped. Protected APIs provide dashboard, project CRUD, and log CRUD/detail/search/combined filters/pagination. Referenced projects cannot be deleted and may be deactivated.
## Time rules
Timed logs require start/end, treat end at or before start as next day, subtract a break shorter than elapsed time, reject overlaps, and permit back-to-back logs. Manual logs require 1–1440 minutes, clear clock/break values, and may overlap. Mode changes recalculate persisted duration. Planned/cancelled time is excluded from time summaries; billable totals contain no money.
## UI and status
Overview Explore opens `/logs`. Shared authenticated state, overview, headers, cards, feedback, empty states, `AvFormDrawer`, `AvRecordActions`/`AvConfirmDialog`, pagination, generated contracts, Zustand, and shared store helpers power responsive Logs, Detail, and Projects pages. The app is Workflow Ready / Level 3 but remains `comingSoon`, version `null`, destination pending, with authenticated browser E2E unavailable.
## Limitations
No categories, tags, live timer, exports, recurrence, surveillance, payroll, invoices, integrations, legal calculations, or AI.
