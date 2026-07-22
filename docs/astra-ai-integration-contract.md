# Astra AI Integration Contract

**Status:** Frozen v1.0
**Created:** 2026-07-22
**Owner:** Karthikeyan Ramalingam
**Architecture Review:** Astra
**Implementation Agent:** Codex

This document is the permanent integration standard for adding Astra AI
capabilities to Ansiversa applications.

It implements Iteration 1 task `I1-009 — Astra AI Integration Contract`.

The personal-data awareness governance established by I1-001 lives at:

```text
docs/astra-user-data-awareness-contract.md
```

---

# Purpose

Astra is the governed intelligence layer for the fixed Ansiversa ecosystem of
100 solution applications.

This contract defines how every application describes, registers, validates,
and maintains its Astra capabilities without weakening the platform
architecture.

The contract exists so Astra integration is not reinvented inside each app.

---

# Operating Principle

```text
Implementation remains within approved architecture.
```

Architecture changes require Product Owner approval from Karthikeyan and
architecture review by Astra.

Codex may make implementation decisions only inside the assigned frozen task and
approved architecture.

---

# Ownership Model

## Product Vision

Owner: Karthikeyan Ramalingam

Responsibilities:

- Product vision
- Platform direction
- Scope approval
- Final architecture approval
- Production approval

## Architecture

Reviewer: Astra

Responsibilities:

- Architecture review
- Governance compliance
- Long-term maintainability
- Platform consistency
- Security and privacy boundaries
- Documentation quality
- Design challenge

## Implementation

Engineer: Codex

Responsibilities:

- Implementation within approved scope
- Refactoring within approved architecture
- Tests
- Documentation updates
- Validation
- Repository integrity

---

# Core Architecture Rule

```text
Applications own capabilities.
Astra owns orchestration.
```

Applications own:

- Business rules
- Services
- Database access
- Validation rules
- Calculation rules
- App-specific Astra tools
- App-specific Astra documentation
- Supported questions

Astra owns:

- Assistant entry point
- Intent routing
- Tool orchestration
- Tool execution lifecycle
- Response assembly
- Action validation
- Safety and identity priority
- OpenAI boundary enforcement

Astra must not duplicate application business logic.

Applications must not create separate Assistant UIs.

The platform Assistant remains the single Astra user experience.

---

# Required Astra App Document

Every Astra-enabled application must include an `astra-ai.md` file before its
Astra capabilities are approved.

Required backend location:

```text
ansiversa-api/app/modules/<app_module>/astra-ai.md
```

Required frontend location only when frontend-specific Astra behavior exists:

```text
ansiversa/src/modules/<app-slug>/astra-ai.md
```

Do not create empty frontend `astra-ai.md` files. If the frontend only exposes
canonical routes and uses the shared Assistant UI, the backend contract is
sufficient.

---

# astra-ai.md Required Sections

Every backend `astra-ai.md` must include these sections:

- App Identity
- Ownership Boundary
- Supported User Questions
- Unsupported User Questions
- Registered Tools
- Tool Result Contracts
- Business Rules
- Privacy Rules
- OpenAI Boundary
- Supported Actions
- Performance Boundaries
- Validation Requirements
- Current Limitations
- Future Enhancements

---

# astra-ai.md Template

```markdown
# [App Name] Astra AI Contract

**Status:** Draft
**App:** [Catalog app name]
**Module:** `app/modules/<app_module>`
**Created:** YYYY-MM-DD
**Last Reviewed:** YYYY-MM-DD

---

# App Identity

Describe the app's approved catalog identity, purpose, workflow, and canonical
routes.

---

# Ownership Boundary

The app owns its business logic, data access, validation, calculations, and
app-specific Astra tools.

Astra owns orchestration, routing, response assembly, action validation, and
safety boundaries.

---

# Supported User Questions

List the questions Astra may answer using this app's approved tools.

---

# Unsupported User Questions

List questions Astra must reject, redirect, or answer without this app's private
data.

---

# Registered Tools

For each tool:

- Tool name
- Purpose
- Authentication requirement
- Owner-scoping rule
- Read-only/write status
- Input arguments
- Output schema
- Timeout
- Result limit
- Owning service method

---

# Tool Result Contracts

Define exactly which fields may leave the app service layer.

List endpoints must stay lightweight.
Detail-style tool results must be bounded to the fields Astra needs.

---

# Business Rules

Document the app-owned rules Astra must consume rather than duplicate.

Examples:

- Completion rules
- Recommendation rules
- Ranking rules
- Calculation rules
- Validation rules
- Archived/deleted record behavior

---

# Privacy Rules

Document fields and records that tools must not expose.

Include:

- Sensitive fields
- Internal identifiers
- Admin-only data
- Deleted records
- Raw payloads
- Notes or long text that should only appear as bounded previews

---

# OpenAI Boundary

Document what may be sent to OpenAI, if anything.

OpenAI must not receive:

- User IDs
- Authentication claims
- Database schemas
- SQL
- Raw records
- Internal IDs
- Secrets
- Full personal context payloads

---

# Supported Actions

List canonical navigation actions Astra may return.

Every route must be an approved internal Ansiversa route.

---

# Performance Boundaries

Document query limits, result limits, timeout expectations, and indexes relied
on by the tools.

---

# Validation Requirements

List unit tests, service tests, Assistant regression prompts, ownership tests,
privacy tests, and browser checks.

Platform-wide browser matrices live in
`docs/iterations/2026-07-next/04-validation-plan.md` during Iteration 1.

---

# Current Limitations

Document known limitations of the current Astra integration.

---

# Future Enhancements

Document future ideas without authorizing implementation.
```

