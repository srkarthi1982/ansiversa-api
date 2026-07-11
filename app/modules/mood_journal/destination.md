# Mood Journal Destination

## App Name

Mood Journal

## Destination Status

Approved v1.0

## Final Product Vision

Mood Journal should mature into a private reflection workspace that helps users
record daily mood entries, review recent reflections, search notes and tags,
and understand personal patterns while keeping sensitive emotional data
protected by default.

The product should support personal reflection without becoming a clinical
mental-health tool, therapy replacement, crisis-support service, surveillance
system, social mood feed, or default server-backed diary.

At its destination, Mood Journal should feel calm, private, and honest: users
can record how they feel, reflect over time, and choose explicitly whether any
data ever leaves the browser.

## Target Users

- Users building a private daily reflection habit.
- People who want a simple mood and note history in the browser.
- Routine builders tracking consistency through a local streak.
- Users who want lightweight tags and search for personal reflection.
- Privacy-conscious users who do not want emotional notes stored on a server by
  default.
- Users preparing private notes for therapy, coaching, or self-review without turning the app into a clinician.
- Users who prefer quick check-ins over long-form journaling.

## Core User Problems

- Mood reflections are sensitive and should not be stored remotely without
  explicit consent.
- Users need a low-friction way to record one entry per day.
- Reflection value comes from reviewing patterns, not over-measuring emotion.
- Users need search and filtering without turning the journal into analytics
  surveillance.
- Mood apps can become risky if they imply diagnosis, therapy, crisis support,
  or health monitoring.
- Mood scales can oversimplify complex feelings, so tags and notes need room for personal context.
- Too many prompts, streaks, or reminders can make emotional tracking feel like another chore.

## Final Capabilities

- Record one date-keyed mood entry per day.
- Save mood level, optional mood label, tags, note, and update timestamp.
- Update or reset today's entry.
- Review local history sorted by date.
- Search notes and tags.
- Filter entries by mood level.
- Delete entries with confirmation.
- Calculate a local streak from consecutive recorded days.
- Validate browser-local stored data before loading it.
- Provide optional export/import or encrypted sync only after explicit
  governance review.

## Advanced Capabilities

- Export/import private journal data.
- Optional encrypted account sync with clear consent and recovery boundaries.
- Reminder controls with opt-in scheduling.
- Local-only trend insights that avoid diagnosis.
- Wellness goal links or reflection prompts.
- Custom activities, factors, or tags for user-defined context after privacy review.
- Weekly reflection summaries with source entries visible and no clinical claims.
- Stronger privacy controls for clearing, exporting, or migrating data.
- Local sentiment or tag summaries without server upload.
- Crisis-resource links that are informational and not a replacement for care.

## AI Opportunities

AI opportunities are sensitive and should remain limited, opt-in, and
privacy-reviewed.

Potential AI support includes:

- Local or explicitly approved reflection prompts.
- Summarizing user-selected entries after clear consent.
- Identifying recurring tags or themes without diagnostic claims.
- Helping rewrite a journal note for clarity if the user asks.
- Suggesting non-clinical reflection questions.

AI must not diagnose, provide therapy, detect crisis automatically, send mood
entries to external providers by default, infer mental-health status, or make
medical recommendations.

## Ecosystem Connections

- Study Planner or Course Tracker may receive explicit wellness-related task
  context only if the user chooses to share it.
- Daily Word Challenge and Eco Habit Tracker may complement routine-building
  without reading mood notes.
- File Optimizer may optimize exported journal files after export.
- Calendar or reminder features, if added, must remain opt-in and scoped.

Mood Journal owns private mood entries and reflection history. It should not
absorb habit tracking, therapy, clinical monitoring, social sharing, or
productivity analytics.

## Weekly Return Value

Users return to record daily entries, update today's reflection, search past
notes, review mood-level patterns, and maintain a private streak.

The weekly value is privacy-preserving self-reflection, not diagnosis or
performance tracking.

## Success Criteria

- Users can record, update, search, filter, and delete local mood entries
  without backend runtime storage.
- The browser-first privacy boundary remains clear to users and future agents.
- Reflection features are calm, non-clinical, and non-judgmental.
- Patterns and summaries remain traceable to user-entered entries instead of hidden inference.
- Streaks and reminders support continuity without punishing missed entries.
- Optional sync, export, reminders, or AI features require explicit user action
  and governance review.
- The product never presents itself as therapy, diagnosis, or crisis support.
- Sensitive mood content is never sent to backend services by default.

## Journey Progress

Current Position: 70 / 100
Destination: 100 / 100
Remaining Journey: 30 / 100

This estimate describes product maturity, not feature completion.

Mood Journal already has a live browser-local daily entry, history, search,
filter, streak, delete, and reset workflow. The remaining journey is about
privacy controls, export/import, optional encrypted sync, reminders, and
carefully governed non-clinical insights.

## Future Version Ideas

- V1.1: Add export/import for local entries.
- V1.2: Add stronger privacy and data-clear controls.
- V1.3: Add opt-in reminders.
- V1.4: Add local-only reflection insights.
- V2: Add optional encrypted sync after explicit privacy architecture review.

## Non Goals

- Do not become a clinical mental-health tool.
- Do not become a therapy replacement.
- Do not become a crisis-support service.
- Do not become a medical diagnosis or monitoring product.
- Do not become a social mood feed.
- Do not become a productivity surveillance system.
- Do not become a clinical questionnaire or symptom-correlation product without explicit medical governance.
- Do not provide AI crisis counseling or automated mental-health triage.
- Do not store mood notes on the server by default.
- Do not send journal entries to AI providers without explicit governance and
  user action.
- Do not infer health status from private reflections.

## Guiding Principles

- Keep mood data private and browser-local by default.
- Treat emotional notes as highly sensitive.
- Support reflection without diagnosis.
- Make sync, export, reminders, and AI explicitly opt-in.
- Keep prompts, trends, and streaks gentle rather than burdensome or judgmental.
- Avoid judgmental scoring or productivity framing.
- Preserve user control over deletion and data movement.
- Keep the product calm, lightweight, and non-clinical.

## Governance Notes

This document is aspirational and does not authorize immediate implementation.
Future work must be reviewed by Product Owner and Astra before development.

Any feature involving server persistence, encrypted sync, reminders, AI
analysis, wellness insights, crisis resources, exports, or cross-app sharing of
mood data requires explicit privacy and governance review before
implementation.

## Last Governance Review

Product Owner: Approved on 2026-07-03 for live-app Destination Framework rollout.
Astra: Approved on 2026-07-03. Journey Progress 70 / 100 accepted.
Codex: Drafted destination v1.0 from current backend story, frontend story, and overview metadata.

Status: Approved
