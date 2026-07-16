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

- Journey progress: `20 / 100`
- Development state: Workflow Ready for review
- Destination approval: pending Partner/Astra review
- Reviewed date: not set
- Catalog version: `null`
- Launch status: `comingSoon`
- Production migration: verified at `20260716_0001_meeting_scheduler`

The score reflects a complete V1 workflow that has not received visual approval or live promotion. No approval date or live version is assigned.

## Safety and scope

All records are owner-scoped. Participant information is stored only as user-entered planning data. V1 has no email delivery, calendar sync, video-conferencing integration, availability lookup, reminders, AI generation, or third-party credentials.

## Review checklist

- Confirm overview copy and Explore route.
- Verify create/edit drawers for all three record types.
- Verify delete confirmation for all three record types.
- Verify list search, filters, pagination, and empty states.
- Verify invalid and inaccessible meeting IDs.
- Verify desktop and mobile layouts before approval.
