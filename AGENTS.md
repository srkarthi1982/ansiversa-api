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
