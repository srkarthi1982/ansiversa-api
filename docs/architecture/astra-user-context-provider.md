# Astra User Context Provider

**Status:** Implemented v1.0
**Created:** 2026-07-22
**Iteration Task:** I1-003 — Platform User Context Provider

This document describes the governed backend provider that supplies Astra with
bounded, privacy-safe platform user context.

---

# Purpose

The Platform User Context Provider is the authoritative backend entry point for
safe user-level context used by Astra.

It answers:

```text
Is the user authenticated?
Where is the user in Ansiversa?
Which platform-level context is safe for this intent?
```

It does not export unrestricted personal records and does not query
application-owned databases.

---

# Core Rule

```text
Backend identity is authoritative.
Context loading is intent-driven and bounded.
OpenAI receives only sanitized approved context.
```

The frontend may provide current route and recent-app hints. The frontend may
not provide or override the authenticated user.

---

# Provider Contract

The provider lives in:

```text
app/modules/assistant/user_context.py
```

Primary structures:

- `PlatformUserContext`
- `UserContextApp`
- `UserActivityContext`
- `UserNotificationContext`
- `AssistantPreferenceContext`

The provider returns:

- authentication state
- backend-owned user reference only for tool execution
- validated current route
- canonical current app slug
- bounded favorite apps
- bounded frontend-validated recent apps
- bounded activity summary
- bounded unread notification summary
- safe assistance preferences when present
- source metadata and unavailable-source metadata

---

# Context Profiles

## Minimal

Used for public, safety, and identity paths.

Includes:

- authentication state
- validated current route
- canonical current app slug

The Assistant does not load personal context for deterministic identity and
safety answers.

## Personalization

Used for platform-level recent-app and activity questions.

Includes:

- minimal context
- owner-scoped favorites
- frontend-validated recent apps
- bounded activity summary

## Attention

Used for notification and attention questions.

Includes:

- personalization context
- unread notification summary
- safe notification preference flags when present

## Tool Execution

Used when an approved registered personal-data tool executes.

Includes:

- backend-owned internal user reference
- validated current route
- canonical current app slug

The internal user reference is not included in model-facing sanitized context.

---

# Sources

| Context | Source | Ownership |
| --- | --- | --- |
| Authentication | Existing backend auth | Platform |
| Current route | Frontend hint, backend validated | Shared |
| Current app | Canonical app catalog | Platform |
| Favorites | Existing Favorites service | Platform |
| Recent apps | Frontend-local hints, server validated | Frontend validated |
| Activity | Existing Activity Timeline service | Platform |
| Notifications | Existing Notifications service | Platform |
| Preferences | Existing `UserPreferences` read-only lookup | Platform |

No solution-app database is queried by the central provider.

---

# Privacy Boundary

The provider does not expose:

- passwords or password hashes
- tokens or session data
- email addresses
- phone numbers
- raw profile records
- internal IDs in model-facing context
- raw activity metadata
- full notification bodies
- private app records
- SQL or database schemas
- source paths or infrastructure details
- another user's context

`PlatformUserContext.to_openai_context()` omits backend user IDs and
authentication data.

---

# Failure Behavior

Context source failures degrade safely:

- failed Favorites lookup omits favorites
- failed Activity lookup omits activity summary
- failed Notifications lookup omits notification summary
- invalid recent-app hints are discarded
- anonymous requests return minimal anonymous context

Failures are logged as bounded operational metadata only. Raw context payloads
are not logged.

---

# Assistant Integration

The Assistant builds user context lazily:

```text
Identity / safety / public question
        ↓
No personal-context loading

Platform personal-context question
        ↓
Profile-specific context provider
        ↓
Deterministic response

Registered tool execution
        ↓
Tool-execution context profile
        ↓
I1-002 Tool Executor
```

No public user-context export endpoint was added.

---

# Current Supported Platform Questions

The provider supports deterministic platform-level context answers for:

- unread notification summaries
- recent app summaries
- recent activity summaries
- continue/check-first recommendations from recent or favorite apps

Direct Favorites questions remain routed through the I1-002 tool path and stay
protected by `ASTRA_PERSONAL_DATA_TOOLS_ENABLED=false` until personal-data tool
release gates are approved.

---

# Non-Goals

I1-003 does not implement:

- app-specific record queries
- Quiz tools
- Course Tracker tools
- OpenAI tool orchestration
- persistent memory
- public context export API
- frontend request contract changes
- migrations
- write operations
- recommendations engine
- App #101
