# JSON Formatter Backend Story

## Purpose

The backend supports JSON Formatter as a live browser-first mini app through the parent Apps catalog and API-driven overview metadata. The current V1 product intentionally keeps pasted JSON payloads out of backend systems.

## Workflow

The backend responsibility is Catalog Discovery -> Overview Metadata -> Frontend Runtime Handoff. Runtime formatting, minification, validation, error display, and copying happen entirely in the frontend after the shell routes the user into `/json-formatter/formatter`.

## User Journey

Users discover JSON Formatter through the shared platform catalog, open the overview, and continue into the formatter. From that point, JSON input, parsed output, validation status, and copy actions remain browser-local. The backend only supplies the metadata needed for discovery, navigation, and live status.

## Database Design

No app-specific runtime database tables are required for V1. The parent Apps catalog stores JSON Formatter's status, launch status, version, slug, category, and capability metadata. The overview content data stores the app description and workflow metadata served to the frontend. Pasted JSON, formatted output, validation errors, and snippets are not persisted.

## API Design

There are no dedicated `/api/v1/json-formatter/*` runtime endpoints in V1. Shared catalog and overview endpoints expose the app metadata used by the shell and overview page. This boundary exists because JSON payloads may contain sensitive data and can be formatted safely in the browser.

## Shared Components Used

The backend uses the shared Apps catalog and content metadata systems. This doc-only module path exists to satisfy the Story Documentation Contract for a live browser-first app while making the no-runtime-backend decision explicit.

## Performance Considerations

The primary JSON workflow avoids backend round trips, parser service latency, database writes, and server logs containing pasted JSON. Backend payloads remain limited to compact catalog and overview metadata.

## Current Status

The backend support is live at version `1.0.0`. The parent Apps catalog stores JSON Formatter as `active` with `launchStatus = live`.

## Known Limitations

V1 does not save snippets, run backend parsers, validate schemas, compare JSON documents, index JSON content, or provide shared team libraries.

## Future Enhancements

Future versions may add saved snippets, schema validation, JSON diffing, large-file handling, or team libraries. Persisted snippet features would require an app-specific backend module and index review.

## Current Implementation

Current version: `1.0.0`

Implemented:

* Parent Apps catalog live status
* API-driven overview metadata
* Explicit browser-first runtime boundary
* No app-specific runtime database tables
* No app-specific runtime API routes
* Current-state story documentation
