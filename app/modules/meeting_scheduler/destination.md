# Meeting Scheduler Destination

## Product destination

Meeting Scheduler should give an authenticated user one calm place to create a meeting, record its schedule and timezone, list participants and their response state, and order an agenda.

## V1 journey

1. Open the API-driven overview.
2. Explore `/meeting-scheduler/meetings`.
3. Create or edit a meeting in the shared form drawer.
4. Search and filter meeting records.
5. Open `/meeting-scheduler/meetings/:meetingId`.
6. Add or edit participants and agenda items in shared form drawers.
7. Delete records only through shared confirmation dialogs.

## Destination progress

approved

- Journey progress: `20 / 100`
- Development state: Approved Live
- Destination approval: approved by Astra and Partner for live promotion
- Reviewed date: 2026-07-19
- Catalog version: `1.0.0`
- Launch status: `live`
- Production migration: verified at `20260716_0001_meeting_scheduler`

Destination Status: approved
Current Journey Progress: 20 / 100
Reviewed At: 2026-07-19

The score reflects a complete V1 workflow that has received visual approval and live promotion.

## Safety and scope

All records are owner-scoped. Participant information is stored only as user-entered planning data. V1 has no email delivery, calendar sync, video-conferencing integration, availability lookup, reminders, AI generation, or third-party credentials.

## Review checklist

- Confirm overview copy and Explore route.
- Verify create/edit drawers for all three record types.
- Verify delete confirmation for all three record types.
- Verify list search, filters, pagination, and empty states.
- Verify invalid and inaccessible meeting IDs.
- Verify desktop and mobile layouts before approval.

## Promotion

Approved live at version `1.0.0` after Astra review, Partner manual verification, UI action polish, production-configured isolated migration verification, Apps row promotion, destination metadata sync, overview metadata sync, and validation.
