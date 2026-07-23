# AGENTS.md — Ansiversa API

2026-07-23 - Received Architecture Reviewer and Product Owner approval for Iteration 2 AI SEO Architecture, adopted AI SEO Engineering Law #1 ("Every public claim must have exactly one approved source of truth"), and froze SEO-001 for completion of its documentation/architecture artifact only. SEO-002 through SEO-008 remain Proposed, SEO-003 Canonical Public Rendering remains unresolved, and no runtime, registry, schema, metadata, route, sitemap, robots, frontend, backend, migration, configuration, crawler-submission, production, I1-024, or feature-flag implementation is authorized.

2026-07-23 - Began Iteration 2 AI SEO Architecture as discovery and specification only, with `docs/ai-seo-architecture.md` and `docs/iterations/2026-08-ai-seo/`. Repository evidence confirms the existing Canonical AI Knowledge Registry, public JSON/JSON-LD, `llms.txt`, AI sitemap, robots hints, deployment rewrites, and public smoke verification are the foundation rather than greenfield work. The architecture prioritizes canonical crawlable human-visible pages, one knowledge compiler, human/machine claim parity, explicit roles for `market-study.md`, `destination.md`, `story.md`, and `marketing.md`, platform/app ownership, crawler-purpose separation, and evidence-tiered validation.

2026-07-23 - Completed I1-023 Astra Operational Readiness Specification as documentation-only governance with `docs/astra-operational-readiness-specification.md`, defining mandatory readiness gates, named control-owner roles, evidence provenance, pass/fail criteria, persistent audit, consent, retention, deletion, export, classification, governed environments/accounts, dependency and deployment compatibility, owner isolation, privacy, controlled enablement, rollback, flag restoration, Production Readiness Review, Product Owner launch authority, failure handling, risk acceptance, and deferred scope. Production personal-data execution remains disabled with `ASTRA_PERSONAL_DATA_TOOLS_ENABLED=false`; no runtime, configuration, framework, registry, context-provider, app, database, migration, deployment, test-account, architecture, or production authorization change was introduced.

2026-07-22 - Implemented I1-006 Astra Learning Intelligence as deterministic cross-app orchestration over approved Quiz and Course Tracker registry capabilities, with `app/modules/assistant/learning_intelligence.py`, maximum two tools per request, maximum one tool per source app, safe partial/no-data behavior, explainable recommendation priorities, time-budget guidance, Assistant routing, focused tests, and `docs/architecture/astra-learning-intelligence.md`. Learning Intelligence imports no Quiz or Course Tracker models, services, database sessions, or SQLAlchemy queries; Quiz and Course Tracker remain authoritative for app facts, production execution remains gated by `ASTRA_PERSONAL_DATA_TOOLS_ENABLED=false`, and no Tool Framework, Tool Registry, Context Provider, Integration Contract, OpenAI tool orchestration, frontend contract, migration, write action, memory, all-app intelligence, or App #101 changes were introduced.

2026-07-22 - Implemented I1-005 Course Tracker Astra AI Integration as the second solution-app pilot with Course Tracker-owned `app/modules/course_tracker/astra_tools.py`, `app/modules/course_tracker/astra-ai.md`, seven authenticated owner-scoped read-only registry tools for course progress, active courses, completed courses, nearest completion, stalled courses, deadline summaries, and deterministic next-course action, plus Assistant registry-intent routing and focused tests. Course Tracker data stays inside the Course Tracker module and isolated Course Tracker database boundary; outputs exclude goals, notes, progress-log summaries/reflections, internal IDs, owner IDs, and cross-user records, production execution remains gated by `ASTRA_PERSONAL_DATA_TOOLS_ENABLED=false`, and no framework redesign, write tools, OpenAI tool orchestration, frontend contract changes, migrations, cross-app Quiz/Course reasoning, recommendation engine, persistent memory, or App #101 changes were introduced.

2026-07-22 - Implemented I1-004 Quiz Astra AI Integration as the first solution-app pilot with Quiz-owned `app/modules/quiz/astra_tools.py`, `app/modules/quiz/astra-ai.md`, five authenticated owner-scoped read-only registry tools for progress, submitted-result platforms, recent submitted attempts, repeated-evidence topic performance, and deterministic next-platform guidance, plus Assistant registry-intent routing and focused tests. Quiz data stays inside the Quiz module and isolated Quiz database boundary; outputs exclude question text/options/answer keys/explanations/raw responses/internal IDs/cross-user records, production execution remains gated by `ASTRA_PERSONAL_DATA_TOOLS_ENABLED=false`, and no write tools, OpenAI tool orchestration, frontend contract changes, migrations, Course Tracker integration, recommendation engine, persistent memory, or App #101 changes were introduced.

2026-07-22 - Implemented I1-003 Platform User Context Provider with bounded minimal/personalization/attention/tool-execution profiles, backend-owned identity, canonical route/current-app validation, owner-scoped Favorites via existing service, frontend-local recent-app validation, Activity and Notification summaries through existing owner-scoped services, safe read-only preference lookup, OpenAI-safe context serialization, deterministic platform-context answers, and lazy loading that bypasses personal context for identity/safety/public questions. No public context-export endpoint, frontend request contract change, app-specific database query, app tools, OpenAI tool orchestration, write operations, migrations, persistent memory, recommendation engine, or App #101 changes were introduced.

2026-07-22 - Implemented I1-012 Astra Tool Registry by extending the approved Assistant tool framework with permanent capability metadata, handler-free discovery entries, ownership/authentication/owner-scope/read-only/permission/version/enabled/deprecated documentation, optional registration-owner validation, registry-driven deterministic intent lookup, disabled/deprecated safe execution blocking, focused registry tests, and `docs/architecture/astra-tool-registry.md`. No app-specific tools, I1-003 User Context Provider, OpenAI tool orchestration, persistent registry database, admin UI, write operations, migrations, or App #101 changes were introduced.

2026-07-22 - Applied the I1-002 personal-data release-gate correction by keeping the Astra Tool Framework intact while disabling personal-data tool execution by default with server-owned `ASTRA_PERSONAL_DATA_TOOLS_ENABLED=false`, preserving test-only enabled coverage for the Favorites demonstration tool, documenting that production remains blocked until persistent audit logging, user controls, deletion/export handling, and seeded verification gates are approved and implemented, and introducing no I1-012 registry, I1-003 context provider, app tools, OpenAI tool orchestration, write operations, migrations, or App #101 changes.

2026-07-22 - Implemented I1-002 Astra AI Tool Framework as shared Assistant runtime infrastructure with explicit tool definitions, backend-owned execution context, allowlisted runtime registry, secure executor, argument/result validation, read-only Phase 1 enforcement, bounded route-safe actions, safe audit metadata logging, optional authenticated Assistant context, a platform Favorites summary demonstration tool, focused tests, and `docs/architecture/astra-tool-framework.md`. No solution-app tools, I1-012 registry metadata, I1-003 context provider, OpenAI tool orchestration, write operations, migrations, recommendations, AI memory, or App #101 changes were introduced.

2026-07-22 - Completed the Phase 2 Foundation Checkpoint verification for I1-009 and I1-001 with `docs/iterations/2026-07-next/phase-2-foundation-checkpoint.md`, confirming cross-reference integrity, planning synchronization, governance consistency, I1-002 readiness, documentation-only validation, and no runtime Astra implementation, tool execution, app integration, personal-data queries, migrations, OpenAI calls, or App #101 changes.

2026-07-22 - Implemented I1-001 Astra AI User Data Awareness Phase 1 as documentation-only governance with the canonical `docs/astra-user-data-awareness-contract.md`, covering authoritative backend identity, app-owned data boundaries, privacy policy, OpenAI personal-context allowlist, audit policy, retention/deletion governance, seeded verification environment rules, and explicit non-goals. No runtime Astra implementation, tool execution, application integration, personal-data queries, migrations, or App #101 changes were introduced.

2026-07-22 - Implemented I1-009 Astra AI Integration Contract as a documentation-only governance standard with the canonical `docs/astra-ai-integration-contract.md`, app-level `astra-ai.md` template, ownership boundaries, backend/frontend responsibilities, OpenAI/privacy/security limits, tool documentation lifecycle, and explicit non-goals. No runtime Astra orchestration, personal-data tooling, migrations, OpenAI calls, or App #101 changes were introduced.

2026-07-20 - Repaired the production Notifications schema mismatch by adding parent migration `20260720_0003` for missing `message`, `isRead`, and `metadataJson` columns, preserving legacy `body` data through backfill, restoring unread indexes, and keeping the Notifications drawer UI unchanged.

2026-07-20 - Implemented AI SEO Public Deployment and Crawl Readiness fixes by making backend public knowledge routes serve cached deterministic registry-derived responses independent of runtime filesystem artifact visibility, adding the read-only production smoke verifier, documenting canonical web/API topology, cache policy, robots/sitemap behavior, Search Console checklist, baseline evidence template, and monitoring cadence, with no Assistant behavior, embeddings, vector database, OpenAI calls, or App #101 changes.

2026-07-20 - Implemented Ansiversa AI SEO Public Knowledge Publishing Phase 1 with registry-derived public artifacts (`llms.txt`, `llms-full.txt`, AI sitemap, public AI JSON export, JSON-LD graph, reusable metadata, and robots hints), read-only public knowledge routes, deterministic publisher validation, visibility filtering, no Assistant behavior changes, no embeddings/vector/RAG, and no exposure of authenticated/internal/restricted/future/source-path documentation.

2026-07-20 - Implemented AI Knowledge Foundation Phase 2 Assistant Retrieval Parity by migrating `/api/v1/assistant/query` to load deterministic knowledge from the cached Canonical AI Knowledge Registry, preserving the Assistant API/UI/OpenAI boundary, route-safe actions, context behavior, fallback behavior, related-app and future/current separation, visibility filtering, and legacy DB/FAQ retrieval only as a logged registry-failure fallback.

2026-07-20 - Implemented AI Knowledge Foundation Phase 1 as a backend-owned deterministic canonical registry with 100 app records, 14 categories, public platform/page knowledge, explicit visibility, current/future separation, source traceability, allowlisted bounded Markdown/JSON parsing, secret scanning, related-app generation, build/check drift commands, an immutable test adapter, readiness/gap artifacts, focused tests, and no production Assistant switch, OpenAI calls, embeddings, public AI SEO output, database changes, or App #101.

2026-07-20 - Ran the parent production migration against `ansiversadb-ansiversa.aws-ap-south-1.turso.io`, advancing Alembic from `20260703_0001` through Notifications Center `20260720_0001` to Universal Activity Timeline `20260720_0002` head. Verified both parent tables and the Activity Timeline owner/time and owner/type/time indexes in production.

2026-07-20 - Added Universal Activity Timeline Phase 1 with the parent `ActivityTimeline` table, owner-scoped list/summary APIs, bounded safe publisher contract, canonical route validation, 30-minute navigation deduplication, latest-1,000 retention, failure-safe shared integrations, and three pilot apps. This is a private journey history—not `AuditLogs`, analytics, surveillance, or app-owned record history—and stores no prompts, raw payloads, or private record values.

2026-07-20 - Expanded the existing parent `Notifications` infrastructure into Notifications Center Phase 1 with owner-scoped pagination/filtering/counts, bounded types, sanitized source/action responses, canonical internal-route validation, idempotent read/read-all behavior, a governed shared publisher service, existing `UserPreferences` notification controls, focused tests, and no duplicate notification persistence. Push, email, SMS, scheduling, public publishing, and production seed data remain deferred.

* 2026-07-19: Implemented Ansiversa AI Assistant Phase 4 Context & Conversation Memory support with optional session context in `/assistant/query`, deterministic route/app/recent/favorite/history-aware retrieval, bounded OpenAI context forwarding, route-safe actions, focused service tests, and no migrations or permanent memory.

* 2026-07-19: Polished Ansiversa AI Assistant deterministic responses for financial-advice safety questions and explicit out-of-scope prompts so they no longer fall through to generic About matches, with focused tests for guidance, uncertainty, and validated actions.

* 2026-07-19: Added the Ansiversa AI Assistant environment contract with namespaced OpenAI provider settings, master gateway/debug switches, message/context limits, local `.env` placeholder values, `.env.example` documentation, and matching runtime configuration support.

* 2026-07-19: Implemented Ansiversa AI Assistant Phase 3 Grounded OpenAI Response Generation with server-side Responses API integration, deterministic retrieval/action authority, bounded public context, response mode metadata, provider failure fallback, focused mocked service tests, and no embeddings, vector database, tool calls, migrations, or frontend secrets.

* 2026-07-19: Implemented Ansiversa AI Assistant Phase 2 Backend Knowledge Retrieval Foundation with `POST /api/v1/assistant/query`, deterministic public catalog/page/FAQ retrieval, validated navigation actions, safe source metadata, focused service tests, and no OpenAI, external AI APIs, migrations, or user-data indexing.

* 2026-07-19: Aligned current user-facing platform copy with the permanent curated 100-app boundary: Ansiversa is permanently curated at exactly 100 solution apps, growth after 100 is horizontal, and apps may be replaced while the total catalog boundary remains 100.

* 2026-07-19: Promoted Salary Breakdown Calculator App #095 to approved live version `1.0.0` after Astra review, Partner manual verification, UI action polish, production Apps row promotion, destination metadata sync `20 / 100`, overview metadata sync, production-configured isolated migration verification, validation, and final catalog verification at 100 live / 0 comingSoon.

* 2026-07-19: Promoted Net Worth Tracker App #096 to approved live version `1.0.0` after Astra review, Partner manual verification, UI action polish, production Apps row promotion, destination metadata sync `0 / 100`, overview metadata sync, production-configured isolated migration verification, and validation.

* 2026-07-19: Promoted Meeting Scheduler App #089 to approved live version `1.0.0` after Astra review, Partner manual verification, UI action polish, production Apps row promotion, destination metadata sync `20 / 100`, overview metadata sync, production-configured isolated migration verification, and validation.

* 2026-07-19: Promoted Emergency Checklist App #100 to approved live version `1.0.0` after Astra review, Partner manual verification, UI action polish, production Apps row promotion, destination metadata sync `20 / 100`, overview metadata sync, production-configured isolated migration verification, and validation.

* 2026-07-19: Promoted Work Log Tracker App #092 to approved live version `1.0.0` after Astra review, Partner manual verification, UI action polish, production Apps row promotion, destination metadata sync `18 / 100`, overview metadata sync, production-configured isolated migration verification, and validation.

* 2026-07-19: Promoted Errand Planner App #098 to approved live version `1.0.0` after Astra review, Partner manual verification, production Apps row promotion, destination metadata sync `20 / 100`, overview metadata sync, production-configured isolated migration verification, and validation.

* 2026-07-19: Promoted Local Services Finder App #099 to approved live version `1.0.0` after Astra review, Partner manual verification, production Apps row promotion, destination metadata sync `20 / 100`, overview metadata sync, production-configured isolated migration verification, and validation.

* 2026-07-19: Promoted Savings Goal Planner App #094 to approved live version `1.0.0` after Astra review, Partner manual verification, production Apps row promotion, destination metadata sync `20 / 100`, overview metadata sync, production-configured isolated migration verification, and validation.

2026-07-21 - Added governed Platform Identity Knowledge and reputation guardrails: safety boundaries remain first, public identity precedes context/app/fuzzy retrieval, founder/owner/architect roles remain distinct, Astra and the fixed 100-app model receive deterministic answers, and general Python/transport/weather/sports prompts return a zero-action scope response.

## Repository Purpose

`ansiversa-api` is the central API platform for the Ansiversa ecosystem.

Production domain:

```text
https://api.ansiversa.com
```

API docs:

```text
https://api.ansiversa.com/docs
```

This API is intended to become the single access layer for:

* Parent/global Ansiversa services
* Web mini-apps
* Future iOS app
* Future Android app
* AI services
* Cross-app dashboard and activity aggregation
* Future public/developer APIs

The existing Ansiversa web apps must remain stable. This API should evolve gradually and safely.

---

## Core Architecture Rule

Ansiversa API is a central access layer, not a single giant database.

Parent/global services and mini-apps may have separate database engines.

Golden rule:

```text
Scalability is not about powerful databases.
It is about refusing to store what you do not own.
```

The API may aggregate data across databases, but each domain must continue to own its own data.

---

## Technology Stack

Use:

* Python
* FastAPI
* SQLAlchemy
* Alembic
* Pydantic / pydantic-settings
* Turso/libSQL where suitable
* PostgreSQL-compatible architecture where future migration is possible
* Vercel deployment

Do not introduce unnecessary frameworks.

Keep the code simple, modular, typed, and readable.

---

## Folder Structure Standard

Current/future structure should follow this pattern:

```text
app/
  main.py
  core/
    config.py
    database.py
    security.py
  modules/
    health/
      routes.py
    auth/
      routes.py
      schemas.py
      service.py
    apps/
      routes.py
      schemas.py
      service.py
    quiz/
      routes.py
      schemas.py
      service.py
      db.py
      models.py
    resume_builder/
      routes.py
      schemas.py
      service.py
      db.py
      models.py
```

Parent/global configuration lives under:

```text
app/core/
```

Mini-app-specific DB/session/model configuration lives inside that mini-app module.

Do not create one unsafe giant model layer for all apps.

---

## API Route Standard

Use versioned routes:

```text
/api/v1/...
```

Examples:

```text
/api/v1/health/
/api/v1/auth/...
/api/v1/apps/...
/api/v1/quiz/...
/api/v1/resume-builder/...
```

Use clear OpenAPI tags.

Keep route files thin. Business logic should live in service files.

For App #041 onward, backend mini apps should use the current factory route
export convention:

```text
router.py
  Owns APIRouter definitions and endpoint functions.

routes.py
  Re-exports router from router.py for compatibility with app.main imports.
```

Do not mix business logic into `routes.py` or `router.py`. Business logic stays
in `service.py`, and database query helpers stay in `repository.py` only when
the module needs that split.

## OpenAPI Contract Standard

The full ecosystem OpenAPI schema is not always suitable for mini-app frontends.
Mini-apps should eventually generate SDKs from module-specific OpenAPI schemas.

Examples:

* Quiz frontend should generate from Quiz schema.
* Resume Builder frontend should generate from Resume Builder schema.
* Parent web can generate from Parent/global schema.

## Astra AI Integration Contract

The permanent Astra integration standard lives at:

```text
docs/astra-ai-integration-contract.md
```

Every Astra-enabled app must follow that contract.

Core rule:

```text
Applications own capabilities.
Astra owns orchestration.
```

Applications own business rules, services, database access, validation,
calculations, app-specific Astra tools, app-specific Astra documentation, and
supported questions.

Astra owns the shared Assistant entry point, intent routing, tool orchestration,
tool execution lifecycle, response assembly, action validation, safety and
identity priority, and OpenAI boundary enforcement.

Astra must not duplicate application business logic. Applications must not
create separate Assistant UIs.

Every Astra-enabled backend module must include:

```text
app/modules/<app_module>/astra-ai.md
```

Frontend modules create `src/modules/<app-slug>/astra-ai.md` only when
frontend-specific Astra behavior exists beyond shared routes/actions and the
shared Assistant UI.

I1-009 is contract-only. It does not authorize I1-001 user-data awareness,
I1-002 tool execution, I1-003 context provider, app pilots, personal-data
tooling, migrations, OpenAI calls, or runtime Astra orchestration.

Before personal-data tools go live, the platform must resolve:

* audit sink for Astra personal-data tool execution
* consent, retention, deletion, and OpenAI personal-context allowlist
* seeded authenticated test-data ownership and environment

## Astra User Data Awareness Contract

The Phase 1 personal-data awareness governance standard lives at:

```text
docs/astra-user-data-awareness-contract.md
```

Core rule:

```text
Backend identity is authoritative.
Applications own user data.
Astra receives only approved, minimized context.
OpenAI never determines identity, ownership, or permissions.
```

I1-001 defines what Astra is allowed to know about an authenticated user's own
Ansiversa data. It does not implement runtime data retrieval.

User-data awareness must follow these boundaries:

* authenticated backend user context is the only authoritative identity
* application services remain the only source of app-owned data
* personal context must be owner-scoped, purpose-bound, minimized, bounded, and
  read-only in Phase 1
* OpenAI receives only categories allowed by the governed personal-context
  allowlist
* future personal-data access must be auditable without logging raw personal
  payloads
* retention, deletion, export, consent, and seeded verification behavior must
  follow the governance contract before tools go live

I1-001 does not authorize I1-002 tool execution, I1-003 context provider, app
pilots, application queries, personal-data queries, runtime audit logging,
migrations, OpenAI orchestration, AI memory, recommendations, or App #101.

## Astra Tool Framework

The shared runtime tool framework lives in:

```text
app/modules/assistant/tools.py
app/modules/assistant/platform_tools.py
docs/architecture/astra-tool-framework.md
docs/architecture/astra-tool-registry.md
```

I1-002 authorizes shared Assistant tool infrastructure only.

Framework boundaries:

* tool definitions are explicit and allowlisted
* tool context is backend-owned and injects authenticated user context
* callers and models cannot provide owner IDs or user IDs
* Phase 1 tools must be read-only
* arguments and results are validated and bounded
* actions are filtered to approved internal routes
* failures return structured safe results without stack traces, SQL, secrets,
  tokens, or raw personal payloads
