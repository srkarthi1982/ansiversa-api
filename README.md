# Ansiversa API

`ansiversa-api` is the central FastAPI backend platform for the Ansiversa ecosystem.
It provides a stable API foundation for parent services, mini-apps, future mobile apps,
AI services, and cross-app aggregation.

Production: https://api.ansiversa.com

Docs: https://api.ansiversa.com/docs

## Iteration 2 — AI SEO Architecture

Iteration 2 architecture is approved. SEO-001 is frozen and authorized only for
completion of its documentation and architecture artifact. The permanent
architecture and planning package are:

```text
docs/ai-seo-architecture.md
docs/iterations/2026-08-ai-seo/
```

The iteration extends the existing Canonical AI Knowledge Registry and public
publisher. SEO-002 Contract V1 is approved and Frozen; SEO-003 through SEO-008
remain Proposed; SEO-003 remains unresolved; and AI SEO runtime implementation,
frontend/backend changes, metadata changes, crawler submissions, marketing
automation, video generation, and production changes remain unauthorized.

SEO-002's approved contract is:

```text
docs/ai-seo-per-app-public-knowledge-contract.md
```

## Local Setup

Use Python 3.13. The current `libsql-experimental` driver can terminate during
remote Turso connections under Python 3.14.

Create and activate a virtual environment:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create local environment values:

```bash
cp .env.example .env
```

Run locally:

```bash
uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/api/v1/health/
http://127.0.0.1:8000/api/v1/health/db/
http://127.0.0.1:8000/api/v1/auth/status/
http://127.0.0.1:8000/api/v1/auth/me
http://127.0.0.1:8000/api/v1/me/profile
http://127.0.0.1:8000/api/v1/me/preferences
http://127.0.0.1:8000/api/v1/me/favorites
http://127.0.0.1:8000/api/v1/me/notifications
http://127.0.0.1:8000/api/v1/me/notifications/unread-count
http://127.0.0.1:8000/api/v1/me/dashboard
http://127.0.0.1:8000/api/v1/apps/
http://127.0.0.1:8000/api/v1/categories/
http://127.0.0.1:8000/api/v1/faqs
http://127.0.0.1:8000/api/v1/admin/status
http://127.0.0.1:8000/api/v1/admin/categories
http://127.0.0.1:8000/api/v1/admin/apps
http://127.0.0.1:8000/api/v1/admin/apps/meta
http://127.0.0.1:8000/api/v1/admin/users
```

## Environment

Settings are loaded with `pydantic-settings` from environment variables and `.env`.
Do not commit secrets. Keep `.env` local only.

`PARENT_DATABASE_URL` controls the parent/global SQLAlchemy engine. Local development
falls back to SQLite:

```text
sqlite:///./ansiversa_api.db
```

When `PARENT_DATABASE_URL` uses a `libsql://` Turso database URL, set the
matching `TURSO_AUTH_TOKEN` before starting the API or running Alembic.

The Quiz API module uses its own database connection. Configure
`QUIZ_DATABASE_URL`; all Turso/libSQL database connections reuse the shared
`TURSO_AUTH_TOKEN`. Quiz models and sessions remain isolated from the
parent/global database and Alembic context. `QUIZ_ATTEMPT_EXPIRE_HOURS`
controls incomplete-attempt expiry and defaults to `2`.

The Research Assistant API module uses its own database connection. Configure
`RESEARCH_ASSISTANT_DATABASE_URL`; it reuses the shared `TURSO_AUTH_TOKEN` for
Turso/libSQL connections. Research Assistant models and sessions remain isolated
from the parent/global database and Alembic context.

The AI Notes Summarizer API module uses its own database connection. Configure
`AI_NOTES_SUMMARIZER_DATABASE_URL`; it reuses the shared `TURSO_AUTH_TOKEN` for
Turso/libSQL connections. AI Notes Summarizer models and sessions remain
isolated from the parent/global database and Alembic context.

Each persistent mini app uses its own isolated `*_DATABASE_URL`. For the
newer billing and document workflow apps, configure
`INVOICE_RECEIPT_MAKER_DATABASE_URL`, `CONTRACT_GENERATOR_DATABASE_URL`,
`PRESENTATION_DESIGNER_DATABASE_URL`, and `CAREER_PLANNER_DATABASE_URL` before
deploying or running their Alembic contexts. Turso/libSQL connections reuse the
shared `TURSO_AUTH_TOKEN`.

Auth uses these environment variables:

```text
JWT_SECRET_KEY
JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES
ANSIVERSA_AUTH_SECRET
AUTH_COOKIE_NAME
AUTH_SESSION_HINT_COOKIE_NAME
AUTH_COOKIE_DOMAIN
AUTH_COOKIE_SECURE
AUTH_COOKIE_SAMESITE
AUTH_COOKIE_MAX_AGE_SECONDS
```

Set a strong `JWT_SECRET_KEY` outside source control before enabling auth outside
local development. `ANSIVERSA_AUTH_SECRET` must match the parent `web`
`ANSIVERSA_AUTH_SECRET` value so legacy parent `salt:hash` passwords can be
verified during login.

Local development defaults the auth cookie to HttpOnly, `Secure=false`,
`SameSite=lax`, and no domain. Production defaults to HttpOnly, `Secure=true`,
`SameSite=none`, and domain `.ansiversa.com`. Explicit auth cookie environment
values override these defaults. Browser clients also receive a readable
`ansiversa_has_session=1` hint cookie by default so guest shell loads can avoid
calling `/api/v1/auth/me`; this hint contains no token or user data.

## Astra AI Integration

The permanent app-level Astra integration standard is documented in:

```text
docs/astra-ai-integration-contract.md
```

Every Astra-enabled app must keep business logic inside the app module while
Astra orchestrates through the shared Assistant architecture. The contract
defines required `astra-ai.md` sections, backend and frontend responsibilities,
tool documentation requirements, OpenAI boundaries, privacy rules, and
validation expectations.

I1-009 establishes the contract only. User-data awareness, tool execution,
context provider work, app pilots, personal-data tools, migrations, and runtime
Astra orchestration require separate frozen tasks.

The Phase 1 user-data awareness governance contract is documented in:

```text
docs/astra-user-data-awareness-contract.md
```

This contract defines authenticated identity, app-owned data boundaries,
privacy rules, the OpenAI personal-context allowlist, audit model, retention
and deletion governance, and seeded verification environment rules. It does not
implement runtime personal-data access.

The shared Astra Tool Framework architecture is documented in:

```text
docs/architecture/astra-tool-framework.md
docs/architecture/astra-tool-registry.md
docs/architecture/astra-user-context-provider.md
```

I1-002 implements the runtime definition, context, executor, validation,
bounded result, safe audit-metadata, and deterministic demonstration-tool
foundation. It does not implement app-specific tools, the I1-012 Tool Registry,
I1-003 User Context Provider, write operations, AI memory, recommendations, or
App #101.

Personal-data tools are disabled by default through the server-owned
`ASTRA_PERSONAL_DATA_TOOLS_ENABLED=false` setting. Production must remain
disabled until persistent audit logging, user controls, deletion/export
handling, and seeded verification gates are approved and implemented. Tests and
governed non-production verification may enable the setting deliberately.

The permanent production-trust evidence standard is documented in:

```text
docs/astra-operational-readiness-specification.md
```

I1-023 defines readiness gates, control owners, evidence, pass/fail criteria,
audit, consent, retention, deletion, export, governed verification,
dependency/deployment compatibility, owner isolation, privacy, controlled
enablement, rollback, flag restoration, review, risk acceptance, and launch
authority. It is specification-only. It does not implement any control, enable
personal-data tools, approve operational readiness, or authorize production.

Permanent governance rule:

> Verification does not imply release. Release is a business decision informed
> by engineering evidence, not an engineering decision made because tests
> passed.

I1-012 implements the permanent Astra Tool Registry metadata and discovery layer
on top of the I1-002 framework. The registry exposes handler-free capability
metadata, including ownership, intents, authentication, owner-scope, read-only
state, version, enabled/disabled state, deprecated state, schemas, timeouts, and
documentation paths. It does not implement app-specific tools, persistent
registry storage, admin registry UI, I1-003 User Context Provider, OpenAI tool
orchestration, migrations, or App #101.

I1-003 implements the governed Platform User Context Provider in the Assistant
backend. The provider builds intent-driven profiles for minimal,
personalization, attention, and tool-execution context using backend auth,
canonical route validation, Favorites, Activity, Notifications, and safe
preference reads. It does not add a public context export endpoint, query
solution-app databases, change the frontend request contract, implement app
tools, add migrations, or expose backend user IDs to OpenAI.