---

# Backend Contract

Astra-enabled backend modules may add:

```text
astra_tools.py
astra-ai.md
```

`astra_tools.py` is allowed only when a frozen task explicitly implements
app-owned Astra tools.

The app service layer remains the authority for business logic. Tool handlers
must call app-owned services instead of querying databases directly from the
central Assistant.

Tool handlers must:

- Receive authenticated user context from the backend
- Enforce owner scoping
- Return bounded structured results
- Stay read-only in Phase 1
- Avoid raw SQL exposure
- Avoid stack traces in user-facing output
- Avoid logging raw personal payloads

---

# Frontend Contract

Frontend modules must:

- Expose canonical routes through existing route metadata
- Use the shared platform Assistant UI
- Preserve contextual navigation
- Preserve action route validation
- Avoid app-specific Assistant panels
- Avoid app-specific Assistant state outside approved shared contracts

Frontend modules may add frontend `astra-ai.md` only when they introduce
frontend-specific Astra behavior beyond shared route/action support.

---

# Tool Registration Contract

Tool registration is governed separately by I1-012, but every app-level tool
must be documented here before it is registered.

Each registered tool must declare:

- Name
- Owning app
- Version
- Description
- Supported intents
- Authentication requirement
- Owner-scoped status
- Read-only/write capability
- Input schema
- Output schema
- Timeout
- Result limit
- Enabled/disabled state

Tool registration metadata must not replace app-owned business logic.

---

# OpenAI Boundary

OpenAI is optional and explanation-only.

OpenAI must not:

- Choose or override user identity
- Generate SQL
- Receive database schemas
- Receive raw personal records
- Receive authentication tokens or claims
- Change deterministic facts
- Change app-owned recommendation order
- Produce navigation actions

Deterministic safety, identity, and permission routing outrank tool routing and
model routing.

---

# Privacy And Security Rules

Phase 1 personal-data tools must be:

- Authenticated
- Owner-scoped
- Bounded
- Read-only
- Auditable
- Minimal in output shape

Before personal-data tools go live, the platform must resolve:

- Audit sink for Astra personal-data tool execution
- Consent, retention, deletion, and OpenAI personal-context allowlist
- Seeded authenticated test-data ownership and environment

I1-001 resolves those decisions as governance policy in
`docs/astra-user-data-awareness-contract.md`. Runtime implementation remains
blocked until a later approved task implements the required audit sink,
consent/user-control behavior, deletion/export behavior, and seeded
verification setup.

---

# Documentation Lifecycle

When an app gains an Astra capability:

1. App business feature exists or is approved.
2. App service/API contract exists.
3. `astra-ai.md` documents supported questions and tool boundaries.
4. Tool implementation stays inside the app module.
5. Tool registration metadata is added through the Tool Registry.
6. Assistant regression prompts are documented.
7. Ownership, privacy, and route-safety tests pass.
8. Browser verification uses the shared platform matrix plus app-specific
   prompts.
9. Astra review confirms architecture compliance.
10. Karthikeyan approves any architecture-affecting change.

---

# Backward Compatibility

This contract does not require existing applications to implement Astra tools
immediately.

Existing apps remain backward compatible.

The contract applies when:

- A frozen task adds Astra behavior to an app
- A future enhancement touches app intelligence
- A new app-level tool is proposed
- An existing app changes behavior that affects Astra support

---

# Explicit Non-Goals

This contract does not:

- Implement I1-001 user-data awareness
- Implement I1-002 tool execution
- Implement I1-003 context provider
- Implement Quiz Astra tools
- Implement Course Tracker Astra tools
- Add runtime Astra orchestration
- Add personal-data tools
- Add migrations
- Add OpenAI calls
- Add App #101

---

# Validation

For I1-009, validation is documentation-only:

- Markdown files must remain readable.
- Task IDs must remain sequential and unique.
- Cross references must resolve where they point to iteration package files.
- `git diff --check` must pass.
- Repositories must remain clean after commit and push.

Runtime, browser, backend, and frontend build validation begin when a frozen
task changes runtime code.