* personal-data tools are disabled by default with server-owned
  `ASTRA_PERSONAL_DATA_TOOLS_ENABLED=false`
* audit metadata is safe operational metadata only; persisted personal-data
  audit logging remains a release gate before personal-data tools go live

I1-012 extends the registry with permanent capability metadata and discovery:

* owning app
* supported intents
* authentication requirement
* owner-scoped status
* read-only/write mode
* permission scope
* input/output schemas
* timeout
* version
* enabled/disabled state
* deprecated state
* visibility
* result limit
* documentation path

Normal discovery omits disabled and deprecated tools. Disabled and deprecated
tools fail safely before handler execution if direct execution is attempted.
The Assistant resolves deterministic tool intents through registry lookup.

The I1-002 demonstration tool is `get_user_favorites_summary`, a platform
Favorites summary tool. It does not create solution-app integrations. Because
Favorites are authenticated personal data, production execution remains disabled
until persistent audit logging, user controls, deletion/export handling, and
seeded verification gates are approved and implemented.

I1-002 and I1-012 do not authorize Quiz tools, Course Tracker tools, OpenAI
tool selection, OpenAI rewriting of tool facts, write operations, AI memory,
recommendations, autonomous workflows, migrations, or App #101.

## Astra Operational Readiness

The permanent operational-readiness evidence standard lives at:

```text
docs/astra-operational-readiness-specification.md
```

I1-023 is specification-only. It establishes the evidence required before
production authorization may be considered; it does not implement controls or
authorize production.

Permanent rule:

```text
Verification does not imply release.
```

Operational-readiness gates cover:

* governance and personal-data classification
* persistent audit
* consent and user controls
* retention, deletion, and export
* governed environments and synthetic accounts
* dependency and deployment compatibility
* owner isolation and privacy
* safe failure behavior
* controlled enablement, rollback, and flag restoration
* evidence review, launch authority, and risk acceptance

Missing, stale, contradictory, or unowned mandatory evidence is a failed gate.
Controlled verification must restore
`ASTRA_PERSONAL_DATA_TOOLS_ENABLED=false` unless a separate Product Owner launch
decision explicitly authorizes continued production operation.

Only Karthikeyan Ramalingam, as Product Owner, may authorize production launch.
Codex produces implementation and evidence within separately approved tasks.
Astra reviews architecture and governance. Passing tests, completed
implementation, or approved runtime verification do not authorize release.

I1-023 does not authorize an audit sink, consent UI, deletion/export runtime,
test accounts, migrations, dependency changes, deployment changes, personal-data
enablement, additional app onboarding, or App #101.

## Astra User Context Provider

The governed user context provider lives in:

```text
app/modules/assistant/user_context.py
docs/architecture/astra-user-context-provider.md
```

I1-003 authorizes bounded platform-level user context only.

Context profiles:

* `minimal`
* `personalization`
* `attention`
* `tool_execution`

Provider boundaries:

* backend authentication remains the only authoritative identity
* the frontend cannot provide or override the authenticated user
* current routes are validated before use
* current app is resolved through the canonical app catalog
* Favorites use the existing owner-scoped Favorites service
* recent apps are frontend-local hints validated against the catalog
* Activity uses the existing owner-scoped Activity Timeline service and returns
  summaries only
* Notifications use the existing owner-scoped Notifications service and return
  unread summaries only
* preference lookup is read-only and must not create or update rows
* model-facing context must omit backend user IDs, emails, tokens, raw activity
  metadata, full notification bodies, private app records, SQL, source paths,
  and infrastructure details
* identity, safety, and public-knowledge answers must not load unnecessary
  personal context

I1-003 does not authorize app-specific record queries, Quiz tools, Course
Tracker tools, OpenAI tool orchestration, public context export endpoints,
frontend request contract changes, write operations, migrations, persistent
memory, recommendation engine, or App #101.

## Public API Data Discipline

Principle:

User-facing APIs must only fetch and return the fields required by the UI.

Never expose complete database records to public clients when the UI only
consumes a subset of fields.

Payload size is part of the API contract.

Workflow:

```text
UI
↓
Field Audit
↓
API Response Contract
↓
Optimized SELECT Query
↓
Minimal Payload
```

Rules:

1. Public APIs

* Return only fields required by the UI.
* Create dedicated response schemas when necessary.
* Avoid sending metadata that is not displayed.
* Never use SELECT * for user-facing endpoints.

2. List Endpoints

* Return lightweight summary models only.
* Never return large text or blob fields unless the list UI displays them.
* Return only fields actually consumed by the frontend.

3. Dashboard Endpoints

* Return summary information only.
* Replace large content with previews when appropriate.
* Do not include full document bodies, transcripts, notes, markdown, JSON
  payloads, render payloads, or similar large fields unless the dashboard
  requires them.

4. Detail Endpoints

* Return the complete record required for viewing or editing.
* Edit drawers and edit pages must load full records from detail endpoints
  instead of bloating list or dashboard responses.

5. Create and Update

* Validate update DTOs independently from create DTOs.
* Never accept or require create-only parent IDs during update operations unless
  the backend update schema explicitly supports parent reassignment.

6. Admin APIs

* Admin endpoints may return complete records.
* Admin screens are internal tools and are allowed to access all fields.

7. New Mini Apps

Before implementing any user-facing endpoint:

* Audit the UI fields.
* Define the response contract.
* Select only those columns from the database.
* Return minimal payloads.
* Verify list, dashboard, and detail endpoints follow lightweight/detail
  separation before approval.

8. Forbidden Pattern

```text
Database
↓
Return full ORM model
↓
Frontend ignores 50% to 80% of fields
```

This pattern must not be used.

9. Goal

Reduce:

* Database reads
* Network payload size
* Serialization overhead
* Browser transfer size
* Future infrastructure costs

Permanent Principle:

```text
Data is expensive.

Do not transport unused data.
```

## UI Action Button Contract

Ansiversa follows a consistent action-first button design across the parent app
and all mini apps.

Titles describe the object. Buttons describe the action.

1. Action button labels

* Buttons should describe only the action.
* The surrounding heading, card title, form title, or dialog title provides the
  context.
* Avoid repeating the object name inside the button.

Preferred examples:

* Create
* Save
* Update
* Add
* Start
* Play
* Generate
* Scan
* Upload
* Download
* Import
* Export
* Submit
* Continue
* Review
* Finish

Avoid:

* Create Project
* Create Draft
* Create Template
* Add History
* Save Project
* Update Template

2. Record actions

* Edit and Delete actions for existing records should use icon-only buttons
  where practical.
* Every icon button must include an accessible aria-label.
* Tooltips or title attributes should be provided when supported by the
  component.
* Icon buttons should maintain a consistent size throughout the platform.

3. Mobile-first behavior

* Action controls should not wrap because of long button labels.
* Prefer compact controls on cards and responsive layouts.
* Preserve touch-friendly spacing.

4. Shared implementation

* Repeated action controls should use shared frontend components whenever
  possible.
* Follow the Rule of 4 before introducing shared abstractions.

5. Consistency

* All future mini apps must follow this contract by default.
* During app review, verify button wording and record actions before approving
  the app.

## Parent Content Metadata Standard

Parent content pages are served through the `Metadata` table.

The `Metadata` table uses a key/content JSON structure.

Content routes expose typed endpoints:

```text
/api/v1/content/metadata/home
/api/v1/content/metadata/about
/api/v1/content/metadata/terms
/api/v1/content/metadata/privacy
/api/v1/content/metadata/pricing
```

Use typed Pydantic response schemas such as:

* `HomeResponse`
* `AboutResponse`
* `LegalResponse`
* `PricingResponse`

The generic `/metadata` list and PUT/DELETE routes remain available for
management and testing.

Parent content must be stored and updated through the API. Do not require
frontend applications to hardcode page content.

Mini-app overview metadata CTA labels must follow the platform standard:

```text
Explore
```

Do not use app-specific start labels such as `Start`, `Start App`, or
`Explore <App Name>` for the primary overview CTA or final CTA. When overview
metadata changes, sync the metadata table and verify the stored
`overview:<app-slug>` record returns the updated label. Overview CTA paths
must enter the first real app workflow page, not route back to the overview
page itself, unless the mini-app has no workflow page.

The hard validation command is:

```text
python3 -m app.modules.content.scripts.validate_overview_ctas
```

The validator must pass before overview metadata sync, new mini-app approval,
or live promotion. It checks primary/final CTA labels, missing or placeholder
paths, and first workflow route alignment against the frontend
`APP_MODULE_PAGES` registry when a workflow route exists.

Mini-app CRUD APIs must support visible frontend edit flows for user-created
long-lived records before approval. Update schemas must be explicit and
owner-scoped. Frontend update payloads must be checked against these schemas:
create-only parent fields such as `courseId`, `sessionId`, `questionId`,
`scanId`, or `projectId` must be rejected unless reassignment is intentionally
supported by the update schema and service.

The parent Alembic history includes a merge revision for the metadata and user
settings branches. Preserve that merged migration history.

## Mini App Catalog Identity Rule

The Apps catalog is the single source of truth for every mini-app identity.

These fields must always come from the Apps catalog and nowhere else:

* App name
* Key
* Slug
* Logo key
* Category
* Route identity

Never invent, rename, or substitute app names during development.

Examples:

```text
Incorrect: File Compressor
Correct: File Optimizer

Incorrect: Text-to-Speech Converter
Correct: Voice Converter
```

If a task handoff, readiness report, capability matrix, AGENTS log, story,
overview, metadata file, route, or production record uses a different app name,
key, slug, logo key, category, or route identity than the Apps catalog, treat it
as documentation drift.

Required action before development:

1. Stop implementation.
2. Verify the Apps catalog.
3. Use the catalog identity.
4. Correct every stale active-repository reference.
5. Continue development only after the repo uses one consistent identity.

There must never be two active names referring to the same application anywhere
in the repository. For every mini app there must be exactly one name, slug, and
key across documentation, readiness reports, capability matrices, stories,
overview metadata, routes, task logs, catalog exports, database rows, and
production metadata.

Before promotion, any discovered identity mismatch must be fixed in
documentation and metadata. The Apps catalog is the authority. Never allow
contract drift.

---

## Environment and Secrets

Never commit secrets.

`.env` must stay ignored.

Use `.env.example` for safe placeholders.

Database URLs, auth secrets, API keys, and tokens must only come from environment variables.

---

## Database Rules

Use SQLAlchemy cleanly.

Use Alembic for migrations.

Local development database files live under:

```text
db/
```

Do not assume local DB files are in the repository root or module folders.

Do not mix unrelated app metadata into one migration context unless intentionally designed.

When adding a mini-app DB engine, isolate it clearly.

Never allow one mini-app to directly own another mini-app's data.

Cross-app reads should happen through approved API/service aggregation only.

## Mini App Boundary

Each mini-app must remain self-contained.

Review scope:

```text
app/modules/<app>
```

Typical files:

```text
models.py
routes.py
schemas.py
service.py
```

Do not modify unrelated modules.

Do not modify parent database unless explicitly requested.

## Mini App Approval Checklist Contract

For every new mini app, before approval:

1. Overview metadata complete
2. Protected workflow routes complete
3. Create/Edit/Delete support for long-lived user records
4. Create buttons use simple labels: Create / Add / Save
5. Saved-record actions use icon buttons where practical
6. API responses return only frontend-required fields
7. Update payloads exclude create-only parent IDs
8. Required DB indexes reviewed/added
9. Empty/loading/error/success states present
10. lint/typecheck/build/backend compileall passed
11. `market-study.md`, `destination.md`, `story.md`, and `marketing.md`
    present and aligned
12. apps.json/catalog/readiness docs updated
13. Mandatory authenticated Codex E2E gate passed with evidence
14. Karthik manual acceptance approval completed
15. Production migration and live promotion only after explicit approval

## Mandatory Codex End-to-End Testing Gate

Before presenting an application for user review, Codex must complete authenticated end-to-end testing with the dedicated normal-user Ansiversa test account. Compile, typecheck, lint, build, API tests, and migration validation do not replace this gate.

Codex must:

1. Log in through the real Ansiversa login workflow.
2. Open the app Overview and follow `Explore` into the first real workflow.
3. Test every route and workflow documented in `story.md`.
4. Test create, view, edit, delete, search, filters, pagination, refresh, persistence, and back-button navigation where applicable.
5. Test valid, invalid, boundary, duplicate, and stale-form inputs.
6. Test loading, empty, populated, error, filtered-empty, unauthorized, and missing-record states.
7. Test direct URLs and invalid or inaccessible record IDs.
8. Test desktop and mobile viewports for overflow, drawer/dialog behavior, focus, and responsive layout.
9. Inspect browser console output and failed network/API requests.
10. Record every defect, fix every in-scope defect, retest affected workflows after each fix, and run a complete regression pass after the final fix.
11. Remove disposable test records where appropriate.
12. Provide screenshots or equivalent browser evidence and a structured E2E report covering executed, passed, and failed cases; defects and fixes; regression results; and remaining limitations.

Codex must not mark an app ready for user review until this gate passes. If credentials, browser access, or another required test dependency is unavailable, report the app as technically implemented but E2E-blocked.

Test credentials must be supplied through environment variables or an existing authenticated browser session. They must never be committed, documented, printed, logged, or shown in screenshots. The test account must have no administrative privileges.

The approval order is permanent:

1. Codex technical and authenticated E2E approval
2. Karthik manual acceptance approval
3. Live promotion

## Story Documentation Contract

Starting from App #026, every new mini-app must include a `story.md` file in
both the frontend module and backend module.

Required locations:

* Frontend: `ansiversa/src/modules/<app-slug>/story.md`
* Backend: `ansiversa-api/app/modules/<app_module>/story.md`

`story.md` is the module's Proof of Concept and long-term technical memory. It
explains the app's purpose, workflow, architecture, technical decisions, current
status, known limitations, and future direction.

Requirements:

1. Every new mini-app from App #026 onward must create both frontend and backend
   `story.md`.
2. `story.md` must explain WHY the module exists and WHY the workflow, API,
   database, and UI decisions were made.
3. `story.md` must stay updated whenever the workflow, database, API, UI,
   production status, or major behavior changes.
4. `story.md` is treated as production source code, not optional documentation.
5. Future AI coding engines should be able to understand the module by reading
   the frontend and backend story files.
6. At the App #040 checkpoint, backfill `story.md` files for Apps #001-#025
   using the matured template from Apps #026-#040.

### Story Documentation Philosophy

`story.md` is not a chronological logbook, changelog, diary, or task history.

Its purpose is to describe the current implementation of the module as it exists
today.

The document must always present the current architecture, workflow, API design,
database design, UI behavior, and technical decisions.

When the module evolves:

* Update the existing sections to reflect the new implementation.
* Replace outdated information.
* Keep the document concise and accurate.
* Do not append historical implementation notes.

Example:

Avoid:

```text
Yesterday:

* userId was an integer.

Today:

* userId is a serial number.
```

Preferred:

```text
User IDs use serial numbers.
```

The document should always read as if someone is opening the project for the
first time and wants to understand the module exactly as it exists today.

Historical information belongs in:

* Git commit history
* Pull requests
* Task logs
* Release notes
* Issue trackers

It does not belong in `story.md`.

`story.md` is the module's living architectural description and Proof of Concept
(POC).

It should answer:

* What does the module do today?
* How does it work today?
* Why is it designed this way today?
* What are the current limitations?
* What are the planned future improvements?

It should never require the reader to understand previous versions before
understanding the current one.

Minimum sections:

* Purpose
* Workflow
* User Journey
* Database Design
* API Design
* Shared Components Used
* Performance Considerations
* Current Status
* Known Limitations
* Future Enhancements
* Current Implementation

## Market Study Documentation Contract

Every new Ansiversa mini-app must include a `market-study.md` file in the
backend module during initial app development.

Required location:

* Backend: `ansiversa-api/app/modules/<app_module>/market-study.md`

`market-study.md` is the module's external market intelligence layer. It
captures competitor patterns, user pain points, pricing and paywall signals,
AI capability trends, UX patterns, risks, and Ansiversa-specific opportunities.

It is research only.

It does not define product requirements.

It does not create implementation commitments.

All product decisions still require Partner approval and must be reflected
separately in `destination.md`.

Requirements:

1. Every new mini-app must create backend `market-study.md` during initial
   development, alongside `story.md` and `destination.md`.
2. The document must use the established Ansiversa market-study template:
   Document Status, Market Version, Created, Last Reviewed, Next Review,
   Purpose, Problem Statement, Target Users, Competitor Landscape, Common Market
   Features, user love signals, complaints/friction, pricing/paywall
   observations, AI trends, UX patterns, opportunities, avoid list, product
   questions, sources, review notes, and revision history.
3. The document must summarize public research in original words.
4. The document must include source links for public references used.
5. The document must not copy competitor wording, UI, screenshots, templates,
   prompts, scoring models, proprietary workflows, or protected content.
6. The document must not modify code, APIs, database, metadata, catalog files,
   readiness documents, `story.md`, or `destination.md` unless separately
   requested and approved.
7. Market Version begins at `1` and increments only when the market
   understanding is meaningfully refreshed.
8. `Last Reviewed` must be updated whenever the study is materially refreshed.
9. Future product planning may learn from `market-study.md`, but implementation
   scope must still come from approved Partner/Astra direction and
   `destination.md`.

### Market Study Philosophy

`market-study.md` exists so Ansiversa learns before it builds.

It should answer:

* What real user problem exists in the market?
* Which direct, indirect, and AI-based alternatives already serve this need?
* Why do users like those alternatives?
* Why do users abandon or complain about them?
* What pricing, trust, privacy, and paywall patterns shape user expectations?
* Which UX patterns are worth studying without copying?
* What opportunities fit Ansiversa's platform identity?
* What should Ansiversa avoid?

`market-study.md` is not a feature backlog, roadmap, implementation spec, or
marketing document.

The correct sequence for new mini-app product memory is:

```text
market-study.md
External market intelligence and user problem learning

destination.md
Approved mature product destination and Journey Progress

story.md
Current implementation and technical memory

marketing.md
Approved public communication, launch, video, social, SEO, and guardrails
```

## Marketing Framework Documentation Contract

Every newly developed Ansiversa mini-app must include a `marketing.md` file in
the backend module as part of the normal development lifecycle.

Required location:

* Backend: `ansiversa-api/app/modules/<app_module>/marketing.md`

The required documentation order for every app is:

```text
market-study.md
Research: understand market reality, users, competitors, and opportunities

destination.md
Vision: define the long-term product destination, principles, non-goals, and
maturity roadmap

story.md
Implementation: document the current architecture, workflow, capabilities,
limitations, and technical state

marketing.md
Communication: define public product messaging, Google Veo video prompts,
social media, landing page copy, advertisements, SEO, marketing assets, and
guardrails
```

An app is not documentation-complete until all four files exist and agree with
each other.

Development workflow:

```text
Research
    -> market-study.md

Vision
    -> destination.md

Implementation
    -> story.md

Communication
    -> marketing.md
```

Marketing Framework v1.0 is frozen. New apps must use the approved Marketing
Framework v1.0 structure. Do not redesign or restructure the framework for
individual apps. Only update content specific to the app.

`marketing.md` must be truthful to the current implementation documented in
`story.md`. Current features, future marketing opportunities, and marketing
guardrails must remain clearly separated. Do not advertise future capabilities
as current product behavior.

The Ansiversa parent platform must also maintain these same four documents. No
exceptions.

This is a permanent Ansiversa development standard.

## Destination Progress Governance

`destination.md` is the source of truth for each product's approved destination
and Journey Progress.

The Apps table may store destination metadata for portfolio visibility:

```text
destination_progress
destination_status
destination_reviewed_at
```

`destination_progress` stores the current approved Journey Progress from the
product's approved `destination.md`. The destination itself is always `100 / 100`
and must not be stored as a separate target value.

Journey Progress measures product maturity and alignment with the approved
destination. It does not measure feature count.

Journey Progress may:

* Increase
* Remain unchanged
* Decrease

A decrease is valid when a product drifts away from its approved identity,
trust boundary, privacy boundary, ecosystem boundary, or governance principles.

Destination metadata must only be populated from approved `destination.md`
documents. Do not estimate, recalculate, or infer Journey Progress from code,
feature count, roadmap size, or implementation volume.

### Destination Metadata Promotion Rule

Every time a mini-app is promoted to Live, the promotion process must also
update the parent Apps table destination metadata.

The values must be taken only from the app's approved `destination.md`.

Required updates:

* `destination_progress`
* `destination_status`
* `destination_reviewed_at`

Promotion is not complete until destination metadata, Apps API, and `apps.json`
are synchronized.

### Destination-First Development Rule

Every new Ansiversa mini-app must create `destination.md` during initial app
development.

The document should be prepared before the app is promoted and should describe
the intended mature product, not only the initial release.

`story.md` describes the current implementation.

`destination.md` describes the intended mature destination.

Journey Progress begins from the first approved version and is updated as the
product matures.

### Journey Progress Update Rule

Journey Progress is reviewed whenever an app is promoted or undergoes a major
governance review.

