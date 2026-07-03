# Course Tracker Destination

## App Name

Course Tracker

## Destination Status

Approved v1.0

## Final Product Vision

Course Tracker should mature into a focused course progress workspace that
helps users organize courses, break them into modules, record learning effort,
and review completion over time.

The product should support learning accountability without becoming a learning
management system, school administration product, gradebook, certification
authority, marketplace, or external course provider.

At its destination, Course Tracker should help users understand where they are
in each course, what modules remain, how much effort they have invested, and
what learning activity should move next.

## Target Users

- Students tracking coursework and course completion.
- Online learners managing self-paced courses.
- Professionals studying certifications or skills programs.
- Self-learners organizing structured learning commitments.
- Users who want course-level progress separate from daily study planning.

## Core User Problems

- Course progress is often scattered across provider dashboards, notes, and
  memory.
- Users need a simple way to break courses into modules and track status.
- Learning effort is hard to review when study logs are not connected to the
  course.
- Users need completion metrics without turning the app into a school system.
- Course tracking should support planning without pretending to validate
  grades or certifications.

## Final Capabilities

- Create and maintain owner-scoped course records.
- Store provider, category, goal, date range, and status for each course.
- Add ordered modules under courses.
- Update module status as learning progresses.
- Record progress logs with minutes, summaries, and reflections.
- Optionally connect progress logs to course modules.
- Review active courses, completed courses, module completion, total minutes,
  completion rate, and recent progress.
- Keep progress logs as historical learning records.
- Support course-level links to Study Planner and Smart Textbook Scanner.
- Keep course data lightweight and reviewable across devices.

## Advanced Capabilities

- Due-date reminders and course milestone alerts.
- Calendar export for course milestones.
- Grade tracking when explicitly user-entered.
- Certificate storage or File Optimizer handoff for uploaded certificates.
- LMS import with explicit user consent and limited scope.
- Study Planner task generation from unfinished modules.
- Course comparison across providers or categories.
- Learning analytics across courses, minutes, and completion trends.

## AI Opportunities

AI may help users interpret course progress and plan next steps, but it must
not become an academic authority or certification evaluator.

Potential AI support includes:

- Suggesting module breakdowns from user-provided course outlines.
- Summarizing progress logs into review insights.
- Identifying stalled courses or repeated blockers.
- Recommending study focus based on incomplete modules.
- Creating Study Planner task suggestions from user-approved course data.
- Explaining progress trends without judging user ability.

AI must not assign grades, certify completion, impersonate a provider, scrape
course platforms, or claim that a user has mastered material without evidence.

## Ecosystem Connections

- Study Planner can receive study tasks based on unfinished course modules.
- Smart Textbook Scanner can link scans to course modules.
- AI Notes Summarizer can summarize course notes provided by the user.
- Concept Explainer can explain topics from course modules.
- Memory Trainer can receive reviewed facts after user approval.
- File Optimizer may help optimize certificates or exported course documents.

Course Tracker owns course structure and progress review. It should not absorb
daily study scheduling, textbook extraction, note summarization, or concept
teaching.

## Weekly Return Value

Users return weekly to update module status, record course progress, review
learning minutes, check completion, and decide which course or module needs
attention next.

The value is sustained learning accountability rather than one-time course
setup.

## Success Criteria

- Users can track courses, modules, progress logs, and review metrics in one
  clear workflow.
- Course progress remains owner-scoped and easy to update.
- Modules and progress logs stay connected to the correct course.
- Review metrics help users understand progress without claiming academic
  authority.
- Ecosystem handoffs support learning without turning Course Tracker into an
  LMS.
- Future analytics improve reflection and planning rather than surveillance or
  grading.

## Journey Progress

Current Position: 64 / 100
Destination: 100 / 100
Remaining Journey: 36 / 100

This estimate describes product maturity, not feature completion.

Course Tracker already has a live course, module, progress-log, and review
workflow. The remaining journey is about richer course planning, reminders,
analytics, ecosystem handoffs, and optional imports while keeping the product
out of LMS, grading, and certification authority territory.

## Future Version Ideas

- V1.1: Add module due dates and reminder-ready metadata.
- V1.2: Add Study Planner task handoff from incomplete modules.
- V1.3: Add learning trends and progress analytics.
- V1.4: Add certificate/file handoff support.
- V2: Add governed LMS import for user-selected course data.

## Non Goals

- Do not become an LMS.
- Do not become a school administration system.
- Do not become a gradebook by default.
- Do not issue certificates or validate credentials.
- Do not scrape external course providers.
- Do not become a course marketplace.
- Do not replace Study Planner, Smart Textbook Scanner, Concept Explainer, or
  AI Notes Summarizer.
- Do not treat progress metrics as mastery proof.
- Do not automate academic decisions.

## Guiding Principles

- Track learning progress without claiming learning authority.
- Keep courses, modules, and logs simple and reviewable.
- Treat progress logs as historical records.
- Support user agency rather than provider control.
- Let adjacent learning apps handle their own workflows.
- Make AI planning suggestions optional and evidence-based.
- Prefer steady accountability over complex administration.

## Governance Notes

This document is aspirational and does not authorize immediate implementation.
Future work must be reviewed by Product Owner and Astra before development.

Any feature involving LMS import, external provider integration, grades,
certificates, reminders, AI planning, or academic analytics requires explicit
governance review before implementation.

## Last Governance Review

Product Owner: Approved on 2026-07-03 for live-app Destination Framework rollout.
Astra: Approved on 2026-07-03. Journey Progress 64 / 100 accepted.
Codex: Drafted destination v1.0 from current backend story, frontend story, and overview metadata.

Status: Approved
