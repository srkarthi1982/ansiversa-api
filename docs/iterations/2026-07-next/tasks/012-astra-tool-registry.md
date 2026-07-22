# I1-012 — Astra Tool Registry

**Iteration:** 2026-07-next
**Priority:** High
**Status:** Frozen
**Depends On:** I1-002 — Astra AI Tool Framework
**Primary Repository:** `ansiversa-api`
**Supporting Repository:** `ansiversa`

---

# Objective

Create a governed Tool Registry for Astra AI.

The Tool Registry becomes the authoritative catalog of every tool available to Astra.

Rather than hard-coding tool selection inside the Assistant, Astra should discover approved tools through a central registry while preserving application ownership.

---

# Existing System Touchpoints

Extend the Tool Framework, Assistant orchestration, app-owned tool metadata,
Knowledge documentation, and generated API contract documentation. The registry
owns registration/discovery metadata only; tool execution remains in I1-002.

---

# Vision

Every application registers only the tools it owns.

Example:

Quiz

- get_quiz_progress_summary
- get_completed_quiz_platforms
- recommend_next_quiz_platform

Course Tracker

- get_course_progress_summary
- recommend_next_course_action

Notifications

- get_unread_notifications

Dashboard

- get_dashboard_summary

Astra discovers these through the Tool Registry.

---

# Core Principle

> Applications own tools.
> Astra owns orchestration.

Applications never execute another application's business logic.

---

# Registry Responsibilities

The Tool Registry should know:

- tool name
- owning application
- description
- supported intents
- authentication requirement
- owner-scoped status
- read-only/write capability
- input schema
- output schema
- timeout
- version
- enabled/disabled state

---

# Registry Structure

Suggested logical model:

```text
Tool
 ├── Name
 ├── App
 ├── Description
 ├── Intent Tags
 ├── Authentication
 ├── Owner Scoped
 ├── Read Only
 ├── Timeout
 ├── Version
 ├── Handler
```

Implementation details may differ.

---

# Registration

Each application registers its own tools during startup.

Example:

```text
Quiz
    ↓
Register Quiz Tools

Course Tracker
    ↓
Register Course Tools

Notifications
    ↓
Register Notification Tools
```

Applications must not register tools for another application.

---

# Discovery

The Assistant should request tools from the registry rather than importing application modules directly.

Example flow:

```text
User Question
      ↓
Intent
      ↓
Tool Registry
      ↓
Matching Tool
      ↓
Application Service
```

---

# Tool Metadata

Every tool should declare:

- unique name
- owning app
- supported intents
- description
- expected arguments
- result type
- timeout
- permissions
- read/write mode

---

# Read-Only vs Write

Clearly distinguish:

Read-only

- summaries
- recommendations
- progress
- searches

Write

- create
- update
- delete
- submit

Phase 1 supports read-only tools only.

---

# Authentication

Registry metadata should indicate:

- anonymous allowed
- authenticated required
- admin only
- owner scoped

---

# Validation

Reject duplicate:

- tool names
- routes
- conflicting ownership

Reject invalid:

- missing metadata
- missing handler
- unsupported schemas

---

# Versioning

Every tool should expose:

- version
- deprecated flag

Future versions may coexist during migrations.

---

# Performance

Requirements:

- lightweight lookup
- cached registry
- deterministic selection
- bounded execution
- timeout support

---

# Documentation

Document:

- registration process
- ownership rules
- naming conventions
- metadata contract
- lifecycle
- versioning

---

# Tests

Include tests for:

- registration
- duplicate registration
- discovery
- authentication metadata
- owner-scoping
- disabled tool
- timeout
- invalid metadata

---

# Browser Verification

Verify:

- Assistant still functions normally
- correct tools selected
- no UI regressions
- unsupported tools rejected

---

# Acceptance Criteria

The task is complete when:

- Tool Registry exists.
- Every tool has declared metadata.
- Applications own their registrations.
- Astra discovers tools through the registry.
- Duplicate registrations are prevented.
- Registry tests pass.

---

# Success Criteria

The Tool Registry becomes the single source of truth for Astra capabilities across all 100 applications.

Adding a new application tool should require registration only—no Assistant redesign.

---

# Future Scope

Not included:

- dynamic plugin downloads
- third-party tools
- external MCP servers
- autonomous tool generation
- write-capable orchestration
- AI-generated tools

---

# Delivery

After implementation, report:

- registry architecture
- registration mechanism
- metadata schema
- discovery flow
- validation rules
- test results
- documentation updates
- repository status

Confirm explicitly:

- Applications own their tools.
- Astra owns orchestration.
- Tool discovery is registry-driven.
- Read-only tools remain the default.
- Existing Assistant behavior remains unchanged.
- Exactly 100 apps remain.
- No App #101 was introduced.
- All repositories remain clean and aligned with `origin/main`.