Journey Progress may increase, remain unchanged, or decrease depending on how
closely the current product aligns with its approved destination.

Feature count alone must never determine Journey Progress.

## Mini App Versioning

Mini-app version numbers are owned by the parent `Apps` catalog record.

Governance:

* Apps with `launchStatus = live` must have an approved release version.
* Apps with `launchStatus != live` must keep `Apps.version = NULL`.
* `NULL` means no approved release exists yet.

Use semantic versioning:

```text
1.0.0 = first stable release
1.1.0 = feature improvement
1.1.1 = bug fix
2.0.0 = major workflow/design change
```

Do not store competing mini-app versions in frontend metadata, overview content,
or app-local configuration.

Approval promotions must update the parent `Apps` table row before status
documentation is complete:

```text
status = active
launchStatus = live
version = 1.0.0
```

When Partner and Astra approve an app and request live promotion, updating and
re-reading the production parent `Apps` table is mandatory and non-optional.
Do not report the app as live, update live counts, sync final readiness docs, or
move to the next app until the production row has been verified as
`active` / `live` / `1.0.0`.

After updating the row, sync `app/modules/content/data/overview/apps.json` so
the catalog export reflects the same `launchStatus` and `version`.

## Mini App Database Rule

Every mini-app owns its own database.

Do not use:

```text
ansiversadb
```

unless explicitly requested.

Only migrate the target app database.

Avoid duplicate Alembic revisions.

If current head is already correct:

```text
Do not create a new migration.
```

## Database Index Contract

Every new persistent database table introduced by a mini app must include an
index review before the app is approved for production.

Indexes must be designed from the application's user-facing query patterns,
not from speculation.

Required review areas:

* ownerId / userId list queries
* createdAt sorting
* updatedAt sorting
* parent foreign-key lookups
* dashboard/status filters
* timeline/history queries
* review/detail navigation
* frequently used ordering columns

Avoid:

* speculative indexes
* duplicate indexes
* indexes on large text/blob/json columns
* full-text/trigram indexes unless the feature explicitly requires search

Index creation is part of the mini app completion checklist and must be
completed before production promotion.

When introducing a new API endpoint or changing query behavior, re-evaluate
whether an additional index is required.

## Production Migration Rule

Scenario 1:

```text
New app
↓
New tables
↓
Alembic revision
↓
Upgrade head
```

Scenario 2:

```text
Existing production schema
↓
Reuse schema
↓
No revision required
↓
Upgrade head still executed
↓
Verification only
```

Both scenarios are valid.

For schema-reuse cases, report:

```text
Production schema verification completed.

No new revision files were required because the existing schema was reused.
```

Do not overstate schema-reuse work as a normal new-table production migration.

---

## Auth and Security Direction

Future auth must support:

* Web clients
* Mobile clients
* Bearer token/JWT usage
* Secure API docs testing
* Role and permission checks
* Parent-owned user/session concepts

Do not implement temporary insecure shortcuts in production paths.

---

## FastAPI Standards

Use:

* typed request/response schemas
* clear status codes
* explicit error handling
* small routers
* dependency injection where useful
* OpenAPI-friendly route definitions

Avoid:

* hidden globals for request-specific state
* large route handlers
* untyped dictionaries for important contracts
* hardcoded environment values

---

## CORS Standard

CORS must be controlled from settings/environment.

Initial allowed origins should include:

```text
http://localhost:4321
https://ansiversa.com
https://www.ansiversa.com
```

More app domains may be added later intentionally.

---

## Deployment Standard

The API is deployed to Vercel.

Production domain:

```text
https://api.ansiversa.com
```

After deployment, verify:

```text
/
/docs
/api/v1/health/
```

---

## Verification Required Before Commit

Before committing code, verify at minimum:

```bash
python -m compileall app
uvicorn app.main:app --reload
```

Then manually check:

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/api/v1/health/
```

If dependencies change, update:

```text
requirements.txt
```

---

## Git Rules

Use clear commits.

Examples:

```text
chore: initialize FastAPI foundation
feat: add settings and middleware foundation
feat: add parent database engine
feat: add quiz API module foundation
fix: correct CORS settings parsing
docs: update API setup guide
```

Do not commit broken runtime code.

Do not commit `.venv`, `.env`, caches, or local machine files.

---

## Development Philosophy

This repository must grow slowly and safely.

Do not rewrite existing Ansiversa web apps.

Do not migrate all mini-apps at once.

Recommended migration path:

1. Parent/global API foundation
2. Auth/session foundation
3. Apps/catalog API
4. Dashboard API
5. One mini-app API pilot
6. Mobile-ready API contracts
7. Gradual mini-app API migration

The API should become the stable bridge between:

```text
Web apps
iOS app
Android app
AI workers
Mini-app databases
Parent database
```

---

## Ansiversa 101 Principle

Ansiversa is not an endless app factory.

The ecosystem is permanently limited to:

```text
1 Platform
+
100 Solution Apps
=
101 Total Products
```

There will be no App #102, App #103, or unlimited expansion.

Ansiversa may identify thousands of problems in the market, but it will only
choose the best 100 problems worth solving inside the ecosystem.

After all 100 solution apps are complete, Codex must not propose new apps by
default.

Post-100 work must focus on:

* Improving existing apps
* Strengthening workflows
* Improving performance
* Improving quality
* Improving ease of use
* Removing friction
* Studying competitors
* Identifying user pain points
* Improving retention
* Replacing weak apps only when clearly justified

If a new app idea appears after 100, it must not be added as App #101 or App
#102. It must answer:

```text
Which existing solution app should this replace?
```

Every app must continuously earn its place.

The goal is not to build more apps.

The goal is to maintain the best 100 everyday software solutions, each strong
enough to stand on its own.

Current status:

```text
Platform + 100 live solution apps
Remaining live approvals toward 100 solution apps: 0
Current workflow: Post-100 platform work must focus on horizontal improvements across shared capabilities, quality, accessibility, performance, PWA, search, payments, AI integration, security, and user experience.
```

---

## Current Milestone

Initial production milestone completed:

* FastAPI foundation created
* Health route working
* Swagger docs working
* Vercel deployment working
* Custom domain live at `https://api.ansiversa.com`

Next milestone:

* settings/config foundation
* CORS middleware
* `.env.example`
* README expansion

---

## Task Log (Recent)

* 2026-07-19: Implemented Ansiversa AI Assistant Phase 2 Backend Knowledge Retrieval Foundation with `POST /api/v1/assistant/query`, deterministic public catalog/page/FAQ retrieval, validated navigation actions, safe source metadata, focused service tests, and no OpenAI, external AI APIs, migrations, or user-data indexing.

* 2026-07-19: Promoted Shift Planner App #091 to approved live version `1.0.0` after Astra review and Partner manual verification, production-configured isolated migration verification at `20260716_0003_shift_planner`, parent Apps row promotion to `active` / `live`, destination metadata sync to `18 / 100` / `approved` / `2026-07-19`, overview metadata sync, catalog count verification at 92 live / 8 comingSoon, and validation; no business-logic changes were made.

* 2026-07-19: Promoted Decision Maker App #097 to approved live version `1.0.0` after Astra review and Partner manual verification, production-configured isolated migration verification at `20260716_0009_decision_maker`, parent Apps row promotion to `active` / `live`, destination metadata sync to `20 / 100` / `approved` / `2026-07-19`, overview metadata sync, catalog count verification at 91 live / 9 comingSoon, and validation; no business-logic changes were made.

* 2026-07-18: Promoted Bill Splitter App #093 to approved live version `1.0.0` after Astra review and Partner manual verification, production-configured isolated migration verification at `20260716_0005_bill_splitter`, parent Apps row promotion to `active` / `live`, destination metadata sync to `20 / 100` / `approved` / `2026-07-18`, overview metadata sync, catalog count verification at 90 live / 10 comingSoon, and validation; no business-logic changes were made.

* 2026-07-18: Promoted Leave Planner App #090 to approved live version `1.0.0` after Astra review and Partner manual verification, production-configured isolated migration verification at `20260716_0002_leave_planner`, parent Apps row promotion to `active` / `live`, destination metadata sync to `20 / 100` / `approved` / `2026-07-18`, overview metadata sync, catalog count verification at 89 live / 11 comingSoon, and validation; no business-logic changes were made.

* 2026-07-18: Promoted Travel Itinerary Builder App #046 to approved live version `1.0.0` after Astra review and Partner manual verification, production-configured isolated migration verification at `20260718_0001_travel_itinerary_builder`, parent Apps row promotion to `active` / `live`, destination metadata sync to `20 / 100` / `approved` / `2026-07-18`, overview metadata sync, catalog count verification at 88 live / 12 comingSoon, and validation; no business-logic changes were made.

* 2026-07-18: Certified Travel Itinerary Builder App #046 backend behavior during authenticated E2E hardening by moving activity time ordering validation into the service layer for user-safe API errors, updating focused service regression coverage, removing placeholder-era story language, and revalidating Travel Itinerary Builder service tests plus backend compileall. The app remains `comingSoon` with `version = null`; no live promotion was performed.

* 2026-07-18: Implemented Travel Itinerary Builder App #046 backend to Workflow Ready with isolated `TRAVEL_ITINERARY_BUILDER_DATABASE_URL`, owner-scoped itineraries and categories, itinerary day and activity CRUD through parent ownership, date-range validation, duplicate trip/day/activity/category rules, lightweight list/dashboard responses, complete detail DTOs, migration `20260718_0001_travel_itinerary_builder`, lifecycle documentation, generated contracts, focused service tests, local isolated migration verification, and no live promotion.

* 2026-07-18: Certified Emergency Checklist App #100 backend behavior during authenticated E2E hardening by enforcing archived checklist restore-only behavior before archive/delete/update/item mutations, updating module story documentation, extending focused service regression coverage, and revalidating Emergency Checklist service tests plus backend compileall. The app remains `comingSoon` with `version = null`; no live promotion was performed.

* 2026-07-18: Certified Local Services Finder App #099 backend behavior during authenticated E2E hardening by narrowing list/dashboard summaries to frontend-required fields, keeping detail-only alternate phone, email, and website on detail/create/update/action responses, enforcing archived provider restore-only behavior before delete/update/archive/prefer/unprefer, updating module story documentation, extending focused service regression coverage, and revalidating Local Services Finder service tests plus backend compileall. The app remains `comingSoon` with `version = null`; no live promotion was performed.

* 2026-07-18: Certified Errand Planner App #098 backend behavior during authenticated E2E hardening by narrowing list/dashboard summaries to frontend-required fields, keeping detail-only description and notes on detail/create/update/status responses, enforcing archived errand restore-only behavior before delete/update, updating module story documentation, extending focused service regression coverage, and revalidating Errand Planner service tests plus backend compileall. The app remains `comingSoon` with `version = null`; no live promotion was performed.

* 2026-07-18: Certified Decision Maker App #097 backend behavior during authenticated E2E hardening by narrowing list summaries to frontend-required fields, keeping full edit/view fields on detail responses, enforcing archived decision restore-only behavior, blocking archived decision deletion until restore, updating module story documentation, extending focused service regression coverage, and revalidating Decision Maker service tests plus backend compileall. The app remains `comingSoon` with `version = null`; no live promotion was performed.
* 2026-07-18: Certified Net Worth Tracker App #096 backend behavior during authenticated E2E hardening by adding case-insensitive owner-scoped account-name uniqueness, blocking archived account metadata/balance updates except restore-only activation, updating module story documentation, extending focused service regression coverage, and revalidating Net Worth Tracker service tests plus backend compileall. The app remains `comingSoon` with `version = null`; no live promotion was performed.

* 2026-07-17: Certified Salary Breakdown Calculator App #095 backend behavior during authenticated E2E by revalidating focused salary service coverage for six-frequency normalization, deduction order, negative recurring-net rollback, same/cross-currency comparison, ownership isolation, filters, pagination, cascade delete, overview CTA validation, and backend compileall. No backend code change was required; the app remains `comingSoon` with `version = null`, and no live promotion was performed.

* 2026-07-17: Certified Savings Goal Planner App #094 backend behavior during authenticated E2E hardening by blocking transaction deletion while goals are paused, cancelled, or archived, extending focused service regression coverage, and revalidating Savings Goal Planner service tests plus backend compileall. The app remains `comingSoon` with `version = null`; no live promotion was performed.

* 2026-07-17: Certified Bill Splitter App #093 backend behavior during authenticated E2E hardening by adding case-insensitive bill participant uniqueness, extending focused service regression coverage, and revalidating Bill Splitter service tests plus backend compileall. The app remains `comingSoon` with `version = null`; no live promotion was performed.

* 2026-07-17: Certified Work Log Tracker App #092 backend behavior during authenticated E2E hardening by adding case-insensitive owner-scoped project name/code uniqueness, excluding planned logs from project logged-minute summaries, and extending service regression tests for both rules. Revalidated `tests.test_work_log_tracker_service` and backend compileall while keeping the app `comingSoon` with `version = null` and no live promotion.

* 2026-07-17: Certified Shift Planner App #091 against disposable localhost databases; added case-insensitive owner-scoped shift-type duplicate protection and regression coverage, passed focused service/compile checks plus authenticated Playwright ownership and scheduling workflows, and preserved comingSoon/version null pending Karthik acceptance.

* 2026-07-16: Implemented Emergency Checklist App #100 backend to Workflow Ready with isolated `EMERGENCY_CHECKLIST_DATABASE_URL`, owner-scoped categories and reusable checklists, checklist item CRUD through parent ownership, duplicate category protection, duplicate checklist protection within category, complete/reopen item actions, complete/reset checklist actions, archive/restore read-only rules, item-title search, combined filters, pagination, dashboard metrics, migration `20260716_0012_emergency_checklist`, lifecycle documentation, overview metadata, generated contracts, and regression tests. Ran the production-configured isolated migration to head and verified `ChecklistCategories`, `EmergencyChecklists`, `ChecklistItems`, the custom version table, ten indexes, two foreign keys, and empty starting row counts. The app remains `comingSoon` with `version = null`; authenticated E2E, manual approval, and live promotion remain pending.

* 2026-07-16: Implemented Local Services Finder App #099 backend to Workflow Ready with isolated `LOCAL_SERVICES_FINDER_DATABASE_URL`, owner-scoped service providers and categories, duplicate category protection, duplicate provider protection within category, preferred/unpreferred actions, archive/restore behavior, contact fields, rating validation, combined filters, pagination, dashboard metrics, migration `20260716_0011_local_services_finder`, lifecycle documentation, overview metadata, generated contracts, and regression tests. Ran the production-configured isolated migration to head and verified `ServiceCategories`, `ServiceProviders`, the custom version table, ten indexes, and empty starting row counts. The app remains `comingSoon` with `version = null`; authenticated E2E, manual approval, and live promotion remain pending.

* 2026-07-16: Implemented Errand Planner App #098 backend to Workflow Ready with isolated `ERRAND_PLANNER_DATABASE_URL`, owner-scoped errands and categories, duplicate category protection, category delete protection, status actions for complete/reopen/archive/restore, overdue/due-today/due-soon detection, combined filters, pagination, dashboard metrics, migration `20260716_0010_errand_planner`, lifecycle documentation, overview metadata, generated contracts, and regression tests. Ran the production-configured isolated migration to head and verified `ErrandCategories`, `Errands`, the custom version table, nine indexes, one foreign key, and empty starting row counts. The app remains `comingSoon` with `version = null`; authenticated E2E, manual approval, and live promotion remain pending.

* 2026-07-16: Implemented Work Log Tracker App #092 backend to Workflow Ready with isolated `WORK_LOG_TRACKER_DATABASE_URL`, owner-scoped projects and timed/manual logs, overnight/break calculations, active timed overlap prevention, billable time summaries, protected CRUD, combined filters, pagination, migration `20260716_0004_work_log_tracker`, lifecycle documentation, generated contracts, compileall, and regression tests. Ran the production-configured migration to head and verified both application tables, the custom version table, eleven indexes, one foreign key, and empty starting row counts. The app remains `comingSoon` with `version = null`; authenticated E2E remains pending.

* 2026-07-16: Implemented Shift Planner App #091 backend to Workflow Ready with isolated `SHIFT_PLANNER_DATABASE_URL`, owner-scoped shift types, lightweight members, and shifts; overnight and break-aware duration; same-member conflict prevention; safe historical deactivation; protected CRUD, combined filters, pagination, metrics, migration `20260716_0003_shift_planner`, overview routing, lifecycle documentation, generated contracts, compileall, and regression tests. Ran the production-configured migration to head and verified all three application tables, the custom version table, twelve indexes, two foreign keys, and empty starting row counts. The app remains `comingSoon` with `version = null`; authenticated E2E remains pending.

