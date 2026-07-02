# Time Zone Scheduler

## Purpose

Time Zone Scheduler supports a privacy-first browser-local workflow for comparing meeting times across participant time zones. V1 keeps meeting titles, dates, participant zones, and saved schedules out of backend persistence.

## Workflow

The frontend provides a public overview and protected Scheduler, Schedules, and Insights routes. Users create a local schedule, compare converted times through browser-native `Intl` APIs, and save schedules in browser storage.

## User Journey

Users start at `/time-zone-scheduler`, continue to `/time-zone-scheduler/scheduler`, create a schedule with a highlighted My Time zone, then inspect saved schedules and local insights.

## Database Design

There is no Time Zone Scheduler database in V1. The backend does not store schedules, participant zones, calendar events, invitations, reminders, or notification state.

## API Design

There are no Time Zone Scheduler runtime APIs in V1. The backend only serves parent catalog and overview metadata through existing content endpoints. No backend scheduling, calendar sync, notification, invitation, or cloud synchronization route exists for this app.

## Shared Components Used

The frontend uses the shared Ansiversa shell, authenticated page state, page header, form drawer, empty state, feedback stack, stat grid, record actions, and card patterns.

## Performance Considerations

V1 avoids calendar SDKs, scheduler libraries, backend upload/storage, cloud sync, notification services, and heavy time-zone packages. The backend footprint is limited to overview metadata and documentation.

## Current Status

Approved Live. App #048 is promoted to `active` / `live` with version `1.0.0` after Astra/Partner approval, review data-model fix, production Apps row promotion, overview metadata sync, tracked catalog export update, validation, route/sidebar verification, and local-only persistence review.

## Known Limitations

Browser support determines available time-zone enumeration and conversion behavior. V1 does not support recurring meetings, availability polling, calendar export, invitations, notifications, team sharing, or synchronized history.

## Future Enhancements

Future versions may add approved calendar handoff, import/export, recurring meetings, availability notes, or shared team schedules after privacy and architecture review.

## Current Implementation

The backend owns only catalog and overview metadata for Time Zone Scheduler. No backend runtime persistence or app-specific API module exists for schedule content.
