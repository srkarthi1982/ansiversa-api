# Quiz Astra AI Contract

**Status:** Implemented v1.0
**Created:** 2026-07-22
**Iteration Task:** I1-004 — Quiz Astra AI Integration

This document defines the Quiz-owned Astra tools and boundaries.

---

# Ownership

Quiz owns:

- Quiz data
- Quiz database access
- Quiz result interpretation
- Quiz Astra tool handlers
- Quiz recommendation rules

Astra owns:

- Assistant intent routing
- Tool Registry discovery
- Tool execution lifecycle
- response assembly
- safety, identity, and OpenAI boundaries

The central Assistant does not contain Quiz SQL or Quiz business rules.

---

# Registered Tools

Quiz registers five read-only tools through `app/modules/quiz/astra_tools.py`.

## `get_quiz_progress_summary`

Returns bounded progress metrics for the authenticated user:

- attempt count
- submitted result count
- average submitted score
- last attempt timestamp
- platforms started
- platforms completed through submitted results

## `get_completed_quiz_platforms`

Returns Quiz platforms where the authenticated user has submitted results.

Completion in this first pilot means:

```text
At least one submitted Quiz result exists for the platform.
```

This is a submitted-result completion signal, not a mastery or curriculum
completion rule.

## `get_recent_quiz_attempts`

Returns bounded recent submitted result summaries:

- platform
- subject
- topic
- roadmap
- score percent
- completion timestamp

It does not expose question text, options, selected answers, answer keys,
explanations, or response payloads.

## `get_quiz_topic_performance`

Returns strongest and weakest topic summaries only when repeated evidence
exists.

Minimum evidence:

```text
2 submitted results per topic
```

A single attempt is not enough to label a topic strongest or weakest.

## `recommend_next_quiz_platform`

Returns a deterministic next-platform recommendation.

Rules:

- Prefer active Quiz platforms without submitted results.
- If all active platforms have submitted results, suggest continuing a completed
  platform to improve.
- Do not use OpenAI to invent recommendations.

---

# Learning Intelligence Use

I1-006 may consume approved Quiz tool results through the Tool Registry for
cross-app learning guidance with Course Tracker.

Quiz remains authoritative for Quiz facts. Learning Intelligence may use:

- `get_quiz_progress_summary`
- `get_quiz_topic_performance`
- `recommend_next_quiz_platform`

It must not query the Quiz database directly, expose question-bank content, or
merge Quiz data ownership with Course Tracker.

---

# Privacy Boundary

Quiz Astra tools never expose:

- user IDs
- internal result IDs
- internal attempt IDs
- question text
- answer options
- answer keys
- explanations
- raw response JSON
- another user's records
- SQL or database details

All tool results are bounded and owner-scoped.

---

# Runtime Gate

Quiz Astra tools are authenticated personal-data tools.

Production execution remains disabled by default through:

```text
ASTRA_PERSONAL_DATA_TOOLS_ENABLED=false
```

Tests and governed non-production verification may enable the gate deliberately.

---

# Non-Goals

I1-004 does not implement:

- Quiz write tools
- question generation
- question-bank disclosure
- OpenAI tool orchestration
- persistent memory
- recommendations engine
- Course Tracker integration
- frontend contract changes
- migrations
- App #101
