# Job Description Analyzer Destination

## App Name

Job Description Analyzer

## Destination Status

Approved v1.0

## Final Product Vision

Job Description Analyzer should become Ansiversa's focused job-posting review
workspace: a place where career users can save job descriptions, structure fit
analysis, track skill matches, and record next steps without turning Ansiversa
into an applicant tracking system, recruiting automation platform, job scraper,
hiring-decision engine, or guaranteed employment advice product.

At maturity, Job Description Analyzer should help users answer practical
questions like "What does this role actually require?", "Which skills match my
profile?", "What gaps should I prepare for?", "What responsibilities matter
most?", and "What should I do before applying?" The product should convert job
postings into reviewable career signals while keeping user judgment and
personal career context visible.

The mature product should serve job seekers, career changers, students,
coaches, and professionals who compare roles and prepare applications. It
should help users understand job descriptions more clearly, not decide their
career for them or claim objective hiring outcomes.
Its market-informed identity is explainable role-decoding: requirements,
skills, seniority, red flags, inclusive-language concerns, and preparation
signals should remain tied to highlighted job-posting evidence rather than a
single opaque fit score.

## Target Users

- Job seekers comparing roles before applying.
- Career changers mapping job requirements to existing skills.
- Students and graduates learning how to interpret job postings.
- Professionals preparing for internal moves or promotion paths.
- Career coaches helping users review role fit and preparation gaps.
- Ansiversa users who need a structured job-review workflow inside the platform.

## Core User Problems

- Job descriptions are long, inconsistent, and often difficult to compare.
- Users may miss important responsibilities, keywords, or required skills.
- Job seekers need to separate role requirements from nice-to-have language.
- Fit analysis can become subjective unless evidence and recommendations stay
  connected to the job posting.
- AI extraction can overstate match quality or hide uncertainty if not reviewed.
- Employer-focused clarity and inclusion review is a different workflow from
  candidate preparation, and those modes should not be blurred casually.
- Career tools can drift into scraping, applicant tracking, recruiting
  decisions, or guaranteed job-match scoring if boundaries are unclear.

## Final Capabilities

- Create, edit, archive, and delete long-lived job description records.
- Store role title, company, location, employment type, source URL, status,
  seniority, description text, and private notes.
- Create and edit analysis records with match score, summary, keywords,
  responsibilities, recommendations, and status.
- Create and edit skill match records with category, match level, evidence, and
  recommendation.
- Record analysis history events, summaries, status changes, and next steps.
- Keep dashboard and list responses lightweight with previews, counts, statuses,
  and company/role metadata.
- Load full job descriptions, analysis bodies, evidence, recommendations, and
  next-step text only through detail endpoints where needed.
- Support AI-assisted extraction only after quality, explainability, privacy,
  and governance review.
- Support resume comparison only through explicit user action and governed
  integration with Resume Builder.
- Preserve user review before treating any match score or recommendation as
  actionable.
- Keep candidate-first and employer-review signals clearly labeled if both are
  ever supported.

## Advanced Capabilities

- AI-assisted extraction of skills, responsibilities, keywords, and seniority.
- Highlighted source spans for extracted requirements, red flags, and
  recommendations.
- Resume comparison with visible evidence and gap explanations.
- Keyword coverage scoring and preparation checklists.
- Role comparison across saved job descriptions.
- Skill taxonomy support connected to Career Planner or Course Tracker.
- Exportable review reports for personal preparation.
- Interview preparation handoffs to AI Job Interviewer or Interview Coach.
- Job Tracker integration for application status and follow-up planning.
- Confidence and uncertainty indicators for extracted analysis.

## AI Opportunities

- Extract likely responsibilities, required skills, keywords, and seniority
  signals from a saved job description.
- Compare a job description against a user-selected resume or profile after
  explicit permission.
- Explain why a skill is matched, partial, missing, or strong.
- Suggest preparation steps, learning topics, or resume focus areas.
- Identify vague, inflated, or conflicting job posting language.
- Summarize role expectations in plain language.
- Generate interview preparation prompts from reviewed job requirements.

AI features must not replace user judgment or claim hiring certainty. Job
descriptions, resumes, profiles, skill evidence, and analysis notes should be
sent to an AI provider only through an approved backend path with explicit
governance, privacy handling, explainability expectations, and clear product
messaging.

## Ecosystem Connections

- Resume Builder: compare selected resumes against job requirements only after
  explicit user action.
- Career Planner: turn identified skill gaps into career goals and milestones.
- Course Tracker or Study Planner: convert missing skills into learning plans.
- AI Job Interviewer and Interview Coach: generate practice questions from
  reviewed role requirements.
