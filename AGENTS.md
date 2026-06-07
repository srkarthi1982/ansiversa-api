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

Do not mix unrelated app metadata into one migration context unless intentionally designed.

When adding a mini-app DB engine, isolate it clearly.

Never allow one mini-app to directly own another mini-app's data.

Cross-app reads should happen through approved API/service aggregation only.

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
