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
http://127.0.0.1:8000/api/v1/apps/
http://127.0.0.1:8000/api/v1/categories/
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
avatarUrl
createdAt
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
foundation phase. Favorites and Dashboard APIs are intentionally deferred.

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
`/api/v1/auth/status/`, `/api/v1/apps/`, and `/api/v1/categories/`.
