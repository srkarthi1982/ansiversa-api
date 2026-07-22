# I1-006 — Astra Learning Intelligence

**Iteration:** 2026-07-next
**Priority:** High
**Status:** Completed
**Depends On:** I1-001 — Astra AI User Data Awareness
**Depends On:** I1-002 — Astra AI Tool Framework
**Depends On:** I1-012 — Astra Tool Registry
**Depends On:** I1-003 — Platform User Context Provider
**Depends On:** I1-004 — Quiz Astra AI Integration
**Depends On:** I1-005 — Course Tracker Astra AI Integration
**Related Future Task:** I1-013 — Astra Intent Engine
**Related Future Task:** I1-014 — Astra Response Builder
**Primary Repository:** `ansiversa-api`
**Supporting Repository:** `ansiversa` only if API or UI contracts change

---

# Objective

Enable Astra AI to combine approved, authenticated, owner-scoped learning data from Quiz and Course Tracker to provide personalized learning guidance.

This is the first cross-app intelligence task in Ansiversa.

Astra should move beyond reporting isolated app data and begin helping the authenticated user decide:

- what to study next
- what to revise
- what to finish first
- whether to continue a course or improve a weak Quiz topic
- where recent learning activity has stalled
- which learning action provides the most immediate value

---

# Existing System Touchpoints

Future implementation should extend Assistant orchestration, registered Quiz and
Course Tracker tools, the Intent Engine, and the Response Builder. Do not merge
Quiz and Course Tracker data ownership or move app-specific learning rules into
the central Assistant.

---

# Vision

Quiz and Course Tracker remain independent applications with separate databases, business rules, services, and Astra tools.

Astra Learning Intelligence combines their approved structured outputs into one explainable learning recommendation.

```text
Quiz
- attempts
- scores
- weak topics
- completed platforms
        ↓

Course Tracker
- active courses
- progress
- completed courses
- stalled courses
        ↓

Astra Learning Intelligence
        ↓

Personalized guidance
- revise
- continue
- finish
- resume
- start next
```

---

# Core User Experience

A user should be able to ask:

- What should I study today?
- Should I continue my course or revise Quiz?
- What is my most important learning task?
- Which course should I finish first?
- Which Quiz topic should I revise?
- What have I ignored recently?
- What am I closest to completing?
- I have one hour. What should I focus on?
- I completed Soft Skills. What should I do next?
- Am I making good learning progress?
- Where am I struggling?
- Continue where I stopped.
- Give me a learning summary.

Astra must answer using the authenticated user’s real Quiz and Course Tracker data.

---

# Governance Principle

> Cross-app intelligence may combine approved tool results, but it must not bypass app ownership or duplicate app business rules.

Quiz remains authoritative for Quiz data.

Course Tracker remains authoritative for Course Tracker data.

Astra Learning Intelligence owns only:

- orchestration
- comparison
- prioritization
- explanation
- validated cross-app recommendations

---

# Architecture

```text
Authenticated User Question
        ↓
Learning Intent Resolution
        ↓
Approved Tool Plan
        ├── Quiz Astra Tools
        └── Course Tracker Astra Tools
        ↓
Backend-Owned User Context
        ↓
Bounded Structured Results
        ↓
Deterministic Learning Rules
        ↓
Ranked Recommendation
        ↓
Optional OpenAI Explanation
        ↓
Validated Actions
```

---

# Mandatory Preflight

Before implementation, inspect:

- Astra Tool Framework
- Platform User Context Provider
- Quiz Astra tools
- Course Tracker Astra tools
- Quiz `astra-ai.md`
- Course Tracker `astra-ai.md`
- current Assistant service
- current Assistant response modes
- route registry
- existing recommendation rules
- learning-related Knowledge Registry entries
- current performance and timeout limits

Do not redesign Quiz or Course Tracker while implementing this task.

Do not introduce unsupported learning concepts.

---

# Scope

This task includes:

- learning intent classification
- approved multi-tool orchestration
- Quiz and Course Tracker result combination
- deterministic prioritization
- explainable recommendation reasons
- bounded multi-tool execution
- safe cross-app actions
- no-data and partial-data behavior
- regression coverage
- production verification
- learning intelligence documentation

---

# Non-Goals

Do not add:

- write actions
- automatic course completion
- automatic Quiz start
- background study plans
- calendar scheduling
- notifications
- long-term memory
- autonomous agents
- unrestricted multi-step tool chains
- external learning services
- model-generated SQL
- all-app cross-intelligence
- health, finance, or career orchestration
- App #101

---

# Tool Orchestration

Phase 1 should support a small, approved tool plan.

Possible tools:

```text
Quiz
- get_quiz_progress_summary
- get_quiz_topic_performance
- get_completed_quiz_platforms
- recommend_next_quiz_platform

Course Tracker
- get_course_progress_summary
- get_course_nearest_completion
- get_stalled_courses
- recommend_next_course_action
```

The exact tools used must come from I1-004 and I1-005.

Do not create hidden duplicate queries inside Learning Intelligence.

---

# Multi-Tool Limits

Initial limits:

- maximum 2 tools per request
- maximum 1 Quiz tool
- maximum 1 Course Tracker tool
- sequential or parallel execution only where safe
- bounded timeout per tool
- bounded combined timeout
- bounded result payload
- no recursive tool calls
- no model-controlled loop
- no automatic retries beyond approved policy

If one tool fails, Astra may continue with the available source only when the answer remains truthful.

---

# Deterministic Recommendation Model

Introduce a small, explainable prioritization model.

Possible recommendation types:

```text
FINISH_NEAREST_COURSE
REVISE_WEAKEST_TOPIC
RESUME_STALLED_COURSE
CONTINUE_RECENT_LEARNING
START_NEXT_QUIZ_PLATFORM
INSUFFICIENT_DATA
NO_LEARNING_ACTIVITY
```

Every recommendation must include:

- recommendation type
- source app
- source item
- reason code
- reason
- supporting facts
- confidence
- action route where applicable

---

# Initial Prioritization Rules

Use explicit, deterministic rules.

Suggested order:

## 1. Urgent deadline

If Course Tracker has a schema-backed overdue or due-soon item, it may take priority.

Only use when deadline data actually exists.

## 2. Near completion

Prefer an active course close to completion when finishing it provides clear value.

Example:

```text
Python Fundamentals — 92% complete
```

## 3. Significant weak topic

Recommend Quiz revision when:

- sufficient attempts exist
- performance is materially weaker than other topics
- the result is statistically meaningful under Quiz business rules

## 4. Stalled learning

Recommend resuming an active course that has been inactive beyond the approved threshold.

## 5. Recent continuity

When no stronger priority exists, continue the most recent valid learning activity.

## 6. Next platform

When the user completed a governed Quiz platform and has no stronger active course priority, recommend the next approved Quiz platform.

## 7. Empty state

When no meaningful learning data exists, provide a truthful starting recommendation.

Do not hide rule priority inside OpenAI prompts.

---

# Time-Aware Questions

Support bounded time-budget questions such as:

- I have 30 minutes. What should I study?
- I have one hour. What should I focus on?
- I have two hours tonight.

Phase 1 should use simple deterministic guidance.

Example model:

```text
Up to 30 minutes
→ revise one weak Quiz topic or continue a short learning step

31–60 minutes
→ continue nearest-completion course or focused Quiz revision

More than 60 minutes
→ primary task plus secondary review
```

Do not estimate exact course completion time unless real duration data exists.

Do not fabricate study-duration precision.

---

# Supported Intents

## Daily guidance

- What should I study today?
- What should I focus on?
- Give me my next learning task.
- What is most important now?

## Course versus Quiz

- Should I continue my course or revise Quiz?
- Should I finish a course or practice a weak topic?
- What gives me more value right now?

## Completion

- What am I closest to completing?
- Which learning task should I finish first?
- What can I complete quickly?

