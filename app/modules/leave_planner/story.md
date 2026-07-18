# Leave Planner Story

Leave Planner #090 is a personal, authenticated leave-balance planner. `/leave-planner` is the API-driven overview; Explore opens `/leave-planner/leaves`; `/leave-planner/leaves/:leaveId` provides direct detail; `/leave-planner/types` manages custom allowances.

The isolated backend uses `LeaveTypes` and `LeaveEntries`. Every query and mutation is owner-scoped. Type names are unique per owner without case sensitivity. Types with history cannot be deleted and can be deactivated; inactive types remain visible for history and cannot be used for new entries. Entry overlap is rejected except when the existing entry is cancelled or rejected. Opposite first/second half entries may share one weekday because they occupy distinct portions of that date; weekend half-day entries are rejected.

The dashboard exposes allowance, used, planned, remaining, and upcoming counts. List search covers title, reason, notes, and type name. Type, status, period, and date filters combine with pagination.

The frontend uses `AvAppOverviewPage`, `AvAuthenticatedPageState`, `AvFormDrawer`, `AvRecordActions`, `AvConfirmDialog`, `AvPagination`, shared cards, empty states, page headers, inline feedback, generated contracts, and shared store helpers. The app is approved live at version `1.0.0` after authenticated E2E, Astra review, Partner manual verification, production migration verification, destination metadata sync, overview metadata sync, and parent Apps row promotion.
