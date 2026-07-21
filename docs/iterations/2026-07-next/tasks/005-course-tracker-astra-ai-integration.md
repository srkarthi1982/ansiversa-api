Next, create:

```text
docs/iterations/2026-07-next/tasks/005-course-tracker-astra-ai-integration.md
```

Use this content:

````markdown
# I1-005 — Course Tracker Astra AI Integration

**Iteration:** 2026-07-next  
**Priority:** Critical  
**Status:** Discussing  
**Depends On:** I1-001 — Astra AI User Data Awareness  
**Depends On:** I1-002 — Astra AI Tool Framework  
**Depends On:** I1-003 — Platform User Context Provider  
**Depends On:** I1-004 — Quiz Astra AI Integration  
**Primary Repository:** `ansiversa-api`  
**Supporting Repository:** `ansiversa` only if API or UI contracts change

---

# Objective

Integrate Course Tracker with Astra AI through authenticated, owner-scoped, read-only tools.

Astra should be able to answer questions about the authenticated user’s courses, progress, completion status, stalled learning, deadlines, and recommended next actions using real Course Tracker data.

This task validates that the Astra Tool Framework can support a second solution app with a different data model and business workflow.

---

# Why Course Tracker Is the Second Pilot

Course Tracker complements Quiz but represents a different kind of user journey.

Quiz focuses on:

- attempts
- scores
- topic performance
- learning-platform completion

Course Tracker focuses on:

- courses
- modules or milestones
- progress
- status
- dates
- completion
- stalled work
- next learning action

Together, Quiz and Course Tracker provide the first meaningful cross-app learning foundation for Astra.

---

# Core User Experience

A user should be able to ask:

- Which courses am I currently taking?
- Which course am I closest to completing?
- What course should I continue today?
- Which courses have I completed?
- Which course have I ignored recently?
- What is my progress in Python Fundamentals?
- Do I have any overdue course work?
- What did I work on most recently?
- Which course should I finish first?
- Show my learning progress.
- Continue where I stopped.
- What should I study next?

Astra must answer using the authenticated user’s actual Course Tracker records.

---

# Architecture

```text
Authenticated User Question
        ↓
Assistant Intent Resolution
        ↓
Course Tracker Astra Tool Selection
        ↓
Backend-Owned User Context
        ↓
Course Tracker Service Layer
        ↓
Owner-Scoped Course Tracker Database Query
        ↓
Structured Tool Result
        ↓
Deterministic Recommendation Rules
        ↓
Optional OpenAI Explanation
        ↓
Validated Course Tracker Actions
```

---

# Governance Principle

> Course Tracker owns its data, business rules, Astra tools, and recommendations.

The central Assistant must not contain Course Tracker SQL or duplicate its business logic.

---

# Mandatory Preflight

Before implementation, inspect:

- Course Tracker backend module
- Course Tracker frontend module
- database models
- migrations
- service layer
- schemas
- API routes
- `story.md`
- `destination.md`
- `market-study.md`
- certification history
- canonical Course Tracker routes
- existing progress and completion rules
- current Astra Tool Framework contracts
- Quiz Astra implementation for reusable patterns

Use the actual Course Tracker domain model.

Do not invent:

- course statuses
- milestones
- progress formulas
- deadlines
- completion thresholds
- module concepts
- recommendation rules

unless they already exist or are formally introduced through Course Tracker business logic.

---

# Astra Tool Contract

Create Course Tracker-owned Astra tools in a module such as:

```text
app/modules/course_tracker/astra_tools.py
```

or the repository-approved equivalent.

The Course Tracker module should register only approved, read-only tools.

---

# Initial Read-Only Tools

## 1. `get_course_progress_summary`

Purpose:

Return a bounded summary of the authenticated user’s Course Tracker activity.

Possible output:

```json
{
  "courseCount": 6,
  "activeCourseCount": 3,
  "completedCourseCount": 2,
  "pausedCourseCount": 1,
  "averageProgressPercent": 64.5,
  "lastActivityAt": "2026-07-20T16:30:00Z"
}
```

Use only statuses and fields supported by the actual schema.

---

## 2. `get_active_courses`

Purpose:

Return bounded active courses and their current progress.

Possible output:

```json
{
  "courses": [
    {
      "name": "Python Fundamentals",
      "progressPercent": 82,
      "status": "active",
      "lastUpdatedAt": "2026-07-20T16:30:00Z"
    }
  ]
}
```

Rules:

