# Ansiversa Parent Backend Story

## Purpose

The Ansiversa parent backend is the central FastAPI platform that provides
shared authentication, catalog metadata, parent database access, public and
protected APIs, and registration points for isolated mini-app modules.

## Architecture

The backend is organized around a parent API layer plus isolated feature
modules. Shared platform concerns live under `app/core` and parent modules such
as auth, content, apps, favorites, notifications, profile, dashboard, admin, and
audit. Mini-app backends live under `app/modules/<module_name>` and expose their
own models, schemas, services, routes, and database configuration.

## Authentication

Authentication is handled through the shared auth module. Protected endpoints
reuse the current-user dependency so mini-app records remain scoped to the
signed-in user. Admin-only APIs use dedicated admin dependencies layered on top
of the same authenticated user model.

## Parent Database

The parent database owns shared platform data such as users, roles, apps,
categories, overview metadata, favorites, notifications, dashboard records,
preferences, audit logs, and other cross-app platform records.

## Mini App Isolation

Mini-app modules own their app-specific database connection, SQLAlchemy models,
Pydantic schemas, service layer, routes, and Alembic configuration. Records are
owner-scoped where user data is stored. Mini-app migrations remain isolated from
the parent database and from other mini-app databases.

## Module Registration

Modules are registered through `app/main.py` by including each router under the
shared API version prefix. This keeps the parent API surface explicit while
allowing each mini-app to maintain its own internal ownership boundary.

## Overview Metadata

The content module stores and serves overview metadata for approved apps.
Metadata files under `app/modules/content/data/overview` describe app overview
pages, CTAs, audience sections, resource sections, and technical sections. The
sync script writes those records into the parent metadata table.

## API Contracts

The backend follows the User API Response Contract and Platform Foundation v1
patterns. Dashboard and list endpoints return lightweight summaries. Detail
endpoints return full editable records. Protected endpoints enforce current-user
ownership checks before reading, updating, or deleting user records.

## Database Strategy

The backend uses a parent Alembic configuration for shared platform tables and
isolated Alembic configurations for mini-app databases. Phase-1 indexes support
the safest known query patterns for owner-scoped dashboards, lists, and detail
flows without over-indexing early schemas.

## Performance Considerations

The backend keeps list responses compact, avoids exposing unnecessary long
text/blob fields in dashboard APIs, uses explicit indexes for common
owner-scoped query paths, and keeps app databases isolated to reduce blast
radius between mini-app workflows.

## Current Status

The parent backend is the active API foundation for the Ansiversa platform. It
supports shared platform modules, live mini-app APIs, workflow-ready review
apps, overview metadata sync, generated OpenAPI types, and isolated mini-app
database ownership.

## Known Limitations

The parent backend does not automatically promote mini-apps to production.
Every mini-app still requires its own validation, review, production migration
decision, catalog promotion, and Partner approval before becoming live.

## Future Enhancements

Future backend work can add richer admin review tooling, production migration
dashboards, cross-app analytics, stronger metadata validation, additional shared
platform services, and deeper Story Book integration.

## Current Implementation

The current implementation includes FastAPI app initialization, shared settings,
CORS and timing middleware, stable OpenAPI operation IDs, parent database
configuration, auth routes, content and overview metadata routes, app catalog
routes, protected user modules, admin modules, isolated mini-app route
registration, isolated mini-app Alembic configurations, and living story files
for implemented modules.