* 2026-07-16: Implemented Leave Planner App #090 backend to Workflow Ready with isolated `LEAVE_PLANNER_DATABASE_URL`, owner-scoped leave types and entries, weekday and half-day duration rules, overlap prevention, safe historical type deactivation, protected CRUD APIs, combined search/filter/pagination, dashboard balances, Alembic migration `20260716_0002_leave_planner`, overview routing to `/leave-planner/leaves`, lifecycle documentation, generated OpenAPI contracts, compileall, and service tests. Ran the production-configured migration to head and verified `LeaveTypes`, `LeaveEntries`, the custom version table, ten indexes, one foreign key, and empty starting row counts. The app remains `comingSoon` with `version = null`; authenticated E2E remains pending.
* 2026-07-16: Implemented Meeting Scheduler App #089 backend to Workflow Ready with isolated `MEETING_SCHEDULER_DATABASE_URL`, owner-scoped meetings with nested participants and agenda items, protected CRUD APIs, search/status/period filters, pagination, dashboard summaries, Alembic migration `20260716_0001_meeting_scheduler`, overview Explore routing to `/meeting-scheduler/meetings`, lifecycle documentation, generated OpenAPI contracts, compileall verification, service smoke tests, and production migration verification covering the custom version table, three empty starting tables, nine indexes, and two cascade foreign keys. The app remains `comingSoon` with `version = null` and no live promotion.
* 2026-07-15: Fixed Symptom Journal App #084 production fetch failures by passing the shared libSQL/Turso auth connect args into the isolated symptom journal database engine, verified the isolated version table at `20260715_0001_symptom_journal`, smoke-tested dashboard/categories/entries/insights API responses plus entry creation, removed temporary smoke-test entry and category rows, and kept the app `comingSoon` with version `null`.
* 2026-07-15: Promoted Vaccination Tracker App #083 backend to approved live version `1.0.0` after Astra/Partner approval, backend database-auth fix verification, production Apps row promotion, destination metadata sync `20 / 100` approved on `2026-07-15`, overview metadata sync, production migration verification at `20260715_0001_vaccination_tracker`, tracked catalog export update, and production catalog verification at 82 live / 18 comingSoon.
* 2026-07-15: Fixed Vaccination Tracker App #083 production fetch failures by passing the shared libSQL/Turso auth connect args into the isolated vaccination tracker database engine, verified the isolated version table at `20260715_0001_vaccination_tracker`, smoke-tested dashboard/profiles/vaccines/records/insights API responses, removed temporary smoke-test profile and vaccine rows, and kept the app `comingSoon` with version `null`.
* 2026-07-15: Promoted Water Intake Tracker App #082 backend to approved live version `1.0.0` after Astra/Partner approval, backend database-auth fix verification, production Apps row promotion, destination metadata sync `20 / 100` approved on `2026-07-15`, overview metadata sync, production migration verification at `20260715_0001_water_intake_tracker`, tracked catalog export update, and production catalog verification at 81 live / 19 comingSoon.
* 2026-07-15: Fixed Water Intake Tracker App #082 production fetch failures by passing the shared libSQL/Turso auth connect args into the isolated water intake database engine, verified the isolated version table at `20260715_0001_water_intake_tracker`, smoke-tested dashboard/entries/drink-types/insights API responses, removed the temporary smoke-test goal row, and kept the app `comingSoon` with version `null`.
* 2026-07-15: Promoted Doctor Visit Tracker App #081 backend to approved live version `1.0.0` after Astra/Partner approval, production Apps row promotion, destination metadata sync `20 / 100` approved on `2026-07-15`, overview metadata sync, production migration verification at `20260715_0001_doctor_visit_tracker`, tracked catalog export update, and production catalog verification at 80 live / 20 comingSoon.
* 2026-07-15: Promoted Home Maintenance Planner App #080 backend to approved live version `1.0.0` after Astra/Partner approval, production Apps row promotion, destination metadata sync `20 / 100` approved on `2026-07-15`, overview metadata sync, production migration verification at `20260715_0001_home_maintenance_planner`, tracked catalog export update, and production catalog verification at 79 live / 21 comingSoon.
* 2026-07-15: Promoted Birthday & Anniversary Reminder App #079 backend to approved live version `1.0.0` after Astra/Partner approval, production Apps row promotion, destination metadata sync `20 / 100` approved on `2026-07-15`, overview metadata sync, production migration verification at `20260715_0001_birthday_and_anniversary_reminder`, tracked catalog export update, and production catalog verification at 78 live / 22 comingSoon.
* 2026-07-15: Promoted Packing Checklist App #078 backend to approved live version `1.0.0` after Astra/Partner approval, production Apps row promotion, destination metadata sync `20 / 100` approved on `2026-07-15`, overview metadata sync, production migration verification at `20260715_0001_packing_checklist`, tracked catalog export update, and production catalog verification at 77 live / 23 comingSoon.
* 2026-07-15: Promoted Emergency Contacts Organizer App #077 backend to approved live version `1.0.0` after Astra/Partner approval, production Apps row promotion, destination metadata sync `20 / 100` approved on `2026-07-15`, overview metadata sync, production migration verification at `20260715_0001_emergency_contacts_organizer`, tracked catalog export update, and production catalog verification at 76 live / 24 comingSoon.
* 2026-07-15: Ran Vehicle Document Tracker App #088 production-configured isolated database migration to Alembic head `20260715_0001_vehicle_document_tracker`, verified `VehicleDocumentsVehicles`, `VehicleDocumentTypes`, `VehicleDocuments`, 18 required indexes, custom version table, empty starting row counts, and kept the parent Apps row `comingSoon` with version `null`.
* 2026-07-15: Implemented Vehicle Document Tracker App #088 backend to Workflow Ready with isolated `VEHICLE_DOCUMENT_TRACKER_DATABASE_URL`, owner-scoped vehicles and document records, shared system plus user-managed document types, protected vehicle/type/document CRUD APIs, archive/restore actions, search/filter/sort/pagination support, issue/expiry/reminder date validation, dashboard and insights summaries, Alembic migration `20260715_0001_vehicle_document_tracker`, overview Explore routing to `/vehicle-document-tracker/documents`, market-study/destination/story/marketing documentation, generated OpenAPI contracts, local migration validation, compileall verification, service smoke tests, production migration verification, and no production Apps row live promotion. The app remains `comingSoon` with `version = null`.
* 2026-07-15: Ran Driver Logbook App #087 production-configured isolated database migration to Alembic head `20260715_0001_driver_logbook`, verified `DriverVehicles`, `DriverTrips`, 14 required indexes, custom version table, empty starting row counts, and kept the parent Apps row `comingSoon` with version `null`.
* 2026-07-15: Implemented Driver Logbook App #087 backend to Workflow Ready with isolated `DRIVER_LOGBOOK_DATABASE_URL`, owner-scoped `DriverVehicles` and `DriverTrips` tables, protected vehicle CRUD/archive/restore APIs, protected trip CRUD/archive/restore APIs, search/filter/sort/pagination support, odometer-derived distance, time duration validation, odometer order validation, dashboard and insights summaries, Alembic migration `20260715_0001_driver_logbook`, overview Explore routing to `/driver-logbook/trips`, market-study/destination/story/marketing documentation, generated OpenAPI contracts, local migration validation, compileall verification, service smoke tests, production migration verification, and no production Apps row live promotion. The app remains `comingSoon` with `version = null`.
* 2026-07-15: Ran Fuel Expense Tracker App #086 production-configured isolated database migration to Alembic head `20260715_0001_fuel_expense_tracker`, verified `FuelVehicles`, `FuelEntries`, 12 required indexes, custom version table, empty starting row counts, and kept the parent Apps row `comingSoon` with version `null`.
* 2026-07-15: Implemented Fuel Expense Tracker App #086 backend to Workflow Ready with isolated `FUEL_EXPENSE_TRACKER_DATABASE_URL`, owner-scoped `FuelVehicles` and `FuelEntries` tables, protected vehicle CRUD/archive/restore APIs, protected fuel entry CRUD APIs, search/filter/sort/pagination support, derived unit price, odometer order validation, dashboard and insights summaries, Alembic migration `20260715_0001_fuel_expense_tracker`, overview Explore routing to `/fuel-expense-tracker/entries`, market-study/destination/story/marketing documentation, generated OpenAPI contracts, local migration validation, compileall verification, service smoke tests, production migration verification, and no production Apps row live promotion. The app remains `comingSoon` with `version = null`.
* 2026-07-15: Ran First Aid Guide App #085 production-configured isolated database migration to Alembic head `20260715_0001_first_aid_guide`, verified `FirstAidCategories`, `FirstAidGuides`, `UserGuideBookmarks`, `UserGuideHistory`, 15 required indexes, custom version table, empty starting row counts, and kept the parent Apps row `comingSoon` with version `null`.
* 2026-07-15: Implemented First Aid Guide App #085 backend to Workflow Ready with isolated `FIRST_AID_GUIDE_DATABASE_URL`, system-managed first-aid categories and guide topics, owner-scoped bookmarks and viewing history, protected category/guide CRUD APIs, bookmark/unbookmark endpoints, recently viewed tracking, search/filter/sort/pagination support, dashboard and insights summaries, Alembic migration `20260715_0001_first_aid_guide`, overview Explore routing to `/first-aid-guide/guides`, market-study/destination/story/marketing documentation, generated OpenAPI contracts, local migration validation, compileall verification, service smoke tests, production migration verification, and no production Apps row live promotion. The app remains `comingSoon` with `version = null`.
* 2026-07-15: Ran Symptom Journal App #084 production-configured isolated database migration to Alembic head `20260715_0001_symptom_journal`, verified `SymptomCategories`, `SymptomEntries`, 14 required indexes, custom version table, empty starting row counts, and kept the parent Apps row `comingSoon` with version `null`.
* 2026-07-15: Implemented Symptom Journal App #084 backend to Workflow Ready with isolated `SYMPTOM_JOURNAL_DATABASE_URL`, owner-scoped symptom categories and entries, default category seeding, protected category/entry CRUD APIs, archive/restore actions, severity and temperature validation, search/filter/sort/pagination support, dashboard and insights summaries, Alembic migration `20260715_0001_symptom_journal`, overview Explore routing to `/symptom-journal/entries`, market-study/destination/story/marketing documentation, generated OpenAPI contracts, local migration validation, compileall verification, service smoke tests, production migration verification, and no production Apps row live promotion. The app remains `comingSoon` with `version = null`.
* 2026-07-15: Ran Vaccination Tracker App #083 production-configured isolated database migration to Alembic head `20260715_0001_vaccination_tracker`, verified `VaccinationProfiles`, `VaccineTypes`, `VaccinationRecords`, 20 required indexes, custom version table, empty starting row counts, and kept the parent Apps row `comingSoon` with version `null`.
* 2026-07-15: Implemented Vaccination Tracker App #083 backend to Workflow Ready with isolated `VACCINATION_TRACKER_DATABASE_URL`, owner-scoped profiles, vaccine types, and vaccination records, default vaccine type seeding, protected profile/vaccine/record CRUD APIs, archive/restore actions, duplicate dose protection, search/filter/sort/pagination support, due-date dashboard and insights summaries, Alembic migration `20260715_0001_vaccination_tracker`, overview Explore routing to `/vaccination-tracker/records`, market-study/destination/story/marketing documentation, generated OpenAPI contracts, local migration validation, compileall verification, service smoke tests, production migration verification, and no production Apps row live promotion. The app remains `comingSoon` with `version = null`.
* 2026-07-15: Ran Water Intake Tracker App #082 production-configured isolated database migration to Alembic head `20260715_0001_water_intake_tracker`, verified `WaterGoals`, `WaterEntries`, required indexes, custom version table, empty starting row counts, and kept the parent Apps row `comingSoon` with version `null`.
* 2026-07-15: Implemented Water Intake Tracker App #082 backend to Workflow Ready with isolated `WATER_INTAKE_TRACKER_DATABASE_URL`, owner-scoped daily goals and intake entries, default drink types, protected goal and entry CRUD APIs, drink type listing, paginated search/filter/sort support, daily/weekly/monthly summaries, dashboard and insights calculations, unit conversion between ml and L, Alembic migration `20260715_0001_water_intake_tracker`, overview Explore routing to `/water-intake-tracker/entries`, market-study/destination/story/marketing documentation, generated OpenAPI contracts, local migration validation, compileall verification, service smoke tests, production migration verification, and no production Apps row live promotion. The app remains `comingSoon` with `version = null`.
* 2026-07-15: Ran Doctor Visit Tracker App #081 production-configured isolated database migration to Alembic head `20260715_0001_doctor_visit_tracker`, verified `DoctorSpecialties`, `DoctorVisits`, required indexes, custom version table, empty starting row counts, and kept the parent Apps row `comingSoon` with version `null`.
* 2026-07-15: Implemented Doctor Visit Tracker App #081 backend to Workflow Ready with isolated `DOCTOR_VISIT_TRACKER_DATABASE_URL`, owner-scoped specialties and visit records, default specialty seeding, protected specialty/visit CRUD APIs, archive/restore actions, search/filter/sort support, dashboard and insights summaries, Alembic migration `20260715_0001_doctor_visit_tracker`, overview Explore routing to `/doctor-visit-tracker/visits`, market-study/destination/story/marketing documentation, generated OpenAPI contracts, local migration validation, compileall verification, service smoke tests, production migration verification, and no production Apps row live promotion. The app remains `comingSoon` with `version = null`.
* 2026-07-15: Ran Home Maintenance Planner App #080 production-configured isolated database migration to Alembic head `20260715_0001_home_maintenance_planner`, verified `MaintenanceAreas`, `MaintenanceCategories`, `MaintenanceTasks`, `MaintenanceTaskCompletions`, required indexes, custom version table, empty starting row counts, and kept the parent Apps row `comingSoon` with version `null`.
* 2026-07-15: Implemented Home Maintenance Planner App #080 backend to Workflow Ready with isolated `HOME_MAINTENANCE_PLANNER_DATABASE_URL`, owner-scoped maintenance areas, categories, tasks, and completion history, default area/category seeding, protected task/area/category CRUD APIs, complete/reopen/archive/restore actions, recurrence advancement, cost/provider fields, search/filter/sort support, dashboard and insights summaries, Alembic migration `20260715_0001_home_maintenance_planner`, overview Explore routing to `/home-maintenance-planner/tasks`, market-study/destination/story/marketing documentation, generated OpenAPI contracts, local migration validation, compileall verification, service smoke tests, production migration verification, and no production Apps row live promotion. The app remains `comingSoon` with `version = null`.
* 2026-07-15: Ran Birthday & Anniversary Reminder App #079 production-configured isolated database migration to Alembic head `20260715_0001_birthday_and_anniversary_reminder`, verified `ReminderTypes`, `ReminderContacts`, `ReminderAcknowledgements`, required indexes, custom version table, empty starting row counts, and kept the parent Apps row `comingSoon` with version `null`.
* 2026-07-15: Implemented Birthday & Anniversary Reminder App #079 backend to Workflow Ready with isolated `BIRTHDAY_AND_ANNIVERSARY_REMINDER_DATABASE_URL`, owner-scoped `ReminderTypes`, `ReminderContacts`, and `ReminderAcknowledgements` tables, default reminder type seeding, protected reminder/type CRUD APIs, favourite/archive/restore/acknowledge actions, search/filter/sort support, dashboard and insights summaries, Alembic migration `20260715_0001_birthday_and_anniversary_reminder`, overview Explore routing to `/birthday-and-anniversary-reminder/reminders`, market-study/destination/story/marketing documentation, generated OpenAPI contracts, local migration validation, compileall verification, service smoke tests, production migration verification, and no production Apps row live promotion. The app remains `comingSoon` with `version = null`.
* 2026-07-15: Ran Packing Checklist App #078 production-configured isolated database migration to Alembic head `20260715_0001_packing_checklist`, verified `PackingCategories`, `PackingChecklists`, `PackingItems`, required indexes, custom version table, empty starting row counts, and kept the parent Apps row `comingSoon` with version `null`.
* 2026-07-15: Implemented Packing Checklist App #078 backend to Workflow Ready with isolated `PACKING_CHECKLIST_DATABASE_URL`, owner-scoped `PackingCategories`, `PackingChecklists`, and `PackingItems` tables, seeded packing categories, protected checklist/category/item CRUD APIs, duplicate/archive/restore actions, pack/unpack item actions, search/filter/sort support, dashboard and insights summaries, Alembic migration `20260715_0001_packing_checklist`, overview Explore routing to `/packing-checklist/checklists`, market-study/destination/story/marketing documentation, generated OpenAPI contracts, local migration validation, compileall verification, service smoke tests, production migration verification, and no production Apps row live promotion. The app remains `comingSoon` with `version = null`.
* 2026-07-15: Ran Emergency Contacts Organizer App #077 production-configured isolated database migration to Alembic head `20260715_0001_emergency_contacts_organizer`, verified `Categories`, `Contacts`, required indexes, custom version table, empty starting row counts, and kept the parent Apps row `comingSoon` with version `null`.
* 2026-07-15: Implemented Emergency Contacts Organizer App #077 backend to Workflow Ready with isolated `EMERGENCY_CONTACTS_ORGANIZER_DATABASE_URL`, owner-scoped `Categories` and `Contacts` tables, default category seeding, protected contact/category CRUD APIs, favourite/primary actions, search/filter/sort support, dashboard and insights summaries, Alembic migration `20260715_0001_emergency_contacts_organizer`, overview Explore routing to `/emergency-contacts-organizer/contacts`, market-study/destination/story/marketing documentation, generated OpenAPI contracts, local migration validation, compileall verification, service smoke tests, and no production Apps row live promotion. The app remains `comingSoon` with `version = null`.
* 2026-07-14: Promoted Household Expense Splitter App #076 backend to approved live version `1.0.0` after Astra/Partner approval, production Apps row promotion, destination metadata sync `20 / 100` approved on `2026-07-15`, overview metadata sync, production migration verification at `20260715_0001_household_expense_splitter`, tracked catalog export update, and production catalog verification at 75 live / 25 comingSoon.
* 2026-07-14: Implemented Household Expense Splitter App #076 backend to Workflow Ready with isolated `HOUSEHOLD_EXPENSE_SPLITTER_DATABASE_URL`, owner-scoped `Members`, `Expenses`, `ExpenseParticipants`, and `Settlements` tables, equal/manual split validation, member delete protection, expense archive/restore/delete APIs, settlement CRUD, search/filter/sort support, dashboard and insights summaries, Alembic migration `20260715_0001_household_expense_splitter`, overview Explore routing to `/household-expense-splitter/members`, market-study/destination/story/marketing documentation, generated OpenAPI contracts, local migration validation, compileall verification, and service smoke tests. The app remains `comingSoon` with no live promotion.
* 2026-07-14: Promoted Document Expiry Tracker App #073 backend to approved live version `1.0.0` after Astra/Partner approval, production Apps row promotion, destination metadata sync `20 / 100` approved on `2026-07-14`, overview metadata sync, production migration verification at `20260715_0001_document_expiry_tracker`, tracked catalog export update, and production catalog verification at 72 live / 28 comingSoon.
* 2026-07-14: Ran Document Expiry Tracker App #073 production-configured isolated database migration to Alembic head `20260715_0001_document_expiry_tracker`, verified `Documents`, required indexes, custom version table, empty starting row count, and kept the parent Apps row `comingSoon` with version `null`.
* 2026-07-14: Implemented Document Expiry Tracker App #073 backend to Workflow Ready with isolated `DOCUMENT_EXPIRY_TRACKER_DATABASE_URL`, owner-scoped `Documents` table, computed expiry statuses, create/edit/delete/archive/restore/renew APIs, dashboard and filter support, Alembic migration `20260715_0001_document_expiry_tracker`, overview Explore routing to `/document-expiry-tracker/documents`, market-study/destination/story/marketing documentation, generated OpenAPI contracts, local migration validation, compileall verification, and service smoke tests. The app remains `comingSoon` with no live promotion.
* 2026-07-14: Promoted EMI / Loan Calculator App #072 backend to approved live version `1.0.0` after Astra/Partner approval, production Apps row promotion, destination metadata sync `20 / 100` approved on `2026-07-14`, overview metadata sync, production migration verification at `20260714_0001_emi_loan_calculator`, tracked catalog export update, and production catalog verification at 71 live / 29 comingSoon.
* 2026-07-14: Ran EMI / Loan Calculator App #072 production-configured isolated database migration to Alembic head `20260714_0001_emi_loan_calculator`, verified `LoanScenarios`, required indexes, custom version table, empty starting row count, and kept the parent Apps row `comingSoon` with version `null`.
* 2026-07-14: Implemented EMI / Loan Calculator App #072 backend to Workflow Ready with isolated `EMI_LOAN_CALCULATOR_DATABASE_URL`, `LoanScenarios` model, Decimal-safe reducing-balance EMI calculations, zero-interest and extra-payment handling, dynamic amortization schedules, owner-scoped protected scenario CRUD, duplicate action, dashboard summaries, Alembic migration `20260714_0001_emi_loan_calculator`, overview Explore routing to `/emi-loan-calculator/calculator`, market-study/destination/story/marketing documentation, generated OpenAPI contracts, local migration validation, compileall verification, service smoke tests, and no production migration or Apps row live promotion.
* 2026-07-13: Promoted Subscription Manager App #071 backend to approved live version `1.0.0` after Astra/Partner approval, production Apps row promotion, destination metadata sync `20 / 100` approved on `2026-07-13`, overview metadata sync, production migration verification at `20260713_0001_subscription_manager`, tracked catalog export update, and production catalog verification at 70 live / 30 comingSoon.
* 2026-07-13: Synced Subscription Manager App #071 production overview metadata so both persisted `Explore` actions now route to `/subscription-manager/subscriptions`, verified the `overview:subscription-manager` row, and re-ran overview CTA validation.
* 2026-07-13: Ran Subscription Manager App #071 production-configured isolated database migration to Alembic head `20260713_0001_subscription_manager`, verified `SubscriptionManagerCategories`, `SubscriptionManagerSubscriptions`, `SubscriptionManagerRenewals`, required indexes, foreign keys, custom version table, empty starting row counts, and kept the parent Apps row `comingSoon` with version `null`.
* 2026-07-13: Implemented Subscription Manager App #071 backend to Workflow Ready with isolated `SUBSCRIPTION_MANAGER_DATABASE_URL`, `SubscriptionManagerCategories`, `SubscriptionManagerSubscriptions`, and `SubscriptionManagerRenewals` models, owner-scoped protected CRUD APIs, duplicate/pause/cancel subscription actions, manual renewal history, currency-separated dashboard insights, Alembic migration `20260713_0001_subscription_manager`, overview Explore routing to `/subscription-manager/subscriptions`, market-study/destination/story/marketing documentation, generated OpenAPI contracts, local migration validation, compileall verification, service smoke test, and no production migration or Apps row live promotion.
* 2026-07-13: Promoted School Administration App #070 backend to approved live version `1.0.0` after Astra/Partner approval, production Apps row promotion, destination metadata sync `20 / 100` approved on `2026-07-13`, overview metadata sync, production migration verification at `20260713_0001_school_administration`, tracked catalog export update, and production catalog verification at 69 live / 31 comingSoon.
* 2026-07-13: Ran School Administration App #070 production-configured isolated database migration to Alembic head `20260713_0001_school_administration`, verified `SchoolStudents`, `SchoolClasses`, `SchoolEnrollments`, `SchoolAttendance`, required indexes, foreign keys, unique constraints, empty starting row counts, and kept the parent Apps row `comingSoon` with version `null`.
* 2026-07-13: Implemented School Administration App #070 backend to Workflow Ready with isolated `SCHOOL_ADMINISTRATION_DATABASE_URL`, `SchoolStudents`, `SchoolClasses`, `SchoolEnrollments`, and `SchoolAttendance` models, owner-scoped protected CRUD APIs, explicit enrolment assignment/removal, duplicate student/class actions, attendance duplicate prevention, dashboard insights, Alembic migration `20260713_0001_school_administration`, overview Explore routing to `/school-administration/students`, market-study/destination/story/marketing documentation, generated OpenAPI contracts, local migration validation, compileall verification, and no production migration or Apps row live promotion.
* 2026-07-12: Promoted VAT Assistant UAE App #069 backend to approved live version `1.0.0` after Astra/Partner approval, production Apps row promotion, destination metadata sync `20 / 100` approved on `2026-07-12`, overview metadata sync, tracked catalog export update, production migration verification, and production catalog verification at 68 live / 32 comingSoon.
* 2026-07-12: Completed a read-only remote-state audit for VAT Assistant UAE App #069 and confirmed the production-configured isolated database had already been accidentally migrated early to Alembic head `20260712_0001_vat_assistant_uae`; verified `VATRegistrations`, `VATReturns`, `VATTransactions`, required indexes, foreign keys, empty starting row counts, no generic `alembic_version` table, and custom `vat_assistant_uae_alembic_version`.
* 2026-07-12: Implemented VAT Assistant UAE App #069 backend to Workflow Ready with isolated `VAT_ASSISTANT_UAE_DATABASE_URL`, `VATRegistrations`, `VATReturns`, and `VATTransactions` models, owner-scoped protected CRUD APIs, duplicate actions, deterministic dashboard insights, Alembic migration `20260712_0001_vat_assistant_uae`, overview Explore routing to `/vat-assistant-uae/registrations`, market-study/destination/story/marketing documentation, generated OpenAPI contracts, local migration validation, compileall verification, and no Apps row live promotion.
* 2026-07-12: Promoted Corporate Tax UAE App #068 backend to approved live version `1.0.0` after Astra/Partner approval, production Apps row promotion, destination metadata sync `20 / 100` approved on `2026-07-12`, overview metadata sync, tracked catalog export update, and production catalog verification at 67 live / 33 comingSoon.
* 2026-07-12: Ran Corporate Tax UAE App #068 production-configured isolated database migration to Alembic head `20260712_0001_corporate_tax_uae`, verified `CorporateTaxPeriods`, `CorporateTaxAdjustments`, `CorporateTaxObligations`, required indexes, foreign keys, empty starting row counts, and kept the parent Apps row `comingSoon` with version `null`.
* 2026-07-12: Implemented Corporate Tax UAE App #068 backend to Workflow Ready with isolated `CORPORATE_TAX_UAE_DATABASE_URL`, `CorporateTaxPeriods`, `CorporateTaxAdjustments`, and `CorporateTaxObligations` models, owner-scoped protected CRUD APIs, duplicate period, local complete obligation action, estimate-only dashboard insights, Alembic migration `20260712_0001_corporate_tax_uae`, overview Explore routing to `/corporate-tax-uae/tax-periods`, market-study/destination/story/marketing documentation, generated OpenAPI contracts, local migration validation, compileall verification, and no Apps row live promotion.
* 2026-07-12: Promoted Trip Cost Calculator App #067 backend to approved live version `1.0.0` after Astra/Partner approval, production Apps row promotion, destination metadata sync `22 / 100` approved on `2026-07-12`, overview metadata sync, browser workflow verification, tracked catalog update, and production catalog verification at 66 live / 34 comingSoon.
* 2026-07-12: Ran Trip Cost Calculator App #067 production-configured isolated database migration to Alembic head `20260712_0001_trip_cost_calculator`, verified `TripCostTrips`, `TripCostExpenses`, required indexes, foreign key, empty starting row counts, and kept the parent Apps row `comingSoon` with version `null`.
* 2026-07-12: Implemented Trip Cost Calculator App #067 backend to Workflow Ready with isolated `TRIP_COST_CALCULATOR_DATABASE_URL`, `TripCostTrips` and `TripCostExpenses` models, owner-scoped protected CRUD APIs, duplicate trip, comparison summaries, dashboard insights, Alembic migration `20260712_0001_trip_cost_calculator`, overview Explore routing to `/trip-cost-calculator/trips`, market-study/destination/story/marketing documentation, generated OpenAPI contracts, local migration validation, compileall verification, and no Apps row live promotion.
* 2026-07-12: Promoted Parking Expense Tracker App #066 backend to approved live version `1.0.0` after Astra/Partner approval, production Apps row promotion, destination metadata sync `22 / 100` approved on `2026-07-12`, overview metadata sync, browser workflow verification, tracked catalog update, and production catalog verification at 65 live / 35 comingSoon.
* 2026-07-12: Ran Parking Expense Tracker App #066 production-configured isolated database migration to Alembic head `20260712_0001_parking_expense_tracker`, verified `ParkingExpenseLocations`, `ParkingExpenseEntries`, required indexes, foreign key, empty starting row counts, and kept the parent Apps row `comingSoon` with version `null`.
* 2026-07-12: Implemented Parking Expense Tracker App #066 backend to Workflow Ready with isolated `PARKING_EXPENSE_TRACKER_DATABASE_URL`, `ParkingExpenseLocations` and `ParkingExpenseEntries` models, owner-scoped protected CRUD APIs, dashboard insights, Alembic migration `20260712_0001_parking_expense_tracker`, overview Explore routing to `/parking-expense-tracker/expenses`, market-study/destination/story/marketing documentation, generated OpenAPI contracts, local migration validation, compileall verification, and no Apps row live promotion.
* 2026-07-12: Promoted Vehicle Maintenance Tracker App #065 backend to approved live version `1.0.0` after Astra/Partner approval, production Apps row promotion, destination metadata sync `24 / 100` approved on `2026-07-12`, overview metadata validation, manual maintenance update bug-fix verification, tracked catalog export update, and production catalog verification at 64 live / 36 comingSoon.
* 2026-07-12: Ran Vehicle Maintenance Tracker App #065 production-configured isolated database migration to Alembic head `20260712_0001_vehicle_maintenance_tracker`, verified `VehicleMaintenanceVehicles`, `VehicleMaintenanceRecords`, `VehicleMaintenanceReminders`, required indexes, foreign keys, empty starting row counts, and kept the parent Apps row `comingSoon` with version `null`.
* 2026-07-12: Implemented Vehicle Maintenance Tracker App #065 backend to Workflow Ready with isolated `VEHICLE_MAINTENANCE_TRACKER_DATABASE_URL`, `VehicleMaintenanceVehicles`, `VehicleMaintenanceRecords`, and `VehicleMaintenanceReminders` models, owner-scoped protected CRUD APIs, duplicate vehicle, local complete reminder action, dashboard insights, Alembic migration `20260712_0001_vehicle_maintenance_tracker`, overview Explore routing to `/vehicle-maintenance-tracker/vehicles`, market-study/destination/story/marketing documentation, generated OpenAPI contracts, local migration validation, compileall verification, and no Apps row live promotion.
* 2026-07-12: Promoted Car Pool App #064 backend to approved live version `1.0.0` after Astra/Partner approval, production Apps row promotion, destination metadata sync `26 / 100` approved on `2026-07-12`, overview metadata validation, manual My Trips bug-fix verification, tracked catalog export update, and production catalog verification at 63 live / 37 comingSoon.
* 2026-07-12: Synced parent overview metadata for Car Pool App #064 so the primary and final `Explore` actions now serve `/car-pool/rides`, verified the persisted `overview:car-pool` record, and re-ran overview CTA validation.
* 2026-07-12: Ran Car Pool App #064 production-configured isolated database migration to Alembic head `20260712_0001_car_pool`, verified `CarPoolRides`, `CarPoolPassengers`, `CarPoolRequests`, required indexes, foreign keys, empty starting row counts, and kept the parent Apps row `comingSoon` with version `null`.
* 2026-07-12: Implemented Car Pool App #064 backend to Workflow Ready with isolated `CAR_POOL_DATABASE_URL`, `CarPoolRides`, `CarPoolPassengers`, and `CarPoolRequests` models, owner-scoped protected CRUD APIs, duplicate ride, local join/leave, request approve/reject actions, dashboard insights, Alembic migration `20260712_0001_car_pool`, overview Explore routing to `/car-pool/rides`, market-study/destination/story/marketing documentation, generated OpenAPI contracts, local migration validation, compileall verification, and no Apps row live promotion.
* 2026-07-11: Promoted Rent a Car App #063 backend to approved live version `1.0.0` after Astra/Partner approval, production Apps row promotion, destination metadata sync `28 / 100` approved on `2026-07-11`, overview metadata sync, tracked catalog export update, and production catalog verification at 62 live / 38 comingSoon.
* 2026-07-11: Ran Rent a Car App #063 production-configured isolated database migration to Alembic head `20260711_0001_rent_a_car`, verified `RentACarSearches`, `RentACarVehicleOptions`, `RentACarBookings`, required indexes, foreign keys, empty starting row counts, and kept the parent Apps row `comingSoon` with version `null`.
* 2026-07-11: Implemented Rent a Car App #063 backend to Workflow Ready with isolated `RENT_A_CAR_DATABASE_URL`, `RentACarSearches`, `RentACarVehicleOptions`, and `RentACarBookings` models, owner-scoped protected CRUD APIs, duplicate/preferred actions, deterministic dashboard insights, Alembic migration `20260711_0001_rent_a_car`, overview Explore routing to `/rent-a-car/searches`, market-study/destination/story/marketing documentation, generated OpenAPI contracts, production-configured migration verification, compileall verification, and no Apps row live promotion.
* 2026-07-11: Promoted Family Task Planner App #062 backend to approved live version `1.0.0` after Astra/Partner approval, production Apps row promotion, destination metadata sync `30 / 100` approved on `2026-07-11`, overview metadata sync, tracked catalog export update, and production catalog verification at 61 live / 39 comingSoon.
* 2026-07-11: Ran Family Task Planner App #062 production-configured isolated database migration to Alembic head `20260711_0001_family_task_planner`, verified `FamilyTaskMembers`, `FamilyTaskCategories`, `FamilyTasks`, required indexes, empty starting row counts, and kept the parent Apps row `comingSoon` with version `null`.
* 2026-07-11: Implemented Family Task Planner App #062 backend to Workflow Ready with isolated `FAMILY_TASK_PLANNER_DATABASE_URL`, `FamilyTaskMembers`, `FamilyTaskCategories`, and `FamilyTasks` models, owner-scoped protected CRUD APIs, task duplicate/complete/reopen actions, dashboard/calendar/insight summaries, Alembic migration `20260711_0001_family_task_planner`, overview Explore routing to `/family-task-planner/dashboard`, market-study/destination/story/marketing documentation, generated OpenAPI contracts, local migration validation, compileall verification, and no Apps row live promotion.
* 2026-07-11: Completed the market-informed destination refinement pass for Book Summary Generator, Client Feedback Analyzer, Job Description Analyzer, Social Caption Generator, and AI Translator and Tone Fixer by adding source-respectful comprehension, feedback-to-action review, explainable role-decoding, brand-safe caption drafting, meaning-preserving multilingual communication, non-goal, and governance-boundary details without changing approval status, Journey Progress, or review metadata.
* 2026-07-11: Continued market-informed destination refinement for File Optimizer, Creative Title Generator, QR Code Creator, Time Zone Scheduler, and LinkedIn Bio Optimizer by adding transparent optimization, honest title ideation, reliable static QR, deterministic time-zone clarity, truthful profile-positioning, non-goal, and governance-boundary details without changing approval status, Journey Progress, or review metadata.
* 2026-07-11: Continued market-informed destination refinement for Password Generator, Invoice and Receipt Maker, Clipboard Manager, Voice Converter, and Grammar and Paraphrasing Assistant by adding conservative secret-generation, deterministic billing-document, intentional clipboard-memory, ethical speech-preview, controlled-revision, non-goal, and governance-boundary details without changing approval status, Journey Progress, or review metadata.
* 2026-07-11: Continued market-informed destination refinement for Browser PDF Reader, Career Planner, Proposal Writer, Markdown Editor, and Price Checker by adding source-grounded reading, user-owned career strategy, scope-clarity proposal, portable Markdown ownership, price-source transparency, non-goal, and governance-boundary details without changing approval status, Journey Progress, or review metadata.
* 2026-07-11: Continued market-informed destination refinement for Meeting Minutes AI, Email Assistant, Formula Finder, API Tester, and Presentation Designer by adding source-traceability, send-safety, formula-applicability, secret-handling, narrative-review, non-goal, and governance-boundary details without changing approval status, Journey Progress, or review metadata.
* 2026-07-11: Continued market-informed destination refinement for AI Job Interviewer, Portfolio Creator, Quiz, Contract Generator, and JSON Formatter by adding ethical-simulation, proof-of-work, question-quality, legal-draft, browser-local-privacy, non-goal, and governance-boundary details without changing approval status, Journey Progress, or review metadata.
* 2026-07-11: Continued market-informed destination refinement for Resume Builder, Research Assistant, Visiting Card Maker, Smart Textbook Scanner, and Interview Coach by adding resume-truth, evidence-first-research, card-scanability, source-fidelity, interview-feedback, non-goal, and governance-boundary details without changing approval status, Journey Progress, or review metadata.
* 2026-07-11: Continued market-informed destination refinement for Lesson Builder, Prompt Builder, Snippet Generator, Study Planner, and Speech Writer by adding educator-review, prompt-privacy, snippet-trust, study-recovery, speech-authenticity, non-goal, and governance-boundary details without changing approval status, Journey Progress, or review metadata.
* 2026-07-11: Continued market-informed destination refinement for Course Tracker, Job Tracker, Eco Habit Tracker, AI Notes Summarizer, and Memory Trainer by adding market-supported learning-ledger, job-search-momentum, eco-impact-transparency, source-linked-summary, active-recall, non-goal, and governance-boundary details without changing approval status, Journey Progress, or review metadata.
* 2026-07-11: Continued market-informed destination refinement for Dictionary+, Daily Word Challenge, Concept Explainer, Interview Scheduler, and Mood Journal by adding market-supported source-authority, originality, guided-learning, time-zone/candidate-experience, mood-privacy, non-goal, and opt-in AI/integration boundaries without changing approval status, Journey Progress, or governance metadata.
* 2026-07-11: Continued market-informed destination refinement for Medicine Reminder, Health Report Organizer, Wellness and Goal Planner, Task Prioritizer, and Project Tracker by tightening target-user, problem, advanced-capability, success, non-goal, AI/privacy, and guiding-principle details from their market studies without changing approval status, Journey Progress, or governance metadata.
* 2026-07-11: Refined market-informed destination strategy for Expense Tracker, Fitness Tracker, Goal Tracker, Language Learning Buddy, and Meal Planner by adding mature product vision, target-user, problem, retention, success, future-boundary, and guiding-principle details from their market studies without changing approval status, Journey Progress, or governance metadata.
* 2026-07-11: Promoted Health Report Organizer App #061 backend to approved live version `1.0.0` after Astra/Partner approval, production Apps row promotion, destination metadata sync `24 / 100` approved on `2026-07-11`, overview metadata sync, tracked catalog export update, and production catalog verification at 60 live / 40 comingSoon.
* 2026-07-11: Ran Health Report Organizer App #061 production-configured isolated database migration to Alembic head `20260711_0001_health_report_organizer`, verified `HealthReportCategories`, `HealthReportFacilities`, `HealthReports`, `HealthReportAttachments`, `HealthReportNotes`, required indexes, empty starting row counts, and kept the parent Apps row `comingSoon` with version `null`.
* 2026-07-11: Implemented Health Report Organizer App #061 backend to Workflow Ready with isolated `HEALTH_REPORT_ORGANIZER_DATABASE_URL`, reports/categories/facilities/attachments/notes models, owner-scoped protected CRUD APIs, dashboard summaries, Alembic migration `20260711_0001_health_report_organizer`, overview Explore routing to `/health-report-organizer/reports`, market-study/destination/story/marketing documentation, generated OpenAPI contracts, local migration validation, compileall verification, and no Apps row live promotion.
* 2026-07-11: Promoted Medicine Reminder App #060 backend to approved live version `1.0.0` after Astra/Partner approval, production Apps row promotion, destination metadata sync `32 / 100` approved on `2026-07-11`, overview metadata sync, tracked catalog export update, and production catalog verification at 59 live / 41 comingSoon.
* 2026-07-11: Synced Medicine Reminder App #060 overview metadata so the primary and final `Explore` actions route to `/medicine-reminder/medicines`, verified the persisted metadata record, and kept the parent Apps row `comingSoon` with version `null`.
* 2026-07-11: Ran Medicine Reminder App #060 production-configured isolated database migration to Alembic head `20260711_0001_medicine_reminder`, verified `MedicineReminderMedicines`, `MedicineReminderSchedules`, `MedicineReminderDoseLogs`, `MedicineReminderNotes`, required indexes, empty starting row counts, and kept the parent Apps row `comingSoon` with version `null`.
* 2026-07-11: Implemented Medicine Reminder App #060 backend to Workflow Ready with isolated `MEDICINE_REMINDER_DATABASE_URL`, `MedicineReminderMedicines`, `MedicineReminderSchedules`, `MedicineReminderDoseLogs`, and `MedicineReminderNotes` models, owner-scoped protected CRUD APIs, dashboard summaries, Alembic migration `20260711_0001_medicine_reminder`, overview Explore routing to `/medicine-reminder/medicines`, market-study/destination/story/marketing documentation, generated OpenAPI contracts, local migration validation, compileall verification, and no Apps row live promotion.
* 2026-07-10: Promoted Language Learning Buddy App #058 backend to approved live version `1.0.0` after Astra/Partner approval, production Apps row promotion, destination metadata sync `35 / 100` approved on `2026-07-10`, overview metadata sync, tracked catalog export update, and production catalog verification at 58 live / 42 comingSoon.
* 2026-07-10: Ran Language Learning Buddy App #058 production-configured isolated database migration to Alembic head `20260710_0001`, verified `LanguageVocabulary`, `LanguagePracticeSessions`, required indexes, empty starting row counts, and kept the parent Apps row `comingSoon` with version `null`.
* 2026-07-10: Implemented Language Learning Buddy App #058 backend to Workflow Ready with isolated `LANGUAGE_LEARNING_BUDDY_DATABASE_URL`, `LanguageVocabulary` and `LanguagePracticeSessions` models, owner-scoped protected CRUD APIs, dashboard summaries, Alembic migration `20260710_0001_add_language_learning_buddy_tables.py`, overview CTA metadata, market-study/destination/story/marketing documentation, generated OpenAPI contracts, local migration/CRUD validation, and no Apps row live promotion.
* 2026-07-10: Promoted Fitness Tracker App #043 backend to approved live version `1.0.0` after Astra/Partner approval, production Apps row promotion, destination metadata sync, isolated database migration verification, overview metadata sync, tracked catalog export update, and production catalog verification at 57 live / 43 comingSoon.
* 2026-07-10: Ran Fitness Tracker App #043 production-configured isolated database migration to Alembic head `20260710_0001`, verified `FitnessActivities`, `FitnessLogs`, required indexes, and empty starting row counts while keeping the parent Apps row `comingSoon` with version `null`.
* 2026-07-10: Implemented Fitness Tracker App #043 backend to Workflow Ready with isolated `FITNESS_TRACKER_DATABASE_URL`, `FitnessActivities` and `FitnessLogs` models, owner-scoped protected CRUD APIs, dashboard summaries, Alembic migration `20260710_0001_add_fitness_tracker_tables.py`, overview CTA metadata, market-study/destination/story/marketing documentation, generated OpenAPI contracts, and no Apps row live promotion.
* 2026-07-10: Promoted Meal Planner App #042 backend to approved live version `1.0.0` after Astra/Partner approval, production legacy schema/FK repair, Apps row promotion, destination metadata sync, overview metadata sync, tracked catalog export update, and production catalog verification at 56 live / 44 comingSoon.
* 2026-07-10: Added Meal Planner migration `20260710_0004` to rebuild `MealPlanEntries` after the legacy `MealPlans` repair so calendar entries reference the current `MealPlans` table instead of the removed legacy table.
* 2026-07-10: Added Meal Planner migration `20260706_0003` to rebuild legacy production `MealPlans` tables to the current weekly-plan schema, preserving existing plan fields and removing hidden required legacy columns that blocked meal plan creation.
* 2026-07-10: Added the permanent Marketing Framework Documentation Contract so every future Ansiversa app and the parent platform require `market-study.md`, `destination.md`, `story.md`, and frozen-structure `marketing.md` before documentation completion.
* 2026-07-06: Implemented Meal Planner App #042 backend to Workflow Ready with isolated `MEAL_PLANNER_DATABASE_URL`, `Recipes`, `MealPlans`, and `MealPlanEntries` models, owner-scoped protected CRUD APIs, paginated/searchable list endpoints, Alembic migration `20260706_0001_add_meal_planner_tables.py`, overview CTA metadata, story/destination/market-study documentation, generated OpenAPI schema, and no Apps row live promotion.
* 2026-07-05: Added the permanent Market Study Documentation Contract so every future mini-app creates backend `market-study.md` during initial development alongside `story.md` and `destination.md`.
* 2026-07-05: Promoted Goal Tracker App #055 backend to approved live version `1.0.0` after Astra/Partner approval, production Apps row promotion, destination metadata sync, isolated database verification, overview metadata sync, tracked catalog export update, and production catalog verification at 55 live / 45 comingSoon.
* 2026-07-05: Added the permanent Ansiversa 101 Principle limiting the ecosystem to 1 Platform plus 100 Solution Apps, shifting post-100 backend/API work from new app creation to strengthening quality, workflows, performance, retention, and justified replacement only.
* 2026-07-05: Implemented Goal Tracker App #055 backend to Workflow Ready with isolated `GOAL_TRACKER_DATABASE_URL`, `GoalTrackerGoals`, `GoalTrackerMilestones`, and `GoalTrackerCheckIns` models, owner-scoped protected APIs, duplicate support, Alembic migration `20260705_0001_goal_tracker`, overview CTA metadata, story/destination documentation, compileall verification, generated OpenAPI schema, and no Apps row live promotion.
* 2026-07-05: Synced backend catalog references to finalized Apps table export `Apps_202607051332.json`, replaced the tracked `apps.json` export, aligned destination metadata validation with Apps table field names, and removed stale Cover Letter Writer active-roadmap references.
* 2026-07-05: Promoted Wellness and Goal Planner App #054 to approved live version `1.0.0` after Astra/Partner approval, production Apps row promotion, destination metadata sync, isolated database migration verification, Notes persistence verification, tracked catalog export update, and production catalog verification at 54 live / 46 comingSoon.
* 2026-07-05: Fixed Wellness and Goal Planner App #054 reflection Notes persistence with isolated migration `20260705_0002_wellness_reflection_body`, separate reflection body storage, service round-trip verification, and no Apps row live promotion.
* 2026-07-05: Implemented Wellness and Goal Planner App #054 backend to Workflow Ready with isolated `WELLNESS_AND_GOAL_PLANNER_DATABASE_URL`, `WellnessAreas`, `WellnessGoals`, and `WellnessReflections` models, owner-scoped protected APIs, Alembic migration `20260705_0001`, overview CTA metadata, story/destination documentation, compileall verification, generated OpenAPI schema, and no Apps row live promotion.
* 2026-07-04: Added a non-sensitive readable `ansiversa_has_session` auth hint cookie alongside the HttpOnly `ansiversa_session` cookie so browser clients can skip `/api/v1/auth/me` on clear guest loads while clearing both cookies on logout.
* 2026-07-04: Promoted Task Prioritizer App #052 to approved live version `1.0.0` after Astra/Partner approval, updating and re-reading the production parent Apps row as `active` / `live` / `1.0.0`, syncing destination metadata `45 / 100` approved on `2026-07-04`, updating the tracked catalog export, and verifying 52 live apps / 48 comingSoon apps with no version-rule violations.
* 2026-07-04: Migrated and verified the production Task Prioritizer App #052 Turso database at revision `20260704_0001`, confirming `TaskPrioritizerTasks`, `TaskPrioritizerTaskPriorities`, `TaskPrioritizerPriorityRules`, `TaskPrioritizerPriorityHistory`, and required query-pattern indexes; kept the parent Apps row unpromoted pending explicit Live approval.
* 2026-07-04: Implemented Task Prioritizer App #052 backend to Workflow Ready with isolated `TASK_PRIORITIZER_DATABASE_URL`, task/priority/rule/history models, owner-scoped protected APIs, local priority scoring, Alembic migration `20260704_0001`, overview CTA metadata, story/destination documentation, compileall verification, local migration, and no Apps row live promotion.
* 2026-07-04: Promoted Project Tracker to approved live version `1.0.0` as the 51st live developed app with production Apps row promotion, destination metadata `58 / 100` approved on `2026-07-04`, catalog export sync, production API verification, overview CTA validation, and canonical roadmap identity preserved as item 49 while Expense Tracker remains item 51.
* 2026-07-04: Hardened the overview Explore CTA contract with `validate_overview_ctas`, explicit checklist wording, first-workflow route validation against frontend `APP_MODULE_PAGES`, corrected stale workflow-ready overview metadata, and synced all 100 overview metadata records.
* 2026-07-04: Corrected Project Tracker to the expected DB-backed Workflow Ready V1 with isolated `PROJECT_TRACKER_DATABASE_URL` runtime, `ProjectTrackerProjects` and `ProjectTrackerTasks` models, protected owner-scoped APIs, Alembic migration `20260704_0001`, overview/story/destination documentation, and preserved canonical roadmap numbering so Project Tracker remains item 49 and Expense Tracker remains item 51; no Apps row live promotion was added.