- Job Tracker: move reviewed jobs into application tracking after user action.
- LinkedIn Bio Optimizer: align profile improvement suggestions with selected
  role signals.
- Dashboard or profile areas: may show high-level counts without exposing full
  job descriptions or private notes by default.

## Weekly Return Value

Users return weekly while searching for jobs, comparing roles, preparing
applications, reviewing skill gaps, and deciding what to improve before an
interview. The weekly value is structured clarity: each job posting becomes a
reviewable record with role context, analysis, evidence, skill matches, and
next steps instead of another pasted note or browser tab.

The mature product earns trust by being a preparation tool. It helps users read
job descriptions more clearly, but it does not scrape job boards, apply on a
user's behalf, make hiring decisions, guarantee fit, or replace career judgment.

## Success Criteria

- Users can save, analyze, review, and revisit job descriptions easily.
- Job descriptions, analyses, skill matches, and history remain connected.
- Match scores and recommendations are tied to visible evidence and review.
- Users can see uncertainty, source wording, and mode boundaries before using
  analysis for applications or hiring-content review.
- Dashboard and list APIs stay lightweight while detail endpoints provide full
  text only where needed.
- Users understand whether analysis is manually entered, AI-assisted, or
  otherwise generated.
- Any AI extraction, resume comparison, export, or cross-app handoff is
  explicit and governance-reviewed.
- The product does not drift into applicant tracking, recruiting automation,
  job scraping, hiring decisions, or guaranteed career advice.
- Career preparation improves while preserving user accountability.

## Journey Progress

Current Position: 60 / 100
Destination: 100 / 100
Remaining Journey: 40 / 100

This estimate describes product maturity, not feature completion. Job
Description Analyzer already has a strong live V1 with isolated backend
storage, editable job descriptions, analysis records, skill matches, history,
owner-scoped APIs, lightweight list responses, detail endpoints, and protected
frontend workflow pages. The remaining journey is mostly analysis-quality and
career-integration maturity: AI extraction, resume comparison, evidence-backed
match explanations, role comparison, preparation plans, export, and governed
handoffs to Resume Builder, Career Planner, Job Tracker, and interview tools.

## Future Version Ideas

- V1.1: Improve review states, history filters, skill evidence display, and
  match-score explanations.
- V1.2: Add role comparison, preparation checklists, and keyword coverage
  summaries.
- V1.3: Add explicit handoffs to Resume Builder, Career Planner, Job Tracker,
  AI Job Interviewer, and Interview Coach.
- V1.4: Add exportable review reports and skill taxonomy support.
- V2: Consider AI-assisted extraction, resume comparison, automated gap
  analysis, or richer career planning only after governance review and
  destination update.

## Non Goals

Job Description Analyzer is not intended to become:

- An applicant tracking system.
- A recruiting automation platform.
- A job board or job scraper.
- An automated job application tool.
- A hiring-decision engine.
- A background-checking product.
- A compensation advice authority.
- A legal employment advice product.
- A guaranteed job-fit scoring engine.
- A resume builder.
- A legal compliance or hiring fairness certification tool.

These directions should remain out of scope unless the destination itself is
reviewed and intentionally changed.

## Guiding Principles

Every Job Description Analyzer feature should:

- Preserve job description, analysis, skill evidence, and history context.
- Improve role understanding before automating career decisions.
- Keep match scores explainable and reviewable.
- Separate source-backed evidence from recommendations, assumptions, and user
  decisions.
- Keep full job and analysis text out of list and dashboard payloads.
- Treat AI extraction as governed infrastructure, not a default shortcut.
- Avoid scraping, applying, recruiting, and hiring-decision scope.
- Keep resume comparison, export, AI, and cross-app handoffs explicit and
  scoped.
- Prefer focused handoffs to adjacent career tools instead of absorbing their
  responsibilities.

## Governance Notes

This destination is aspirational. It describes the target product direction,
not the current implementation and not an authorization to build every feature
now.

destination.md is not a promise of what will be built next. It is a
description of what the product could ultimately become if time, user value,
and platform direction remain aligned.

Product owner and Astra review are required before accepting, prioritizing, or
implementing any destination item. Particular care is needed before approving
AI extraction, resume comparison, export, job-board integrations, scraping,
application automation, career scoring, or cross-app automation because job
descriptions, resumes, analysis notes, skill gaps, career plans, and application
activity can reveal employment status, compensation goals, private career
strategy, location plans, identity details, and sensitive personal ambitions.

## Last Governance Review

Product Owner: Approved on 2026-07-03. Job Description Analyzer selected as
the next live app for the Destination Framework.
Astra: Approved on 2026-07-03. Journey Progress 60 / 100 accepted.
Codex: Drafted destination and identified governance discussion points.

Status:

Approved
