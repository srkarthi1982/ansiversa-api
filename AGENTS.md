# AGENTS.md — Ansiversa API

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
11. apps.json/catalog/readiness docs updated
12. Production migration and promotion only after manual approval

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
* 2026-06-13: Added five validated overview metadata seed files selected from the reference app catalog for Concept Explainer, Course Tracker, Cover Letter Writer, Meeting Minutes AI, and Meal Planner; updated the overview sync command to ignore the reference-only `apps.json` catalog.
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
