# I1-009 — Astra AI Integration Contract

**Iteration:** 2026-07-next
**Priority:** High
**Status:** Completed
**Depends On:** Planning Freeze approval
**Primary Repository:** `ansiversa-api`
**Supporting Repository:** `ansiversa`

---

# Objective

Define the standard integration contract that every Ansiversa application must follow to integrate with Astra AI.

This contract ensures that Astra capabilities evolve consistently across all existing and future application enhancements.

The objective is to make Astra AI a first-class capability of every solution app while preserving application ownership and business boundaries.

---

# Existing System Touchpoints

Document extension points for the existing Assistant, Knowledge Registry, app
module documentation, frontend Assistant UI, and generated API contracts. This
task defines the contract; it does not redesign runtime architecture.

---

# Vision

Every application should answer two questions:

1. How does the user use this feature directly?
2. How will Astra AI help the user use this feature?

Every new feature should be designed with Astra integration in mind.

---

# Core Principle

> Every app owns its Astra capabilities.

The central Assistant coordinates tools but does not own application business logic.

Applications own:

- business rules
- services
- database access
- Astra tools
- Astra documentation
- supported questions

---

# Required Documentation

Every Astra-enabled application should include:

```text
market-study.md
story.md
destination.md
marketing.md
astra-ai.md
```

The new `astra-ai.md` document becomes the AI contract for that application.

---

# astra-ai.md Standard

Every application should document:

## App Identity

- app name
- purpose
- supported workflows

## Supported User Questions

Examples:

- What can Astra answer?
- Which questions are unsupported?

## Registered Tools

For every tool document:

- tool name
- description
- input arguments
- output schema
- authentication requirement
- owner-scoping rule
- read-only status

## Business Rules

Document:

- completion rules
- recommendation rules
- calculation rules
- validation rules

Astra must never duplicate these rules.

---

## Privacy Rules

Document:

- excluded fields
- sensitive data
- hidden data
- administrator-only data
- unsupported requests

---

## Actions

Document:

- supported navigation actions
- canonical routes
- unsupported actions

---

## Performance

Document:

- expected query limits
- result limits
- timeout expectations

---

## Test Coverage

Document:

- unit tests
- integration tests
- Assistant regression prompts
- browser verification

---

# Backend Responsibilities

Each backend module should own:

```text
service.py
router.py
schemas.py
astra_tools.py
astra-ai.md
```

Exact file names may follow repository conventions.

---

# Frontend Responsibilities

Frontend applications should:

- expose canonical routes
- expose validated actions
- preserve contextual navigation
- support Astra entry points where appropriate

No application-specific Assistant UI should be created.

The platform Assistant remains the single Astra experience.

---

# Development Rule

Whenever an application gains a new feature:

1. Business feature implemented
2. API completed
3. Tests completed
4. Documentation updated
5. Astra integration reviewed
6. `astra-ai.md` updated
7. Assistant regression verified

The feature is not considered complete until Astra integration has been reviewed.

---

# Governance

This contract applies to:

- all future enhancements
- all future Astra tools
- all future recommendations
- all future app intelligence

It does not require immediate Astra implementation for every feature.

It requires every feature to remain Astra-ready.

---

# Documentation Updates

Update:

- backend AGENTS.md
- frontend AGENTS.md
- workspace AGENTS.md
- coding standards
- app template
- iteration documentation

Add Astra integration guidance to future development documentation.

---

# Acceptance Criteria

The task is complete when:

- Astra integration standards are documented
- app responsibilities are clearly defined
- documentation structure is standardized
- future enhancements include Astra review
- no application duplicates Assistant business logic
- governance documentation is updated

---

# Implementation Result

The canonical contract is documented at:

```text
docs/astra-ai-integration-contract.md
```

This task updates API governance documentation and README references only.

No runtime Astra implementation is introduced by I1-009.

No personal-data tools are implemented by I1-009.

No app pilot integration is started by I1-009.

I1-009 establishes the standard that later frozen tasks must follow.

---

# Success Criteria

After this task every future enhancement naturally answers:

- What does this feature do?
- How does Astra understand it?
- How does Astra help the user?

Astra becomes part of the standard Ansiversa development lifecycle rather than a feature added later.

---

# Delivery

After implementation report:

- documentation created
- templates updated
- governance updates
- affected repositories
- backward compatibility
- known limitations
- repository status

Confirm explicitly:

- Every application owns its Astra capabilities.
- Business logic remains inside the application.
- Astra orchestrates rather than duplicates application behavior.
- Existing applications remain backward compatible.
- Exactly 100 apps remain.
- No App #101 was introduced.
- All repositories remain clean and aligned with `origin/main`.
