# Leave Planner Destination

## Destination

A calm personal workspace for defining leave allowances, planning absences, and understanding used, planned, and remaining balances.

## Journey

Overview → Leaves → Leave detail, with Leave types as the allowance-management route. Create/edit uses shared form drawers; delete uses shared record actions and confirmation dialogs.

## Progress

- Journey progress: `20 / 100`
- Development state: Approved Live
- Approval: approved after Astra review and Partner manual verification
- Reviewed date: `2026-07-18`
- Launch status: `live`
- Version: `1.0.0`
- Production migration: verified at `20260716_0002_leave_planner`

## Calculation contract

Full-day duration counts inclusive Monday–Friday dates. Half leave is 0.5 day and must be a single date. Weekends are excluded; holidays are not. Approved and taken consume balance. Planned and pending are separate. Cancelled and rejected consume neither. Overlapping non-cancelled/non-rejected entries are rejected. Negative remaining balances are permitted and displayed.
