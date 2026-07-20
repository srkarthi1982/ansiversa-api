# Ansiversa Platform Story

## Document Status

Status: Platform Story v1.0  
Subject: Ansiversa parent platform  
Created: 2026-07-10  
Framework: Story Framework v1.0  
Scope: Current implementation truth for `ansiversa-api`

## Product Summary

`ansiversa-api` is the central FastAPI backend platform for the Ansiversa
ecosystem. It provides the API foundation for the parent platform, mini-apps,
future mobile apps, AI services, and cross-app aggregation.

Production API:

```text
https://api.ansiversa.com
```

API documentation:

```text
https://api.ansiversa.com/docs
```

## Current Role In The Ecosystem

The parent API is responsible for shared platform capabilities:

- Authentication.
- User profile and preferences.
- Favorites.
- Notifications.
- Dashboard data.
- Content metadata.
- App catalog.
- Categories.
- FAQs.
- Admin and audit foundations.
- Mini-app route registration.
- Parent/global database migrations.
- Shared configuration and deployment foundation.

Individual mini-apps remain modular. Persistent mini-apps use isolated database
configuration and separate Alembic contexts where needed.

## Current Technical Foundation

The platform currently uses:

- Python 3.13.
- FastAPI.
- SQLAlchemy.
- Alembic.
- Pydantic settings.
- Turso/libSQL for remote database deployment.
- SQLite fallback for local development.
- Vercel deployment configuration.

The parent/global database is controlled by:

```text
PARENT_DATABASE_URL
```

Local development falls back to:

```text
sqlite:///./ansiversa_api.db
```

## Authentication Story

The platform includes authentication endpoints for:

- Register.
- Login.
- Logout.
- Forgot password.
- Reset password.
- Change password.
- Current user lookup.
- Auth status.

Authentication uses an HttpOnly session cookie and a readable session hint
cookie. Production cookie settings are designed for the `.ansiversa.com` domain.

The API supports current password hashing while also maintaining compatibility
with legacy parent `salt:hash` password verification.

## Mini-App Architecture Story

Mini-apps live under:

```text
app/modules/
```

The repository currently contains 72 module directories. Persistent apps can
own separate database URLs and separate Alembic contexts. This preserves app
boundaries and avoids forcing every app into one large schema.

This architecture supports Ansiversa's product philosophy:

- Shared platform foundation.
- Focused app responsibilities.
- Isolated app data where appropriate.
- Independent app evolution.
- Platform-wide discovery and governance.

## Documentation Story

Ansiversa now treats documentation as part of product completion.

Every app should follow this lifecycle:

```text
market-study.md
        |
        v
destination.md
        |
        v
story.md
        |
        v
marketing.md
```

At the time this platform story was created:

- 55 app-level `marketing.md` files exist.
- No module with a `story.md` is missing its corresponding `marketing.md`.
- The parent platform now follows the same four-document lifecycle.
- `AGENTS.md` records the documentation contract as a permanent development
  standard.

## Current Product Truth

Ansiversa currently provides a platform foundation and a fixed curated catalog
of 100 individual solution apps. It is not yet a fully mature AI operating
system, payment platform, or cross-app intelligence layer.

Current truthful claims:

- Ansiversa has a central API foundation.
- Ansiversa supports shared parent services.
- Ansiversa hosts modular mini-app APIs.
- Ansiversa uses a permanent 100-app catalog and category model.
- Ansiversa AI Assistant uses backend-owned deterministic public knowledge
  retrieval from the Canonical AI Knowledge Registry through
  `/api/v1/assistant/query`.
- Ansiversa has a formal documentation lifecycle.
- Ansiversa has completed `marketing.md` coverage for live story-backed apps.

Claims to avoid today:

- Do not claim every app is AI-powered.
- Do not claim cross-app AI intelligence is fully implemented.
- Do not claim Stripe subscriptions or entitlements are live unless verified.
- Do not claim mobile apps are live unless implemented.
- Do not claim Ansiversa replaces professional advice.
- Do not imply Ansiversa will routinely add apps beyond the permanent
  100-app boundary.

## AI Knowledge Foundation

The AI Knowledge Foundation provides a generated, backend-owned canonical
knowledge registry for the parent platform, public/account/legal pages, 14
categories, and exactly 100 solution apps. It deterministically derives public
purpose, audiences, current capabilities, use cases, aliases, related apps, and
separately marked future direction from allowlisted route and metadata sources.
Visibility and source traceability are explicit, and build/check commands
enforce drift and secret scanning. Assistant retrieval now consumes the cached
registry as its normal knowledge source. Public AI SEO artifacts are generated
from the same registry and exposed through governed public deployment routes.

## Current Limitations

Known platform limitations:

- OpenAI-powered app generation and cross-app intelligence are future platform
  capabilities, not current assistant retrieval behavior.
- Stripe monetization and entitlement logic are future platform capabilities.
- Cross-app dashboards and recommendations are still evolving.
- Some apps are V1 or workflow-ready rather than mature full-featured products.
- Documentation must continue to stay synchronized with implementation.
- Platform-level branding, frameworks, and marketing playbook documents are
  future governance opportunities.

## Strategic Implementation Pattern

Ansiversa has developed a repeatable product pattern:

1. Research the market.
2. Define the destination.
3. Implement the current product.
4. Record the story.
5. Communicate through governed marketing.
6. Use feedback to refine the market understanding.

This turns the repository into more than code. It becomes institutional product
memory.

## Revision History

- 2026-07-20: Updated AI Knowledge Foundation status for public AI SEO
  publishing and deployment readiness.
- 2026-07-10: Created platform-level story document for `ansiversa-api`.