- owner-scoped
- bounded list
- stable ordering
- no internal database IDs unless required
- no unrestricted notes or free-text content

---

## 3. `get_completed_courses`

Purpose:

Return courses completed by the authenticated user.

Possible output:

```json
{
  "completedCourses": [
    {
      "name": "Introduction to SQL",
      "completedAt": "2026-07-12T10:00:00Z"
    }
  ],
  "completedCount": 1
}
```

Completion must follow existing Course Tracker business rules.

---

## 4. `get_course_nearest_completion`

Purpose:

Identify the active course closest to completion.

Possible output:

```json
{
  "course": {
    "name": "Python Fundamentals",
    "progressPercent": 92
  },
  "reasonCode": "HIGHEST_ACTIVE_PROGRESS",
  "reason": "This active course has the highest completion percentage."
}
```

Do not recommend a completed, archived, or invalid course.

---

## 5. `get_stalled_courses`

Purpose:

Identify active courses with no recent progress.

Possible output:

```json
{
  "stalledCourses": [
    {
      "name": "Data Structures",
      "progressPercent": 35,
      "inactiveDays": 18
    }
  ]
}
```

Use an approved deterministic inactivity threshold.

If no threshold currently exists, document the gap and introduce one through Course Tracker business rules rather than hiding it inside Astra.

---

## 6. `get_course_deadline_summary`

Purpose:

Return approved deadline or due-date information where the actual schema supports it.

Possible output:

```json
{
  "overdueCount": 1,
  "dueSoonCount": 2,
  "courses": [
    {
      "name": "Cloud Fundamentals",
      "dueDate": "2026-07-24",
      "status": "due_soon"
    }
  ]
}
```

If Course Tracker does not support deadlines, do not create fake deadline behavior. Document it as unsupported.

---

## 7. `recommend_next_course_action`

Purpose:

Recommend what the user should do next based on real Course Tracker data.

Possible result:

```json
{
  "primaryRecommendation": {
    "course": "Python Fundamentals",
    "actionType": "continue",
    "reasonCode": "NEAREST_COMPLETION",
    "reason": "This course is 92% complete and requires the least remaining effort."
  },
  "alternatives": [
    {
      "course": "Data Structures",
      "actionType": "resume",
      "reasonCode": "STALLED_ACTIVE_COURSE"
    }
  ]
}
```

Recommendation order must be deterministic.

---

# Tool Arguments

Prefer tools with minimal arguments.

Examples:

```json
{
  "limit": 5
}
```

or:

```json
{
  "courseName": "Python Fundamentals"
}
```

Forbidden arguments:

- `userId`
- `ownerId`
- table names
- raw SQL
- arbitrary field selectors
- unrestricted sort expressions
- unbounded date ranges
- hidden statuses

The backend injects authenticated ownership.

---

# Owner Scoping

Every Course Tracker Astra tool must retrieve only the authenticated user’s data.

Required flow:

```text
Authenticated JWT
        ↓
Backend Current User
        ↓
Assistant Tool Context
        ↓
Course Tracker Service
        ↓
Owner-Scoped Query
```

Cross-user data access is a release-blocking defect.

---

# Progress and Completion Rules

Astra must use the same progress and completion rules as Course Tracker.

Do not infer completion from:

- opening a course
- creating a course
- a guessed percentage threshold
- frontend-local state
- a user’s claim alone
- inactivity

If progress is stored differently across course records, normalize it through the Course Tracker service layer.

---

# Recommendation Rules

Recommendations should be deterministic and explainable.

Possible factors:

- highest active completion percentage
- most recently active course
- nearest deadline
- overdue status
- stalled active course
- explicit priority if supported
- incomplete prerequisites if supported
- last user activity
- completion state

Do not use:

- arbitrary OpenAI ranking
- sensitive profile inference
- fabricated course dependencies
- another user’s patterns
- unsupported “best course” claims
- generic world knowledge in place of actual course data

Every recommendation must include a structured reason.

---

# Supported Intents

## Summary

- Show my Course Tracker progress.
- How many courses am I taking?
- How many courses have I completed?
- What is my average progress?

## Active Courses

- Which courses am I currently doing?
- What courses are still active?
- Show my unfinished courses.

## Completion

- Which courses have I finished?
- Did I complete Python Fundamentals?
- What have I completed?

## Nearest Completion

- Which course am I closest to completing?
- What should I finish first?
- Which course needs the least work?

## Stalled Work

