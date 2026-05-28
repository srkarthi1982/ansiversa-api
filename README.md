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

Current scope includes parent users, password hashing, JWT access tokens, and
the current-user dependency. Refresh tokens, social login, roles, session
tables, and mini-app auth are intentionally not enabled yet.

## Deployment

The API is deployed on Vercel and served from:

```text
https://api.ansiversa.com
```

After deployment, verify `/`, `/docs`, `/api/v1/health/`, `/api/v1/health/db/`,
and `/api/v1/auth/status/`.
