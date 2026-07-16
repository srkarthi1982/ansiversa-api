# Leave Planner Story

Leave Planner #090 is a personal, authenticated leave-balance planner. `/leave-planner` is the API-driven overview; Explore opens `/leave-planner/leaves`; `/leave-planner/leaves/:leaveId` provides direct detail; `/leave-planner/types` manages custom allowances.

The isolated backend uses `LeaveTypes` and `LeaveEntries`. Every query and mutation is owner-scoped. Types with history cannot be deleted and can be deactivated; inactive types remain visible for history and cannot be used for new entries. Entry overlap is rejected except when the existing entry is cancelled or rejected.

The dashboard exposes allowance, used, planned, remaining, and upcoming counts. List search covers title, reason, notes, and type name. Type, status, period, and date filters combine with pagination.

The frontend uses `AvAppOverviewPage`, `AvAuthenticatedPageState`, `AvFormDrawer`, `AvRecordActions`, `AvConfirmDialog`, `AvPagination`, shared cards, empty states, page headers, inline feedback, generated contracts, and shared store helpers. The app remains `comingSoon`, `version = null`, pending authenticated E2E and human approval.
