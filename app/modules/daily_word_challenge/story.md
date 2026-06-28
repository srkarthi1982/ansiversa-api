# Daily Word Challenge Backend Story

## Purpose

Daily Word Challenge is a live browser-first vocabulary mini app. The backend
supports it through the parent Apps catalog and API-driven overview metadata,
while the current runtime challenge, word list, and progress state remain
frontend-owned.

## Workflow

The backend responsibility supports the Discover Word -> Filter Vocabulary ->
Mark Learned -> Track Local Streak workflow. Runtime interaction stays in the
frontend. Backend metadata lets the shared shell present the app consistently as
live and route users into `/daily-word-challenge/challenge`.

## User Journey

Users open the daily challenge, see the deterministic word for the day, filter
the bundled vocabulary list, mark words as learned for the current date, and
track a local streak from browser storage.

## Database Design

No app-specific runtime database tables are required for V1. The parent Apps
catalog stores the live status and version. Content metadata stores the overview
payload served to the frontend. User progress is intentionally local to the
browser in the current implementation.

## API Design

The backend exposes shared platform catalog and overview metadata endpoints for
this app. There are no dedicated Daily Word Challenge runtime endpoints in V1
because the vocabulary data and progress logic run locally in the frontend.

## Shared Components Used

The backend uses the shared Apps catalog and content metadata systems. This
doc-only module path documents the backend boundary required by the Story
Documentation Contract for a live browser-first app.

## Performance Considerations

The primary workflow avoids backend round trips. The API only serves compact
catalog and overview metadata for discovery and navigation. Local progress
avoids storing personal vocabulary activity on the server.

## Current Status

The backend support is approved live at version `1.0.0`. The parent Apps
catalog stores Daily Word Challenge as `active` with `launchStatus = live`.

## Known Limitations

V1 uses bundled challenge data and browser-local progress. It does not sync
streaks to the account, adapt words by skill level, or preserve progress across
devices.

## Future Enhancements

Future versions may add account-backed streaks, difficulty bands, Dictionary+
integration, reminders, and server-backed vocabulary progress.

## Current Implementation

Current version: `1.0.0`

Implemented:

* Parent Apps catalog live status
* API-driven overview metadata
* Browser-first runtime boundary documented in the backend repo
* Current-state story documentation
