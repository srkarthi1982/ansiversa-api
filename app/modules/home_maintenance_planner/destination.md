# Home Maintenance Planner Destination

Document Status: Not approved for live promotion
Destination Status: null
Destination Reviewed At: null
Created: 2026-07-15

## Product Vision

Home Maintenance Planner should become a practical private workspace for planning recurring and one-time household maintenance. It helps users keep due dates, areas, categories, provider details, and cost records together without claiming professional inspection or safety certification.

## Core Workflows

1. Create a maintenance task.
2. Assign a home area and maintenance category.
3. Set due date, recurrence, priority, optional costs, provider details, reference number, and notes.
4. Search, filter, and sort active tasks.
5. Mark a task complete.
6. For recurring tasks, move the due date forward predictably while recording completion history.
7. Reopen, archive, restore, or delete tasks where appropriate.
8. Review dashboard and insights.

## Task Lifecycle

Tasks start as upcoming, due soon, due today, or overdue based on their due date and reminder lead time. One-time tasks become completed when marked complete. Recurring tasks record the completion and advance to the next due date instead of creating duplicate visible tasks.

## Recurrence Behavior

Supported recurrence options are one-time, weekly, monthly, quarterly, six-monthly, yearly, and custom day interval. Custom intervals must be explicit positive day counts. Completion must never create duplicate active next occurrences.

## Cost Tracking

Estimated cost, actual cost, and currency are optional. Costs are used only for user review and insights. The app does not provide quotes, estimates from contractors, purchasing advice, or accounting compliance.

## Data Ownership

Every area, category, task, and completion record is scoped to the authenticated user. Users must never access another user's records.

## UX Expectations

The app should feel quiet and operational: clear lists, concise forms, responsive filters, visible due status, and practical insights. It should avoid decorative analytics and keep mobile entry comfortable.

## Safety Limitations

Home Maintenance Planner is not a substitute for qualified professionals. It must not claim professional inspection, guaranteed safety, regulatory compliance, emergency repair, contractor certification, or automated property diagnosis. Hazardous electrical, gas, structural, fire-safety, or similar work should be handled by qualified professionals.

## Acceptance Criteria

- Protected task, area, category, dashboard, and insights workflows exist.
- One-time and recurring tasks can be created, edited, completed, reopened, archived, restored, and deleted.
- Recurring completion advances the due date without duplicate active tasks.
- Search, filters, sorting, cost fields, provider fields, and validation work.
- Overview CTA opens `/home-maintenance-planner/tasks`.
- Production DB migration is applied and verified.
- App remains active / comingSoon / version null.

## Manual Verification Requirements

Manual verification should confirm create/edit/delete, recurrence, completion, reopening, filters, insights, costs, mobile layout, keyboard labels, owner isolation, and public catalog coming-soon status.

## Readiness Checklist

- Backend module complete.
- Frontend workflow complete.
- Documentation lifecycle complete.
- Overview metadata synced and validated.
- Production migration verified.
- No live promotion.

