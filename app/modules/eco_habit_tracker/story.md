# Eco Habit Tracker Backend Story

## Purpose

The backend supports Eco Habit Tracker as a live browser-first mini app through the parent Apps catalog and API-driven overview metadata. The current V1 product intentionally keeps habit progress local to the browser instead of creating account-backed tracking tables.

## Workflow

The backend responsibility is Catalog Discovery -> Overview Metadata -> Frontend Runtime Handoff. Runtime habit filtering, daily completion toggles, streak calculation, and reset behavior happen in the frontend after the shell routes the user into `/eco-habit-tracker/tracker`.

## User Journey

Users discover Eco Habit Tracker through the shared platform catalog, open the overview, and continue into the tracker. From that point, search terms, selected filters, completed habit IDs, and streak history remain browser-local. The backend only supplies the metadata needed for discovery, navigation, and live status.

## Database Design

No app-specific runtime database tables are required for V1. The parent Apps catalog stores Eco Habit Tracker's status, launch status, version, slug, category, and capability metadata. The overview content data stores the app description and workflow metadata served to the frontend. Habit completion history and streak data are not persisted on the server.

## API Design

There are no dedicated `/api/v1/eco-habit-tracker/*` runtime endpoints in V1. Shared catalog and overview endpoints expose the app metadata used by the shell and overview page. This boundary exists because the current habit list and progress model are lightweight enough for browser-local tracking.

## Shared Components Used

The backend uses the shared Apps catalog and content metadata systems. This doc-only module path exists to satisfy the Story Documentation Contract for a live browser-first app while making the no-runtime-backend decision explicit.

## Performance Considerations

The primary habit workflow avoids backend round trips, database writes, and server logs containing personal habit activity. Backend payloads remain limited to compact catalog and overview metadata.

## Current Status

The backend support is live at version `1.0.0`. The parent Apps catalog stores Eco Habit Tracker as `active` with `launchStatus = live`.

## Known Limitations

V1 does not sync streaks, send reminders, calculate carbon impact, support social challenges, or provide account-backed habit history.

## Future Enhancements

Future versions may add account-backed streaks, reminders, impact estimates, goals, and challenges. Persisted progress features would require an app-specific backend module and index review.

## Current Implementation

Current version: `1.0.0`

Implemented:

* Parent Apps catalog live status
* API-driven overview metadata
* Explicit browser-first runtime boundary
* No app-specific runtime database tables
* No app-specific runtime API routes
* Current-state story documentation
