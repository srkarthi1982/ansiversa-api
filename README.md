# Ansiversa API

`ansiversa-api` is the central FastAPI backend platform for the Ansiversa ecosystem.
It provides a stable API foundation for parent services, mini-apps, future mobile apps,
AI services, and cross-app aggregation.

Production: https://api.ansiversa.com

Docs: https://api.ansiversa.com/docs

## Local Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
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
```

## Environment

Settings are loaded with `pydantic-settings` from environment variables and `.env`.
Do not commit secrets. Keep `.env` local only.

`PARENT_DATABASE_URL` controls the parent/global SQLAlchemy engine. Local development
falls back to SQLite:

```text
sqlite:///./ansiversa_api.db
```

Auth uses these environment variables:

```text
JWT_SECRET_KEY
JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES
```

Set a strong `JWT_SECRET_KEY` outside source control before enabling auth outside
local development.

## Migrations

Alembic is configured for the parent/global database only and reads
`PARENT_DATABASE_URL` from app settings. Parent/global migrations belong to this
parent Alembic context. Mini-app migrations should be introduced later only when
needed and kept isolated.

Create a parent/global migration:

```bash
alembic revision --autogenerate -m "message"
```

Apply migrations:

```bash
alembic upgrade head
```

## Auth

The auth module provides the parent/global authentication foundation only.
Mini-app-specific auth is intentionally not introduced here.

```text
/api/v1/auth/status/
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me
```

Use `/api/v1/auth/login` from Swagger `/docs` to get a bearer token, then use
Authorize to test protected routes such as `/api/v1/auth/me`.

Current scope is aligned to the real parent `web` auth schema. The API uses
parent-compatible `Users` and `Roles` tables, including `Users.name`,
`Users.passwordHash`, `Users.roleId`, and `Users.status`. Passwords are stored
with secure hashing, and `passwordHash` is never exposed in API responses.

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

## Profile and Preferences

The profile module provides protected current-user profile and settings
foundation endpoints. These endpoints reuse the auth current-user dependency
and do not duplicate authentication logic.

```text
GET   /api/v1/me/profile
PATCH /api/v1/me/profile
GET   /api/v1/me/preferences
PUT   /api/v1/me/preferences
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
`/api/v1/faqs`, plus protected admin verification at
`/api/v1/admin/status`.
