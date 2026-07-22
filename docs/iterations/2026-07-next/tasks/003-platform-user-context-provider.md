# I1-003 — Platform User Context Provider

**Iteration:** 2026-07-next
**Priority:** Critical
**Status:** Frozen
**Depends On:** I1-001 — Astra AI User Data Awareness
**Depends On:** I1-002 — Astra AI Tool Framework
**Depends On:** I1-012 — Astra Tool Registry
**Primary Repository:** `ansiversa-api`
**Supporting Repository:** `ansiversa` only if the Assistant request contract must change

---

# Objective

Create a governed Platform User Context Provider that supplies Astra AI with a small, authenticated, privacy-safe view of the current user’s Ansiversa context.

The provider must make it possible for Astra to understand:

- who the authenticated user is internally
- whether the user is authenticated
- the current page and current app
- favorite apps
- recently opened apps
- recent platform activity
- unread notification summary
- safe user preferences relevant to assistance

The provider must not expose unrestricted personal records or application database contents.

---

# Existing System Touchpoints

Extend Auth, Assistant context handling, Favorites, Activity, Notifications,
Dashboard, and the frontend Assistant context contract where needed. Do not add a
public user-context export endpoint or move app business logic into the shell.

---

# Problem Statement

Astra currently understands:

- the Ansiversa platform
- public platform identity
- the fixed catalog of 100 apps
- app purposes and relationships
- the current frontend route
- bounded session conversation context

However, Astra does not yet have a single governed backend source for authenticated user context.

Without a shared provider:

- every Astra tool may retrieve user context differently
- authentication rules may be duplicated
- favorites, recent activity, and preferences may become inconsistent
- tool prompts may receive unnecessary private data
- cross-app recommendations may become difficult to audit
- user context logic may spread across the central Assistant service

The Platform User Context Provider must become the authoritative entry point for safe user-level context.

---

# Architecture

```text
Authenticated Assistant Request
        ↓
Backend Authentication
        ↓
Platform User Context Provider
        ↓
Approved Context Sources
        ├── User profile summary
        ├── Favorites
        ├── Recent apps
        ├── Activity summary
        ├── Notifications summary
        └── Assistance preferences
        ↓
Bounded Structured Context
        ↓
Deterministic Retrieval / Astra Tools
        ↓
Optional OpenAI Explanation
````

---

# Core Governance Rule

> Astra receives only the minimum user context required to answer the current question.

The provider must not become a general user-data export service.

---

# Context Contract

Introduce a repository-appropriate structured contract similar to:

```python
class PlatformUserContext:
    is_authenticated: bool
    user_reference: str | None
    current_route: str | None
    current_app_slug: str | None
    favorite_apps: list[UserContextApp]
    recent_apps: list[UserContextApp]
    activity_summary: UserActivityContext | None
    notification_summary: UserNotificationContext | None
    assistant_preferences: AssistantPreferenceContext | None
```

The exact schema should follow current backend conventions.

---

# User Identity

The provider may carry a governed internal user reference for backend execution.

Rules:

* User identity must come from authenticated backend state.
* The frontend must not supply the authoritative user ID.
* OpenAI must not receive raw authentication claims.
* OpenAI must not receive tokens, session identifiers, email addresses, or database ownership IDs unless separately approved.
* Tool handlers must receive backend-owned identity through execution context.
* Cross-user context access is forbidden.

A public display name may be included only when needed for natural greetings and permitted by existing profile governance.

---

# Current Route and App Context

The provider should safely resolve:

* current canonical route
* current solution app slug
* whether the user is on a platform page or app page
* current workflow section where useful

The frontend may submit the current route as contextual input.

The backend must:

* validate the route
* reject malformed or external routes
* map it through canonical route metadata
* avoid trusting an arbitrary app slug from the client

Examples:

```text
/quiz/results
→ current_app_slug: quiz

/bill-splitter/bills
→ current_app_slug: bill-splitter

