# Job Tracker Destination

## App Name

Job Tracker

## Destination Status

Approved v1.0

## Final Product Vision

Job Tracker should mature into a focused job-search organization workspace
that helps users track job opportunities, applications, follow-ups, insights,
and pipeline movement without losing context.

The product should support job-search clarity without becoming a job board,
application automation tool, recruiter, ATS, resume scorer, career predictor,
or hiring-decision engine.

At its destination, Job Tracker should help users understand what roles they
are pursuing, where each application stands, what follow-up is needed, and what
insights should shape their next action.

## Target Users

- Job seekers managing active applications.
- Professionals exploring a career move.
- Career changers comparing opportunities.
- Students tracking internships or entry-level applications.
- Career coaches helping users organize job-search activity.
- Users tailoring resumes, cover letters, and interview preparation for different roles.
- Professionals managing recruiter conversations and follow-up timing.

## Core User Problems

- Job opportunities and application status often get scattered across emails,
  spreadsheets, bookmarks, and memory.
- Users need follow-up dates, contacts, documents, and priorities in one
  workflow.
- Insights should support action without pretending to predict hiring outcomes.
- Job tracking can drift into scraping, auto-applying, or recruiter workflows.
- AI match scoring can mislead if treated as truth instead of a review signal.
- Rejection-heavy pipelines can create anxiety if status review feels punitive.
- Duplicate applications, resume versions, contacts, and follow-up dates are hard to manage in spreadsheets once search volume grows.

## Final Capabilities

- Create owner-scoped job listings with role, company, location, source,
  status, priority, and notes.
- Add application records under tracked jobs.
- Track pipeline status, follow-up dates, contacts, resume versions, cover
  letters, and notes.
- Record insights, priorities, recommendations, and next actions.
- Edit and delete jobs, applications, and insights.
- Keep dashboard/list payloads lightweight with preview fields.
- Load detail records before editing full notes or descriptions.
- Expose application history when the workflow matures.
- Connect interviews, resumes, and follow-up communication through explicit
  handoffs.
- Support analytics that describe activity without guaranteeing outcomes.

## Advanced Capabilities

- Application history timeline.
- Reminder notifications for follow-up dates.
- Interview Scheduler integration.
- Resume Builder and Job Description Analyzer handoffs.
- Email Assistant handoff for follow-up drafts.
- Job-search analytics across status, priority, and response patterns.
- Exportable job-search records so users retain ownership of sensitive career data.
- Duplicate-role and stale-follow-up review signals that support quality over application volume.
- Optional job posting import from user-provided sources.
- AI-assisted fit review grounded in user-provided job and resume context.

## AI Opportunities

AI can help organize and interpret job-search context, but it must not decide
career fit or promise hiring outcomes.

Potential AI support includes:

- Summarizing next actions across applications.
- Highlighting missing follow-up dates or contacts.
- Comparing a job listing with user-approved resume context.
- Suggesting preparation tasks before an interview.
- Grouping insights by priority or timeline.
- Drafting follow-up notes through Email Assistant handoff.

AI must not auto-apply to jobs, scrape job boards without governance, guarantee
fit, rank the user's employability, or replace user judgment about career
decisions.

## Ecosystem Connections

- Resume Builder can provide approved resume versions for applications.
- Job Description Analyzer can analyze saved job listings.
- Interview Scheduler can attach interview events to applications.
- AI Job Interviewer and Interview Coach can prepare from selected job context.
- Email Assistant can draft follow-ups after user approval.
- Career Planner can use job-search activity for broader planning.
- LinkedIn Bio Optimizer can align profile positioning for target roles.

Job Tracker owns jobs, applications, insights, and future application history.
It should not absorb resume building, job analysis, interview scheduling,
email sending, career planning, profile optimization, or job board behavior.

## Weekly Return Value

Users return to add new opportunities, update application statuses, record
insights, check follow-up dates, prepare interviews, and review the overall job
search pipeline.

The weekly value is momentum: users know which opportunities need action and
which ones are waiting.

## Success Criteria

- Users can manage jobs, applications, and insights in one clear workflow.
- Pipeline status and follow-up actions remain easy to scan.
- Review copy and analytics support momentum without shaming rejection or inactivity.
- Insights support user judgment without becoming prediction or scoring.
- Detail-heavy notes stay out of lightweight list payloads.
- Ecosystem handoffs strengthen job-search flow without product overlap.
- The product avoids scraping, auto-applying, recruiting automation, and hiring
  authority.

## Journey Progress

Current Position: 62 / 100
Destination: 100 / 100
Remaining Journey: 38 / 100

This estimate describes product maturity, not feature completion.

Job Tracker already has a live jobs, applications, and insights workflow with
owner-scoped persistence. The remaining journey is about application history,
reminders, interview links, resume/job-analysis handoffs, analytics, and
carefully governed import or AI review.

## Future Version Ideas

- V1.1: Add application history timeline.
- V1.2: Add follow-up reminders.
- V1.3: Add Interview Scheduler integration.
- V1.4: Add Resume Builder and Job Description Analyzer handoffs.
- V2: Add governed job import and AI-assisted fit review.

## Non Goals

- Do not become a job board.
- Do not scrape job listings by default.
- Do not auto-apply to jobs.
- Do not become an ATS or recruiting platform.
- Do not guarantee interviews, offers, fit, or hiring outcomes.
- Do not score employability as objective truth.
- Do not encourage spam applications, mass autofill, or low-quality application volume.
- Do not make rejection tracking feel punitive.
- Do not replace Resume Builder, Job Description Analyzer, Interview
  Scheduler, Email Assistant, Career Planner, or LinkedIn Bio Optimizer.
- Do not send follow-ups without explicit user action.
- Do not make career decisions for the user.

## Guiding Principles

- Track the job search without owning the job market.
- Support preparation and follow-through over prediction.
- Treat insights and AI suggestions as review signals, not truth.
- Favor quality, context, and follow-up over raw application count.
- Keep user agency central to every application decision.
- Use explicit handoffs for resumes, interviews, emails, and career planning.
- Keep payloads lightweight until detail is needed.
- Avoid automation that could harm user trust or platform policy compliance.

## Governance Notes

This document is aspirational and does not authorize immediate implementation.
Future work must be reviewed by Product Owner and Astra before development.

Any feature involving job-board import, reminders, external integrations,
AI-assisted fit review, resume matching, interview links, email follow-ups, or
application automation requires explicit governance review before
implementation.

## Last Governance Review

Product Owner: Approved on 2026-07-03 for live-app Destination Framework rollout.
Astra: Approved on 2026-07-03. Journey Progress 62 / 100 accepted.
Codex: Drafted destination v1.0 from current backend story, frontend story, and overview metadata.

Status: Approved
