# Family Task Planner Destination

## App Name

Family Task Planner

## Destination Status

Approved v1.0

## Final Product Vision

Family Task Planner should become Ansiversa's calm household coordination workspace: a place where families can capture responsibilities, assign ownership, review what is due, and understand workload without turning home life into corporate project management.

## Target Users

- Families coordinating chores, errands, shopping, bills, and child-related responsibilities.
- Couples and shared households splitting everyday work.
- Caregivers who need a simple way to keep household support tasks visible.
- Users who want ownership, dates, and completion history without chat, social feeds, or complex project boards.

## Core User Problems

- Household tasks are often scattered across memory, messages, paper notes, and calendars.
- Ownership becomes unclear when multiple family members share responsibilities.
- Recurring chores and bills are easy to forget without visible review.
- Generic project-management tools feel too heavy and business-oriented for home life.
- Families need simple workload awareness without turning task completion into pressure or competition.

## Final Capabilities

- Create, edit, duplicate, complete, reopen, and delete household tasks.
- Assign tasks to family members.
- Group tasks by household categories.
- Track priority, due date, recurring label, status, notes, and description.
- Search, filter, and sort tasks.
- Maintain family members and categories.
- Review due-today, upcoming, completed, pending, overdue, and workload summaries.
- View a simple upcoming schedule grouped by date.
- Review completion rate, most active member, workload, and category distribution.
- Keep list responses lightweight and detail endpoints complete.
- Support accessible responsive workflows inside the Ansiversa shell.

## Advanced Capabilities

- Real recurring task instance generation after the recurrence model is approved.
- Platform notifications and reminders after notification governance approval.
- Household sharing after multi-user family account governance.
- Calendar integration after integration governance.
- Exportable household task summaries.
- Cross-app links to Medicine Reminder, Emergency Contacts Organizer, Home Maintenance Planner, Household Expense Splitter, and Wellness and Goal Planner through approved APIs.

## AI Opportunities

- Suggest draft household task lists from user-entered routines.
- Detect overloaded members or stale tasks for user review.
- Summarize weekly household completion patterns.
- Suggest category cleanup or recurring task candidates.

AI must remain optional, reviewed, and clearly separated from the current manual household workflow.

## Ecosystem Connections

Family Task Planner can later connect with Home Maintenance Planner, Emergency Contacts Organizer, Household Expense Splitter, Medicine Reminder, Wellness and Goal Planner, and Dashboard summaries through approved APIs. It must not directly own or mutate records in those apps.

## Weekly Return Value

Users return weekly to review upcoming household work, add new responsibilities, complete tasks, rebalance ownership, and confirm that important family duties are not forgotten.

## Success Criteria

- Users can create and assign household tasks quickly.
- Categories and family members make task lists easy to scan.
- Dashboard and insights show what needs attention without project-management complexity.
- Completion and reopening are low-friction.
- The app remains practical without chat, notifications, external calendar sync, or AI.

## Journey Progress

Current Position: 30 / 100
Destination: 100 / 100
Remaining Journey: 70 / 100

This estimate describes product maturity, not feature completion. Workflow Ready V1 includes task CRUD, family member CRUD, category CRUD, duplicate/complete/reopen actions, dashboard summaries, simple calendar grouping, insights, owner-scoped APIs, isolated database storage, overview routing, production database migration, and manual QA verification. The remaining journey includes governed household sharing, reminder delivery, richer recurrence behavior, exports, cross-app connections, and carefully governed AI assistance.

## Future Version Ideas

- V1.1: Recurring task instance generation and weekly review flow.
- V1.2: Household summary export.
- V1.3: Platform reminders after notification governance.
- V2: Approved multi-user household sharing.
- V2+: AI-assisted household planning under strict review.

## Non Goals

- Do not become Project Tracker.
- Do not become Task Prioritizer.
- Do not add chat, messaging, SMS, email, or push notifications before governance approval.
- Do not add social feeds, leaderboards, or gamified family pressure by default.
- Do not directly own records from other family, health, home, or finance apps.
- Do not send household data to AI by default.

## Guiding Principles

- Home coordination should feel calm and practical.
- The app should make ownership visible without blame.
- Tasks should stay lightweight and easy to complete.
- Advanced reminders, sharing, and AI must be opt-in and approved.
- The household workflow should remain distinct from business project management.

## Governance Notes

Astra: Approved on 2026-07-11.

Partner: Approved Family Task Planner live promotion after manual workflow verification.

Codex: Ran production-configured isolated database migration, verified schema/indexes, synced overview metadata, and prepared live promotion metadata.