## Weakness

- Where am I struggling?
- Which topic should I revise?
- What is my weakest learning area?

## Stalled work

- What have I ignored?
- Which course should I resume?
- Where did I stop?

## Time budget

- I have 30 minutes.
- I have one hour to study.
- What can I do in two hours?

## Summary

- Give me a learning summary.
- How is my learning progress?
- What have I completed recently?

Include reasonable typo and shorthand variants using existing Assistant normalization.

---

# Response Contract

Introduce a stable internal result structure similar to:

```json
{
  "primaryRecommendation": {
    "type": "FINISH_NEAREST_COURSE",
    "sourceApp": "course-tracker",
    "title": "Continue Python Fundamentals",
    "reasonCode": "NEAREST_COMPLETION",
    "reason": "This course is 92% complete.",
    "supportingFacts": [
      "Progress: 92%",
      "Last updated: 2026-07-20"
    ],
    "confidence": "high",
    "action": {
      "label": "Open Course Tracker",
      "route": "/course-tracker/courses"
    }
  },
  "secondaryRecommendations": [],
  "sourcesUsed": [
    "quiz",
    "course-tracker"
  ]
}
```

Exact schemas should follow backend conventions.

---

# Response Modes

## Deterministic

Use when the recommendation and explanation can be generated safely from structured facts.

## OpenAI Grounded

Use when a more natural comparison improves readability.

OpenAI may explain:

- why one task has priority
- how Quiz and Course Tracker data relate
- what the user can do next

OpenAI must not change:

- scores
- progress
- dates
- completion status
- recommendation type
- recommendation order
- source app
- action routes
- reason codes

## Fallback

Use when:

- user is unauthenticated
- both tools fail
- no meaningful learning data exists
- intent is unsupported
- the request asks for unrestricted educational advice outside Ansiversa

---

# Partial Data Behavior

Examples:

## Quiz data only

> I found Quiz activity but no active Course Tracker records. Your weakest Quiz topic is Leadership, so revising it is the clearest next step.

## Course Tracker data only

> I found active Course Tracker progress but no completed Quiz attempts. Python Fundamentals is 92% complete, so continuing it is the strongest next action.

## No data

> You do not yet have enough Quiz or Course Tracker activity for a personalized recommendation. You can start a Quiz platform or add a course to Course Tracker.

Do not pretend both sources were used when only one succeeded.

---

# Actions

Possible actions:

- Start Quiz → `/quiz/play`
- View Quiz Results → `/quiz/results`
- View Quiz Attempts → `/quiz/attempts`
- Open Course Tracker → `/course-tracker/courses`

Rules:

- maximum 2–3 actions
- primary action first
- canonical internal routes only
- no record mutation
- no invented detail routes
- no automatic app execution
- preserve intent-prefetch behavior

---

# Privacy Rules

Do not expose:

- another user’s learning data
- raw Quiz answers
- answer keys
- unrestricted course notes
- internal IDs
- hidden scoring metadata
- SQL
- schemas
- source paths
- authentication data
- raw tool payloads
- model reasoning traces

Only expose user-facing facts needed for the recommendation.

---

# Explainability

Every recommendation must answer:

```text
What should I do?
Why?
Which app contains it?
What fact supports the recommendation?
```

Example:

> Continue Python Fundamentals because it is already 92% complete. This is the shortest path to your next completed course.

Avoid vague answers such as:

> You may want to continue learning.

---

# Confidence

Use bounded confidence levels:

```text
high
medium
low
insufficient
```

Possible rules:

- High: strong direct evidence and stable rule
- Medium: valid evidence with competing options
- Low: limited evidence
- Insufficient: not enough data

Do not expose mathematical confidence values unless explicitly governed.

---

# Cross-App Conflict Resolution

When Quiz and Course Tracker produce competing recommendations, use deterministic tie-breaking.

Suggested order:

1. urgent deadline
2. near completion
3. serious weak-topic gap
4. stalled course
5. recent continuity
6. next platform
7. alphabetical/stable fallback only when all else is equal

