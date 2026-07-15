# First Aid Guide Story

## Purpose

First Aid Guide gives users organized educational first-aid reference topics. It is a learning and preparedness tool, not an emergency service, doctor, diagnosis system, or treatment advisor.

## Workflow

Users browse guide topics, search and filter by category, open guide details, bookmark useful topics, and review recently viewed or most-viewed topics.

## User Journey

The user opens `/first-aid-guide/guides`, searches or filters topics, reads concise educational guidance, sees what to avoid and when to seek emergency help, and bookmarks useful topics.

## Database Design

The module owns an isolated database configured by `FIRST_AID_GUIDE_DATABASE_URL`.

Tables:

- `FirstAidCategories`
- `FirstAidGuides`
- `UserGuideBookmarks`
- `UserGuideHistory`

The Alembic version table is `first_aid_guide_alembic_version`.

## API Design

The API prefix is `/api/v1/first-aid-guide`.

Routes cover dashboard, insights, category CRUD, guide CRUD, guide browsing, guide detail, bookmark, unbookmark, and view-history tracking.

## Shared Components Used

The frontend uses the shared authenticated page wrapper, API client, store helpers, overview page, cards, and app shell routing.

## Performance Considerations

Indexes cover category ordering, guide category/order lookups, guide title, reviewed date, user bookmarks, and user history by guide and viewed date.

## Current Status

Approved live at version `1.0.0` after Astra review, Partner approval, production-configured isolated database migration verification, backend database-authentication fix verification, production Apps row promotion, overview metadata sync, and manual browser workflow verification. Destination metadata is synced at `20 / 100`, status `approved`, reviewed on `2026-07-15`.

## Known Limitations

V1 has concise seed content only, no offline mode, no external medical APIs, no emergency dispatch, and no AI.

## Future Enhancements

Possible future improvements include reviewed content expansion, printable preparedness checklists, and offline caching after approval.

## Current Implementation

The production catalog row is `active` / `live` / `1.0.0`. The implementation provides system-managed guide content, owner-scoped bookmarks/history, FastAPI endpoints, SQLAlchemy models, Pydantic schemas, Alembic migration, React routes, typed API integration, Zustand state, and readiness documentation.
