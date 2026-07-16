# Meeting Scheduler Market Study

## Identity

- Catalog: App #089
- Canonical name: Meeting Scheduler
- Slug: `meeting-scheduler`
- Category: Work & Planning
- Status: review-ready, not live

## User need

People often keep meeting time, invitees, response notes, and discussion topics in separate messages or documents. A focused personal scheduler can keep the planned record together without pretending to send invitations or synchronize an external calendar.

## Existing alternatives

Calendar suites are strong at delivery, reminders, conferencing, and shared availability. Team scheduling products optimize booking links and external coordination. Notes products capture agendas but rarely keep participant response state beside a structured schedule. Ansiversa should not duplicate those network effects. Its useful niche is an authenticated, owner-scoped planning record that remains simple and explicit.

## Product boundary

Meeting Scheduler stores meetings, participants, invitation-response labels, and ordered agenda items. It supports search, status and time-period filters, detail review, and summary counts. It does not send email, issue calendar invitations, host calls, check live availability, create conference links, or claim that a participant has actually received or responded to an invitation.

## Overlap review

- Interview Scheduler manages recruiting interviews and candidate-specific rounds; Meeting Scheduler is general-purpose.
- Time Zone Scheduler compares times; Meeting Scheduler records one chosen timezone on a scheduled meeting.
- Meeting Minutes AI organizes notes and follow-up after a meeting; Meeting Scheduler focuses on planning before and maintaining the scheduled record.
- No approved Event Planner app exists in the finalized 100-app catalog, so that identity must not be introduced.

## V1 decision

Build a protected Meetings list and Meeting detail workflow. Use three isolated tables and owner checks at every nested boundary. Keep external delivery and calendar integrations outside V1.