Document every tie-break rule.

OpenAI must not resolve ties independently.

---

# Audit Logging

Record safe metadata:

- request ID
- learning intent
- tools used
- source success/failure
- recommendation type
- confidence
- duration
- response mode

Do not log:

- raw user records
- Quiz answers
- course notes
- full tool results
- tokens
- private prompts
- hidden reasoning

---

# Performance

Measure:

- intent resolution time
- Quiz tool duration
- Course Tracker tool duration
- combined orchestration duration
- response formatting duration
- total API latency
- result payload size

Requirements:

- no all-app scan
- no all-user aggregation
- maximum 2 tools
- no repeated tool calls
- no N+1 cross-app lookup
- bounded timeout
- no unnecessary OpenAI call when deterministic response is sufficient

---

# Tests

## Intent

- daily guidance
- course-versus-Quiz comparison
- near completion
- weak topic
- stalled work
- time-budget request
- learning summary
- unrelated question does not trigger learning intelligence

## Tool orchestration

- both tools succeed
- Quiz only succeeds
- Course Tracker only succeeds
- both fail
- timeout
- one empty result
- maximum tool count enforced
- no recursive tool call

## Recommendation rules

- deadline priority
- nearest completion
- weak topic
- stalled course
- recent activity
- next Quiz platform
- no data
- deterministic tie
- stable ordering

## Ownership

- current user only
- another user excluded
- caller cannot supply owner ID
- anonymous request rejected

## OpenAI preservation

- provider cannot change recommendation
- provider cannot alter facts
- provider cannot invent completion
- provider cannot change route
- provider cannot add unsupported source

## Safety

- request for another user’s learning data
- request for raw Quiz answers
- request for answer keys
- SQL-like prompt
- hidden schema request
- prompt injection
- write request
- unsupported general educational advice

---

# Exact Regression Prompts

```text
What should I study today?
Should I continue my course or revise Quiz?
What am I closest to completing?
Which Quiz topic should I revise?
Which course should I finish first?
What have I ignored recently?
I have 30 minutes. What should I study?
I have one hour to learn.
I completed Soft Skills. What should I do next?
Give me my learning summary.
Continue where I stopped.
Where am I struggling?
Show another user's learning progress.
Use user ID 123 and tell me what they should study.
Give me the Quiz answer key.
Mark my course as completed.
```

---

# Browser Verification

Use real Astra AI UI with authenticated test data.

Use the shared platform browser matrix in `04-validation-plan.md`.

Verify:

- answer readability
- primary and secondary actions
- correct app navigation
- no overflow
- loading state
- partial-data state
- no-data state
- failure state
- conversation follow-up
- current app context
- reset behavior
- contextual sidebar remains correct

---

# Conversation Follow-Up

Support bounded follow-up sequences.

Example:

```text
User:
What should I study today?

Astra:
Continue Python Fundamentals.

User:
Why?

Astra:
Because it is 92% complete and is your nearest course completion.
```

Another:

```text
User:
Should I continue my course or revise Quiz?

Astra:
Continue Python Fundamentals.

User:
What is my weakest Quiz topic?

Astra:
Leadership, based on your completed attempts.
```

Reset must remove prior conversational dependency.

---

# Production Verification

Use a governed production test account containing:

- Quiz history
- Course Tracker history
- at least one active course
- at least one completed course
- at least one weak Quiz topic
- one stalled course where supported

Verify:

- correct recommendation
- partial-data behavior
- owner isolation
- action navigation
- latency
- no data mutation
- safe logging
- no OpenAI fact drift

---

# Documentation

Create:

```text
docs/architecture/astra-learning-intelligence.md
```

Document:

- supported sources
- tool plan
- recommendation rules
- tie-break rules
- confidence
- partial-data behavior
- privacy
- performance
- supported questions
- unsupported questions
- future scope

Update:

