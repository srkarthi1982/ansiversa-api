# Vehicle Maintenance Tracker Destination

## Document Status

Status: Draft for Workflow Ready review  
Destination Progress: 24 / 100  
Destination Status: Workflow Ready  
Reviewed At: 2026-07-12

## Purpose

Vehicle Maintenance Tracker should mature into a dependable private upkeep ledger for personal and household vehicles. Its destination is maintenance memory, reminder clarity, and cost visibility, not becoming a repair marketplace, diagnostic platform, insurance processor, or official registration system.

## Mature Product Vision

At 100 / 100, Vehicle Maintenance Tracker helps users understand what was serviced, what is due next, how much upkeep costs, and which vehicle needs attention. It should make vehicle ownership less forgetful while keeping repairs, inspections, insurance, registration, and legal obligations verified with qualified providers or official sources.

## Target Users

- Personal vehicle owners tracking service history and reminders.
- Families managing more than one household vehicle.
- Frequent drivers watching odometer-based maintenance.
- Users who want private upkeep records before visiting a mechanic or renewal authority.

## Core Problem

Vehicle maintenance details are often scattered across receipts, messages, stickers, glovebox papers, and memory. Users need one calm workspace for vehicles, service history, costs, odometer values, and upcoming reminders without the product pretending to diagnose problems or guarantee compliance.

## Approved V1 Scope

- Vehicle records with name, make, model, year, plate, VIN, odometer, fuel type, status, and notes.
- Vehicle create, edit, delete, duplicate, search, filters, empty state, pagination, and confirmation dialogs.
- Maintenance records with service date, category, odometer, cost, provider, next due signals, and notes.
- Reminder records for upcoming/overdue oil changes, tire rotations, inspections, insurance renewals, registration renewals, and general service.
- Local mark-completed reminder action.
- Insights for total vehicles, maintenance record count, total cost, upcoming/overdue reminders, service frequency, and monthly activity.
- Protected owner-scoped backend APIs and isolated database storage.

## Non-Goals

- No live diagnostics, OBD/telematics integration, or mechanical fault detection.
- No repair marketplace, appointment booking, mechanic ratings, or provider pricing.
- No insurance processing, registration submission, legal compliance guarantee, or official renewal workflow.
- No parts inventory, fleet dispatch, warranty adjudication, or payment processing.
- No notifications until platform notification governance approves the pattern.

## Future Direction

Future approved versions may add recurring service templates, reminder notifications, document attachments, receipt exports, calendar export, maintenance intervals, cross-app expense links, and carefully governed AI summaries of user-entered maintenance history.

## AI and Integration Boundary

AI may eventually summarize service patterns, detect incomplete maintenance records, or draft neutral upkeep summaries. It must not diagnose faults, estimate legal compliance, recommend unsafe repairs, replace professional advice, or infer sensitive personal behavior from vehicle use.

## Success Criteria

- Users can create vehicle profiles quickly.
- Maintenance history is easy to review by vehicle.
- Odometer, cost, category, and provider details stay visible.
- Upcoming and overdue reminders are easy to distinguish.
- The app remains honest about being a recordkeeping workflow.

## Journey Progress Rationale

The Workflow Ready implementation establishes the core data model, protected workflow, CRUD foundation, reminder review, local completion action, and deterministic insights. The remaining maturity requires recurring intervals, attachments, exports, approved notifications, integrations, richer analytics, and stronger governance around safety-sensitive maintenance advice.
