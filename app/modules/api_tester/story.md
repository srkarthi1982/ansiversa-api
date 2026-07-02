# API Tester

## Purpose

API Tester provides a browser-local workflow for saving and explicitly running API requests from the Ansiversa frontend. V1 avoids backend request execution so URLs, headers, bearer tokens, and payloads are not stored or proxied by Ansiversa servers.

## Workflow

The frontend provides a public overview and protected Workspace, Collections, History, and Insights routes. Users create request records, run them through browser fetch when CORS allows, and keep local run history.

## User Journey

Users start at `/api-tester`, continue to `/api-tester/workspace`, save local request metadata, run requests explicitly, then inspect saved requests, run history, and stats.

## Database Design

There is no API Tester database in V1. The backend does not store request URLs, headers, tokens, payloads, responses, or run history.

## API Design

There are no API Tester runtime APIs in V1. The backend only serves parent catalog and overview metadata through existing content endpoints. No backend proxy or server-side execution route exists for this app.

## Shared Components Used

The frontend uses the shared Ansiversa shell, page header, authenticated page state, form drawer, empty state, feedback stack, stat grid, and card patterns.

## Performance Considerations

V1 avoids heavy API testing libraries, Monaco, CodeMirror, backend upload/storage, cloud sync, and server-side execution. The backend footprint is limited to overview metadata and documentation.

## Current Status

Workflow Ready. App #047 remains `comingSoon` and awaits Astra/Partner review before production promotion.

## Known Limitations

Browser execution may fail when a target API blocks cross-origin requests. V1 does not support backend proxying, shared collections, secret vaulting, file uploads, or synchronized history.

## Future Enhancements

Future versions may add safe environment variables, import/export, richer response inspection, or an explicitly approved proxy/runtime after privacy review.

## Current Implementation

The backend owns only catalog and overview metadata for API Tester. No backend runtime persistence or app-specific API module exists for request or response content.