- backend `AGENTS.md`
- Assistant story
- Quiz `astra-ai.md`
- Course Tracker `astra-ai.md`
- backend contracts
- shared resources
- iteration backlog
- dependencies
- risk register
- validation plan

---

# Acceptance Criteria

The task is complete when:

- Astra can combine Quiz and Course Tracker data
- maximum tool count is enforced
- source apps remain authoritative
- recommendations are deterministic
- reasons are explainable
- tie-break rules are documented
- partial-data behavior is truthful
- no-data behavior is useful
- OpenAI cannot change facts or ranking
- actions are canonical
- cross-user isolation is proven
- no write operations occur
- browser verification passes
- production verification passes
- architecture documentation is complete

---

# Success Criteria

After this task, a user can ask:

> What should I study today?

Astra must:

1. authenticate the user
2. retrieve approved Quiz and Course Tracker summaries
3. apply deterministic learning priorities
4. select one clear primary recommendation
5. explain why
6. provide a safe app action
7. remain truthful when data is partial or missing

This becomes Ansiversa’s first real cross-app personal intelligence capability.

---

# Future Scope

Not included:

- generating a weekly study plan
- creating calendar events
- sending reminders
- starting Quiz automatically
- completing course steps
- proactive daily briefings
- long-term learning memory
- external course providers
- AI-generated educational content
- broader cross-app productivity intelligence

---

# Delivery

After implementation, report:

- commit hashes
- supported intents
- tools used
- orchestration limits
- recommendation rules
- tie-break rules
- confidence behavior
- partial-data behavior
- action routes
- API changes
- tool latency
- total response latency
- backend tests
- browser results
- production verification
- documentation paths
- known limitations
- repository status

Confirm explicitly:

- Astra combines only the authenticated user’s Quiz and Course Tracker data.
- Quiz and Course Tracker remain the sources of truth.
- OpenAI cannot generate SQL or choose another user.
- OpenAI cannot change recommendation facts or order.
- Tool execution is bounded.
- Recommendations are deterministic and explainable.
- No write actions were added.
- Existing app behavior remains unchanged.
- Existing Astra identity, safety, discovery, and app-specific integrations remain unchanged.
- Exactly 100 apps remain.
- No App #101 was introduced.
- All changed repositories are clean and aligned with `origin/main`.

---

# Implementation Result

**Completed:** 2026-07-22

I1-006 implemented deterministic Astra Learning Intelligence as cross-app
orchestration over the already approved Quiz and Course Tracker capabilities.

Implemented:

- `app/modules/assistant/learning_intelligence.py`
- Learning Intelligence intent classification
- bounded tool plans with maximum two tools per request
- maximum one Quiz tool and one Course Tracker tool per request
- deterministic recommendation composition
- intent-specific prioritization for weakness, completion, stalled work,
  summary, daily guidance, comparison, and time-budget questions
- safe partial-data and no-data behavior
- Assistant routing before single-tool routing
- focused Learning Intelligence tests
- `docs/architecture/astra-learning-intelligence.md`

The implementation deliberately did not implement I1-013 or I1-014. It uses the
existing Assistant deterministic routing and response contract. Broader intent
engine and response builder work remain separately governed tasks.

Architecture validation:

```text
Direct app database access: No
Foundation changes required: No
Cross-app framework changes required: No
```

Learning Intelligence imports no Quiz or Course Tracker models, services,
database sessions, or SQLAlchemy queries. Quiz and Course Tracker remain the
sources of truth.

Tool plans use registered capability names only:

```text
Quiz:
get_quiz_progress_summary
get_quiz_topic_performance
recommend_next_quiz_platform

Course Tracker:
get_course_progress_summary
get_course_nearest_completion
get_stalled_courses
recommend_next_course_action
```

Out of scope remained out of scope:

- no write actions
- no direct app database queries
- no OpenAI tool orchestration
- no model-controlled tool loops
- no calendar scheduling
- no notifications
- no long-term memory
- no all-app intelligence
- no frontend contract changes
- no migrations
- no App #101
