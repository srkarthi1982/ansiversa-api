# Astra Learning Intelligence

**Status:** Implemented v1.0
**Created:** 2026-07-22
**Iteration Task:** I1-006 — Astra Learning Intelligence

This document describes the first cross-app Astra intelligence layer.

---

# Purpose

Astra Learning Intelligence combines approved Quiz and Course Tracker tool
results into one deterministic learning recommendation.

It proves that Astra can compose app capabilities without owning app data or
duplicating app business logic.

---

# Core Rule

```text
Apps own learning facts.
Astra owns cross-app orchestration.
Learning Intelligence combines tool results, not databases.
```

Learning Intelligence does not import Quiz or Course Tracker models, services,
database sessions, or SQLAlchemy queries.

---

# Supported Sources

I1-006 supports only the already-approved learning app pilots:

- Quiz
- Course Tracker

Both sources remain authenticated, owner-scoped, read-only, and production-gated
through `ASTRA_PERSONAL_DATA_TOOLS_ENABLED=false`.

---

# Tool Plan

Each Learning Intelligence request may execute at most:

```text
2 tools total
1 Quiz tool
1 Course Tracker tool
```

Approved tool plans use registered capability names only.

Examples:

```text
daily guidance
  recommend_next_course_action
  get_quiz_topic_performance

learning summary
  get_course_progress_summary
  get_quiz_progress_summary

weakness
  get_quiz_topic_performance
  recommend_next_course_action

completion
  get_course_nearest_completion
  recommend_next_quiz_platform

stalled work
  get_stalled_courses
  get_quiz_topic_performance
```

If a capability is unavailable, Learning Intelligence continues only when the
remaining source can support a truthful answer.

---

# Recommendation Rules

Recommendations are deterministic.

Priority order:

```text
1. urgent Course Tracker deadline
2. nearest Course Tracker completion
3. repeated weak Quiz topic
4. stalled Course Tracker course
5. recent learning continuity
6. next Quiz platform
7. insufficient data
```

Intent-specific questions may promote the relevant recommendation type. For
example, a weakest-topic question prioritizes Quiz revision when Quiz provides
repeated evidence.

OpenAI does not choose, reorder, or invent recommendations in I1-006.

---

# Response Contract

The internal recommendation model contains:

- recommendation type
- source app
- title
- reason code
- reason
- supporting facts
- confidence
- optional validated action
- deterministic priority

The public Assistant response remains unchanged:

```text
answer
actions
sources
confidence
responseMode
```

No frontend API contract change was introduced.

---

# Confidence

Learning Intelligence maps internal confidence to the existing Assistant
confidence values.

Rules:

- `high`: strong direct app evidence and stable deterministic rule
- `medium`: valid evidence with partial or competing signals
- `low`: insufficient evidence or unavailable learning sources

No mathematical confidence score is exposed.

---

# Time Budget

I1-006 recognizes bounded time-budget prompts such as:

- 30 minutes
- one hour
- two hours

The response adds simple deterministic session guidance. It does not estimate
exact course completion time unless an app-owned tool provides that fact.

---

# Actions

Actions come only from sanitized tool results.

Supported actions include:

- `/course-tracker/courses`
- `/quiz/play`
- `/quiz/results`

The Tool Framework validates action routes against the allowed route set.

---

# Privacy

Learning Intelligence does not expose:

- another user's learning data
- raw Quiz answers
- Quiz answer keys
- course goals
- course notes
- progress-log summaries or reflections
- internal IDs
- source paths
- SQL
- schemas
- tokens
- raw tool payloads
- hidden reasoning traces

It uses only bounded tool result facts already approved by Quiz and Course
Tracker.

---

# Partial Data

If both tools succeed, Learning Intelligence may compare both sources.

If only Quiz succeeds, it may recommend Quiz revision or a next Quiz platform.

If only Course Tracker succeeds, it may recommend a course action.

If neither source provides meaningful learning data, it returns a truthful
empty-state response.

It never pretends both apps contributed when only one app provided useful data.
Response sources list only apps that contributed successful facts; checked but
empty sources may inform the no-data response without appearing as supporting
sources.

---

# Performance

I1-006 enforces:

- maximum two tool executions
- maximum one tool per learning app
- no recursive tool calls
- no model-controlled loops
- no direct app database access
- no all-app scan
- no unnecessary OpenAI call

Safe metadata is logged for learning intent, tools used, source status,
duration, and response mode. Raw records and raw tool payloads are not logged.

---

# Supported Questions

Examples:

- What should I study today?
- Should I continue my course or revise Quiz?
- What is my most important learning task?
- What am I closest to completing?
- Which Quiz topic should I revise?
- What have I ignored recently?
- I have one hour to study.
- Give me my learning summary.
- Continue where I stopped.
- Where am I struggling?

---

# Unsupported Questions

I1-006 does not support:

- write actions
- marking courses complete
- starting Quiz automatically
- creating study plans
- calendar scheduling
- notifications
- long-term memory
- external course providers
- AI-generated educational content
- all-app intelligence
- health, finance, or career orchestration
- App #101

---

# Architecture Validation

Current evidence:

```text
Quiz onboarding                 foundation changes required: No
Course Tracker onboarding       foundation changes required: No
Learning Intelligence           cross-app framework changes required: No
```

I1-006 validates:

```text
Direct app database access: No
Foundation changes required: No
Cross-app framework changes required: No
```
