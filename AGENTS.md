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

2. Admin APIs

* Admin endpoints may return complete records.
* Admin screens are internal tools and are allowed to access all fields.

3. New Mini Apps

Before implementing any user-facing endpoint:

* Audit the UI fields.
* Define the response contract.
* Select only those columns from the database.
* Return minimal payloads.

4. Forbidden Pattern

```text
Database
↓
Return full ORM model
↓
Frontend ignores 50% to 80% of fields
```

This pattern must not be used.

5. Goal

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

The parent Alembic history includes a merge revision for the metadata and user
settings branches. Preserve that merged migration history.

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
* 2026-06-13: Added five status-aware, catalog-aligned overview metadata seed files for QR Code Creator, Clipboard Manager, File Compressor, Text-to-Speech Converter, and Speech-to-Text Converter.
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
