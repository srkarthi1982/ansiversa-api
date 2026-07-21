# I1-002 — Astra AI Tool Framework

**Iteration:** 2026-07-next  
**Priority:** Critical  
**Status:** Discussing  
**Depends On:** I1-001 — Astra AI User Data Awareness  
**Primary Repository:** `ansiversa-api`

---

# Objective

Create a governed backend tool framework that allows Astra AI to retrieve approved, authenticated, owner-scoped information from Ansiversa application services.

The framework will become the standard integration layer between Astra AI and the fixed ecosystem of 100 solution apps.

This task establishes the shared architecture only.

It does not integrate all 100 apps and does not introduce write actions.

---

# Problem Statement

Astra currently understands:

- platform identity
- public knowledge
- app capabilities
- navigation
- recommendations
- bounded session context

Astra does not yet have a governed mechanism for retrieving authenticated user data from application databases.

Without a shared tool framework, user-data support could gradually produce:

- one large Assistant service
- duplicated query logic
- direct database access
- inconsistent permission checks
- app-specific conditions inside central Assistant code
- difficult auditing
- unsafe model-generated SQL
- poor maintainability

The Tool Framework must prevent that architecture.

---

# Architecture Principle

```text
User Question
        ↓
Assistant Intent Resolution
        ↓
Approved Tool Selection
        ↓
Authenticated Tool Context
        ↓
App-Owned Business Service
        ↓
Owner-Scoped Database Query
        ↓
Structured Tool Result
        ↓
Deterministic or Grounded Explanation
        ↓
Validated Response and Actions
```

The Assistant orchestrates tools.

Each application owns its own business logic and data access.

---

# Core Governance Rule

> Every app owns its Astra capabilities.

The central Assistant must not contain application-specific database queries.

An app may register approved Astra tools that call its existing service layer.

---

# Phase 1 Scope

This task includes:

- shared tool definitions
- tool registry
- tool execution context
- tool executor
- tool-result contract
- authentication enforcement
- owner-scope enforcement
- read-only enforcement
- tool allowlisting
- argument validation
- output validation
- bounded execution
- safe audit metadata
- deterministic tool-selection support
- optional OpenAI function/tool-selection support
- framework tests
- framework documentation
- one non-sensitive demonstration tool

This task does not include broad user-data integration across solution apps.

---

# Non-Goals

Do not add:

- raw SQL generation
- model-generated SQL execution
- arbitrary table access
- direct database connections from the Assistant
- write tools
- inserts
- updates
- deletes
- autonomous workflows
- background agents
- unrestricted multi-step planning
- external SaaS tools
- permanent Assistant memory
- all 100 app integrations
- App #101

---

# Tool Framework Components

Introduce repository-appropriate equivalents of the following concepts.

## Assistant Tool Definition

Describes an approved tool.

Suggested fields:

```python
class AssistantToolDefinition:
    name: str
    description: str
    source_app: str
    input_schema: dict
    output_schema: dict
    requires_authentication: bool
    read_only: bool
    timeout_seconds: float
    visibility: str
```

The exact implementation should follow current backend conventions.

---

## Assistant Tool Context

Carries server-controlled execution context.

Suggested fields:

```python
class AssistantToolContext:
    user_id: str
    request_id: str
    current_route: str | None
    current_app_slug: str | None
```

Rules:

- `user_id` must come from authenticated backend context.
- Tool callers cannot provide or override `user_id`.
- No tool receives another user's identity.
- Sensitive authentication claims must not be forwarded unnecessarily.

---

## Assistant Tool Result

All tools return a stable structured result.

Suggested fields:

```python
class AssistantToolResult:
    tool_name: str
    source_app: str
    status: str
    data: dict
    summary_facts: list[str]
    actions: list[dict]
    metadata: dict
```

Rules:

- `data` must contain bounded, approved fields only.
- `summary_facts` must be factual and derived from the tool result.
- `actions` must use validated internal routes.
- `metadata` must not expose private values, SQL, source paths, tokens, or infrastructure details.

---

## Assistant Tool Registry

The registry must:

- register approved tools explicitly
- reject duplicate tool names
- expose tool metadata for selection
- filter tools by authentication requirement
- filter tools by visibility
- support lookup by exact tool name
- support deterministic intent-to-tool mapping
- provide model-compatible schemas where needed
- remain independent from app implementation imports where possible
- avoid loading every app's heavy runtime code unnecessarily

No arbitrary runtime registration from untrusted input is permitted.

---

## Assistant Tool Executor

The executor must:

- receive a registered tool name
- validate arguments
- inject authenticated context
- enforce read-only policy
- enforce timeout
- execute the approved handler
- validate the structured result
- sanitize actions
- handle failures safely
- record bounded audit metadata
- never return stack traces or raw SQL to the user

---

# Tool Ownership

Every future app tool should live with, or be clearly owned by, its backend module.

Preferred model:

```text
app/modules/quiz/
├── service.py
├── router.py
├── schemas.py
├── astra_tools.py
└── astra-ai.md
```

Exact naming may follow repository standards.

The app tool should call the existing service layer rather than reimplementing business logic.

---

# Demonstration Tool

Add one safe, low-risk demonstration tool to prove the framework.

Preferred candidate:

```text
get_user_favorites_summary
```

Possible result:

```json
{
  "favoriteCount": 3,
  "favorites": [
    {
      "slug": "quiz",
      "name": "Quiz",
      "route": "/quiz/play"
    }
  ]
}
```

Requirements:

- authenticated
- owner-scoped
- read-only
- bounded result count
- validated routes
- no private app-record content
- no model-generated query
- no database schema exposure

An equally safe existing platform source may be selected if Favorites is not the best implementation fit.

---

# Tool Selection

Support two controlled selection paths.

## Deterministic Selection

Known intents should map directly to approved tools.

Example:

```text
Question:
"What are my favorite apps?"

Intent:
user_favorites_summary

Tool:
get_user_favorites_summary
```

Deterministic selection should be preferred when the intent is known.

---

## Optional OpenAI Tool Selection

OpenAI may select from a small allowlisted set of eligible tools only when deterministic routing is insufficient.

Rules:

- OpenAI receives tool names, descriptions, and input schemas only.
- OpenAI must not receive database schemas.
- OpenAI must not receive `user_id`.
- OpenAI must not construct SQL.
- Backend validates every selected tool and argument.
- Tool execution remains server-controlled.
- Unsupported or invalid tool requests are rejected safely.
- Limit tool-call depth and total tool calls per Assistant request.
- Phase 1 should permit at most one read tool execution per request unless explicitly approved otherwise.

---

# Authentication and Ownership

Every authenticated tool must enforce:

```text
HTTP authentication
        ↓
current authenticated user
        ↓
server-owned Tool Context
        ↓
owner-scoped service method
        ↓
database
```

The following are forbidden:

- model-supplied user IDs
- request-body user IDs
- query-parameter user IDs for tool ownership
- caller-selected ownership scopes
- cross-user aggregation
- administrator escalation through Astra
- anonymous access to personal tools

---

# Read-Only Enforcement

Phase 1 tools are strictly read-only.

Forbidden operations include:

- create
- update
- delete
- archive
- send
- publish
- approve
- promote
- mark complete
- reset
- trigger workflow
- modify preferences

A tool definition must explicitly declare:

```text
read_only = true
```

The executor must reject tools that do not satisfy the Phase 1 policy.

---

# Privacy Rules

Tool results must follow data minimization.

Only return information necessary to answer the user's question.

Do not expose:

- passwords
- password hashes
- authentication tokens
- API keys
- database URLs
- raw metadata blobs
- internal IDs unless required and approved
- unrestricted free-text records
- another user's data
- deleted data
- internal audit details
- hidden source references
- SQL statements
- database schemas
- infrastructure topology

---

# Audit Logging

Record safe operational metadata such as:

- request ID
- authenticated user ID or governed internal reference
- tool name
- source app
- execution status
- duration
- response mode
- result count
- fallback reason

Do not log:

- full user prompt unless existing governance explicitly permits it
- private tool-result values
- tokens
- secrets
- SQL
- full personal records
- OpenAI credentials

Use the existing platform audit/activity boundary where appropriate.

Do not publish tool execution as user Activity unless that behavior is separately approved.

---

# Error Handling

Tool failures must not expose implementation details.

Possible safe outcomes:

- tool unavailable
- unsupported question
- insufficient data
- authentication required
- result temporarily unavailable
- request too broad
- execution timeout

A tool failure must not cause:

- unrestricted legacy retrieval
- arbitrary database fallback
- repeated OpenAI calls
- another tool to run without approval
- stack trace disclosure

---

# Performance Boundaries

Establish initial limits:

- bounded tool arguments
- bounded result rows
- bounded response size
- bounded execution timeout
- maximum tool calls per request
- no N+1 query patterns
- no full-table scans where indexes should exist
- no loading all 100 app databases for one question

Record execution duration for verification.

---

# Framework API Boundary

Do not create a public endpoint that lets users execute arbitrary tools by name.

Tool execution should occur through the authenticated Assistant service.

If an internal diagnostic endpoint is necessary for tests, it must be unavailable in production or restricted according to existing governance.

---

# Assistant Response Modes

The existing response modes remain authoritative:

```text
deterministic
openai_grounded
fallback
```

Tool-backed responses should preserve this model.

Suggested behavior:

- deterministic tool selection + deterministic formatter → `deterministic`
- deterministic or model-selected tool + OpenAI explanation → `openai_grounded`
- unsupported, failed, or blocked request → `fallback`

Do not introduce ambiguous or duplicate response modes without approval.

---

# Actions

Tools may return relevant internal actions.

Examples:

- Open Favorites
- Open Quiz
- Open Course Tracker
- Open a validated summary page

Rules:

- canonical routes only
- safe internal navigation only
- maximum 2–3 actions
- no invented routes
- no direct record mutation
- no external URL unless separately approved
- no route created from arbitrary tool data

---

# App Integration Contract

Every future Astra-enabled app should document:

- supported questions
- registered tool names
- authentication requirements
- approved input arguments
- approved output fields
- owner-scoping rule
- business service used
- action routes
- privacy exclusions
- performance bounds
- test coverage
- unsupported questions

This contract will later be stored in an app-level `astra-ai.md` document.

---

# Tests

Add focused tests covering:

## Registry

- successful registration
- duplicate-name rejection
- unknown-tool rejection
- visibility filtering
- authentication filtering
- read-only policy
- deterministic lookup

## Context

- authenticated user injected by backend
- caller cannot override user ID
- anonymous personal-tool request rejected
- current route/app context preserved safely

## Executor

- valid execution
- invalid arguments rejected
- output validation
- timeout handling
- handler exception sanitization
- action validation
- result-size bounds
- read-only enforcement

## Demonstration Tool

- owner-scoped favorites only
- zero favorites
- bounded favorites
- route validity
- no other user's favorites
- no private record leakage

## Assistant Integration

- deterministic tool intent
- tool-backed deterministic response
- mocked OpenAI grounded explanation
- provider cannot change tool facts
- invalid model-selected tool rejected
- invalid arguments rejected
- maximum tool-call count enforced
- existing identity intent still bypasses tools
- existing safety intent still bypasses tools
- existing app discovery remains unchanged

---

# Security Tests

Explicitly test:

- prompt injection requesting arbitrary tool execution
- request for another user's data
- model-supplied `user_id`
- unknown tool name
- write-like tool name
- SQL-like argument payload
- path traversal strings
- oversized arguments
- malformed JSON
- repeated tool calls
- restricted/internal tool request
- hidden schema request
- raw-result disclosure request

Any ownership or restricted-data failure is release-blocking.

---

# Validation

Run at minimum:

```bash
pytest tests/test_assistant_service.py
pytest tests/test_assistant_tools.py
pytest tests/test_assistant_knowledge_audit.py
pytest tests/test_assistant_identity.py
python -m compileall app tests
python -m app.modules.knowledge.check_registry
python -m app.modules.knowledge.check_public
git diff --check
```

If the Assistant API contract changes:

- regenerate frontend OpenAPI types
- run frontend typecheck
- run frontend lint
- run frontend production build
- run relevant Assistant Playwright suites

---

# Documentation

Update:

- backend `AGENTS.md`
- Assistant story
- Knowledge module story if applicable
- backend contracts
- shared resources documentation
- coding standards if the tool contract becomes mandatory
- iteration dependency document
- iteration risk register
- iteration validation plan
- iteration backlog status

Create architecture documentation for the tool framework.

Suggested path:

```text
docs/architecture/astra-tool-framework.md
```

---

# Acceptance Criteria

The task is complete when:

- a governed tool definition contract exists
- a central allowlisted registry exists
- a secure executor exists
- authenticated context is backend-owned
- user ID cannot be model-controlled
- Phase 1 tools are read-only
- arguments and results are validated
- tool calls are bounded
- actions are route-validated
- a safe demonstration tool works end to end
- deterministic and optional grounded response paths work
- existing Assistant identity, safety, and discovery behavior is unchanged
- security tests pass
- documentation is complete
- production behavior remains backward compatible

---

# Success Criteria

After this task, future app integrations should require only:

1. an app-owned service method
2. an app-owned Astra tool definition
3. registry registration
4. tests
5. an `astra-ai.md` contract

The central Assistant should not require large app-specific conditional blocks.

---

# Risks Addressed

This task mitigates:

- unauthorized SQL execution
- cross-user data access
- central Assistant complexity
- duplicated business logic
- uncontrolled model tool use
- database schema exposure
- unrestricted app access
- tool-result privacy leakage
- difficult certification
- future 100-app integration drift

---

# Delivery

After implementation, report:

- commit hashes
- architecture introduced
- framework components
- demonstration tool
- tool registry contents
- authentication and owner-scoping behavior
- read-only enforcement
- tool-call limits
- response modes
- API contract impact
- security test results
- performance measurements
- regression results
- documentation updates
- known limitations
- repository status

Confirm explicitly:

- OpenAI cannot generate or execute SQL.
- OpenAI cannot provide or override user identity.
- Astra can execute only registered allowlisted tools.
- Phase 1 tools are read-only.
- App services remain the source of business truth.
- No private or cross-user data is exposed.
- Existing deterministic identity and safety behavior remains unchanged.
- No external agent framework was added without approval.
- Exactly 100 apps remain.
- No App #101 was introduced.
- All changed repositories are clean and aligned with `origin/main`.