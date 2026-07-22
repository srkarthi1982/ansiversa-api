# I1-013 — Astra Intent Engine

**Iteration:** 2026-07-next
**Priority:** High
**Status:** Frozen
**Depends On:** I1-008 — Astra Dashboard Intelligence
**Depends On:** I1-012 — Astra Tool Registry
**Primary Repository:** `ansiversa-api`
**Supporting Repository:** `ansiversa`

---

# Objective

Implement the Astra Intent Engine.

The Intent Engine becomes responsible for determining what the user is trying to accomplish before selecting tools, retrieving data, or invoking OpenAI.

It serves as the decision layer between the user's message and Astra's execution pipeline.

---

# Existing System Touchpoints

Extract or extend existing Assistant intent and safety routing, Knowledge
identity handling, Tool Registry metadata, and OpenAI gating. Do not replace
deterministic identity/safety routing or allow tools/model routing to outrank it.

---

# Vision

Every Assistant request should first answer:

> "What is the user's intent?"

before deciding:

- which tools to execute
- whether personal data is required
- whether OpenAI is required
- which response mode to use

---

# Architecture

```text
User Message
      ↓
Intent Engine
      ↓
Intent Classification
      ↓
Tool Selection
      ↓
Tool Registry
      ↓
Application Tools
      ↓
Response Builder
```

---

# Responsibilities

The Intent Engine should determine:

- user intent
- confidence
- required tools
- required context profile
- response mode
- supported actions

---

# Initial Intent Categories

Examples:

## Platform

- About Ansiversa
- Founder
- Astra identity
- Supported apps

---

## Navigation

- Open Quiz
- Go to Dashboard
- Open Notifications

---

## User Data

- My progress
- My notifications
- My activity
- My favorites

---

## Learning

- What should I study?
- Which course next?
- Weak Quiz topic

---

## Search

- Find an application
- Find a course
- Find Quiz

---

## Help

- How do I...
- Explain...
- What does this feature do?

---

## Unsupported

Questions outside Astra's supported scope.

---

# Intent Resolution

The engine should classify using:

- deterministic rules
- application metadata
- tool metadata
- context
- conversation references

OpenAI should not perform primary intent classification.

---

# Confidence

Suggested levels:

- High
- Medium
- Low

Low-confidence requests should trigger clarification rather than guessing.

---

# Clarification

Example:

User:

> Open it.

If multiple valid targets exist:

Astra:

> Which one would you like to open?
> • Quiz
> • Course Tracker

Never guess.

---

# Response Modes

The Intent Engine selects:

- Deterministic
- Tool-based
- Tool + OpenAI
- Fallback

---

# Tool Selection

The engine should never execute tools directly.

Instead:

Intent
↓

Tool Registry
↓

Approved Tool

---

# Context Selection

The engine requests only the required context profile.

Examples:

Identity question

↓

No personal context

Progress question

↓

Personalization profile

Learning question

↓

Learning profile

---

# Performance

Requirements:

- deterministic
- lightweight
- bounded execution
- predictable
- cache-friendly

---

# Tests

Include tests for:

- identity intent
- navigation
- learning
- user data
- unsupported
- ambiguous
- clarification
- typo handling
- context selection
- tool selection

---

# Browser Verification

Verify:

- correct intent
- correct actions
- clarification
- no incorrect tool execution
- no unnecessary OpenAI calls

---

# Documentation

Create:

```
docs/architecture/astra-intent-engine.md
```

Document:

- intent categories
- routing flow
- confidence model
- clarification rules
- response mode selection

Update:

- AGENTS
- backend contracts
- Assistant documentation
- iteration documentation

---

# Acceptance Criteria

The task is complete when:

- Intent Engine exists.
- Requests are classified before execution.
- Clarifications replace guessing.
- Correct tools are selected.
- Context remains minimal.
- Tests pass.

---

# Success Criteria

Astra consistently understands what the user wants before deciding how to answer.

Intent classification becomes deterministic, explainable, and extensible.

---

# Future Scope

Not included:

- AI-generated intent models
- external NLP engines
- autonomous planning
- multi-agent reasoning

---

# Delivery

Report:

- architecture
- intent categories
- confidence model
- clarification behavior
- tool routing
- tests
- documentation
- repository status

Confirm explicitly:

- Intent selection remains deterministic.
- OpenAI does not classify primary intent.
- Tool execution remains registry-driven.
- Existing Assistant behavior remains backward compatible.
- Exactly 100 apps remain.
- No App #101 was introduced.
- All repositories remain clean and aligned with `origin/main`.