- Which course have I ignored?
- What have I not continued recently?
- Which course is stalled?
- What should I resume?

## Deadlines

- Do I have overdue course work?
- Which course is due soon?
- What should I complete this week?

Only support these when deadline data exists.

## Recommendations

- What should I study next?
- Which course should I continue today?
- Continue where I stopped.
- What should I focus on first?

Include reasonable typo and shorthand variants using existing normalization.

---

# Response Behavior

## Deterministic

Use when structured facts are sufficient.

Example:

> You have 3 active courses and 2 completed courses. Python Fundamentals is closest to completion at 92%.

## OpenAI Grounded

Use only when explanation adds value.

Example:

> Python Fundamentals is the best course to finish first because it is already 92% complete. Data Structures is also worth revisiting because it has been inactive for 18 days.

OpenAI must not change:

- counts
- progress percentages
- dates
- course names
- statuses
- recommendation order
- reason codes
- actions

## Fallback

Use when:

- user is unauthenticated
- no Course Tracker data exists
- requested analysis is unsupported
- service is unavailable
- insufficient evidence exists

---

# Empty-State Responses

Examples:

> You have not added any courses yet. Open Course Tracker to create your first course.

> You have no completed courses yet, but Python Fundamentals is currently your closest active course to completion.

> Course Tracker does not currently contain deadline information for your courses.

Do not fabricate data to avoid an empty response.

---

# Actions

Return only relevant canonical Course Tracker actions.

Possible actions:

- Open Courses → `/course-tracker/courses`
- Continue Course Tracker → canonical workflow route
- Open Course Tracker Overview → only when appropriate

Use actual canonical routes from the route registry.

Rules:

- maximum 2–3 actions
- canonical internal routes only
- no invented record detail route
- no automatic status change
- no record mutation
- no direct external course URL
- preserve intent-prefetch behavior

---

# Privacy Rules

Do not expose:

- another user’s courses
- private notes or descriptions unless explicitly required and approved
- unrestricted free-text course content
- internal database IDs
- deleted or archived data unless applicable to the user’s question
- SQL
- schema details
- tokens
- hidden metadata
- internal implementation fields

Use the minimum fields necessary.

---

# Performance Boundaries

Requirements:

- bounded course list
- indexed owner-scoped queries
- no N+1 module or milestone loading
- no all-user aggregation
- no full-table scans where indexes should exist
- bounded tool response
- execution timeout
- recorded duration
- no unrelated app database queries

Add a governed migration only if required for indexes or a formally approved progress field.

---

# `astra-ai.md`

Create:

```text
app/modules/course_tracker/astra-ai.md
```

Document:

- app identity
- supported questions
- tool names
- approved arguments
- approved output fields
- owner-scoping
- progress calculation
- completion rules
- stalled-course rule
- deadline support
- recommendation rules
- canonical actions
- privacy exclusions
- unsupported questions
- performance bounds
- tests
- future write capabilities excluded from Phase 1

---

# Backend Tests

## Ownership

- current user receives own courses
- another user’s courses excluded
- caller cannot override user identity
- anonymous request rejected

## Progress

- correct active count
- correct completed count
- correct average progress
- zero-course state
- paused/archived behavior
- invalid progress values handled safely

## Completion

- completed courses returned
- incomplete courses excluded
- completion rule matches Course Tracker service

## Nearest Completion

- correct course selected
- ties handled deterministically
- completed courses excluded
- inactive/archived courses handled correctly

## Stalled Courses

- correct inactivity calculation
- threshold behavior
- recent activity excluded
- no activity history state
- stable ordering

## Deadlines

Where supported:

- overdue
- due soon
- completed courses excluded
- missing dates handled safely
- timezone/date-boundary behavior

## Recommendations

- nearest-completion recommendation
- deadline-first recommendation where approved
- stalled-course recommendation
- no completed course recommended
- deterministic ordering
- structured reason returned
- no OpenAI-dependent ranking

## Tool Framework

- tools registered
- read-only declarations
- argument validation
- output validation
- route/action validation
- timeout and failure sanitization

---

# Assistant Regression Tests

Include exact prompts:

```text
Show my Course Tracker progress.
How many courses am I taking?
Which courses have I completed?
Did I complete Python Fundamentals?
Which course am I closest to completing?
What should I finish first?
Which course have I ignored recently?
What should I resume?
Do I have overdue course work?
Which course should I continue today?
Continue where I stopped.
What should I study next?
Show another user's courses.
Use user ID 123 and show their progress.
Change my course to completed.
```

