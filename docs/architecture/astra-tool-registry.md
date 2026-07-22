# Astra Tool Registry

**Status:** Implemented v1.0
**Created:** 2026-07-22
**Iteration Task:** I1-012 — Astra Tool Registry

This document describes the governed metadata and discovery layer for Astra
tools.

---

# Purpose

The Astra Tool Registry is the authoritative catalog of capabilities available
to Astra.

It answers:

```text
Which approved tools exist?
Who owns them?
What can they do?
Are they enabled?
How may they be discovered?
```

It does not execute tools. Execution remains owned by the I1-002 Tool Framework
executor.

---

# Core Rule

```text
Applications own tools.
Astra owns orchestration.
The registry owns capability metadata and discovery.
```

Applications must register only tools they own. The central Assistant must not
gain app-specific database queries or duplicate application business logic.

---

# Registry Components

## Tool Definition

`AssistantToolDefinition` is the registered runtime definition. I1-012 extends
it with permanent metadata:

- `source_app`
- `deterministic_intents`
- `owner_scoped`
- `permission_scope`
- `version`
- `enabled`
- `deprecated`
- `documentation_path`

The handler remains part of the definition for execution, but handler access is
not exposed through discovery metadata.

## Catalog Entry

`AssistantToolCatalogEntry` is the handler-free discovery view. It exposes:

- tool name
- owning app
- description
- supported intents
- authentication requirement
- owner-scoped status
- read-only/write mode
- permission scope
- input and output schemas
- timeout
- version
- enabled/disabled state
- deprecated state
- visibility
- result limit
- documentation path

Catalog entries are safe metadata. They do not expose database connections,
authenticated user objects, handlers, SQL, secrets, or raw payloads.

## Registry

`AssistantToolRegistry` owns:

- explicit registration
- optional owner assertion during registration
- duplicate-name rejection
- duplicate-intent rejection
- exact-name lookup
- deterministic intent lookup
- authentication-aware listing
- visibility-aware listing
- enabled/disabled filtering
- deprecated-tool filtering
- model schema listing
- capability metadata discovery

---

# Discovery Flow

```text
Assistant intent
        ↓
Tool Registry
        ↓
Capability metadata lookup
        ↓
Approved tool definition
        ↓
I1-002 Tool Executor
```

The Assistant uses registry lookup for deterministic tool intents. It does not
execute raw function names supplied by the user or model.

---

# Enabled State

Registered tools may be enabled, disabled, or deprecated.

Normal discovery omits:

- disabled tools
- deprecated tools
- internal tools unless internal visibility is explicitly requested
- authenticated tools when anonymous discovery is requested

Direct execution attempts for disabled or deprecated tools fail safely with a
bounded unavailable result and do not call the handler.

The server-owned `ASTRA_PERSONAL_DATA_TOOLS_ENABLED=false` gate remains the
production release gate for personal-data execution. I1-012 registry metadata
does not override that gate.

---

# Versioning

Every tool definition declares a semantic version in:

```text
major.minor.patch
```

Future versions may coexist during migrations only through explicit approved
registration and documentation. Deprecation must be declared in metadata before
an older capability is removed.

---

# Validation Rules

The registry rejects:

- duplicate tool names
- duplicate deterministic intents mapped to different tools
- registration owner mismatches when an owner assertion is provided
- invalid tool names
- invalid owning app identifiers
- missing descriptions
- invalid schemas
- invalid version strings
- owner-scoped tools that do not require authentication
- authenticated permission scopes that do not require authentication
- public tools that require authentication

The executor also rejects disabled or deprecated tools before invoking handlers.

---

# Current Registered Capabilities

The registry includes the existing I1-002 demonstration capability:

```text
get_user_favorites_summary
```

Metadata:

- owning app: `platform:favorites`
- version: `1.0.0`
- authentication: required
- owner scoped: yes
- read only: yes
- visibility: authenticated
- enabled in registry: yes
- production execution gate: `ASTRA_PERSONAL_DATA_TOOLS_ENABLED=false`

This remains a platform demonstration tool only. No Quiz, Course Tracker, or
solution-app tools are implemented by I1-012.

I1-004 adds the first solution-app pilot capabilities owned by Quiz:

```text
get_quiz_progress_summary
get_completed_quiz_platforms
get_recent_quiz_attempts
get_quiz_topic_performance
recommend_next_quiz_platform
```

These are authenticated, owner-scoped, read-only Quiz capabilities at version
`1.0.0`. They are registered by the Quiz module and executed through the shared
framework. Production personal-data execution remains controlled by
`ASTRA_PERSONAL_DATA_TOOLS_ENABLED=false` until release gates are approved.

---

# Non-Goals

I1-012 does not implement:

- new app-specific tools
- User Context Provider
- OpenAI tool orchestration
- persistent registry database
- admin registry UI
- dynamic plugin downloads
- external MCP servers
- write-capable orchestration
- AI-generated tools
- migrations
- App #101
