# Career Planner Destination

## App Name

Career Planner

## Destination Status

Approved v1.0

## Final Product Vision

Career Planner should become Ansiversa's focused career-growth planning
workspace: a place to define career goals, build roadmaps, track milestones,
and review progress without turning Ansiversa into a career coach marketplace,
job board, applicant tracking system, performance management suite, or
guaranteed career-outcome product.

At maturity, Career Planner should help users answer practical questions like
"Where am I trying to go?", "What workstream supports this goal?", "Which
milestone comes next?", "What changed in my plan?", and "What should I focus
on this week?" The product should turn broad ambition into structured,
reviewable progress while preserving user agency.

The mature product should serve students, job seekers, career changers,
professionals, and mentors who need a practical path from career intention to
measurable progress. It should support planning and reflection, not decide a
career path for the user.
Its market-informed position is a user-owned career strategy workspace:
multiple paths, tradeoffs, skills, constraints, and next actions stay visible
without treating career planning as a course funnel, employer surveillance
system, or AI prediction engine.

## Target Users

- Students planning a path toward a first role.
- Job seekers organizing readiness work.
- Career changers mapping skills and portfolio gaps.
- Professionals tracking growth and promotion goals.
- Mentors and coaches helping users structure development plans.
- Ansiversa users who need career planning without enterprise HR tooling.

## Core User Problems

- Career goals are often broad, vague, and hard to translate into action.
- Users need to break goals into roadmaps, milestones, notes, and review
  activity.
- Career planning loses momentum when progress and decisions are not visible.
- Users need to compare possible roles, skills, values, salary expectations,
  and personal constraints without being forced into one prescribed path.
- AI career guidance can overpromise certainty or push generic advice.
- Calendar, job search, and portfolio workflows are related but should remain
  separate unless explicitly connected.
- Career tools can drift into job matching, performance management, coaching
  marketplaces, and guaranteed outcome claims.

## Final Capabilities

- Create, edit, archive, and delete long-lived career goals.
- Create and edit roadmaps under goals with focus area, status, notes, and
  ordering.
- Create and edit milestones under roadmaps with success metrics, target dates,
  status, and ordering.
- Record review history for planning, completion, pause, archive, and update
  events.
- Keep dashboard and list responses lightweight with previews, status, counts,
  ordering, and timestamps.
- Load full notes, summaries, and review details only through detail endpoints
  where needed.
- Support guided templates for common career paths after review.
- Support skill-gap suggestions only when evidence and user context are clear.
- Support multiple possible path options and tradeoff review when user context
  justifies it.
- Support reminders, exports, and cross-app handoffs only through explicit user
  action.
- Preserve user control over goals, milestones, and career direction.

## Advanced Capabilities

- Guided career templates for common transitions and growth tracks.
- Private decision criteria for values, constraints, role fit, compensation
  expectations, and timeline assumptions.
- Skill gap suggestions connected to Job Description Analyzer and Course
  Tracker.
- Weekly planning reviews and progress summaries.
- Calendar reminders only after privacy and notification review.
- Exportable career plans and milestone reports.
- Portfolio, resume, and interview-preparation handoffs.
- AI-assisted roadmap suggestions with visible assumptions.
- Mentor or coach collaboration only after permission and privacy review.
- Progress analytics that avoid performance-management scoring.

## AI Opportunities

- Suggest roadmap steps from a user-defined goal.
- Break a roadmap into measurable milestones.
- Identify likely skill gaps from selected job descriptions or resume context.
- Summarize progress and recommend next planning questions.
- Suggest learning, portfolio, or interview-preparation actions.
- Explain tradeoffs between different career paths without claiming certainty.

AI features must not decide the user's career or promise outcomes. Goals,
roadmaps, milestones, notes, job signals, and profile context should be sent to
an AI provider only through an approved backend path with explicit governance,
privacy handling, career-sensitivity review, and clear product messaging.

## Ecosystem Connections