/pricing
→ current_app_slug: null
```

---

# Favorite Apps Context

Use the existing backend-backed Favorites implementation.

Return only bounded app metadata such as:

```json
{
  "slug": "quiz",
  "name": "Quiz",
  "route": "/quiz/play",
  "category": "Learning & Education"
}
```

Rules:

* owner-scoped
* canonical apps only
* validated routes
* bounded result count
* no favorite database row IDs
* no timestamps unless needed
* no hidden or non-catalog apps

---

# Recent Apps Context

Recent Apps currently remain frontend-local.

Phase 1 may include recent apps in the Assistant request context, subject to validation.

Rules:

* accept only known catalog slugs
* discard duplicates
* preserve a bounded order
* reject unknown slugs
* resolve names and routes server-side
* do not treat frontend-local history as authoritative business data
* do not persist it through this task

The provider should clearly distinguish:

```text
backend-owned context
frontend-supplied validated context
```

---

# Activity Context

Use the existing owner-scoped Activity Timeline service.

Return a summary, not the full timeline.

Suggested fields:

```json
{
  "recentActivityCount": 12,
  "lastActivityAt": "2026-07-21T...",
  "recentApps": ["quiz", "course-tracker"],
  "recentActivityTypes": ["navigation", "assistant"]
}
```

Rules:

* bounded lookback
* no unrestricted metadata
* no private app-record contents
* no prompts
* no financial amounts
* no health details
* no document text
* no arbitrary activity payloads

---

# Notification Context

Use the existing Notifications service.

Return summary information only.

Suggested fields:

```json
{
  "unreadCount": 3,
  "hasUnread": true,
  "types": {
    "reminder": 2,
    "system": 1
  }
}
```

Phase 1 must not return full notification bodies to Astra unless explicitly needed and separately approved.

---

# Assistant Preference Context

Use safe existing user preferences where relevant.

Possible fields:

* whether personalized recommendations are enabled
* whether contextual assistance is enabled
* whether user-data assistance is enabled
* preferred response conciseness if such a governed preference exists later

Do not infer sensitive attributes.

Do not include unrelated profile or account fields.

If these preferences do not yet exist, document the gap rather than inventing them.

---

# Context Profiles

Support bounded context profiles so every Assistant request does not retrieve everything.

Suggested profiles:

## Minimal

Used for platform identity, app discovery, safety, and public knowledge.

Includes:

* authentication state
* current route
* current app

## Personalization

Used for app recommendations and “what should I use next?” questions.

Includes:

* minimal context
* favorites
* recent apps
* bounded activity summary

## Attention

Used for “what needs my attention?” questions.

Includes:

* personalization context
* notification summary

## Tool Execution

Used when a registered personal-data tool runs.

Includes:

* backend-owned user reference
* current route/app
* only tool-required context

The provider should retrieve the smallest profile required by the resolved intent.

---

# Lazy Context Retrieval

Do not load all user context before every Assistant request.

Preferred flow:

```text
Resolve high-priority intent
        ↓
Identity / safety / public question?
        → Minimal or no personal context

Personalized recommendation?
        → Personalization profile

Notification question?
        → Attention profile

App-data question?
        → Tool-specific context
