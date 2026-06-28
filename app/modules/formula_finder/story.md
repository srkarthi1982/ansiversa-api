# Formula Finder Backend Story

## Purpose

The backend supports Formula Finder as a live browser-first mini app through the parent Apps catalog and API-driven overview metadata. The current V1 product intentionally keeps formula search, bundled reference data, and favorites in the frontend.

## Workflow

The backend responsibility is Catalog Discovery -> Overview Metadata -> Frontend Runtime Handoff. Runtime formula search, category filtering, copying, and favorites happen in the frontend after the shell routes the user into `/formula-finder/finder`.

## User Journey

Users discover Formula Finder through the shared platform catalog, open the overview, and continue into the finder. From that point, formula queries, favorite IDs, copy actions, and result filtering remain browser-local. The backend only supplies the metadata needed for discovery, navigation, and live status.

## Database Design

No app-specific runtime database tables are required for V1. The parent Apps catalog stores Formula Finder's status, launch status, version, slug, category, and capability metadata. The overview content data stores the app description and workflow metadata served to the frontend. Formula favorites, search terms, and copied formulas are not persisted on the server.

## API Design

There are no dedicated `/api/v1/formula-finder/*` runtime endpoints in V1. Shared catalog and overview endpoints expose the app metadata used by the shell and overview page. This boundary exists because the current formula library is bundled and small enough to search locally.

## Shared Components Used

The backend uses the shared Apps catalog and content metadata systems. This doc-only module path exists to satisfy the Story Documentation Contract for a live browser-first app while making the no-runtime-backend decision explicit.

## Performance Considerations

The primary formula workflow avoids backend round trips and search-service latency. Backend payloads remain limited to compact catalog and overview metadata, and no formula search terms or favorites are logged by app-specific endpoints.

## Current Status

The backend support is live at version `1.0.0`. The parent Apps catalog stores Formula Finder as `active` with `launchStatus = live`.

## Known Limitations

V1 does not store account-backed formula collections, user formulas, worked examples, analytics, or symbolic derivation records.

## Future Enhancements

Future versions may add persisted formula collections, worked examples, expanded content packs, analytics, or API-backed favorites. Persisted features would require an app-specific backend module and index review.

## Current Implementation

Current version: `1.0.0`

Implemented:

* Parent Apps catalog live status
* API-driven overview metadata
* Explicit browser-first runtime boundary
* No app-specific runtime database tables
* No app-specific runtime API routes
* Current-state story documentation