I1-004 implements the first solution-app Astra pilot for Quiz. Quiz registers
app-owned read-only tools for progress, submitted-result platforms, recent
submitted attempts, topic performance, and deterministic next-platform guidance
through `app/modules/quiz/astra_tools.py` and documents the contract in
`app/modules/quiz/astra-ai.md`. Production personal-data execution remains
disabled by default through `ASTRA_PERSONAL_DATA_TOOLS_ENABLED=false`.

I1-005 implements the second solution-app Astra pilot for Course Tracker. Course
Tracker registers app-owned read-only tools for course progress, active courses,
completed courses, nearest completion, stalled courses, deadline summaries, and
deterministic next-course action through
`app/modules/course_tracker/astra_tools.py` and documents the contract in
`app/modules/course_tracker/astra-ai.md`. Course Tracker remains authoritative
for its database and business rules; Astra only orchestrates. Production
personal-data execution remains disabled by default through
`ASTRA_PERSONAL_DATA_TOOLS_ENABLED=false`.

I1-006 implements Astra Learning Intelligence as deterministic cross-app
orchestration over already registered Quiz and Course Tracker capabilities. It
executes at most one Quiz tool and one Course Tracker tool per request through
the Tool Registry, combines structured results into explainable learning
guidance, and introduces no direct app database access, framework redesign,
OpenAI tool orchestration, frontend contract change, migration, or App #101.

## Migrations

The default Alembic environment is configured for the parent/global database
only and reads `PARENT_DATABASE_URL` from app settings. Parent/global migrations
belong to this parent Alembic context under `migrations/parent/`. Mini-app
migrations use isolated Alembic contexts under `migrations/<app-slug>/`, such as
`migrations/research-assistant/`, and read that app's own `*_DATABASE_URL`.

Turso migrations also require `TURSO_AUTH_TOKEN`; Alembic reuses the parent
database engine so the same URL conversion and authentication settings apply to
the API and migrations.

Create a parent/global migration:

```bash
alembic revision --autogenerate -m "message"
```

Apply migrations:

```bash
alembic upgrade head
```

Apply isolated Quiz migrations:

```bash
alembic -c quiz_alembic.ini upgrade head
```

Apply isolated Concept Explainer migrations:

```bash
alembic -c concept-explainer_alembic.ini upgrade head
```

Apply isolated Dictionary+ migrations:

```bash
alembic -c dictionary-plus_alembic.ini upgrade head
```

Apply isolated Lesson Builder migrations:

```bash
alembic -c lesson-builder_alembic.ini upgrade head
```

Apply isolated Memory Trainer migrations:

```bash
alembic -c memory-trainer_alembic.ini upgrade head
```

Apply isolated Research Assistant migrations:

```bash
alembic -c research-assistant_alembic.ini upgrade head
```

Apply isolated AI Notes Summarizer migrations:

```bash
alembic -c ai-notes-summarizer_alembic.ini upgrade head
```

Apply isolated Meeting Minutes AI migrations:

```bash
alembic -c meeting-minutes-ai_alembic.ini upgrade head
```

Apply isolated Email Assistant migrations:

```bash
alembic -c email-assistant_alembic.ini upgrade head
```

Apply isolated Proposal Writer migrations:

```bash
alembic -c proposal-writer_alembic.ini upgrade head
```

Apply isolated Invoice and Receipt Maker migrations:

```bash
alembic -c invoice-receipt-maker_alembic.ini upgrade head
```

Apply isolated Contract Generator migrations:

```bash
alembic -c contract-generator_alembic.ini upgrade head
```

Apply isolated Presentation Designer migrations:

```bash
alembic -c presentation-designer_alembic.ini upgrade head
```

Apply isolated Career Planner migrations:

```bash
alembic -c career-planner_alembic.ini upgrade head
```

Quiz taxonomy routes are read-only and protected by the existing current-user
dependency:

```text
GET /api/v1/quiz/platforms
GET /api/v1/quiz/subjects
GET /api/v1/quiz/topics
GET /api/v1/quiz/roadmaps
```

The secure Quiz attempt lifecycle is also protected by the existing current-user
dependency:

```text
POST /api/v1/quiz/attempts
GET  /api/v1/quiz/attempts/{attempt_id}
POST /api/v1/quiz/attempts/{attempt_id}/submit
```

Quiz attempt tables are intentionally excluded from parent Alembic. After
reviewing the configured `QUIZ_DATABASE_URL`, apply the isolated Quiz migration
chain with:

```bash
alembic -c quiz_alembic.ini upgrade head
```

