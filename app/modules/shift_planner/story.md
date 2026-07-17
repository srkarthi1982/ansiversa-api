# Shift Planner Story

## Purpose and workflow
Shift Planner gives an authenticated user a focused `Types → Members → Shifts → Review` workflow for personal and small-team schedules. The overview enters `/shift-planner/shifts`; supporting routes manage reusable types and a lightweight roster, while shift detail supports direct navigation and missing-record handling.

## Database and API design
The isolated database owns `ShiftTypes`, `ShiftMembers`, and `Shifts`, keyed by authenticated owner. Protected endpoints under `/api/v1/shift-planner` provide dashboard metrics; type and member CRUD; and shift CRUD, detail, search, filters, and pagination. List responses remain lightweight enough for cards while detail returns the full editable record. Referenced types and members cannot be deleted and can instead be deactivated.

## Rules
End time at or before start time means the following day. Net minutes equal gross minutes minus break; the break must be shorter than gross duration. Same-member non-cancelled intervals cannot overlap, including overnight intervals and edits. Boundaries may touch, so back-to-back shifts are allowed. Unassigned shifts and simultaneous shifts for different members are allowed. Inactive references remain visible historically but cannot be used for new shifts.

## UI and shared resources
Routes are `/shift-planner`, `/shifts`, `/shifts/:shiftId`, `/types`, and `/members`. The React module uses generated API contracts, Zustand, shared store helpers, `AvAppOverviewPage`, `AvAuthenticatedPageState`, `AvPageHeader`, `AvCardEmptyState`, `AvInlineFeedback`, `AvFormDrawer`, `AvRecordActions`/`AvConfirmDialog`, `AvPagination`, and shared cards. All create/edit flows use drawers; all deletion flows use confirmed record actions. The shifts page distinguishes first-use and filtered-empty states and exposes combined search, status/type/member/period/date filters, pagination, and metrics.

## Performance and current status
Owner/date, owner/status, owner/member/date, reference, and active-record indexes support the main access paths. Authenticated localhost browser E2E and the permanent Playwright regression gate passed on 2026-07-17. The app is Workflow Ready / Level 3 but remains `comingSoon`, version `null`, destination pending, and awaits Karthik manual acceptance.

## Limitations and future direction
No recurrence, drag-and-drop calendar, payroll, attendance, notifications, external calendars, legal calculations, or AI scheduling. A weekly view may be considered after evidence and approval.