* 2026-07-03: Added permanent Destination Metadata Promotion, Destination-First Development, and Journey Progress Update rules so App #051 and future apps follow the complete Destination Framework lifecycle.

* 2026-07-03: Completed Milestone Review #4 Product Maturity Management by adding destination metadata governance, Apps table destination fields, approved live-app destination progress sync, and minimal public API exposure without starting App #051.

* 2026-07-02: Promoted Price Checker App #050 to approved live version `1.0.0` after Partner/Astra approval, production parent Apps row promotion, overview metadata sync, tracked catalog export update, and production catalog verification at 50 live / 50 comingSoon, with no shopping APIs, scraping, backend runtime storage, price alerts, background jobs, cloud sync, or app runtime database added; App #051 remains unstarted for Milestone Review #3 freeze.
* 2026-07-02: Updated Price Checker App #050 overview metadata, route-aligned catalog export fields, and backend story documentation for the browser-local Workflow Ready V1 while keeping the app active/comingSoon/version null; no shopping APIs, scraping, backend runtime, price alerts, background jobs, cloud sync, app runtime database, or live promotion was added.
* 2026-07-02: Promoted Browser PDF Reader App #049 to approved live version `1.0.0` after Partner/Astra approval, production parent Apps row promotion, overview metadata sync, tracked catalog export update, and production catalog verification at 49 live / 51 comingSoon, with no backend PDF upload, PDF storage, OCR, AI analysis, annotation sync, cloud storage, or app runtime database added.
* 2026-07-02: Updated Browser PDF Reader App #049 overview metadata, route-aligned catalog export fields, and backend story documentation for the browser-local Workflow Ready V1 while keeping the app active/comingSoon/version null; no backend PDF upload, PDF storage, OCR, AI analysis, annotation sync, cloud storage, app runtime database, or live promotion was added.
* 2026-07-02: Promoted Time Zone Scheduler App #048 to approved live version `1.0.0` after Partner/Astra approval, production parent Apps row promotion, overview metadata sync, tracked catalog export update, and production catalog verification at 48 live / 52 comingSoon, with no backend scheduling, notifications, invitations, calendar sync, schedule storage, cloud synchronization, or app runtime database added.
* 2026-07-02: Updated Time Zone Scheduler App #048 overview metadata and backend story documentation for the browser-local Workflow Ready V1 while keeping the app active/comingSoon/version null; no backend scheduling, notifications, invitations, calendar sync, schedule storage, app runtime database, or live promotion was added.
* 2026-07-02: Promoted API Tester App #047 to approved live version `1.0.0` after Partner/Astra approval, production parent Apps row promotion, overview metadata sync, tracked catalog export update, and production catalog verification at 47 live / 53 comingSoon, with no backend proxy, server-side execution route, request-content storage, or app runtime database added.
* 2026-07-02: Updated API Tester App #047 overview metadata for the browser-local request testing Workflow Ready V1 and added backend story documentation; no backend proxy, server-side execution route, request-content storage, app runtime database, or live promotion was added.