- Job Description Analyzer: turn role gaps into career goals and milestones.
- Resume Builder: align resume improvements with selected career goals.
- Portfolio Creator: convert portfolio gaps into roadmap work.
- Course Tracker and Study Planner: turn learning needs into course and study
  plans.
- AI Job Interviewer and Interview Coach: create preparation milestones.
- Job Tracker: connect application activity to career-plan review only through
  explicit handoff.

## Weekly Return Value

Users return weekly to review goals, update roadmaps, complete milestones,
adjust plans, and decide what to focus on next. The weekly value is momentum:
the app keeps direction, workstreams, checkpoints, and review history visible
without forcing the user into a rigid career system.

The mature product earns trust by supporting deliberate progress. It should not
guarantee promotions, choose careers for users, score employability as truth, or
replace professional judgment.

## Success Criteria

- Users can define goals, roadmaps, milestones, and reviews easily.
- Career progress remains visible and editable over time.
- Milestones are measurable without becoming punitive performance scores.
- Career plans support exploration and tradeoffs without claiming salary,
  promotion, or job-offer certainty.
- Dashboard and list APIs stay lightweight while detail endpoints provide full
  editable records where needed.
- Users understand whether suggestions are manual, template-based, or
  AI-assisted.
- Any AI guidance, reminders, exports, mentor review, or cross-app handoff is
  explicit and governance-reviewed.
- The product does not drift into job boards, ATS, HR performance management,
  coaching marketplaces, or guaranteed career outcome claims.

## Journey Progress

Current Position: 62 / 100
Destination: 100 / 100
Remaining Journey: 38 / 100

This estimate describes product maturity, not feature completion. Career
Planner already has a strong live V1 with isolated backend storage, goals,
roadmaps, milestones, review history, owner-scoped APIs, lightweight summaries,
detail endpoints, and protected frontend workflow pages. The remaining journey
is mostly planning-quality and ecosystem maturity: guided templates, progress
reviews, skill-gap suggestions, reminders, exports, and governed handoffs to
resume, job, course, portfolio, and interview workflows.

## Future Version Ideas

- V1.1: Improve review filters, milestone progress states, and roadmap
  ordering.
- V1.2: Add guided templates and weekly review summaries.
- V1.3: Add explicit handoffs to Job Description Analyzer, Resume Builder,
  Portfolio Creator, Course Tracker, Study Planner, and interview tools.
- V1.4: Add exportable career plans and optional reminders.
- V2: Consider AI-assisted roadmap generation, mentor collaboration, or deeper
  analytics only after governance review and destination update.

## Non Goals

Career Planner is not intended to become:

- A job board.
- An applicant tracking system.
- A career coach marketplace.
- A guaranteed career-outcome product.
- An HR performance management suite.
- A compensation planning tool.
- A recruiting platform.
- A learning management system.
- A calendar app.
- A psychometric assessment authority.
- A labor-market oracle or salary guarantee product.

These directions should remain out of scope unless the destination itself is
reviewed and intentionally changed.

## Guiding Principles

Every Career Planner feature should:

- Preserve goal, roadmap, milestone, and review context.
- Support user agency rather than career prediction.
- Keep recommendations explainable, editable, and tied to user-provided
  evidence.
- Keep progress measurable without becoming punitive.
- Keep private notes out of list and dashboard payloads unless required.
- Treat AI guidance as governed support, not authority.
- Keep reminders, exports, mentor review, and cross-app handoffs explicit.
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
AI guidance, mentor collaboration, reminders, exports, job/resume integrations,
progress analytics, or cross-app automation because career plans can reveal job
search activity, private ambitions, compensation goals, identity details,
employment concerns, and long-term personal strategy.

## Last Governance Review

Product Owner: Approved on 2026-07-03. Career Planner selected as one of the
next five live apps for the Destination Framework.
Astra: Approved on 2026-07-03. Journey Progress 62 / 100 accepted.
Codex: Drafted destination and identified governance discussion points.

Status:

Approved
