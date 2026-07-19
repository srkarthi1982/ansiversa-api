# Shift Planner Destination

Destination Status: approved
Current Journey Progress: 18 / 100
Reviewed At: 2026-07-19

## Approved implementation boundary
Shift Planner is a personal or small-team planning tool for reusable shift types, a lightweight internal member roster, assigned or unassigned shifts, net scheduled hours, statuses, search, filters, and conflict prevention.

It supports overnight shifts by treating an end time at or before the start time as the following day. Break time must be non-negative and shorter than gross duration. Same-member active shifts may not overlap; back-to-back, cancelled, unassigned, and different-member shifts may coexist.

## Explicit exclusions
No payroll, wages, legal overtime, attendance, biometric records, contracts, approval chains, notifications, integrations, AI scheduling, or government labor rules.

## Success criteria
Authenticated owner isolation, safe historical deactivation, responsive shared UI, durable CRUD, calculation and conflict coverage, and all technical gates.

## Promotion

Approved live at version `1.0.0` after Astra review, Partner manual verification, production-configured isolated migration verification, Apps row promotion, destination metadata sync, overview metadata sync, and validation.