The Quiz migration chain uses `quiz_alembic_version`, creates
`QuizAttempt` and `QuizAttemptQuestion`, and never creates parent/global tables.
Autogeneration is restricted to these approved API-managed Quiz tables so it
cannot alter legacy Quiz taxonomy, question, or result tables.
`python -m scripts.setup_quiz_attempt_tables` remains a convenience wrapper for
the same isolated Alembic upgrade.

## Auth

The auth module provides the parent/global authentication foundation only.
Mini-app-specific auth is intentionally not introduced here.

```text
/api/v1/auth/status/
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/logout
POST /api/v1/auth/forgot-password
POST /api/v1/auth/reset-password
POST /api/v1/auth/change-password
GET  /api/v1/auth/me
```

Use `/api/v1/auth/login` from Swagger `/docs` to get a bearer token, then use
Authorize to test protected routes such as `/api/v1/auth/me`.
Successful login responses also set the API-managed HttpOnly
`ansiversa_session` cookie for browser clients plus the readable
`ansiversa_has_session=1` hint cookie. Protected endpoints prefer an explicit
bearer token and otherwise use the auth cookie. Logout clears both cookies.

Current scope is aligned to the real parent `web` auth schema. The API uses
parent-compatible `Users` and `Roles` tables, including `Users.name`,
`Users.passwordHash`, `Users.roleId`, and `Users.status`. Passwords are stored
with secure hashing, and `passwordHash` is never exposed in API responses.
Password reset requests always return a generic response. Raw reset tokens are
never stored; only expiring token hashes are persisted. Change-password reuses
the current cookie-or-bearer authenticated user and does not modify the active
session.
API-created users use Argon2 hashes. Existing parent web users with legacy
`salt:hash` HMAC-SHA256 password hashes are supported during login; after a
successful legacy login, the submitted password is rehashed with Argon2 and
`Users.passwordHash` is upgraded automatically.
For parent compatibility, missing or empty legacy `Users.status` values are
treated as active, while `disabled`, `inactive`, and `suspended` users are
blocked.

Safe auth responses include only parent-compatible user fields:

```text
id
email
name
roleId
status
plan
planStatus
countryCode
regionCode
city
timezone
avatarUrl
createdAt
updatedAt
```

Registration stores new users with `status = active` and default `roleId = 2`.
If the default member role is missing, registration creates an idempotent
`Roles` row for `id = 2`, `key = member`.

JWT access tokens stay minimal:

```text
sub
email
type = access
```

Billing/session claims, refresh tokens, social login, full role CRUD, session
tables, and mini-app auth are intentionally not enabled yet.

## Admin and Audit Foundation

The admin foundation adds a reusable admin dependency and a small verification
route only.

```text
GET /api/v1/admin/status
```

Admin access currently means an authenticated active user with `roleId = 1`,
matching the parent web convention. Unauthenticated or invalid bearer tokens
continue to return `401`; authenticated non-admin users return `403`.

The audit foundation adds the parent-compatible `AuditLogs` table and a reusable
`write_audit_log(...)` helper for future admin writes. The helper records actor,
action, entity, metadata, IP address, user agent, and timestamp. Admin CRUD,
audit log listing, permissions registry, billing APIs, and destructive
operations are intentionally deferred.

## Admin Categories

The admin categories module provides protected category management endpoints
aligned with the parent web `adminCategories` Astro action behavior.

```text
GET    /api/v1/admin/categories
POST   /api/v1/admin/categories
PATCH  /api/v1/admin/categories/{category_id}
DELETE /api/v1/admin/categories/{category_id}
```

All routes require an active admin user (`roleId = 1`). Listing uses the web
action defaults and response shape: `page`, `pageSize`, `q`, `status`, `sort`,
`dir`, `items`, `total`, and `totalPages`, with `appsCount` included per
category. Create/update preserve the `cat_` id convention, normalize keys like
the web action, prevent duplicate key/slug conflicts, update `updatedAt`, and
write audit logs. Delete is blocked while any app references the category.

Intentional API difference: search also covers `description`, matching the
Phase 16 API requirement; the current parent web action searches name, id, slug,
and key. Billing APIs, permissions registry, and audit log listing remain
deferred.

## Admin Apps

The admin apps module provides protected app registry management endpoints
aligned with the parent web `adminApps` Astro action behavior.

```text
GET    /api/v1/admin/apps
GET    /api/v1/admin/apps/meta
POST   /api/v1/admin/apps
PATCH  /api/v1/admin/apps/{app_id}
DELETE /api/v1/admin/apps/{app_id}
```