Verify:

- correct tool
- correct authenticated user
- correct result
- correct response mode
- correct actions
- no cross-user data
- no write action
- no invented deadline or course

---

# Cross-App Learning Validation

This task should prepare, but not fully implement, a combined learning view across Quiz and Course Tracker.

Validate that Astra can distinguish:

```text
Quiz data
- attempts
- scores
- topic performance

Course Tracker data
- courses
- progress
- completion
- stalled work
```

Do not merge these into one tool yet unless separately approved.

Document future cross-app questions such as:

- What should I study today?
- Should I continue my course or revise a weak Quiz topic?
- What learning work is closest to completion?

These belong to a later Cross-App Intelligence task.

---

# Browser Verification

Use authenticated test data across:

- Chromium
- Chrome
- tablet
- mobile

Verify:

- personal answers render correctly
- actions navigate correctly
- empty states
- loading and error states
- long answers remain readable
- no horizontal overflow
- current Course Tracker context improves intent
- explicit unrelated questions are not forced into Course Tracker
- contextual sidebar remains correct

---

# Production Verification

Use a governed production test account.

Verify:

- owner-scoped course summaries
- nearest-completion answer
- stalled-course behavior
- no-data behavior
- valid routes
- tool execution latency
- no sensitive logging
- no production data mutation

---

# Validation

Backend:

```bash
pytest tests/test_assistant_tools.py
pytest tests/test_course_tracker_astra_tools.py
pytest tests/test_quiz_astra_tools.py
pytest tests/test_assistant_service.py
pytest tests/test_assistant_knowledge_audit.py
pytest tests/test_assistant_identity.py
python -m compileall app tests
git diff --check
```

Frontend, if changed:

```bash
npm run api:types
npm run typecheck
npm run lint
npm run build
git diff --check
```

Playwright:

- Course Tracker Astra integration
- Quiz Astra regression
- existing Assistant suite
- Course Tracker regression
- navigation-shell regression
- intent-prefetch regression

---

# Acceptance Criteria

The task is complete when:

- Course Tracker owns its Astra tools
- Course Tracker service remains authoritative
- all tools are authenticated and owner-scoped
- all tools are read-only
- active and completed courses can be summarized
- nearest completion is calculated correctly
- stalled work is identified deterministically
- deadline behavior is truthful and schema-backed
- recommendations are explainable
- OpenAI cannot alter facts or ordering
- canonical actions work
- cross-user isolation is proven
- empty states are honest
- `astra-ai.md` exists
- API, browser, and production verification pass

---

# Success Criteria

After this task, a user can ask:

> Which course should I finish first?

Astra must:

1. authenticate the user
2. retrieve real active courses
3. apply Course Tracker progress rules
4. identify the most appropriate next course deterministically
5. explain the reason
6. provide a safe Course Tracker action

This becomes the second reference implementation for Astra-enabled solution apps.

---

# Future Scope

Not included:

- creating a course
- updating progress
- completing a course through Astra
- editing deadlines
- importing external learning platforms
- scheduled reminders
- proactive learning plans
- cross-app Quiz/Course orchestration
- long-term learning memory

---

# Delivery

After implementation, report:

- commit hashes
- tools created
- supported intents
- owner-scoping
- progress and completion logic
- stalled-course rule
- deadline support
- recommendation rules
- actions
- database/index changes
- API changes
- latency
- backend results
- browser results
- production verification
- `astra-ai.md` path
- known limitations
- repository status

Confirm explicitly:

- Astra reads only the authenticated user’s Course Tracker data.
- OpenAI cannot override user identity.
- OpenAI cannot generate SQL.
- Course Tracker business rules remain authoritative.
- All tools are read-only.
- Recommendations are deterministic and explainable.
- No unsupported deadlines or course facts are invented.
- Existing Course Tracker behavior remains unchanged.
- Quiz Astra integration remains unchanged.
- Existing Astra identity, safety, and discovery remain unchanged.
- Exactly 100 apps remain.
- No App #101 was introduced.
- All changed repositories are clean and aligned with `origin/main`.
````

Update `01-priority-backlog.md`:

```text
I1-005 | Course Tracker Astra AI Integration | Critical | Discussing
```

After this, the next task should be the first true combined-intelligence task:

```text
I1-006 — Astra Learning Intelligence
```

That task will allow Astra to use Quiz and Course Tracker together when answering questions such as:

> “What should I study today?”
