# Course Tracker Astra AI Contract

**Status:** Implemented v1.0
**Created:** 2026-07-22
**Iteration Task:** I1-005 — Course Tracker Astra AI Integration

This document defines the Course Tracker-owned Astra tools and boundaries.

---

# Ownership

Course Tracker owns:

- course data
- course database access
- progress and completion rules
- deadline and stalled-course rules
- Course Tracker Astra tool handlers
- deterministic Course Tracker recommendations

Astra owns:

- Assistant intent routing
- Tool Registry discovery
- tool execution lifecycle
- response assembly
- safety, identity, and OpenAI boundaries

The central Assistant does not contain Course Tracker SQL or Course Tracker
business rules.

---

# Registered Tools

Course Tracker registers seven read-only tools through
`app/modules/course_tracker/astra_tools.py`.

## `get_course_progress_summary`

Returns bounded progress metrics for the authenticated user:

- total course count
- active, paused, and completed course counts
- average progress percentage
- total tracked study minutes
- latest activity date

## `get_active_courses`

Returns bounded active courses with:

- name
- provider
- category
- status
- progress percentage
- module counts
- total minutes
- target date
- latest progress date

## `get_completed_courses`

Returns Course Tracker courses whose Course status is `completed`.

Completion follows the existing Course Tracker status model. Astra does not
infer course completion from a guessed threshold or user wording.

## `get_course_nearest_completion`

Returns the active course with the highest Course Tracker completion percentage.

Tie breaking is deterministic:

```text
highest progress
|
v
nearest target date
|
v
course name
```

## `get_stalled_courses`

Returns active courses with no recent progress.

The Course Tracker service-owned threshold is:

```text
14 inactive days
```

An active course with no progress log is treated as stalled because there is no
recorded recent progress.

## `get_course_deadline_summary`

Returns overdue and due-soon active courses using the existing `targetDate`
field.

The Course Tracker service-owned due-soon window is:

```text
7 days
```

Courses without target dates are excluded. Completed and paused courses are not
treated as active deadline work.

## `recommend_next_course_action`

Returns a deterministic next action from real Course Tracker data.

Priority order:

```text
overdue active target date
|
v
nearest active completion
|
v
stalled active course
```

Every recommendation includes:

- course name
- action type
- progress percentage
- reason code
- explanation

OpenAI does not choose, reorder, or invent recommendations.

---

# Learning Intelligence Use

I1-006 may consume approved Course Tracker tool results through the Tool
Registry for cross-app learning guidance with Quiz.

Course Tracker remains authoritative for Course Tracker facts. Learning
Intelligence may use:

- `get_course_progress_summary`
- `get_course_nearest_completion`
- `get_stalled_courses`
- `recommend_next_course_action`

It must not query the Course Tracker database directly, expose private course
content, or merge Course Tracker data ownership with Quiz.

---

# Approved Arguments

Most tools accept only:

```json
{
  "limit": 5
}
```

The nearest-completion and recommendation tools accept no arguments.

Forbidden caller-controlled arguments include:

- `userId`
- `ownerId`
- raw SQL
- table names
- arbitrary sort fields
- unrestricted date ranges

Backend authentication injects the user identity.

---

# Privacy Boundary

Course Tracker Astra tools never expose:

- owner IDs
- internal course IDs
- internal module IDs
- internal progress-log IDs
- course goals
- module notes
- progress-log summaries
- progress-log reflections
- another user's records
- SQL or database details
- tokens or infrastructure metadata

All tool results are bounded, owner-scoped, and read-only.

---

# Canonical Actions

Course Tracker tools may return only validated internal Course Tracker actions.

Preferred route:

```text
/course-tracker/courses
```

Fallback route:

```text
/course-tracker
```

The Tool Framework filters actions against the allowed route registry.

---

# Runtime Gate

Course Tracker Astra tools are authenticated personal-data tools.

Production execution remains disabled by default through:

```text
ASTRA_PERSONAL_DATA_TOOLS_ENABLED=false
```

Tests and governed non-production verification may enable the gate
deliberately.

---

# Non-Goals

I1-005 does not implement:

- Course Tracker write tools
- creating, updating, completing, or deleting courses through Astra
- external course imports
- Quiz and Course Tracker combined reasoning
- OpenAI tool orchestration
- recommendation engine
- persistent memory
- frontend contract changes
- migrations
- App #101
