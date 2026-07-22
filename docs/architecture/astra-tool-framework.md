# Astra Tool Framework

**Status:** Implemented v1.0
**Created:** 2026-07-22
**Iteration Task:** I1-002 — Astra AI Tool Framework

This document describes the shared backend runtime framework that executes
approved Astra tools.

---

# Purpose

The Astra Tool Framework provides the governed runtime layer for tool-backed
Assistant answers.

It allows Astra to execute approved, authenticated, owner-scoped, read-only
tools without moving application business logic into the central Assistant.

---

# Architecture Rule

```text
Applications own capabilities.
Astra owns orchestration.
Backend identity is authoritative.
```

The framework executes tools. It does not own app data or app business rules.

---

# Runtime Components

## Tool Definition

`AssistantToolDefinition` describes an approved tool:

- stable tool name
- description
- source app or platform source
- input schema
- output schema
- handler
- authentication requirement
- read-only declaration
- timeout
- visibility
- deterministic intents
- result limit

Tool definitions are explicit. Untrusted input cannot register tools.

## Tool Context

`AssistantToolContext` carries server-controlled execution context:

- request ID
- authenticated user object, when present
- current route
- current app slug
- allowed route set
- maximum tool calls

Callers and models cannot provide or override user identity.

## Tool Registry

`AssistantToolRegistry` provides the I1-002 runtime registry:

- explicit registration
- duplicate-name rejection
- exact-name lookup
- deterministic intent lookup
- authentication filtering
- visibility filtering
- model-compatible schema exposure

This is not the full I1-012 Tool Registry. I1-012 remains responsible for
longer-term metadata, discovery, versioning, and enabled/disabled state.

## Tool Executor

`AssistantToolExecutor` owns the execution lifecycle:

- lookup the allowlisted tool
- enforce authentication
- enforce Phase 1 read-only policy
- validate arguments
- execute the handler
- enforce timeout boundary
- validate and sanitize result shape
- route-validate actions
- record safe audit metadata
- return structured safe failures

The executor does not return stack traces, SQL, secrets, tokens, or raw personal
payloads to the user.

---

# Execution Pipeline

```text
Assistant message
        ↓
Safety / identity / restricted-request checks
        ↓
Deterministic tool intent
        ↓
Allowlisted tool lookup
        ↓
Backend-owned Tool Context
        ↓
Tool argument validation
        ↓
App-owned or platform-owned service call
        ↓
Bounded Tool Result
        ↓
Action route validation
        ↓
Deterministic Assistant response
```

OpenAI does not select or rewrite tool facts in I1-002.

---

# Demonstration Tool

I1-002 includes one safe demonstration tool:

```text
get_user_favorites_summary
```

The tool:

- requires authentication
- uses the existing Favorites service
- scopes results to the authenticated user
- is read-only
- returns a bounded favorites summary
- validates app routes against Assistant allowed routes
- excludes user IDs, favorite IDs, internal IDs, tokens, SQL, and raw records

This is a platform user-feature tool, not a solution-app integration.

Production personal-data execution is not approved by I1-002. The
demonstration tool remains disabled by default behind the backend-owned
`ASTRA_PERSONAL_DATA_TOOLS_ENABLED` setting until persistent audit logging,
user controls, deletion/export handling, and seeded verification gates are
approved and implemented.

---

# Security Model

Phase 1 enforcement:

- personal-data tools are disabled by default
- authenticated tools require backend-authenticated user context
- caller-supplied identity fields are rejected
- write tools are rejected
- arguments are schema-validated
- SQL-like and path traversal argument payloads are rejected
- result data size is bounded
- result item count is bounded
- actions are filtered to approved internal routes
- execution metadata is logged without raw payloads

Restricted requests, identity questions, and professional-boundary prompts
remain higher priority than tool routing.

---

# Audit Boundary

I1-002 records safe operational metadata through framework logging:

- request ID
- tool name
- source app
- outcome
- status
- duration
- result count
- response mode
- fallback reason

The permanent persisted personal-data audit sink remains a release gate before
personal-data tools go live.

---

# Release Gate

`ASTRA_PERSONAL_DATA_TOOLS_ENABLED` is a server-owned feature gate.

Default:

```text
false
```

When disabled:

- personal-data tool intent returns a bounded unavailable response
- the Favorites service is not queried
- no personal data is returned
- no tool actions are generated
- the request does not fall through to unrestricted retrieval or OpenAI

When enabled in governed test or non-production verification, existing
authenticated, owner-scoped, read-only execution remains unchanged.

Production must remain disabled until the remaining personal-data release gates
are approved and implemented.

---

# Extension Points

Future app tools should add:

1. app-owned service method
2. app-owned `astra_tools.py`
3. app-level `astra-ai.md`
4. explicit registration through the approved registry path
5. focused tests for ownership, privacy, bounds, and route safety

The central Assistant should not gain app-specific database queries or broad
conditional blocks.

---

# Backward Compatibility

The Assistant API response shape remains unchanged.

Existing public knowledge, identity, safety, discovery, route validation,
fallback behavior, and optional grounded OpenAI behavior remain compatible.

Guest users continue to receive public Assistant behavior. Authenticated
personal tools run only when the user is authenticated, the deterministic tool
intent is approved, and the server-owned personal-data tool gate is enabled.

---

# Non-Goals

I1-002 does not implement:

- Quiz tools
- Course Tracker tools
- solution-app tool integrations
- I1-012 Tool Registry metadata/versioning/discovery
- I1-003 User Context Provider
- OpenAI tool selection
- runtime OpenAI orchestration for tool facts
- AI memory
- recommendations
- autonomous workflows
- write operations
- migrations
- App #101