```

This protects latency, privacy, and query cost.

---

# Data Source Ownership

| Context               | Source of Truth                   | Ownership |
| --------------------- | --------------------------------- | --------- |
| Authentication        | Backend auth                      | Platform  |
| Current route         | Frontend input, backend validated | Shared    |
| Current app           | Canonical route registry          | Platform  |
| Favorites             | Parent database                   | Platform  |
| Recent apps           | Frontend-local bounded state      | Frontend  |
| Activity summary      | Activity Timeline service         | Platform  |
| Notification summary  | Notifications service             | Platform  |
| Assistant preferences | User Preferences                  | Platform  |

No application database should be queried directly by the central context provider.

App-owned personal data belongs to app-specific Astra tools.

---

# Privacy and Security

The provider must never expose:

* passwords or hashes
* tokens or sessions
* email addresses unless explicitly necessary
* phone numbers
* database URLs
* internal IDs in model-facing context
* unrestricted profile fields
* raw activity metadata
* full notification bodies by default
* private app records
* hidden audit data
* another user’s context
* source paths
* SQL
* infrastructure details

---

# OpenAI Boundary

OpenAI may receive a sanitized subset of context only when needed for explanation.

Example permitted context:

```json
{
  "currentApp": "Quiz",
  "favoriteApps": ["Quiz", "Course Tracker"],
  "recentApps": ["Quiz", "AI Notes Summarizer"],
  "unreadNotificationCount": 2
}
```

OpenAI must not receive:

* backend user ID
* tokens
* ownership columns
* internal activity metadata
* raw notification records
* database identifiers
* unrelated profile information

Deterministic identity and safety responses should continue bypassing OpenAI and personal-context loading.

---

# Failure Behavior

The provider must degrade safely.

Examples:

* Favorites unavailable → omit favorites context
* Activity unavailable → omit activity summary
* Notifications unavailable → omit notification summary
* Recent-app input invalid → discard invalid entries
* User unauthenticated → return anonymous/minimal context
* Database timeout → continue with available approved context where safe

A partial context failure must not expose an internal error or trigger unrestricted fallback access.

---

# Caching

Context caching may be used only when safe.

Rules:

* user-scoped cache keys
* short bounded lifetime
* immediate invalidation where existing state management supports it
* no shared cache between users
* no caching of tokens
* no public/CDN caching
* freshness documented for each context source

Phase 1 may avoid caching if query performance is already acceptable.

---

# Auditability

Record bounded operational metadata:

* request ID
* context profile requested
* context sources used
* source success/failure
* duration
* sanitized item counts

Do not log full personal context payloads.

Do not log raw prompts unless already approved by existing governance.

---

# API Contract

Prefer integrating the provider inside the existing authenticated Assistant endpoint.

Do not introduce a public endpoint that exports complete user context.

If the Assistant request schema changes to include recent-app context:

* validate every slug
* limit list length
* regenerate frontend OpenAPI types
* preserve backward compatibility where possible

---

# Initial Supported Questions

This task should prepare or enable context for questions such as:

* What are my favorite apps?
* Which apps did I open recently?
* What have I been doing recently?
* Do I have unread notifications?
* Which app should I continue using?
* What should I check first?

App-specific record questions remain for later Astra tools.

---

# Tests

Add focused tests covering:

## Authentication

* authenticated context
* anonymous minimal context
* caller cannot supply user ID
* another user’s data excluded

## Route Context

* valid app route
* valid platform route
* nested workflow route
* invalid route
* external route
* unknown app route

## Favorites

* owner-scoped favorites
* no favorites
* bounded results
* unknown catalog app excluded
* validated canonical routes

## Recent Apps

* valid bounded input
* duplicate slugs removed
* unknown slugs removed
* excessive list trimmed
* order preserved
* frontend input does not become authoritative ownership data

## Activity

* owner-scoped summary
* bounded lookback
* no raw private metadata
* unavailable service degradation

## Notifications

* unread summary
* zero unread
* type summary
* no full message leakage
* unavailable service degradation

## Context Profiles

* minimal profile avoids unnecessary queries
* personalization profile loads approved sources
* attention profile includes notification summary
* tool profile carries server-owned user reference
* identity intent bypasses unnecessary personal context
* safety intent bypasses unnecessary personal context

## OpenAI Sanitization

* only approved fields included
* user ID removed
* tokens removed
* internal IDs removed
* provider cannot infer unsupported facts from context

---

# Performance Targets

Measure:

* minimal-context build latency
* personalization-context build latency
* attention-context build latency
* number of database calls
* payload size
* cache behavior if introduced

Requirements:

* no queries to all 100 app databases
* no N+1 app lookup
* no unbounded timeline query
* no unbounded notification query
* no unnecessary personal-context loading for identity/public questions

---

# Documentation

Update:

* backend `AGENTS.md`
* Assistant story
* Activity story if its summary contract changes
* Notifications story if its summary contract changes
* backend contracts
* shared resources documentation
* Astra Tool Framework architecture document
* iteration backlog
* dependencies
* risk register
* validation plan

Create architecture documentation such as:

```text
docs/architecture/astra-user-context-provider.md
```

---

# Acceptance Criteria

The task is complete when:

* one authoritative Platform User Context Provider exists
* authenticated identity is backend-owned
* current route and app are validated canonically
* favorites are owner-scoped
* recent apps are validated and bounded
* activity is summarized safely
* notifications are summarized safely
* context profiles prevent unnecessary retrieval
* OpenAI receives only sanitized approved context
* identity and safety paths remain deterministic
* partial context failures degrade safely
* no public user-context export endpoint exists
* tests prove cross-user isolation
* performance remains bounded
* documentation is complete

---

# Success Criteria

After this task, Astra can safely answer platform-level personal-context questions without app-specific database access.

The provider becomes the shared foundation for later:

* Quiz Astra tools
* Course Tracker Astra tools
* personalized recommendations
* cross-app intelligence
* attention summaries
* dashboard intelligence

---

# Risks Addressed

This task mitigates:

* duplicated user-context logic
* cross-user data exposure
* unnecessary OpenAI context
* excessive database access
* inconsistent favorites/recent/activity state
* leaking private activity or notification content
* slow context construction
* central Assistant complexity

---

# Delivery

After implementation, report:

* commit hashes
* context contract
* supported profiles
* sources used
* authentication behavior
* owner-scoping behavior
* route validation behavior
* recent-app validation
* OpenAI sanitization
* failure degradation
* performance measurements
* API contract changes
* tests
* documentation
* known limitations
* repository status

Confirm explicitly:

* The frontend cannot choose or override the authenticated user.
* OpenAI does not receive backend user IDs or authentication data.
* Context loading is intent-driven and bounded.
* Identity and safety questions do not unnecessarily load personal data.
* No app database is queried directly by the central context provider.
* No private activity or notification content is exposed.
* No public context-export endpoint was added.
* Existing Assistant behavior remains backward compatible.
* Exactly 100 apps remain.
* No App #101 was introduced.
* All changed repositories are clean and aligned with `origin/main`.
