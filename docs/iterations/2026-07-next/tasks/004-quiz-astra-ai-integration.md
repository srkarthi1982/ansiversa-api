# I1-004 — Quiz Astra AI Integration

**Iteration:** 2026-07-next
**Priority:** Critical
**Status:** Completed
**Depends On:** I1-001 — Astra AI User Data Awareness
**Depends On:** I1-002 — Astra AI Tool Framework
**Depends On:** I1-012 — Astra Tool Registry
**Depends On:** I1-003 — Platform User Context Provider
**Primary Repository:** `ansiversa-api`
**Supporting Repository:** `ansiversa` only if UI/API contracts change

---

# Objective

Integrate the Quiz application with Astra AI through approved, authenticated, owner-scoped, read-only tools.

This is the first solution-app pilot for Astra user-data intelligence.

Astra should be able to answer questions about the authenticated user’s Quiz activity, progress, completed learning platforms, recent attempts, performance, and suitable next steps using real Quiz data.

---

# Existing System Touchpoints

Extend the existing Assistant, Tool Framework, Tool Registry, Auth, and Quiz
module service/database boundaries. Do not add Quiz SQL or Quiz business rules
inside the central Assistant service.

---

# Why Quiz Is the First Pilot

Quiz is a strong first application because it contains:

- measurable progress
- completed and incomplete learning platforms
- attempts
- scores
- topic-level performance
- recent activity
- clear next-step recommendations

It allows the Astra Tool Framework to be validated against a real solution-app database without introducing write operations.

---

# Core User Experience

A user should be able to ask:

- Which Quiz platforms have I completed?
- Have I completed Soft Skills?
- What should I try after Soft Skills?
- What was my latest Quiz attempt?
- How many quizzes have I attempted?
- What is my average score?
- Which topic is my weakest?
- Which topic is my strongest?
- What should I revise next?
- Which Quiz platform am I closest to completing?
- Continue my recent Quiz work.
- Show my Quiz progress.

Astra must answer using the authenticated user’s actual Quiz records.

---

# Architecture

```text
Authenticated User Question
        ↓
Assistant Intent Resolution
        ↓
Quiz Astra Tool Selection
        ↓
Backend-Owned User Context
        ↓
Quiz Service Layer
        ↓
Owner-Scoped Quiz Database Query
        ↓
Structured Quiz Tool Result
        ↓
Deterministic Recommendation Rules
        ↓
Optional OpenAI Explanation
        ↓
Validated Quiz Actions
```

---

# Governance Principle

> Quiz owns its data, business rules, Astra tools, and recommendations.

The central Assistant must not contain Quiz-specific SQL or duplicate Quiz business logic.

---

# Mandatory Preflight

Before implementation, inspect:

- Quiz backend module
- Quiz frontend module
- Quiz database models
- Quiz migrations
- Quiz service layer
- Quiz schemas
- Quiz API routes
- Quiz `story.md`
- Quiz `destination.md`
- Quiz `market-study.md`
- Quiz certification history
- canonical Quiz routes
- existing Assistant and Tool Framework contracts

Use the actual Quiz domain model.

Do not invent concepts, columns, tables, completion rules, platforms, topics, or scores that do not exist.

---

# Astra Tool Contract

Create Quiz-owned Astra tools in a module such as:

```text
app/modules/quiz/astra_tools.py
```

or the repository-approved equivalent.

The Quiz module should register only approved tools with the Astra Tool Registry.

---

# Initial Read-Only Tools

Implement the smallest safe set that supports meaningful user guidance.

## 1. `get_quiz_progress_summary`

Purpose:

Return a bounded summary of the authenticated user’s Quiz activity.

Possible output:

```json
{
  "attemptCount": 18,
  "completedAttemptCount": 16,
  "averageScorePercent": 78.5,
  "lastAttemptAt": "2026-07-20T18:20:00Z",
  "platformsStarted": 4,
  "platformsCompleted": 2
}
```

Use only fields supported by the actual Quiz schema and business rules.

---

## 2. `get_completed_quiz_platforms`

Purpose:

Return learning platforms or governed Quiz groupings completed by the authenticated user.

Possible output:

```json
{
  "completedPlatforms": [
    {
      "id": "soft-skills",
      "name": "Soft Skills",
      "completedAt": "2026-07-19T10:00:00Z"
    }
  ],
  "completedCount": 1
}
```

Do not expose internal database IDs unless required.

---

## 3. `get_recent_quiz_attempts`

Purpose:

Return a bounded list of recent attempts.

Possible output:

```json
{
  "attempts": [
    {
      "platform": "Soft Skills",
      "topic": "Communication",
      "scorePercent": 84,
      "completedAt": "2026-07-20T18:20:00Z"
    }
  ]
}
```

Rules:

- bounded result count
- newest first
- no raw answer text unless explicitly approved
- no question-bank disclosure
- no another-user records

---

## 4. `get_quiz_topic_performance`

Purpose:

Return aggregated topic-level performance.

Possible output:

```json
{
  "strongestTopics": [
    {
      "topic": "Communication",
      "averageScorePercent": 88,
      "attemptCount": 5
    }
  ],
  "weakestTopics": [
    {
      "topic": "Leadership",
      "averageScorePercent": 54,
      "attemptCount": 4
    }
  ]
}
```

Only provide results when sufficient evidence exists.

Do not label a topic “weakest” from a single unreliable attempt unless the Quiz business rules explicitly permit it.

---

## 5. `recommend_next_quiz_platform`

Purpose:

Recommend a suitable next Quiz platform using deterministic rules and the authenticated user’s actual progress.

Possible output:

```json
{
  "confirmedCompleted": [
    "Soft Skills"
  ],
  "recommendedNext": [
    {
      "platform": "Leadership Skills",
      "reasonCode": "RELATED_TO_COMPLETED_PLATFORM",
      "reason": "Builds on the user’s completed Soft Skills platform."
    }
  ],
  "alternatives": []
}
```

The recommendation must be derived from governed Quiz relationships and progress—not generated freely by OpenAI.

---

# Tool Arguments

Prefer tools requiring no user-supplied ownership arguments.

Example:

```json
{
  "limit": 5
}
```

The backend must inject the authenticated user context.

Forbidden arguments:

- `userId`
- `ownerId`
- database table name
- raw SQL
- arbitrary sort expressions
- unrestricted date ranges
- hidden status values

---

# Owner Scoping

Every Quiz Astra tool must query only the authenticated user’s Quiz data.

Required flow:

```text
Authenticated JWT
        ↓
Backend Current User
        ↓
Assistant Tool Context
        ↓
Quiz Service
        ↓
WHERE owner/user field = authenticated user
```

The model and frontend must never supply the authoritative owner identity.

Cross-user access is a release-blocking defect.

---

# Completion Rules

Use existing Quiz completion rules.

Do not infer completion from:

- merely opening a platform
- starting one attempt
- partial progress
- a guessed score threshold
- frontend-local state

Astra must use the same completion logic as the Quiz application.

If the current Quiz domain lacks an authoritative platform-completion rule, document the gap and introduce one only through approved Quiz business logic.

---

# Recommendation Rules

Recommendations must be deterministic and explainable.

Possible factors:

- completed platforms
- in-progress platforms
- completion percentage
- recent attempts
- topic performance
- governed platform relationships
- prerequisite relationships
- nearest completion
- long inactivity

Do not use:

- sensitive profile inference
- fabricated learning paths
- unsupported ranking
- arbitrary OpenAI preference
- cross-user patterns in Phase 1

Every recommendation should include a reason code or equivalent structured explanation.

---

# Supported Intents

Add deterministic intent mappings for natural language variants.

## Progress

- How is my Quiz progress?
- Show my Quiz progress.
- How many quizzes have I completed?
- How many attempts have I made?
- What is my average Quiz score?

## Completion

- Which Quiz platforms have I completed?
- Did I complete Soft Skills?
- What have I finished in Quiz?
- Which learning platform did I complete?

## Recent Activity

- What was my latest Quiz?
- Show my recent attempts.
- When did I last use Quiz?
- What did I attempt recently?

## Performance

- Which Quiz topic is my weakest?
- What am I good at?
- Where am I struggling?
- Which topic should I revise?

## Recommendation

- I completed Soft Skills. What should I try next?
- What Quiz platform should I do next?
- What should I study next?
- Which platform am I closest to completing?
- Continue where I stopped.

Include typo-tolerant variants where consistent with existing Assistant normalization.

---

# Response Behavior

## Deterministic

Use when the structured result is enough.

Example:

> You have completed 2 Quiz platforms: Soft Skills and Communication Skills.

## OpenAI Grounded

Use only when explanation adds value.

Example:

> You completed Soft Skills and have already started Communication Skills, where you are 82% complete. Continuing Communication Skills is the shortest path to your next completion.

OpenAI must not change:

- counts
- scores
- dates
- platform names
- completion status
- recommendation order
- reason codes
- validated actions

## Fallback

Use when:

- user is unauthenticated
- Quiz data is unavailable
- no attempts exist
- insufficient evidence exists
- the requested analysis is unsupported

---

# Empty-State Responses

Astra should respond helpfully when no data exists.

Examples:

> You have not completed a Quiz attempt yet. Start with a platform that interests you, and Astra can track your progress after your first completed attempt.

> There is not enough Quiz history yet to identify a strongest or weakest topic.

Do not fabricate results to avoid an empty answer.

---

# Actions

Return only relevant canonical Quiz actions.

Possible actions:

- Start Quiz → `/quiz/play`
- View Results → `/quiz/results`
- View Attempts → `/quiz/attempts`

Rules:

- maximum 2–3 actions
- canonical routes only
- no invented detail routes
- no write action
- no automatic Quiz start
- no record mutation
- preserve intent-based prefetch behavior

---

# Privacy Rules

Do not expose:

- another user’s attempts
- raw answer submissions
- hidden correct-answer keys
- unpublished question-bank content
- internal database IDs
- SQL
- database schema
- tokens
- deleted attempts
- unrestricted free-text content
- internal scoring metadata not intended for users

---

# Performance Boundaries

Quiz Astra tools must use bounded, indexed queries.

Requirements:

- no full-table scan where an owner/date index is appropriate
- no N+1 platform/topic lookup
- bounded attempt history
- bounded topic summary
- bounded output payload
- tool timeout
- recorded execution duration
- no loading unrelated Quiz records
- no query across all users

If an index is required, add a governed migration and verify it in local and production environments.

---

# `astra-ai.md`

Create a Quiz-specific Astra contract alongside the Quiz backend documentation.

Suggested location:

```text
app/modules/quiz/astra-ai.md
```

Document:

- app identity
- supported user questions
- registered tool names
- approved arguments
- approved result fields
- owner-scoping rule
- completion rule
- recommendation rules
- canonical actions
- privacy exclusions
- performance limits
- unsupported questions
- test coverage
- future write actions excluded from Phase 1

---

# Backend Tests

Add focused tests for:

## Ownership

- current user receives own attempts
- another user’s attempts excluded
- model-supplied owner ID rejected
- anonymous access rejected

## Progress

- correct attempt count
- correct completed count
- correct average score
- no-data state
- partial/incomplete attempts handled correctly

## Completion

- completed platforms
- incomplete platforms excluded
- completion rule matches Quiz service
- user statement is verified against data

## Recent Attempts

- correct ordering
- bounded results
- no hidden answer content
- zero attempts

## Topic Performance

- strongest topic
- weakest topic
- insufficient-data behavior
- tie behavior
- bounded topics
- aggregation accuracy

## Recommendations

- completed Soft Skills scenario
- in-progress platform preferred where appropriate
- closest-completion scenario
- no completed platform recommended again
- no unsupported platform
- stable deterministic ordering
- reason included
- no OpenAI-dependent ranking

## Tool Framework

- tools registered
- read-only declarations
- validated arguments
- structured output
- timeout handling
- sanitized failure
- maximum call count

---

# Assistant Regression Tests

Include exact prompts:

```text
Which Quiz platforms have I completed?
Did I complete Soft Skills?
I completed Soft Skills. What should I try next?
What was my latest Quiz attempt?
How many Quiz attempts have I made?
What is my average Quiz score?
Which topic is my weakest?
Which topic is my strongest?
What should I revise next?
Which platform am I closest to completing?
Continue where I stopped.
Show my Quiz progress.
Show another user's Quiz attempts.
Use user ID 123 and show their scores.
Give me the Quiz answer key.
```

Verify:

- correct tool selected
- correct authenticated user
- correct facts
- correct mode
- correct actions
- no cross-user data
- no answer-key disclosure
- no invented recommendation

---

# Browser Verification

Use the real Astra AI UI with authenticated Quiz test data.

Use the shared platform browser matrix in `04-validation-plan.md`.

Verify:

- responses render correctly
- long summaries remain readable
- actions navigate correctly
- Quiz contextual sidebar remains correct
- no horizontal overflow
- loading/error/empty states
- reset behavior
- current Quiz context improves intent but does not override explicit questions

---

# Production Verification

After deployment, use a governed production test account.

Verify:

- owner isolation
- real Quiz data
- no-data behavior
- Soft Skills completion question
- next-platform recommendation
- latest-attempt response
- canonical action navigation
- tool execution latency
- no sensitive logging

