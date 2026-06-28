# Markdown Editor Backend Story

## Purpose

The backend supports Markdown Editor as a live browser-first mini app through the parent Apps catalog and API-driven overview metadata. The current V1 product intentionally keeps Markdown drafts and rendered HTML out of backend systems.

## Workflow

The backend responsibility is Catalog Discovery -> Overview Metadata -> Frontend Runtime Handoff. Runtime Markdown editing, preview rendering, copying, and file export happen entirely in the frontend after the shell routes the user into `/markdown-editor/editor`.

## User Journey

Users discover Markdown Editor through the shared platform catalog, open the overview, and continue into the editor. From that point, Markdown text, rendered HTML, stats, copy actions, downloads, clear, and reset actions remain browser-local. The backend only supplies the metadata needed for discovery, navigation, and live status.

## Database Design

No app-specific runtime database tables are required for V1. The parent Apps catalog stores Markdown Editor's status, launch status, version, slug, category, and capability metadata. The overview content data stores the app description and workflow metadata served to the frontend. Markdown drafts, rendered HTML, and exported files are not persisted.

## API Design

There are no dedicated `/api/v1/markdown-editor/*` runtime endpoints in V1. Shared catalog and overview endpoints expose the app metadata used by the shell and overview page. This boundary exists because draft rendering and export can be completed locally without server processing.

## Shared Components Used

The backend uses the shared Apps catalog and content metadata systems. This doc-only module path exists to satisfy the Story Documentation Contract for a live browser-first app while making the no-runtime-backend decision explicit.

## Performance Considerations

The primary editor workflow avoids backend round trips, document uploads, rendered HTML storage, and server logs containing draft content. Backend payloads remain limited to compact catalog and overview metadata.

## Current Status

The backend support is live at version `1.0.0`. The parent Apps catalog stores Markdown Editor as `active` with `launchStatus = live`.

## Known Limitations

V1 does not save account-backed documents, version history, collaboration data, uploaded assets, or rendered HTML records.

## Future Enhancements

Future versions may add saved documents, templates, asset uploads, version comparison, or collaboration. Those features would require an app-specific backend module, storage design, and index review.

## Current Implementation

Current version: `1.0.0`

Implemented:

* Parent Apps catalog live status
* API-driven overview metadata
* Explicit browser-first runtime boundary
* No app-specific runtime database tables
* No app-specific runtime API routes
* Current-state story documentation
