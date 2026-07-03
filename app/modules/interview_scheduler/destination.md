# Interview Scheduler Destination

## App Name

Interview Scheduler

## Destination Status

Approved v1.0

## Final Product Vision

Interview Scheduler should mature into a focused interview-planning workspace
that helps users organize interview schedules, rounds, timing, reminders, and
preparation context across an interview process.

The product should support manual interview organization without becoming a
calendar server, recruiting platform, applicant tracking system, automated
invitation sender, candidate evaluation engine, or Calendly-style booking
product.

At its destination, Interview Scheduler should keep candidate or role context,
round planning, calendar events, and preparation notes connected so users know
what is happening next and what needs attention.

## Target Users

- Job seekers organizing upcoming interviews and follow-ups.
- Recruiters manually tracking interview rounds.
- Hiring teams coordinating interview stages.
- Career coaches helping users prepare for scheduled interviews.
- Professionals managing interview appointments during career transitions.

## Core User Problems

- Interview details are often scattered across emails, calendars, notes, and
  messages.
- Users need round-level preparation context, not just dates.
- Calendar events should stay connected to the candidate, role, and interview
  stage.
- Reminder and integration features can drift into external delivery and
  booking infrastructure.
- Scheduling tools can become risky if they start evaluating candidates or
  automating hiring decisions.

## Final Capabilities

- Create owner-scoped interview schedules with candidate, role, company,
  stage, priority, and target date context.
- Add interview rounds under schedules.
- Store round type, interviewer, timing, status, and preparation notes.
- Create calendar events attached to schedules or rounds.
- Track event timing, location, reminder intent, and status.
- Edit and delete schedules, rounds, and events.
- Keep dashboard and list responses lightweight.
- Load complete editable details only when needed.
- Expose interview history if future workflow requires it.
- Support export or calendar handoff only through explicit user action.

## Advanced Capabilities

- Calendar export or integration with explicit consent.
- Notification reminders with user-controlled delivery.
- Interview history timeline.
- Preparation prompts connected to AI Job Interviewer or Interview Coach.
- Schedule summary export for personal review.
- Candidate pipeline analytics for manual records.
- Conflict warnings across interview events.
- Follow-up task handoff to Email Assistant or Job Tracker.

## AI Opportunities

AI may help prepare and organize interview context, but it must not evaluate
candidates or automate scheduling decisions.

Potential AI support includes:

- Suggesting preparation notes from user-provided role context.
- Summarizing upcoming interview schedule details.
- Recommending follow-up tasks after an interview event.
- Creating practice prompts for AI Job Interviewer or Interview Coach.
- Detecting missing schedule details such as interviewer or location.
- Explaining scheduling conflicts without changing events automatically.

AI must not score candidates, decide hiring suitability, send invites
automatically, contact external participants, or claim interview outcome
predictions.

## Ecosystem Connections

- Job Tracker can link tracked applications to interview schedules.
- AI Job Interviewer can use approved interview context for practice sessions.
- Interview Coach can receive upcoming interview context for readiness work.
- Email Assistant can draft follow-up emails after explicit user action.
- Career Planner can connect interviews to broader career goals.
- Calendar export can remain a handoff rather than shell-owned scheduling.

Interview Scheduler owns interview schedules, rounds, and calendar events. It
should not absorb job tracking, coaching, AI interview simulation, email
communication, recruiting automation, or calendar infrastructure.

## Weekly Return Value

Users return when new interviews are scheduled, rounds change, events approach,
preparation notes need review, follow-ups are created, or job-search context
changes.

The weekly value is readiness and coordination: users can see the next
interview step without losing context.

## Success Criteria

- Users can create, update, delete, and review schedules, rounds, and events in
  one focused workflow.
- Calendar events remain connected to interview context.
- Preparation notes support readiness without becoming evaluation or coaching
  authority.
- Integrations and reminders require explicit governance and user action.
- The product avoids ATS, booking, recruiting automation, and candidate scoring
  scope.
- Ecosystem handoffs strengthen the career workflow without product overlap.

## Journey Progress

Current Position: 61 / 100
Destination: 100 / 100
Remaining Journey: 39 / 100

This estimate describes product maturity, not feature completion.

Interview Scheduler already has a live manual schedule, round, and calendar
workflow. The remaining journey is about reminders, calendar handoffs, history,
preparation integrations, conflict review, and job-search ecosystem links.

## Future Version Ideas

- V1.1: Add interview history route and timeline.
- V1.2: Add calendar export.
- V1.3: Add reminder controls.
- V1.4: Add Job Tracker and Interview Coach handoffs.
- V2: Add governed external calendar integration and preparation prompts.

## Non Goals

- Do not become a calendar server.
- Do not become a Calendly-style booking product.
- Do not become an ATS.
- Do not become a recruiting automation platform.
- Do not send invitations or reminders without explicit user action.
- Do not score candidates or make hiring decisions.
- Do not predict interview outcomes.
- Do not replace Job Tracker, AI Job Interviewer, Interview Coach, Email
  Assistant, or Career Planner.
- Do not silently sync external calendar data.

## Guiding Principles

- Keep interview context attached to every round and event.
- Support manual coordination before external automation.
- Treat reminders and integrations as explicit opt-in features.
- Preserve preparation notes without turning them into evaluation.
- Use ecosystem handoffs for coaching, job tracking, and email.
- Avoid hiring authority and candidate scoring.
- Help users stay ready for the next interview step.

## Governance Notes

This document is aspirational and does not authorize immediate implementation.
Future work must be reviewed by Product Owner and Astra before development.

Any feature involving external calendars, reminders, email invitations,
candidate analytics, AI preparation, job-tracker links, or automated scheduling
requires explicit governance review before implementation.

## Last Governance Review

Product Owner: Approved on 2026-07-03 for live-app Destination Framework rollout.
Astra: Approved on 2026-07-03. Journey Progress 61 / 100 accepted.
Codex: Drafted destination v1.0 from current backend story, frontend story, and overview metadata.

Status: Approved
