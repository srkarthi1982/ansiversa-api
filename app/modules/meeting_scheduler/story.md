# Meeting Scheduler Story

Meeting Scheduler is App #089 (`meeting-scheduler`). It helps authenticated users keep general-purpose meeting schedules, participant response labels, and ordered agenda items together. It remains `comingSoon` with `version = null` while awaiting review.

The overview at `/meeting-scheduler` uses shared API-driven metadata. Explore opens `/meeting-scheduler/meetings`, the primary protected workflow. The list page provides dashboard counts, search, status and upcoming/past filters, pagination, meeting cards, and create/edit/delete actions. `/meeting-scheduler/meetings/:meetingId` shows the schedule, participants, and ordered agenda.

All meeting, participant, and agenda create/edit interactions use `AvFormDrawer`. Destructive actions use `AvRecordActions`, which opens the shared `AvConfirmDialog`. Shared authenticated state, page headers, cards, empty states, inline feedback, pagination, buttons, inputs, and API/store helpers are reused.

The backend uses the isolated `MEETING_SCHEDULER_DATABASE_URL` and three tables: `Meetings`, `MeetingParticipants`, and `MeetingAgendaItems`. Nested writes first resolve the parent meeting by authenticated owner. Meeting deletion cascades to child records. Pydantic validation enforces controlled statuses, optional email format, positive agenda duration, and an end time later than the start time.

API routes live under `/api/v1/meeting-scheduler`: dashboard; paginated meeting list/create; meeting detail/update/delete; nested participant create/update/delete; and nested agenda item create/update/delete. Operation IDs are stable and the generated frontend contract is the API boundary.

V1 deliberately excludes invitation delivery, calendar integration, conferencing, availability checking, reminders, AI generation, and external credentials. Participant response values are organizational labels entered by the owner, not proof of external communication.