All routes require an active admin user (`roleId = 1`). Listing follows the web
action response shape with `items`, `total`, `page`, `pageSize`, `totalPages`,
`sort`, and `dir`, includes `categoryName`, parses capabilities safely, and
supports web-action sorting values such as `newest`, `name-asc`,
`category-desc`, `status-asc`, `featured-desc`, and `updated-desc`. Create and
update normalize key/slug and URLs, validate category existence, prevent
duplicate key/slug conflicts, serialize capabilities using the parent catalog,
update `updatedAt`, and write audit logs. Delete follows the current parent web
action behavior: it deletes the app row and writes an audit log when successful.

Intentional API differences: search also covers `description` per the Phase 17
API requirement; list accepts `launchStatus`, `visibility`, and `pricingGate`
filters plus `sortBy`/`sortDirection` aliases; meta returns categories plus
allowed status/launch/visibility/pricing values and capability options so API
clients can build forms without hardcoding the parent registry constants.
Admin users/roles, billing APIs, permissions registry, and audit log listing
remain deferred.

## Admin Users

The admin users read foundation provides protected user list and detail
endpoints aligned with the parent web `adminUsers` Astro action behavior.

```text
GET /api/v1/admin/users
GET /api/v1/admin/users/{user_id}
```

All routes require an active admin user (`roleId = 1`). Listing follows the
web action defaults and response shape with `items`, `total`, `page`,
`pageSize`, `totalPages`, `sort`, and `dir`, includes role information, and
returns safe location/profile fields only. Detail returns safe admin-readable
fields and never exposes `passwordHash`, reset tokens, or raw Stripe customer
IDs.

Intentional API differences: list search also covers `city`, `countryCode`,
and `regionCode` per the Phase 18 API requirement; list accepts read-only
filters for `status`, `plan`, `planStatus`, and `countryCode` plus
`sortBy`/`sortDirection` aliases. Admin user create/update/delete and admin
password/reset actions remain deferred.

## Profile and Preferences

The profile module provides protected current-user profile and settings
foundation endpoints. These endpoints reuse the auth current-user dependency
and do not duplicate authentication logic.

```text
GET   /api/v1/me/profile
PATCH /api/v1/me/profile
GET   /api/v1/me/preferences
PUT   /api/v1/me/preferences
GET   /api/v1/users/me/settings
PATCH /api/v1/users/me/settings
```

Profile updates are intentionally limited to:

```text
name
countryCode
regionCode
city
timezone
```

Profile endpoints do not allow email, role, status, billing fields, or password
changes. Preferences use the parent-compatible `UserPreferences` table and
auto-create a default row when missing (`productUpdates = false`,
`securityAlerts = true`, `theme = null`).

The separate user-settings foundation returns defaults when no `UserSettings`
row exists and creates the row on first patch. Supported fields are `theme`
(`system`, `light`, `dark`), `language` (`en`, `ta`, `ar`), and
`marketing_emails`.

## Favorites

The favorites module provides protected current-user favorites endpoints backed
by the parent-compatible `Favorites` table.

```text
GET    /api/v1/me/favorites
POST   /api/v1/me/favorites
DELETE /api/v1/me/favorites/{app_id}
```

Favorites list responses include the favorite id, timestamp, and safe app
catalog fields needed by web/mobile clients. Adding a favorite is idempotent
for an existing user/app pair. Phase 11 uses conservative discovery checks only:
the app must exist, `visibility = public`, `status = live`, and
`launchStatus = live`. Advanced pricing/entitlement gating is deferred.

## Notifications

The notifications module provides protected current-user notification endpoints
backed by the parent-compatible `Notifications` table.

```text
GET   /api/v1/me/notifications
GET   /api/v1/me/notifications/unread-count
PATCH /api/v1/me/notifications/{notification_id}
POST  /api/v1/me/notifications/mark-all-read
```

Notification responses include safe read-state fields only: `id`, `title`,
`message`, `type`, `isRead`, `createdAt`, `readAt`, and `metadataJson`. All
operations are scoped to the authenticated user. Listing is newest first with a
default limit of 50. Notification webhook/event processing is intentionally
deferred.

## Dashboard

The dashboard module provides a protected current-user read foundation backed by
the parent-compatible `Dashboard` table.

```text
GET /api/v1/me/dashboard
```

The response includes the authenticated user, favorite count, unread
notification count, recent apps, and dashboard items. Dashboard items are
ordered by newest `lastActivityAt` first and parse `summaryJson` defensively,
returning an empty summary when stored JSON is missing or invalid.

