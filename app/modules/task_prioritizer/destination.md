# Task Prioritizer Destination

## App Name

Task Prioritizer

## Destination Status

Approved v1.0

## Final Product Vision

Task Prioritizer should become Ansiversa's calm personal priority workspace for users who need to choose what to do next without adopting a heavy project-management system. The mature product should help users compare tasks by effort, impact, urgency, due date, context, and personal judgment while keeping the workflow private and understandable.

At maturity, Task Prioritizer should help users answer practical questions like "What deserves attention now?", "What is urgent but low impact?", "Which tasks can wait?", "Which items are overdue?", and "Which priorities did I override manually?"

## Target Users

- Professionals managing a mixed daily task queue.
- Students balancing assignments, study tasks, and deadlines.
- Solo builders deciding what to work on next.
- Families organizing personal or household tasks.
- Ansiversa users who want a lightweight priority layer without external task services.

## Core User Problems

- Task lists often become flat lists where everything feels equally important.
- Users need a simple way to compare urgency, impact, effort, and due date.
- Manual judgment matters and should not be hidden behind opaque automation.
- Prioritization history helps users understand why a task moved up or down.
- Priority data can reveal sensitive plans, deadlines, and personal concerns, so API payloads must remain minimal and owner-scoped.

## Final Capabilities

- Create, edit, delete, duplicate, search, and filter task records.
- Track category, status, due date, effort, impact, urgency, priority score, priority label, manual override, and notes.
- Assign manual priority while preserving system recalculation support.
- Recalculate priorities from local task inputs and approved rules.
- Review priority history and task changes.
- Review workload insights, overdue tasks, urgent tasks, manual overrides, and top priority tasks.
- Support user-owned database persistence with clear ownership boundaries.
- Preserve empty, loading, error, success, and delete-confirmation states.
- Keep prioritization inside the Ansiversa shell without owning global navigation or authentication.

## Advanced Capabilities

- Rule-management UI for category-specific scoring behavior.
- Explainable scoring panels showing why a score changed.
- Import/export after repeated use patterns are validated.
- Optional reminder handoff only after notification governance.
- Explicit handoff from Project Tracker or Work Log Tracker after user action.
- AI-assisted prioritization only after privacy and architecture review.

## AI Opportunities

- Suggest clearer task wording after explicit user action.
- Explain tradeoffs between urgent and important tasks.
- Suggest priority changes from user-provided task context.
- Summarize overdue or stale tasks into a weekly review.

AI features must not receive task titles, notes, due dates, scores, or priority history by default. Any AI handoff must be explicit, privacy-reviewed, and clear about what local data is being sent.

## Ecosystem Connections

- Project Tracker: receive selected tasks for prioritization after explicit handoff.
- Work Log Tracker: convert completed priority decisions into work logs after user action.
- Meeting Scheduler: turn high-priority follow-ups into meeting planning after user action.
- Markdown Editor: export priority review notes.
- Calendar or reminder features only through approved future platform services.

## Weekly Return Value

Users return daily or weekly to review their highest-priority work, adjust task signals, override priority when judgment changes, clear completed work, and understand how their task queue is shifting.

## Success Criteria

- Users can create and update tasks quickly.
- Search and filters make priority review fast.
- Manual override is visible and reversible through task editing.
- Recalculation is predictable and local.
- History explains priority changes without bloated payloads.
- The app does not drift into enterprise project management, reminders, or AI automation without governance review.

## Journey Progress

Current Position: 45 / 100
Destination: 100 / 100
Remaining Journey: 55 / 100

This estimate describes product maturity, not feature completion. Task Prioritizer has a useful DB-backed Workflow Ready V1 with task CRUD, duplicate, filters, local priority scoring, manual override, history, insights, indexes, and overview routing. The remaining journey includes rule-management UI, richer explanations, import/export, accessibility polish, cross-app handoffs, and careful governance for AI, reminders, or collaboration.

## Future Version Ideas

- V1.1: Add rule-management UI and clearer score explanations.
- V1.2: Add import/export and richer history filtering.
- V1.3: Add explicit Project Tracker handoff.
- V1.4: Add optional reminder handoff after notification governance.
- V2: Consider AI-assisted prioritization only after privacy and governance review.

## Non Goals

Task Prioritizer is not intended to become:

- An enterprise project management suite.
- A team ticketing system.
- A calendar platform.
- A notification-heavy reminder product.
- A file storage system.
- A hidden AI decision engine.
- A collaboration or employee-monitoring tool.

## Guiding Principles

Every Task Prioritizer feature should:

- Keep priority reasoning visible.
- Preserve user-created task editability.
- Keep manual judgment first-class.
- Keep data owner-scoped and minimally exposed.
- Avoid AI, notification, calendar, and collaboration drift without approval.
- Stay inside the Ansiversa platform shell and mini-app boundary.

## Governance Notes

This destination is aspirational. It describes the target product direction, not an authorization to build every feature now.

Product owner and Astra review are required before accepting, prioritizing, or implementing any destination item. Particular care is needed before approving AI, reminders, sync, collaboration, notifications, or cross-app handoffs because task priority data can reveal work plans, deadlines, personal routines, family needs, and business activity.

## Last Governance Review

Product Owner: Approved on 2026-07-04.
Astra: Approved on 2026-07-04.
Codex: Implemented DB-backed Workflow Ready V1, completed production database migration, and prepared live promotion metadata.

Status:

Approved Live