* 2026-07-02: Promoted Voice Converter App #046 to approved live version `1.0.0` after Partner/Astra approval, production parent Apps row promotion, overview metadata sync, tracked catalog export update, and production catalog verification at 46 live / 54 comingSoon, with no backend text storage, audio persistence, cloud TTS integration, or app runtime database added.

* 2026-07-02: Added the permanent Mini App Catalog Identity Rule so Apps catalog name, key, slug, logo key, category, and route identity remain the source of truth before development or promotion, preventing stale aliases such as File Compressor or Text-to-Speech Converter from creating contract drift.

* 2026-07-02: Updated Voice Converter App #046 overview metadata for the browser-native text-to-speech Workflow Ready V1 and added backend story documentation; no backend text storage, audio persistence, cloud TTS integration, database runtime, or live promotion was added.

* 2026-07-02: Promoted File Optimizer App #045 to approved live version `1.0.0` after Partner/Astra approval, production parent Apps row promotion, overview metadata sync, tracked catalog export update, and production catalog verification at 45 live / 55 comingSoon, with no backend file upload, compression runtime, or file-content persistence added.

* 2026-07-02: Updated File Optimizer App #045 overview metadata for the frontend-local V1 metadata-only compression estimate workflow and added backend story documentation; no backend file upload, compression runtime, database persistence, or live promotion was added.

* 2026-07-02: Updated Clipboard Manager App #044 live overview metadata so primary and final CTA buttons use `Explore`, then synced `overview:clipboard-manager` to production while keeping `/clipboard-manager/workspace` routing and local-only V1 behavior unchanged.

* 2026-07-02: Promoted Clipboard Manager App #044 to approved live version `1.0.0` after Partner/Astra approval, production parent Apps row promotion, overview metadata sync, tracked catalog export update, and production catalog verification at 44 live / 56 comingSoon, with no backend clipboard-content persistence added.

* 2026-07-02: Synced Clipboard Manager App #044 overview metadata to the frontend-local V1 workflow with CTA routing to `/clipboard-manager/workspace`, local-only privacy messaging, FAQ content, and no backend clipboard-content persistence or live promotion.

* 2026-07-02: Promoted Creative Title Generator App #043 to approved live version `1.0.0` after Partner/Astra approval, production App #043 database migration to revision `20260702_0002`, production parent Apps row promotion, overview metadata sync, tracked catalog export update, and production catalog verification at 43 live / 57 comingSoon.

* 2026-07-02: Reviewed Creative Title Generator App #043 Workflow Ready backend scope, confirming protected owner-scoped APIs, generated schema coverage, isolated Alembic head `20260702_0002`, local create/generate/history/delete smoke behavior, compileall, and diff whitespace checks; no production migration or live promotion was run.

* 2026-07-02: Added Creative Title Generator App #043 backend foundation with isolated database configuration, `TitleProjects`, `GeneratedTitles`, and `TitleJobs` models/migration, owner-scoped protected APIs, deterministic V1 title generation service, overview metadata, and backend story documentation; no production migration or live promotion was run.

* 2026-07-02: Promoted Grammar and Paraphrasing Assistant App #042 to approved live version `1.0.0` after Partner/Astra approval, production App #042 database migration to revision `20260702_0001`, production parent Apps row promotion, overview metadata sync, tracked catalog export update, and production catalog verification at 42 live / 58 comingSoon.

* 2026-07-02: Added Grammar and Paraphrasing Assistant App #042 backend foundation with isolated database configuration, `GrammarProjects`, `GrammarResults`, and `GrammarJobs` models/migration, owner-scoped protected APIs, placeholder V1 generation service, overview metadata sync, and backend story documentation; no live promotion was run.

* 2026-07-02: Added protected `/api/v1/dashboard/summary` for the platform dashboard, returning only total/live/comingSoon/category/progress counts from the parent Apps and Categories tables so dashboard clients do not reuse the heavier Apps catalog payload.

* 2026-07-01: Updated and re-read the production parent Apps row for AI Translator and Tone Fixer App #041 from `active` / `comingSoon` / `version = NULL` to `active` / `live` / `version = 1.0.0`, verified 41 live apps and 59 comingSoon apps, confirmed no Apps version-rule violations, synced the tracked catalog export, and updated story metadata after Partner/Astra approval.

* 2026-07-01: Migrated and verified the production AI Translator and Tone Fixer Turso database at revision `20260701_0001`, confirming `TranslationProjects`, `Translations`, `TranslationTemplates`, `TranslationHistory`, required indexes, and CRUD create/update/delete cleanup behavior; kept the app `active` / `comingSoon` / `version = NULL` with no live promotion.

* 2026-07-01: Added AI Translator and Tone Fixer App #041 backend foundation with isolated database configuration, owner-scoped CRUD APIs for projects, translations, templates, and history, dashboard/detail response contracts, router registration, Alembic migration, overview metadata sync, local migration/schema/index/CRUD verification, and comingSoon story notes; no live promotion was run.

* 2026-07-01: Documented the App #041 onward backend route export convention so `router.py` owns endpoint definitions and `routes.py` re-exports `router` for existing `app.main` compatibility; no backend runtime behavior, migrations, production data, or app promotion changed.

* 2026-07-01: Updated and re-read the production parent Apps row for Snippet Generator App #040 from `active` / `comingSoon` / `version = NULL` to `active` / `live` / `version = 1.0.0`, verified 40 live apps and 60 comingSoon apps, confirmed no Apps version-rule violations, synced the tracked catalog export, and updated story metadata after Partner/Astra approval.

* 2026-07-01: Updated and re-read the production parent Apps row for Prompt Builder App #039 from `active` / `comingSoon` / `version = NULL` to `active` / `live` / `version = 1.0.0`, verified 39 live apps and 61 comingSoon apps, confirmed no Apps version-rule violations, synced the tracked catalog export, and updated story metadata after Partner/Astra approval.

* 2026-07-01: Updated and re-read the production parent Apps row for Speech Writer App #038 from `active` / `comingSoon` / `version = NULL` to `active` / `live` / `version = 1.0.0`, verified 38 live apps and 62 comingSoon apps, confirmed no Apps version-rule violations, synced the tracked catalog export, and updated story metadata after Partner/Astra approval.

* 2026-07-01: Updated and re-read the production parent Apps row for Social Caption Generator App #037 from `active` / `comingSoon` / `version = NULL` to `active` / `live` / `version = 1.0.0`, verified 37 live apps and 63 comingSoon apps, confirmed no Apps version-rule violations, synced the tracked catalog export, and updated story metadata after Partner/Astra approval.