This phase is read-only and partially complete. Dashboard write APIs, activity
webhooks, cross-app summary fetching, admin APIs, and billing APIs are
intentionally deferred.

## Content Metadata

Typed mini-app overview content is stored in the existing parent `Metadata`
table with keys in the form `overview:{app_slug}` and served through:

```text
GET /api/v1/content/metadata/overview/{app_slug}
```

Source overview JSON files live under
`app/modules/content/data/overview`. Validate and recursively upsert all
overview files into the configured parent database with:

```bash
python3 -m app.modules.content.scripts.sync_overview_metadata
```

The sync command validates every file against `OverviewResponse` before any
database writes and fails clearly for invalid JSON, schema mismatches, or
duplicate filename-derived metadata keys. After syncing the canonical
`overview:{app_slug}` records, it removes the obsolete unprefixed `quiz` and
`resume-builder` overview keys when present.

## Apps Catalog

The apps catalog module provides public read endpoints for parent/global app
metadata. It does not connect mini-app databases or migrate existing web logic.
Parent Apps Catalog data depends on Categories through `Apps.categoryId`.

```text
GET /api/v1/apps/
GET /api/v1/apps/{app_key}
GET /api/v1/categories/
GET /api/v1/categories/{category_key_or_slug}
```

Pricing, entitlements, and app-specific data are intentionally not part of this
foundation phase.

## FAQs

The FAQs module provides a public read foundation backed by the parent-compatible
`Faqs` table.

```text
GET /api/v1/faqs
```

Supported query parameters:

```text
appKey
q
page
pageSize
audience
```

The endpoint returns only published FAQs. By default it returns parent FAQs
where `appKey IS NULL` and `audience = user`. Supplying `appKey` scopes results
to that app. Search checks `question` and `answer`; results sort by
`sortOrder ASC`, then `createdAt DESC`, with pagination metadata included.

Admin FAQ CRUD, audit logging, billing, admin APIs, and dashboard changes are
intentionally deferred.

## OpenAPI and Generated Clients

The full OpenAPI schema is available at:

```text
/openapi.json
```

Frontend clients can generate TypeScript SDKs and types from OpenAPI contracts.
Operation IDs are intentionally stable and normalized so generated method names
remain predictable across releases.

The full ecosystem schema is not always the right input for mini-app frontends.
Future mini-app SDKs should generate from module-specific schemas once those are
introduced.

Recommended future schema endpoints:

```text
/openapi.json
/openapi/parent.json
/openapi/quiz.json
/openapi/resume-builder.json
```

For now, only the full `/openapi.json` schema is implemented.

## Deployment

The API is deployed on Vercel and served from:

```text
https://api.ansiversa.com
```

After deployment, verify `/`, `/docs`, `/api/v1/health/`, `/api/v1/health/db/`,
`/api/v1/auth/status/`, `/api/v1/auth/me`, `/api/v1/me/profile`,
`/api/v1/me/preferences`, `/api/v1/me/favorites`,
`/api/v1/me/notifications`, `/api/v1/me/notifications/unread-count`,
`/api/v1/me/dashboard`, `/api/v1/apps/`, `/api/v1/categories/`, and
`/api/v1/faqs`, plus protected workflow dashboards such as
`/api/v1/invoice-receipt-maker/dashboard`, and protected admin verification at
`/api/v1/admin/status` and `/api/v1/admin/categories`.
### Notifications Center

Authenticated notification endpoints live under `/api/v1/me/notifications`: `GET /`, `GET /unread-count`, `PATCH /{notification_id}/read`, `PATCH /read-all`, and `GET/PATCH /preferences`. Lists use `page`/`pageSize`, optional `unreadOnly`, and optional bounded `type`, and return `items`, `total`, `unreadCount`, `page`, and `pageSize`. The existing parent `Notifications` table is authoritative; raw metadata is never exposed and action routes are internal-route validated.
### Universal Activity Timeline

Authenticated `GET /api/v1/activity` supports `page`, `pageSize`, bounded `type`, and canonical app-slug filters; `GET /api/v1/activity/summary` returns the latest five safe items. Dedicated `POST /api/v1/activity/navigation` and `/platform-event` endpoints accept only governed navigation or generic shared-shell events. There is no unrestricted activity-create or admin-browse endpoint. The parent `ActivityTimeline` table retains the latest 1,000 owner-scoped records and stores safe summaries rather than user content.
