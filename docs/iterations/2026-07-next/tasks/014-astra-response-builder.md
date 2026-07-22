# I1-014 — Astra Response Builder

**Iteration:** 2026-07-next
**Priority:** High
**Status:** Frozen
**Depends On:** I1-013 — Astra Intent Engine
**Primary Repository:** `ansiversa-api`
**Supporting Repository:** `ansiversa`

---

# Objective

Implement the Astra Response Builder.

The Response Builder becomes the final stage of Astra's execution pipeline. Its responsibility is to assemble tool results, deterministic logic, and optional OpenAI explanations into a single, consistent, trustworthy response.

It is the only component responsible for constructing the response returned to the frontend.

---

# Existing System Touchpoints

Extend the existing Assistant response schema, response modes, action validation,
OpenAI grounded provider boundary, and frontend Assistant renderer. Do not
execute app business logic in the Response Builder.

---

# Vision

Applications provide facts.

The Tool Registry provides tools.

The Intent Engine decides what is needed.

The Response Builder creates the final answer.

---

# Architecture

```text
User Question
      ↓
Intent Engine
      ↓
Tool Registry
      ↓
Application Tools
      ↓
Structured Results
      ↓
Response Builder
      ↓
Frontend
```

---

# Responsibilities

The Response Builder is responsible for:

- assembling tool results
- selecting the response mode
- preserving deterministic facts
- formatting recommendations
- attaching canonical actions
- building the final Assistant response

It must never execute business logic.

---

# Response Modes

Support the existing modes:

## Deterministic

Tool results alone answer the question.

Example:

> You have completed 4 Quiz platforms.

---

## Grounded Explanation

Structured facts remain unchanged.

OpenAI may improve readability.

Example:

> You have completed 4 Quiz platforms. The next recommended platform is Leadership Skills because it naturally follows Soft Skills.

---

## Fallback

When:

- unsupported request
- no data
- service unavailable
- insufficient information

---

# Response Contract

Every response should contain a structured internal representation.

Suggested model:

```text
Response
 ├── Answer
 ├── Facts
 ├── Recommendations
 ├── Actions
 ├── Sources
 ├── Confidence
 ├── Response Mode
```

Implementation details may differ.

---

# Facts

Facts originate only from:

- applications
- platform services
- deterministic calculations

Facts must never be modified by OpenAI.

Examples:

- counts
- dates
- percentages
- names
- completion status

---

# Recommendations

Recommendations should contain:

- recommendation type
- explanation
- supporting facts
- confidence
- canonical action

---

# Actions

Attach only validated actions.

Examples:

- Open Quiz
- Open Course Tracker
- View Notifications

Actions must use canonical routes.

---

# Confidence

Support bounded confidence levels:

- High
- Medium
- Low
- Insufficient

Confidence should come from deterministic rules.

---

# Formatting Rules

Responses should be:

- concise
- readable
- consistent
- accessible
- mobile friendly

Avoid unnecessary verbosity.

---

# Error Handling

Support graceful handling for:

- tool timeout
- missing data
- unavailable service
- invalid tool output

Never expose:

- stack traces
- SQL
- internal implementation details

---

# Response Consistency

Repeated identical requests should produce equivalent responses unless underlying data changes.

The builder should minimize unnecessary variation.

---

# Performance

Requirements:

- lightweight
- deterministic
- bounded
- reusable
- cache friendly

---

# Tests

Include tests for:

- deterministic response
- grounded response
- fallback
- action generation
- confidence
- formatting
- no-data
- tool failure
- multiple tool results

---

# Browser Verification

Verify:

- shared platform browser matrix from `04-validation-plan.md`

Check:

- readability
- long responses
- actions
- loading state
- follow-up compatibility

---

# Documentation

Create:

```
docs/architecture/astra-response-builder.md
```

Document:

- response flow
- response contract
- response modes
- action attachment
- confidence
- formatting rules

Update:

- backend AGENTS
- Assistant documentation
- backend contracts
- iteration documentation

---

# Acceptance Criteria

The task is complete when:

- Response Builder exists.
- Responses follow one consistent contract.
- Facts remain deterministic.
- Actions are canonical.
- Confidence is supported.
- Tests pass.

---

# Success Criteria

All Astra responses are generated through one consistent response pipeline regardless of which applications supplied the underlying data.

---

# Future Scope

Not included:

- markdown customization
- voice responses
- streaming responses
- charts
- rich media
- autonomous conversations

---

# Delivery

Report:

- architecture
- response contract
- response modes
- action handling
- confidence handling
- formatting rules
- tests
- documentation
- repository status

Confirm explicitly:

- Facts remain application-owned.
- OpenAI cannot modify deterministic facts.
- Canonical actions remain validated.
- Existing Assistant behavior remains backward compatible.
- Exactly 100 apps remain.
- No App #101 was introduced.
- All repositories remain clean and aligned with `origin/main`.