* 2026-07-01: Updated and re-read the production parent Apps row for Job Description Analyzer App #035 from `active` / `comingSoon` / `version = NULL` to `active` / `live` / `version = 1.0.0`, verified 36 live apps and 64 comingSoon apps, confirmed no Apps version-rule violations, synced the tracked catalog export, and updated story metadata after Partner/Astra approval.
* 2026-07-01: Migrated the production Job Description Analyzer Turso database to revision `20260630_0001`, creating `JobDescriptions`, `JobAnalyses`, `SkillMatches`, `AnalysisHistory`, and `job_description_analyzer_alembic_version`; verified production indexes and Vercel environment configuration, and kept the app `active` / `comingSoon` / `version = NULL` for manual QA.
* 2026-07-01: Updated and re-read the production parent Apps row for Book Summary Generator App #036 from `active` / `comingSoon` / `version = NULL` to `active` / `live` / `version = 1.0.0`, verified 35 live apps and 65 comingSoon apps, confirmed no Apps version-rule violations, synced the tracked catalog export, and updated story metadata after Partner/Astra approval.
* 2026-07-01: Updated and re-read the production parent Apps row for Job Tracker App #034 from `active` / `comingSoon` / `version = NULL` to `active` / `live` / `version = 1.0.0`, verified 34 live apps and 66 comingSoon apps, confirmed no Apps version-rule violations, synced the tracked catalog export, and updated the public overview/story metadata after Partner/Astra approval.
* 2026-07-01: Updated and re-read the production parent Apps row for Interview Scheduler App #033 from `active` / `comingSoon` / `version = NULL` to `active` / `live` / `version = 1.0.0`, verified 33 live apps and 67 comingSoon apps, confirmed no Apps version-rule violations, and synced the tracked catalog export after Partner/Astra approval.
* 2026-07-01: Added the combined Apps catalog endpoint for `/api/v1/apps/catalog`, returning apps, categories, and launch-status counts from one active catalog dataset while preserving the existing apps and categories endpoints.
* 2026-07-01: Updated and re-read the production parent Apps row for Client Feedback Analyzer App #032 from `active` / `comingSoon` / `version = NULL` to `active` / `live` / `version = 1.0.0`, verified 32 live apps and 68 comingSoon apps, confirmed no Apps version-rule violations, and synced the tracked catalog export.
* 2026-07-01: Strengthened the live-promotion rule so Partner/Astra-approved promotion requests must update and re-read the production parent Apps table before live status, counts, catalog sync, or next-app handoff are reported.
* 2026-07-01: Updated and re-read the production parent Apps row for LinkedIn Bio Optimizer App #031 from `active` / `comingSoon` / `version = NULL` to `active` / `live` / `version = 1.0.0`, verified 31 live apps and 69 comingSoon apps, and confirmed no Apps version-rule violations.
* 2026-07-01: Promoted LinkedIn Bio Optimizer App #031 in the tracked catalog export to `active` / `live` / version `1.0.0` after Partner/Astra approval and documented V1 versions as immutable snapshots.
* 2026-06-30: Completed App #040 milestone factory inspection Phase 1 for the backend, added the milestone report, tightened Apps #032-#034 update DTOs/services so create-only parent IDs are excluded from update payloads, and kept Apps #031-#040 comingSoon without production migration or live promotion.
* 2026-06-30: Migrated the production Snippet Generator Turso database to revision `20260630_0001`, creating `SnippetProjects`, `SnippetCategories`, `SnippetLibrary`, `SnippetHistory`, and `snippet_generator_alembic_version`; verified production indexes, CRUD create/update/delete cleanup behavior, overview metadata sync, and kept the app `active` / `comingSoon` / `version = NULL`.
* 2026-06-30: Added Snippet Generator App #040 backend foundation with isolated database configuration, owner-scoped CRUD APIs for projects, snippets, categories, and history, dashboard/detail response contracts, router registration, Alembic migration, overview metadata sync, local migration/schema/index/CRUD verification, and coming-soon story notes; no production migration or live promotion was run.
* 2026-06-30: Migrated the production Prompt Builder Turso database to revision `20260630_0001`, preserving the legacy `PromptTemplates` table as `PromptTemplatesLegacy_20260630`; verified production tables, indexes, CRUD create/update/delete cascade behavior, overview metadata, and kept the app `active` / `comingSoon` / `version = NULL`.
* 2026-06-30: Added Prompt Builder App #039 backend foundation with isolated database configuration, owner-scoped CRUD APIs for projects, prompts, templates, and history, dashboard/detail response contracts, router registration, Alembic migration, overview metadata, local migration verification, and coming-soon story notes; no live promotion was run.
* 2026-06-30: Migrated the production Speech Writer Turso database to revision `20260630_0001`, preserving the legacy `Speeches` table as `SpeechesLegacy_20260630`; verified production tables, indexes, CRUD create/update/delete cascade behavior, overview metadata sync, and kept the app `active` / `comingSoon` / `version = NULL`.
* 2026-06-30: Added Speech Writer App #038 backend foundation with repository/service architecture, isolated database configuration, owner-scoped CRUD APIs for projects, speeches, templates, and history, dashboard/detail response contracts, router registration, Alembic migration, overview metadata, local migration verification, and coming-soon story notes; no production migration was completed and no live promotion was run.
* 2026-06-30: Migrated the production Social Caption Generator Turso database to isolated Alembic head `20260630_0002`, creating `CaptionProjects`, `SocialCaptions`, corrected `CaptionTemplates`, `CaptionHistory`, and `social_caption_generator_alembic_version`; preserved the legacy template table as `CaptionTemplatesLegacy_20260630`, verified production indexes, CRUD create/update/delete cascade behavior, overview metadata sync, and kept the app `active` / `comingSoon` / `version = NULL`.
* 2026-06-30: Added Social Caption Generator App #037 backend foundation with repository/service architecture, isolated database configuration, owner-scoped CRUD APIs for projects, captions, templates, and history, dashboard/detail response contracts, router registration, Alembic migration, overview metadata, and coming-soon story notes; no production migration was run.
* 2026-06-30: Migrated the production Book Summary Generator Turso database to revision `20260630_0001`, creating `BookCollections`, `BookSummaries`, `SummaryNotes`, `SummaryHistory`, and `book_summary_generator_alembic_version`; verified production indexes, CRUD create/update/delete cascade behavior, Vercel environment configuration, overview metadata sync, and kept the app `active` / `comingSoon` / `version = NULL`.
* 2026-06-30: Added Book Summary Generator App #036 backend foundation with repository/service architecture, isolated database configuration, owner-scoped CRUD APIs for books, summaries, notes, and history, dashboard/detail response contracts, router registration, Alembic migration, overview metadata, and coming-soon story notes; no production migration was run.
* 2026-06-30: Added Job Description Analyzer App #035 backend foundation with repository/service architecture, isolated database configuration, owner-scoped CRUD APIs for job descriptions, analysis, skill matches, and history, dashboard/detail response contracts, router registration, Alembic migration, overview metadata, and coming-soon story notes; no production migration was run.
* 2026-06-30: Migrated the production Job Tracker Turso database to revision `20260630_0001`, creating `JobListings`, `JobApplications`, `ApplicationInsights`, `ApplicationHistory`, and `job_tracker_alembic_version`; also set the production Vercel `JOB_TRACKER_DATABASE_URL` and `TURSO_AUTH_TOKEN` values needed by the deployed API.
* 2026-06-30: Added Job Tracker V1 backend foundation with repository/service architecture, isolated database configuration, owner-scoped CRUD APIs for jobs/applications/insights/history, dashboard/detail response contracts, router registration, Alembic migration, overview metadata, and coming-soon story notes; no production migration was run.
* 2026-06-30: Completed the App #031-#033 rule audit cleanup by aligning LinkedIn Bio Optimizer overview metadata to enter `/linkedin-bio-optimizer/bios` and expanding its backend story to the full current-implementation contract.
* 2026-06-30: Migrated the production Interview Scheduler Turso database to revision `20260630_0001`, creating `InterviewSchedules`, `InterviewRounds`, `InterviewCalendarEvents`, `InterviewHistory`, and `interview_scheduler_alembic_version`.
* 2026-06-30: Added Interview Scheduler V1 backend foundation with isolated database configuration, owner-scoped CRUD APIs for schedules/rounds/calendar/history, dashboard/detail response contracts, router registration, Alembic migration, overview metadata, and coming-soon story notes; no production migration was run.
* 2026-06-30: Migrated the production Client Feedback Analyzer Turso database to revision `20260630_0001`, creating `ClientProfiles`, `ClientFeedback`, `FeedbackInsights`, `FeedbackReports`, and `client_feedback_analyzer_alembic_version`.
* 2026-06-30: Added Client Feedback Analyzer V1 backend foundation with isolated database configuration, owner-scoped CRUD APIs for clients/feedback/insights/reports, summary/detail schemas, router registration, Alembic migration, and coming-soon story notes.
* 2026-06-30: Migrated the production LinkedIn Bio Optimizer Turso database to revision `20260630_0001`, creating `LinkedInProfiles`, `BioTemplates`, `BioVersions`, and `linkedin_bio_optimizer_alembic_version`.
* 2026-06-30: Added LinkedIn Bio Optimizer V1 backend foundation with isolated database configuration, owner-scoped CRUD APIs for profiles/templates/versions, summary/detail schemas, router registration, Alembic migration, and coming-soon story notes.
* 2026-06-30: Canonicalized LinkedIn Bio Optimizer to `linkedin-bio-optimizer` before App #031 development by aligning the production parent Apps row, catalog export id/slug/website/logo fields, and overview metadata references.
* 2026-06-30: Promoted Invoice and Receipt Maker App #027 in the production parent Apps table with `launchStatus = live` and version `1.0.0` after Astra review, production schema verification, end-to-end workflow verification, and Partner approval.
* 2026-06-29: Promoted Presentation Designer App #029 in the parent Apps table with `launchStatus = live` and version `1.0.0` after review edit support and Partner/Astra approval, bringing live mini-apps to 29.
* 2026-06-29: Added Presentation Designer review history detail and update API support with owner-scoped service methods, update DTOs that keep the optional project association create-only, regenerated frontend API types, and refreshed backend story documentation.
* 2026-06-29: Promoted Career Planner App #030 in the parent Apps table with `launchStatus = live` and version `1.0.0` after review edit support and Partner approval, bringing live mini-apps to 28.
* 2026-06-29: Added Career Planner review history detail and update API support with owner-scoped service methods, update DTOs that keep the optional goal association create-only, regenerated frontend API types, and refreshed backend story documentation.
* 2026-06-29: Promoted Contract Generator App #028 in the parent Apps table with `launchStatus = live` and version `1.0.0` after Astra review, production migration verification, end-to-end workflow verification, and Partner approval, bringing live mini-apps to 27.
* 2026-06-29: Corrected production parent catalog and overview metadata for Apps #027-#030 by aligning Invoice and Receipt Maker to the implemented `invoice-receipt-maker` slug, syncing overview records so CTAs use `Explore` and enter workflow routes, and removing the stale `overview:invoice-and-receipt-maker` metadata key.
* 2026-06-28: Refined the final live-app story backfill batch for Email Assistant with implementation-specific backend database, API, preview/detail response, performance, and limitation details, completing the live-app story refinement pass.
* 2026-06-28: Refined the sixth live-app story backfill batch for Formula Finder, Mood Journal, Eco Habit Tracker, and AI Job Interviewer with implementation-specific backend catalog boundaries, database/API details, performance, and limitation details.
* 2026-06-28: Refined the fifth live-app story backfill batch for QR Code Creator, Password Generator, JSON Formatter, and Markdown Editor with implementation-specific backend catalog boundaries, browser-first runtime decisions, performance, and limitation details.
* 2026-06-28: Refined the fourth live-app story backfill batch for Visiting Card Maker, Interview Coach, Portfolio Creator, and Meeting Minutes AI with implementation-specific backend architecture, API, database, performance, and limitation details.
* 2026-06-28: Refined the third live-app story backfill batch for Memory Trainer, Daily Word Challenge, Smart Textbook Scanner, and Resume Builder with implementation-specific backend architecture, API, database, performance, and limitation details.
* 2026-06-29: Implemented Invoice and Receipt Maker App #027 backend foundation with isolated InvoiceReceiptProjects, InvoiceReceiptDocuments, InvoiceReceiptItems, and InvoiceReceiptHistory tables, initial query-pattern indexes, protected user-scoped API routes, overview metadata, Alembic config, and backend story documentation for Astra review; app remains `comingSoon`.
* 2026-06-29: Implemented Contract Generator App #028 backend foundation with isolated ContractProjects, ContractDocuments, ContractClauses, and ContractHistory tables, initial query-pattern indexes, protected user-scoped API routes, overview metadata, Alembic config, and backend story documentation for Astra review; app remains `comingSoon`.
* 2026-06-29: Implemented Presentation Designer App #029 backend foundation with isolated PresentationProjects, PresentationSlides, PresentationAssets, and PresentationReviewHistory tables, initial query-pattern indexes, protected user-scoped API routes, overview metadata, Alembic config, and backend story documentation for Astra review; app remains `comingSoon`.
* 2026-06-29: Implemented Career Planner App #030 backend foundation with isolated CareerGoals, CareerRoadmaps, CareerMilestones, and CareerReviewHistory tables, initial query-pattern indexes, protected user-scoped API routes, overview metadata, Alembic config, and backend story documentation for Astra review; app remains `comingSoon`.
* 2026-06-28: Refined the second live-app story backfill batch for Study Planner, Course Tracker, Dictionary+, and Lesson Builder with implementation-specific backend architecture, API, database, performance, and limitation details.
* 2026-06-28: Refined the first live-app story backfill batch for Quiz, Research Assistant, AI Notes Summarizer, and Concept Explainer with implementation-specific backend architecture, API, database, performance, and limitation details.
* 2026-06-28: Backfilled current-state story.md documentation for all 26 live mini apps, including doc-only backend story paths for browser-first apps whose runtime behavior is frontend-owned.
* 2026-06-28: Refined the Story Documentation Contract to use Current Implementation instead of Version History so story.md remains a current-state POC rather than a historical changelog.
* 2026-06-28: Promoted Proposal Writer App #026 in the parent Apps table with `launchStatus = live` and version `1.0.0` after Partner approval, bringing live mini-apps to 26 and establishing the first Platform Foundation v1-era live app.
* 2026-06-28: Verified Proposal Writer against mini-app approval contracts, confirmed overview metadata, and refreshed the backend story document to describe the current implementation.
* 2026-06-28: Refined the Story Documentation Contract to clarify that story.md describes the current module implementation, not historical task logs or changelogs.
* 2026-06-28: Added the permanent Story Documentation Contract with App #026 as the first Platform Foundation v1-era app so every future mini app carries frontend and backend story.md technical memory.
* 2026-06-28: Implemented Proposal Writer App #026 backend foundation with isolated ProposalWriterProjects, ProposalWriterSections, ProposalWriterDrafts, and ProposalWriterHistory tables, initial query-pattern indexes, protected user-scoped API routes, overview metadata, Alembic config, and backend story documentation for Astra review; app remains `comingSoon`.
* 2026-06-28: Added the permanent Mini App Approval Checklist Contract as the final readiness gate connecting metadata, workflow, CRUD, UI, API, index, state, verification, catalog, and promotion requirements before App #026.
* 2026-06-28: Added the permanent Database Index Contract after the App #025 Database Index Cleanup milestone so future mini-app persistent tables require query-pattern-based index review before production promotion.
* 2026-06-28: Added the permanent UI Action Button Contract after the App #025 Frontend UI Cleanup milestone so future mini-app buttons use action-first labels and consistent icon-only record actions.
* 2026-06-28: Added the permanent User API Response Contract after the App #025 API Cleanup milestone so future user-facing APIs use lightweight list/dashboard responses, detail endpoints for full records, and minimal payloads by default.
* 2026-06-27: Promoted Email Assistant App #025 in the parent Apps table with `launchStatus = live` and version `1.0.0` after Astra review and Partner approval, bringing live mini-apps to 25.
* 2026-06-27: Implemented Email Assistant App #025 backend foundation with isolated EmailAssistantProjects, EmailAssistantDrafts, EmailAssistantTemplates, and EmailAssistantHistory tables plus protected user-scoped API routes for Astra review; app remains `comingSoon`.
* 2026-06-27: Promoted Meeting Minutes AI in the parent Apps table with `launchStatus = live` and version `1.0.0`, bringing live mini-apps to 24, updated the catalog export, and synced Astra's overview wording refinement.
* 2026-06-27: Applied and verified the isolated Meeting Minutes AI production migration at revision `20260627_0001`, confirming `MeetingMinutesMeetings`, `MeetingMinutesNotes`, `MeetingMinutesActionItems`, and `MeetingMinutesSummaries`.
* 2026-06-27: Implemented Meeting Minutes AI App #024 backend foundation with isolated MeetingMinutesMeetings, MeetingMinutesNotes, MeetingMinutesActionItems, and MeetingMinutesSummaries tables plus protected user-scoped API routes for Astra review; app remains `comingSoon`.
* 2026-06-27: Documented that future mini-app edit support must use update-specific payloads and must not resubmit create-only parent IDs unless the backend update schema supports reassignment.
* 2026-06-27: Promoted Portfolio Creator in the parent Apps table with `launchStatus = live` and version `1.0.0`, bringing live mini-apps to 23, and updated the catalog export.
* 2026-06-27: Documented the permanent mini-app CRUD rule that user-created editable records must expose visible owner-scoped update support before approval.
* 2026-06-27: Implemented Portfolio Creator backend foundation with isolated PortfolioProfiles, PortfolioProjects, PortfolioSkills, and PortfolioPublishSettings tables plus protected user-scoped API routes for Astra review; app remains `comingSoon`.
* 2026-06-27: Promoted AI Job Interviewer in the parent Apps table with `launchStatus = live` and version `1.0.0`, bringing live mini-apps to 22, and updated the catalog export.
* 2026-06-27: Implemented AI Job Interviewer backend foundation with isolated AiJobInterviewSessions, AiJobInterviewQuestions, AiJobInterviewAnswers, and AiJobInterviewResults tables plus protected user-scoped API routes for Astra review; app remains `comingSoon`.
* 2026-06-27: Promoted Interview Coach in the parent Apps table with `launchStatus = live` and version `1.0.0`, bringing live mini-apps to 21, and updated the catalog export.
* 2026-06-27: Fixed and synced Interview Coach overview CTA paths so `Explore` enters `/interview-coach/sessions`, and documented that future overview CTAs must enter the first workflow page.
* 2026-06-27: Documented the permanent overview metadata CTA rule so future mini-app primary and final CTAs use `Explore`.
* 2026-06-27: Updated and synced Interview Coach overview metadata so primary and final CTA buttons use `Explore`.
* 2026-06-27: Implemented Interview Coach backend foundation with isolated InterviewSessions, InterviewQuestions, InterviewAnswers, and InterviewReviews tables plus protected user-scoped API routes for Astra review.
* 2026-06-22: Reduced Quiz attempt creation post-commit reloads by building the attempt response before committing the already-loaded question rows.
* 2026-06-22: Added the Quiz Question play-filter composite index migration for Milestone Review #2 after query-plan investigation confirmed full scans on the 1.4M-row Question table.
* 2026-06-22: Completed Milestone Review #2 Quiz API performance review by narrowing Quiz play/history DB column loading while preserving user-facing response contracts.
* 2026-06-22: Promoted Visiting Card Maker App #021 in the parent Apps catalog with `launchStatus = live` and version `1.0.0` after production manual verification and Partner approval.
* 2026-06-22: Updated Visiting Card Maker overview metadata so primary and final CTA buttons use `Explore` and navigate to `/visiting-card-maker/create`, then synced the metadata table.
* 2026-06-22: Added and applied the isolated Visiting Card Maker production migration, aligned the existing remote `CardProfiles` schema with the V1 API contract, and verified `CardProfiles`, `CardDesigns`, and revision `20260622_0002`.
* 2026-06-22: Promoted Resume Builder App #027 in the parent Apps catalog with `launchStatus = live` and version `1.0.0` after Astra review and Partner verification.
* 2026-06-22: Fixed Resume Builder dashboard preview selection to limit the default/latest project query after real multi-template data exposed a `MultipleResultsFound` 500.
* 2026-06-22: Seeded real Resume Builder data for the Partner account across the Classic, Modern, Minimal, and Timeline templates using the existing production `ResumeProject`, `ResumeSection`, and `ResumeItem` schema.
* 2026-06-22: Completed Resume Builder production schema verification after executing the isolated Alembic upgrade; no new revision files were required because the existing `ResumeProject`, `ResumeSection`, and `ResumeItem` schema was reused, and `resume_builder_alembic_version` was created empty.
* 2026-06-22: Removed ETag/304 behavior from content metadata GET routes and switched metadata API responses to strict `no-store` headers so browser refreshes always fetch fresh DB-backed content.
* 2026-06-22: Implemented Resume Builder App #027 backend foundation by reusing existing production `ResumeProject`, `ResumeSection`, and `ResumeItem` tables, adding protected user-scoped API routes, and leaving the Apps catalog row `comingSoon` with no live version for Astra review.
* 2026-06-22: Promoted Smart Textbook Scanner App #026 in the parent Apps catalog with `launchStatus = live` and version `1.0.0` after Astra review and Partner approval.
* 2026-06-22: Implemented Smart Textbook Scanner App #026 backend foundation with isolated TextbookScans, TextbookPages, and ExtractedNotes tables plus protected user-scoped API routes for Astra review.
* 2026-06-22: Promoted Course Tracker App #025 in the parent Apps catalog with `launchStatus = live` and version `1.0.0` after Astra review and Partner approval.
* 2026-06-22: Implemented Course Tracker App #025 backend foundation with isolated Courses, CourseModules, and CourseProgressLogs tables plus protected user-scoped API routes for Astra review.
* 2026-06-22: Promoted Study Planner App #024 in the parent Apps catalog with `launchStatus = live` and version `1.0.0`, and documented the approval promotion requirement.
* 2026-06-22: Marked Study Planner App #024 approved after Astra review and aligned overview metadata/status documentation.
* 2026-06-22: Synced overview metadata after Study Planner App #024 CTA review so `overview:study-planner` serves `Explore` and routes to `/study-planner/plan`.
* 2026-06-22: Added and applied Study Planner corrective migration `20260622_0002` to align an existing remote Study Planner schema with the App #024 API contract and resolve dashboard 500 errors.
* 2026-06-22: Applied the isolated Study Planner App #024 migration to the configured remote Study Planner database and verified StudyPlans, StudyPlanTasks, StudyLogs, and revision `20260622_0001`.
* 2026-06-22: Implemented Study Planner App #024 backend foundation with isolated StudyPlans, StudyPlanTasks, and StudyLogs tables plus protected user-scoped API routes.
* 2026-06-22: Promoted AI Notes Summarizer App #023 to live launch status at version `1.0.0` after Astra review, production migration, and Partner approval.
* 2026-06-22: Implemented AI Notes Summarizer App #023 backend foundation with isolated NotesDocuments, NoteSummaries, and SummaryJobs tables plus user-scoped API routes.
* 2026-06-21: Promoted Research Assistant App #022 to live launch status at version `1.0.0` after Partner and Astra approval.
* 2026-06-21: Implemented Research Assistant App #022 backend foundation with isolated ResearchTopics, ResearchNotes, ResearchReferences, and ResearchJobs tables plus user-scoped API routes.
* 2026-06-21: Promoted Concept Explainer App #021 to live launch status at version `1.0.0` after Partner approval.
* 2026-06-21: Added nullable `Apps.version` governance so only live apps carry release versions and queued apps use `NULL`.
* 2026-06-21: Promoted Lesson Builder, Memory Trainer, and Dictionary+ to live launch status at version `1.0.0` after Partner approval.
* 2026-06-21: Fixed Dictionary+ overview metadata CTAs to use `Explore` and route directly into the lookup workflow.
* 2026-06-21: Implemented Dictionary+ App #020 backend V1 with isolated DictionaryLookups, SavedWords, and WordLists tables plus user-scoped API routes.
* 2026-06-21: Aligned the Apps catalog export to the approved 100-app roadmap and documented public API data discipline before fresh mini-app development.
* 2026-06-20: Optimized the public FAQ list API with a lightweight user-facing response schema and column-select query while keeping admin FAQ contracts unchanged.
* 2026-06-20: Optimized public Apps and Categories list APIs with lightweight user-facing response schemas and column-select queries while keeping detail and admin contracts unchanged.
* 2026-06-20: Added semantic version support to the parent Apps catalog with a non-null `version` column defaulting existing rows to `1.0.0`, exposed app versions in Apps API contracts, and documented the mini-app versioning rule.
* 2026-06-20: Removed the content metadata process cache and changed metadata responses to revalidation-only CORS-safe headers.
* 2026-06-20: Completed active app overview metadata coverage by adding 53 missing overview JSON files, validating all 153 overview files, syncing metadata records, and verifying all 100 active overview endpoints return `200`.
* 2026-06-20: Added public Apps and Categories catalog `status=active` list filtering after verifying the parent DB stores user-facing records as `active`; admin behavior remains unchanged.
* 2026-06-16: Added and applied a corrective Memory Trainer App #019 migration to rebuild empty legacy Memory Trainer tables to the approved V1 camelCase schema.
* 2026-06-16: Added the protected Memory Trainer API surface for App #019 with an isolated Memory Trainer database, Alembic context, game/session/round/performance ownership, persisted round answers, review data, and progress summary.
* 2026-06-16: Marked Lesson Builder App #018 approved after approval readiness review passed.
* 2026-06-16: Fixed the Lesson Builder App #018 create runtime failure by rebuilding the empty production `LessonPlans` table with the UUID primary key expected by the implemented API.
* 2026-06-16: Added a corrective Lesson Builder App #018 migration to align the existing `lesson-builder-ansiversa` table shape with the implemented `LessonPlans` model.
* 2026-06-16: Locked published Lesson Builder App #018 lessons against updates, section mutations, reordering, and repeat publish calls after backend review.
* 2026-06-16: Added the protected Lesson Builder API surface for App #018 with an isolated Lesson Builder database, Alembic context, lesson/section ownership, ordering, preview data, and publish workflow.
* 2026-06-16: Marked Exam Simulator App #017 approved after manual end-to-end workflow verification passed.
* 2026-06-16: Refined Exam Simulator final overview CTA wording after approval review and synced metadata.
* 2026-06-16: Updated Exam Simulator overview metadata CTA labels to the approved `Explore` copy for manual verification fixes.
* 2026-06-16: Marked Language Flashcards App #016 approved after manual verification passed.
* 2026-06-16: Updated Language Flashcards overview metadata CTA labels to the approved `Explore` copy for manual verification fixes.
* 2026-06-16: Documented the permanent mini-app boundary and isolated database migration rules in the API agent contract.
* 2026-06-16: Added the protected Exam Simulator API surface for App #017 using existing ExamPapers, ExamQuestions, ExamAttempts, and ExamAnswers table mappings without schema migrations.
* 2026-06-16: Added the protected Language Flashcards API surface for App #016 using existing LanguageDecks, LanguageCards, StudySessions, and ReviewLogs table mappings without schema migrations.
* 2026-06-15: Normalized the Apps catalog so the 15 completed apps are live and the remaining 87 apps are coming soon.
* 2026-06-15: Froze approved Mood Journal App #015 overview metadata.
* 2026-06-15: Refined the approved Mood Journal V1 overview CTA labels from Open journal to Explore.
* 2026-06-15: Updated Mood Journal App #015 overview metadata for user-created date-keyed browser entries and the Record → Review → Reflect workflow.
* 2026-06-15: Refined the approved Daily Word Challenge V1 overview CTA labels from Start challenge to Explore.
* 2026-06-15: Updated Daily Word Challenge App #014 overview metadata for deterministic browser vocabulary learning and the Discover → Learn → Complete workflow.
* 2026-06-15: Updated Eco Habit Tracker App #013 overview metadata for date-based browser progress and the Plan → Track → Complete workflow.
* 2026-06-15: Refined the approved Quote Forge V1 technical overview wording to describe its browser-first reference architecture.
* 2026-06-15: Updated Quote Forge App #012 overview metadata for the bundled browser quote collection workflow Browse → Copy → Favorite.
* 2026-06-15: Refined approved Formula Finder V1 overview wording around local favorites, the grouped section, and the final CTA.
* 2026-06-15: Updated Formula Finder App #011 overview metadata for the bundled browser reference-data workflow Search → Explore → Copy → Favorite.
* 2026-06-15: Refined approved FlashNote V1 overview wording around flip-based active recall, session-only tracking, and the final CTA.
* 2026-06-14: Added FlashNote App #010 overview metadata for multiple-record browser persistence through Create → Review → Recall and standardized Cards workspace CTAs.
* 2026-06-14: Added Quick Notepad App #009 overview metadata for the local browser persistence workflow Write → Save → Reopen and standardized Notepad workspace CTAs.
* 2026-06-14: Added Study Timer App #008 overview metadata for the browser-only Set → Start → Focus → Complete workflow and standardized Timer workspace CTAs.
* 2026-06-14: Added Markdown Editor App #007 overview metadata for the browser-only Write → Preview → Export workflow and standardized Editor workspace CTAs.
* 2026-06-14: Added Color Palette Generator App #006 overview metadata for the browser-only Generate → Adjust → Export workflow and standardized Generator workspace CTAs.
* 2026-06-14: Added Unit & Currency Converter App #005 overview metadata for browser-only unit calculations, frontend currency-rate lookup, and standardized Converter workspace CTAs.
* 2026-06-14: Updated QR Code Creator overview metadata for App #004 with the browser-only Input → Preview → Download workflow and standardized workspace CTAs.
* 2026-06-14: Standardized completed mini-app overview CTA labels to `Explore` and corrected JSON Formatter and Password Generator CTA paths to their workspace routes.
* 2026-06-14: Updated the physical JSON Formatter overview metadata backup after validating JSON Formatter V1 through Ansiversa's own metadata update workflow.
* 2026-06-14: Froze Quiz API V1 after completing protected attempt/result history, review details, ownership enforcement, and list-query performance optimization; future enhancements belong in the Quiz V1.1 backlog.
* 2026-06-14: Optimized Quiz attempts/results history lists from per-row N+1 queries to paginated joined summary queries.
* 2026-06-14: Added protected current-user Quiz attempts/results history APIs and submitted result review detail reconstruction.
* 2026-06-13: Added an idempotent corrective parent migration to create the missing `UserSettings` table and restore authenticated Settings API reads and writes.
* 2026-06-13: Updated overview metadata sync to remove obsolete unprefixed `quiz` and `resume-builder` records after canonical `overview:*` records are synced.
* 2026-06-13: Completed the 102-app overview JSON migration with status-aware, catalog-aligned metadata for the coming-soon Horoscope AI and Daily Challenge apps and the live Job Tracker app.
* 2026-06-13: Added five status-aware, catalog-aligned overview metadata seed files for the coming-soon Would You Rather, Guess the Emoji, AI Character Chat, Personality Quiz, and Fortune Teller apps.
* 2026-06-13: Added five status-aware, catalog-aligned overview metadata seed files for Recipe Generator, Language Learning Buddy, Trivia Arena, Riddle Maker, and Puzzle Zone.
* 2026-06-13: Added five status-aware, catalog-aligned overview metadata seed files for Mood Journal, Meditation Script Maker, Sleep Routine Designer, Affirmation Generator, and Shopping List AI.
* 2026-06-13: Added five status-aware, catalog-aligned overview metadata seed files for Markdown Editor, Browser PDF Reader, Clipboard Translator, Wellness and Goal Planner, and Fitness Tracker.
* 2026-06-13: Added five status-aware, catalog-aligned overview metadata seed files for Screenshot Editor, Color Palette Generator, Password Generator, API Tester, and JSON Formatter.
* 2026-06-13: Added status-aware, catalog-aligned overview metadata seed files for QR Code Creator, Clipboard Manager, File Optimizer, and Voice Converter.
* 2026-06-13: Added five status-aware, catalog-aligned overview metadata seed files for Snippet Generator, File Converter, Image Background Remover, Unit and Currency Converter, and Price Checker.
* 2026-06-13: Added five status-aware, catalog-aligned overview metadata seed files for Fanfic Generator, Email Newsletter Writer, AI Translator and Tone Fixer, Rephrase and Paraphraser, and Grammar Fixer using the catalog's exact `grammer-fixer` slug.
* 2026-06-13: Added five status-aware, catalog-aligned overview metadata seed files for AI Meme Creator, Prompt Builder, Speech Writer, Novel Outliner, and Comic Storyboarder.
* 2026-06-13: Added five status-aware, catalog-aligned overview metadata seed files for Blog Writer, Social Caption Generator, Script Formatter, Creative Title Maker, and Quote Forge.
* 2026-06-13: Added five status-aware, catalog-aligned overview metadata seed files for StoryCrafter, Poem Studio, Song Lyric Maker, Ad Copy Assistant, and Book Summary Generator.
* 2026-06-13: Added five status-aware, catalog-aligned overview metadata seed files for Job Description Analyzer, Proposal Writer, Invoice and Receipt Maker, Career Planner, and LinkedIn Bio Optimizer.
* 2026-06-13: Added five status-aware, catalog-aligned overview metadata seed files for the coming-soon Memory Trainer, Smart Textbook Scanner, Homework Helper, Visiting Card Maker, and Interview Coach apps.
* 2026-06-13: Added five status-aware, catalog-aligned overview metadata seed files for Research Assistant, AI Notes Summarizer, Knowledge Duel, Exam Simulator, and Study Timer.
* 2026-06-13: Added five catalog-aligned overview metadata seed files for Quick Notepad, Event Planner, Pet Care Planner, Eco Habit Tracker, and Interview Scheduler, avoiding unsupported feature claims beyond confirmed app scope.
* 2026-06-13: Added five catalog-aligned overview metadata seed files for Lesson Builder, Daily Word Challenge, Email Polisher, Presentation Designer, and Client Feedback Analyzer.
* 2026-06-13: Added five catalog-aligned overview metadata seed files for Dictionary+, Fact Generator, Formula Finder, Language Flashcards, and EduPrompt, keeping content within each app's confirmed live product scope.
* 2026-06-13: Added five validated overview metadata seed files selected from the then-current reference catalog; updated the overview sync command to ignore the reference-only `apps.json` catalog. The finalized Apps table export now governs active app identity.
* 2026-06-13: Added nine validated mini-app overview metadata seed files and a recursive sync command that upserts `overview:{app_slug}` records into the existing `Metadata` table.
* 2026-06-13: Added `app/modules/content/data/overview/quiz.json` with the Quiz mini-app overview metadata payload copied from the React Quiz overview content and validated against `OverviewResponse`; no automatic seeding or runtime loading behavior was added.
* 2026-06-13: Added the generic typed mini-app overview metadata response contract and public `GET /api/v1/content/metadata/overview/{app_key}` route backed by `overview:{app_key}` metadata keys; no migration, seed data, or frontend changes were added.
* 2026-06-12: Corrected parent Alembic online migrations to reuse the authenticated `parent_engine` for production Turso/libSQL connections.
* 2026-06-12: Added the public Contact message workflow with validated typed request/response schemas, parent-owned `ContactMessages` table and migration, and `POST /api/v1/contact`; no email sending or admin UI was added.
* 2026-06-12: Added `app/modules/content/data/pricing.json` with the Pricing metadata payload validated against `PricingResponse`; no automatic seeding or runtime loading behavior was added.
* 2026-06-12: Added the typed Pricing content schema and `GET /api/v1/content/metadata/pricing` endpoint backed by the existing `Metadata` table and generic management routes.
* 2026-06-12: Documented the parent content metadata architecture, typed content endpoints and responses, API-managed content rule, generic metadata management routes, and merged metadata/user-settings Alembic history.
* 2026-06-07: Added and applied an isolated Quiz Alembic migration chain using `QUIZ_DATABASE_URL`, `QuizBase.metadata`, and `quiz_alembic_version`; migrated production Quiz DB to create `QuizAttempt` and `QuizAttemptQuestion` without touching parent Alembic or parent tables.
* 2026-06-07: Consolidated parent and Quiz Turso/libSQL connections onto the shared `TURSO_AUTH_TOKEN` while preserving separate database URLs, engines, sessions, models, and migration boundaries.
* 2026-06-07: Added the secure server-graded Quiz attempt lifecycle with current-user ownership, hierarchy validation, paid/admin difficult-level entitlement, safe pre-submit question responses, two-hour expiry, exact stored-question submission validation, compatible `Result` persistence, answer review after submit, and isolated idempotent setup for `QuizAttempt`/`QuizAttemptQuestion` outside parent Alembic.
* 2026-06-07: Added the isolated read-only Quiz taxonomy API foundation with separate Quiz DB configuration/session/models and protected paginated Platform, Subject, Topic, and Roadmap list routes.
* 2026-06-07: Documented the Quiz API migration plan after inspecting the Quiz repo's Astro actions, data models, user/admin flows, integrations, ownership boundaries, required routes, security risks, and phased cutover strategy.
* 2026-06-07: Fixed production Alembic/Turso migrations by reusing the authenticated parent database engine, documenting `TURSO_AUTH_TOKEN`, declaring Python 3.13 to avoid the Python 3.14 libSQL driver crash, safely baselining the existing production schema, and applying head revision `6a0fd846f731`.
* 2026-06-07: Added password and user settings API foundation: generic forgot-password requests with hashed expiring one-time reset tokens, reset-password and authenticated change-password flows, protected `GET/PATCH /api/v1/users/me/settings` with validated defaults, parent-compatible `PasswordResetTokens` and `UserSettings` tables, and OpenAPI-ready schemas while preserving existing login/register/logout and cookie-session behavior.
* 2026-06-06: Added API-managed auth cookie sessions: successful login now sets the existing JWT in the HttpOnly `ansiversa_session` cookie, protected auth dependencies prefer bearer tokens and otherwise use the cookie, `POST /api/v1/auth/logout` clears the cookie, environment-driven local/production cookie settings were added, and credentialed CORS remains restricted to configured origins.
* 2026-05-31: Phase 24 Admin FAQs API foundation completed: added admin-protected `GET/POST/PATCH/DELETE /api/v1/admin/faqs` routes backed by the existing parent-compatible `Faqs` table, with pagination (`page`, `pageSize`), search, sort/dir plus `sortBy`/`sortDirection` aliases, filters for `appKey`, `audience`, `category`, and `isPublished`, parent schema field preservation, create/update/delete audit logs (`admin.faq.create/update/reorder/delete`), and no changes to public `GET /api/v1/faqs` behavior. Verification: `.venv/bin/python -m compileall app` ✅; `.venv/bin/alembic upgrade head` ✅; `.venv/bin/uvicorn app.main:app --reload` ✅ with local health OK and unauthenticated admin FAQs returning `401`.
* 2026-05-30: Phase 19 parent web password compatibility fix completed: inspected parent `web/src/lib/auth.ts` and confirmed legacy password hashes use `salt:hash` where `hash = HMAC-SHA256(ANSIVERSA_AUTH_SECRET, "${salt}:${password}")`; updated API auth verification to support both Argon2 (`$argon2id$...`) and legacy parent hashes, added `ANSIVERSA_AUTH_SECRET` configuration, aligned legacy status handling so missing/empty statuses are treated as active while `disabled`/`inactive`/`suspended` remain blocked, and upgraded successful allowed legacy logins to Argon2 immediately. Wrong passwords and blocked-status users still return `401`, Argon2 users remain supported, and `passwordHash` remains unexposed. No parent `web` repo changes, password resets, billing APIs, or unrelated auth/session changes added.
* 2026-05-29: Phase 18 admin users read foundation partially completed: inspected parent `web/src/actions/adminUsers.ts`, `web/src/stores/adminUsers.ts`, and `web/src/pages/admin/users.astro`, then added admin-protected read-only `GET /api/v1/admin/users` and `GET /api/v1/admin/users/{user_id}` routes. The API follows parent action defaults for pagination (`page`, `pageSize`), `q`, `roleId`, sort/dir values, status normalization, role info, and location fields, returns safe admin-readable profile/location/avatar fields, and excludes `passwordHash`, reset tokens, and raw Stripe customer IDs. Intentional API additions: search includes `city`, `countryCode`, and `regionCode`; filters include `status`, `plan`, `planStatus`, and `countryCode`; `sortBy`/`sortDirection` aliases are accepted. No parent `web` repo changes, Astro action removal, admin user create/update/delete, admin password/reset actions, billing APIs, permissions registry, or audit log listing added.
* 2026-05-29: Phase 17 admin apps API foundation completed: inspected parent `web/src/actions/adminApps.ts`, `web/src/stores/adminApps.ts`, and parent registry/capability helpers, then added admin-protected `GET /api/v1/admin/apps`, `GET /api/v1/admin/apps/meta`, `POST /api/v1/admin/apps`, `PATCH /api/v1/admin/apps/{app_id}`, and `DELETE /api/v1/admin/apps/{app_id}` routes. The API follows parent action defaults for pagination (`page`, `pageSize`), sort/dir values, category metadata, status/launch/visibility/pricing normalization, URL normalization, key/slug duplicate blocking, capabilities serialization, current delete behavior, and audit actions (`admin.apps.create/update/status/featured/delete`). Intentional API additions: search includes `description`, list accepts `launchStatus`/`visibility`/`pricingGate` filters and `sortBy`/`sortDirection` aliases, meta returns allowed values plus capability options, and create/update validate category existence for clean API errors. No parent `web` repo changes, Astro action removal, billing APIs, admin users/roles, permissions registry, or audit log listing added.
* 2026-05-29: Phase 16 admin categories API foundation completed: inspected parent `web/src/actions/adminCategories.ts` and added admin-protected `GET/POST/PATCH/DELETE /api/v1/admin/categories` routes with web-action-aligned pagination (`page`, `pageSize`), search, `status` filter, `sort`/`dir` sorting, app counts, `cat_` id validation, key/slug normalization, duplicate blocking, `updatedAt` updates, app-reference delete blocking, and audit actions (`admin.categories.create/update/status/delete`). Also accepted API aliases `sortBy`/`sortDirection` and intentionally included `description` in search per Phase 16 requirement; updated README + migration plan. No parent `web` repo changes, Astro action removal, Admin Apps, billing APIs, or unrelated admin modules added.
* 2026-05-29: Phase 15 admin and audit foundation completed: added reusable `require_admin_user` dependency that reuses `get_current_user`, preserves `401` for unauthenticated/invalid tokens, and returns `403` for non-admin users while allowing active `roleId = 1` admins; added protected `GET /api/v1/admin/status` verification route; added parent-compatible `AuditLogs` model/migration and reusable `write_audit_log(...)` helper with safe JSON metadata and optional request IP/user-agent capture; updated README + migration plan. No parent `web` repo changes, admin CRUD endpoints, billing APIs, destructive operations, permissions registry, or audit listing added.
* 2026-05-29: Phase 14 public FAQ read foundation completed: added public `GET /api/v1/faqs` endpoint through a new `app/modules/faqs` module, added parent-compatible `Faqs` model/migration for `id`, `question`, `answer`, `sortOrder`, `appKey`, timestamps, `audience`, `category`, `answer_md`, and `is_published`, implemented published-only parent/app scoping, audience filtering, question/answer search, `sortOrder`/`createdAt` ordering, and pagination metadata, and updated README + migration plan. No parent `web` repo changes, admin FAQ CRUD, audit logging, billing/admin/dashboard changes, or FAQ writes added.
* 2026-05-29: Phase 13 dashboard read foundation partially completed: added protected `/api/v1/me/dashboard` endpoint through a new `app/modules/dashboard` module, reused `get_current_user`, added parent-compatible `Dashboard` model/migration for `_id`, `userId`, `appId`, `lastActivityAt`, `summaryVersion`, timestamps, and `summaryJson`, returned current-user-only counts/recent apps/dashboard items with safe summary JSON parsing, and updated README + migration plan. No parent `web` repo changes, dashboard writes/webhooks, cross-app summaries, admin APIs, or billing APIs added.
* 2026-05-29: Phase 12 notifications foundation completed: added protected `/api/v1/me/notifications` list/unread-count/mark-read/mark-all-read endpoints through a new `app/modules/notifications` module, reused `get_current_user`, added parent-compatible `Notifications` model/migration with read state, timestamps, and metadata, and updated README + migration plan. No parent `web` repo changes, Astro action removal, dashboard, admin, billing, or notification webhooks added.
* 2026-05-29: Phase 11 favorites foundation completed: added protected `/api/v1/me/favorites` list/add/remove endpoints through a new `app/modules/favorites` module, reused `get_current_user`, added parent-compatible `Favorites` model/migration with unique `(appId, userId)` index, implemented conservative public/live app checks plus idempotent duplicate add behavior, and updated README + migration plan. No parent `web` repo changes, Astro action removal, dashboard, notifications, admin, or billing APIs added.
* 2026-05-29: Phase 10 profile/preferences foundation completed: added protected `/api/v1/me/profile` read/update and `/api/v1/me/preferences` read/upsert endpoints through a new `app/modules/profile` module, reused `get_current_user`, added parent-compatible `UserPreferences` model/migration, expanded safe current-user response fields, and updated README + migration plan. No parent `web` repo changes, favorites, notifications, dashboard, billing, or admin APIs added.
* 2026-05-29: Phase 9 auth schema alignment completed: replaced simplified lowercase API `users` auth model with parent-compatible `Users`/`Roles` SQLAlchemy models, added safe corrective Alembic migration to copy local `users` data into `Users`, updated auth schemas/services for `name`/`passwordHash`/`roleId`/`status`, kept JWT claims minimal (`sub`, `email`, `type`), documented safe response shape/default member role behavior, and updated the parent web API migration plan. No parent `web` repo changes, favorites/dashboard/notifications, or billing logic added.
* 2026-05-29: Added `docs/parent-web-api-migration-plan.md` documenting the parent `web` Astro actions/API surface against current `ansiversa-api` coverage, with phased migration classification for public, protected, admin, billing, and deferred/risky APIs; documentation-only task, no runtime endpoints added.
* 2026-05-28: Aligned Apps Catalog with the real parent schema by adding `Categories`, mapping `Apps.categoryId` to `Categories.id`, correcting app catalog model fields to parent naming, adding public category read routes, and documenting that Favorites and Dashboard remain deferred for Foundation Phase 8.1.
* 2026-05-28: Added parent/global Apps Catalog foundation with `apps` table model/migration, public read schemas/services/routes for `/api/v1/apps/` and `/api/v1/apps/{app_key}`, README endpoint notes, and router registration; no web migration, pricing/entitlements, mini-app database connections, or destructive seed operations were added for Foundation Phase 8.
* 2026-05-28: Added stable OpenAPI operation ID generation for future TypeScript clients, documented generated-client strategy in README, and added module-specific OpenAPI schema guidance to this repo contract for Foundation Phase 7.
* 2026-05-28: Added parent/global auth foundation with `users` table migration, Argon2 password hashing via `pwdlib`, JWT access token helpers, OAuth2 bearer/Swagger Authorize support, register/login/me routes, current-user dependency, README auth/env guidance, and dependency pins; no roles, refresh tokens, session tables, social login, billing, or mini-app auth were added for Foundation Phase 6.
* 2026-05-28: Added safe auth module skeleton with typed status response, placeholder service, `/api/v1/auth/status/` route, router registration, and README note; no real auth logic, JWT handling, password flow, or auth tables were added for Foundation Phase 5.
* 2026-05-28: Added parent/global Alembic foundation wired to `ParentBase.metadata` and `PARENT_DATABASE_URL`, created an empty initial parent migration, and documented migration isolation rules and commands for Foundation Phase 4.
* 2026-05-28: Added parent/global SQLAlchemy engine and session foundation with local SQLite fallback, `PARENT_DATABASE_URL` environment sample, DB health route, README note, and local DB ignore rules for Foundation Phase 3.
* 2026-05-28: Added typed settings via `pydantic-settings`, CORS middleware registration, environment sample alignment, concise README setup/deployment notes, and app initialization cleanup for Foundation Phase 2.
* 2026-05-28: Added repository agent instructions for `ansiversa-api`, documenting central API purpose, architecture boundaries, FastAPI standards, deployment expectations, and next milestone.
2026-07-16 - Implemented Bill Splitter App #093 backend foundation with isolated database configuration and Alembic lineage, owner-scoped bills/participants/items/allocations, decimal-safe authoritative totals, equal/single/custom allocation validation, bill adjustments, recorded settlement status, search/filter/pagination/dashboard APIs, OpenAPI contracts, service tests, and overview metadata. Applied the production-configured isolated database migration at `20260716_0005_bill_splitter`; verified four empty application tables, the custom version table, 12 indexes, 4 foreign keys, and 12 numeric columns. No live promotion was performed.
2026-07-16 - Implemented Savings Goal Planner App #094 backend to Workflow Ready with isolated goals, transactions, and milestones; owner-scoped protected APIs; decimal-authoritative balance/progress/pace; prevented negative balances and overfunding; automatic completion; derived milestones; per-currency dashboard; filters/pagination; migration `20260716_0006_savings_goal_planner`; lifecycle documentation; overview metadata; and generated contracts. Applied and verified the production-configured isolated migration with three empty app tables, 15 indexes, 2 foreign keys, 5 numeric columns, and the custom version table. No live promotion was performed.
2026-07-16 - Completed Salary Breakdown Calculator App #095 API milestone with isolated scenarios, earnings, and deductions; six-frequency Decimal normalization; recurring/one-time separation; fixed/base/gross percentage deductions; negative-net rejection; archived read-only rules; owner-scoped CRUD; per-currency dashboard; safe same/cross-currency comparison; migration `20260716_0007_salary_breakdown_calculator`; lifecycle documentation; overview metadata; 15 stable operations; local schema verification; and regression tests. Frontend is implemented in the companion repository. Applied and verified the production-configured isolated migration with three empty app tables, 10 indexes, two foreign keys, six numeric columns, and the custom version table. Authenticated E2E and live promotion remain pending.
2026-07-16 - Implemented Net Worth Tracker App #096 backend to Workflow Ready with isolated accounts, balance entries, snapshots, and snapshot items; Decimal-authoritative currency-separated assets/liabilities/net worth; deterministic history recalculation; history-safe archival/deletion; immutable transactional captures; owner-scoped CRUD and comparison; migration `20260716_0008_net_worth_tracker`; lifecycle documentation; overview metadata; stable operations; local schema validation; and regression tests. Applied and verified the production-configured isolated migration with four empty app tables, 10 indexes, two foreign keys, three numeric columns, one unique constraint, and the custom version table. Authenticated E2E, manual approval, and live promotion remain pending.
2026-07-16 - Implemented Decision Maker App #097 backend to technical Workflow Ready with isolated decisions, options, criteria, and ratings; owner-scoped nested CRUD; 1–5/1–10 scale safeguards; proportional Decimal weight normalization; higher/lower direction scoring; incomplete-option exclusion; deterministic ties/ranks; selected-option and status protections; rating cleanup/cascade behavior; dashboard/filter/pagination APIs; migration `20260716_0009_decision_maker`; lifecycle documentation; overview metadata; stable operations; local schema validation; and regression tests. Applied and verified the production-configured migration at head with four empty application tables, nine indexes, five foreign keys, and the custom version table. Authenticated E2E, manual approval, and live promotion remain pending.