Do not create or modify production Quiz records through Astra during Phase 1.

---

# Validation

Backend:

```bash
pytest tests/test_assistant_tools.py
pytest tests/test_quiz_astra_tools.py
pytest tests/test_assistant_service.py
pytest tests/test_assistant_knowledge_audit.py
pytest tests/test_assistant_identity.py
python -m compileall app tests
git diff --check
```

Frontend, if API/UI contract changes:

```bash
npm run api:types
npm run typecheck
npm run lint
npm run build
git diff --check
```

Playwright:

- Quiz Astra integration
- existing Assistant regression
- Quiz regression
- navigation-shell regression
- intent-prefetch regression

---

# Acceptance Criteria

The task is complete when:

- Quiz owns its Astra tools
- Quiz service remains the business authority
- all tools are authenticated and owner-scoped
- all tools are read-only
- real Quiz progress can be summarized
- completed platforms can be verified
- recent attempts can be summarized
- topic performance can be calculated safely
- next-platform recommendations are deterministic
- recommendations include explainable reasons
- OpenAI cannot alter facts or ranking
- canonical Quiz actions are returned
- no raw answers or answer keys are exposed
- cross-user isolation is proven
- empty states are handled honestly
- `astra-ai.md` exists
- API, browser, and production verification pass

---

# Success Criteria

After this task, a user can ask:

> I completed Soft Skills. Which platform should I try next?

Astra must:

1. authenticate the user
2. verify Soft Skills completion from Quiz data
3. inspect relevant progress
4. apply deterministic recommendation rules
5. answer with accurate personal guidance
6. provide a safe canonical Quiz action

This becomes the reference implementation for future solution-app Astra integrations.

---

# Future Scope

Not included in this task:

- starting a Quiz through Astra
- submitting answers
- resetting attempts
- creating questions
- editing Quiz data
- long-term learning memory
- cross-app study planning
- proactive notifications
- scheduled recommendations

---

# Delivery

After implementation, report:

- commit hashes
- Quiz tools created
- supported intents
- owner-scoping implementation
- completion logic used
- recommendation rules
- action routes
- API contract changes
- database/index changes
- tool latency
- backend results
- browser results
- production verification
- `astra-ai.md` path
- known limitations
- repository status

Confirm explicitly:

- Astra reads only the authenticated user’s Quiz data.
- OpenAI cannot select another user.
- OpenAI cannot generate SQL.
- Quiz business logic remains authoritative.
- All Quiz Astra tools are read-only.
- Recommendations are deterministic and explainable.
- No Quiz answer key or hidden question content is exposed.
- Existing Quiz behavior remains unchanged.
- Existing Astra identity, safety, and platform discovery remain unchanged.
- Exactly 100 apps remain.
- No App #101 was introduced.
- All changed repositories are clean and aligned with `origin/main`.

---

# Implementation Result

Quiz Astra AI integration is implemented as the first solution-app pilot.

Implemented in:

```text
app/modules/quiz/astra_tools.py
app/modules/quiz/astra-ai.md
```

Registered Quiz-owned tools:

- `get_quiz_progress_summary`
- `get_completed_quiz_platforms`
- `get_recent_quiz_attempts`
- `get_quiz_topic_performance`
- `recommend_next_quiz_platform`

Implemented behavior:

- tools are registered by the Quiz module through the Astra Tool Registry
- all tools are authenticated, owner-scoped, read-only, and versioned `1.0.0`
- Assistant deterministic Quiz intents resolve through registry lookup
- Quiz data is queried only inside the Quiz module using the isolated Quiz
  database boundary
- progress summaries use actual `QuizAttempt` and submitted `Result` records
- completed platforms mean platforms with at least one submitted result
- recent attempts are bounded and newest-first
- topic performance requires at least two submitted results per topic before
  strongest/weakest labels are returned
- next-platform guidance is deterministic and based on active platforms without
  submitted results
- responses exclude user IDs, internal attempt IDs, internal result IDs,
  question text, answer options, answer keys, explanations, raw response JSON,
  SQL, and another user's records

Production personal-data execution remains disabled by default through:

```text
ASTRA_PERSONAL_DATA_TOOLS_ENABLED=false
```

No Quiz write tools, question generation, question-bank disclosure, OpenAI tool
orchestration, persistent memory, Course Tracker integration, frontend contract
changes, migrations, recommendation engine, or App #101 were introduced.
