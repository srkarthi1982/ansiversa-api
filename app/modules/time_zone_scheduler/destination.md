# Time Zone Scheduler Destination

## App Name

Time Zone Scheduler

## Destination Status

Approved v1.0

## Final Product Vision

Time Zone Scheduler should become Ansiversa's trusted private meeting-time
comparison utility: a browser-first place to compare one proposed meeting time
across participant time zones, save useful local schedules, and reduce
cross-region planning mistakes without turning Ansiversa into a calendar
server, invitation platform, reminder system, or team scheduling suite.

At maturity, Time Zone Scheduler should help users answer practical questions
like "What time is this for everyone?", "Which zone is my own reference?",
"Will this meeting cross into another date for someone?", and "Which saved
times do I reuse often?" The product should improve scheduling clarity through
simple comparisons, explicit local records, and trustworthy time-zone handling.

The mature product should remain useful for remote work, interviews, client
calls, classes, family coordination, and travel planning while preserving the
privacy boundary that makes V1 valuable: meeting titles, participant zones, and
saved schedules stay local by default.

## Target Users

- Remote teams coordinating calls across regions.
- Recruiters scheduling interviews across candidates and panels.
- Freelancers and consultants planning client meetings in different countries.
- Students, teachers, and tutors arranging classes across time zones.
- Families and friends coordinating calls across countries.
- Travelers comparing home, destination, and participant times.
- Ansiversa users who need lightweight planning without calendar integration.

## Core User Problems

- Time-zone math is easy to get wrong, especially across dates.
- Users often need a quick comparison before creating a real calendar event.
- Many scheduling tools require accounts, invitations, availability polling, or
  calendar access when the user only needs a private comparison.
- Saved meeting-time ideas are scattered across chat, notes, calendars, and
  memory.
- Daylight saving changes and browser time-zone support can create confusion
  unless the product communicates limits clearly.
- Users need repeatable local planning without turning meeting metadata into
  backend scheduling data.

## Final Capabilities

- Create local schedules with title, base date, base time, base time zone,
  participant time zones, and a highlighted My Time zone.
- Compare the same meeting moment across all participant zones using
  browser-native time-zone conversion.
- Clearly show local date changes, local times, and the user's primary
  reference zone.
- Save, search, edit, duplicate, delete, and clear browser-local schedules.
- Show local insights such as total schedules, unique zones, most-used zone,
  average participants, recent schedules, and repeated planning patterns.
- Provide clearer validation for unsupported or misspelled IANA time-zone names.
- Explain browser and daylight-saving limitations when relevant.
- Offer import/export for browser-local backup and portability after review.
- Support calendar handoff or `.ics` export only through explicit user action.
- Provide keyboard-friendly schedule creation, review, edit, and delete flows.
- Preserve local privacy by default with no backend scheduling, invitations,
  reminders, calendar sync, or shared team state.

## Advanced Capabilities

- Browser-local schedule templates for recurring planning patterns.
- Optional `.ics` export for a single schedule after explicit user action.
- Import/export of local schedules for backup or device movement.
- Availability notes that remain local and do not become polling workflows.
- Travel mode for comparing home, destination, and meeting zones.
- DST transition warnings when a selected date is near a known offset change.
- Local favorite zones or zone groups for repeated teams.
- Explicit handoffs to calendar, task, or planning tools after governance
  review.
- Shared team schedules only after separate privacy, identity, sync, and
  architecture review.

## AI Opportunities

- Explain time-zone differences, date changes, and daylight-saving caveats in
  plain language.
- Suggest clearer meeting notes or schedule titles from user-entered context.
- Recommend fairer meeting windows based on selected participant zones after
  explicit user action.
- Summarize local scheduling patterns without sending schedule records by
  default.
- Help prepare calendar descriptions or follow-up messages from a selected
  schedule.
- Teach users what IANA time-zone names mean and why fixed offsets can be
  risky.

AI features must not receive meeting titles, participant zones, dates, notes,
calendar context, or travel details by default. Any AI handoff must be
explicit, privacy-reviewed, and clear about what local schedule data is being
sent.

## Ecosystem Connections

- Calendar-oriented future app: receive a selected schedule through explicit
  export or handoff if a governed calendar product exists later.
- Task Prioritizer or Project Tracker: turn a confirmed meeting into a task or
  project checkpoint only after explicit user action.
- Interview Scheduler: use time comparison as a supporting utility without
  absorbing interview workflow ownership.
- Travel planning tools: compare travel, home, and meeting zones through
  explicit handoff.
- Markdown Editor: export selected meeting-time notes into a planning note.
- Dashboard or profile areas: may show high-level usage only if no sensitive
  schedule details are collected.

## Weekly Return Value

Users return weekly when planning remote meetings, interviews, tutoring
sessions, client calls, family calls, or travel-related coordination. The
weekly value is a trusted comparison board: schedules are quick to create,
saved locally for reuse, and easier to understand than doing time-zone math in
chat messages or memory.

The mature product earns trust by staying focused on clarity. It helps users
compare and remember meeting times, but it does not quietly create calendar
events, send invitations, schedule reminders, or sync meeting details to a
server.

## Success Criteria

- Users can create and understand a multi-zone schedule quickly.
- My Time is visually and semantically clear in every comparison.
- Date changes across zones are easy to notice.
- Saved schedules remain local by default and are easy to find, edit,
  duplicate, and delete.
- Time-zone validation and unsupported-browser states are helpful.
- Local insights improve repeat planning without collecting backend schedule
  data.
- Any calendar export, import/export, AI assistance, or cross-app handoff is
  explicit and privacy-reviewed.
- The product does not drift into calendar hosting, invitations, reminders,
  availability polling, team scheduling, or cloud synchronization.

## Journey Progress

Current Position: 70 / 100
Destination: 100 / 100
Remaining Journey: 30 / 100

This estimate describes product maturity, not feature completion. Time Zone
Scheduler already has a strong live V1 with browser-local schedule creation,
native `Intl` conversion, My Time highlighting, saved schedules, search,
editing, duplication, deletion, clearing, insights, and no backend runtime. The
remaining journey is mostly scheduling-clarity maturity: clearer DST and
unsupported-zone guidance, import/export, optional calendar handoff, favorite
zones, accessibility polish, and careful governance around any AI, sharing,
notification, or calendar integration.

## Future Version Ideas

- V1.1: Improve date-change visibility, unsupported-zone guidance, validation,
  and privacy messaging.
- V1.2: Add import/export and local favorite zones or zone groups.
- V1.3: Add single-schedule `.ics` export or calendar handoff after governance
  review.
- V1.4: Add DST transition guidance, travel-mode comparisons, or schedule
  templates.
- V2: Consider AI schedule explanations, team sharing, availability workflows,
  or notifications only after governance review and destination update.

## Non Goals

Time Zone Scheduler is not intended to become:

- A calendar server.
- A calendar synchronization service.
- An invitation or RSVP platform.
- A reminder or notification system.
- A team availability polling product.
- A Calendly-style booking page.
- A recurring meeting rules engine.
- A workforce scheduling system.
- A shared team calendar.
- A travel booking or itinerary platform.

These directions should remain out of scope unless the destination itself is
reviewed and intentionally changed.

## Guiding Principles

Every Time Zone Scheduler feature should:

- Preserve browser-local privacy by default.
- Improve time-zone clarity before adding scheduling infrastructure.
- Make My Time and date changes easy to scan.
- Be honest about browser and daylight-saving limitations.
- Keep calendar handoffs explicit and user-controlled.
- Avoid invitations, reminders, polling, sync, or booking-platform scope.
- Prefer focused handoffs to adjacent tools instead of absorbing their
  responsibilities.
- Keep the app lightweight, fast, and understandable.

## Governance Notes

This destination is aspirational. It describes the target product direction,
not the current implementation and not an authorization to build every feature
now.

destination.md is not a promise of what will be built next. It is a
description of what the product could ultimately become if time, user value,
and platform direction remain aligned.

Product owner and Astra review are required before accepting, prioritizing, or
implementing any destination item. Particular care is needed before approving
calendar export, calendar sync, invitations, reminders, availability polling,
team sharing, AI assistance, import/export, or cross-app handoffs because
meeting data can reveal work patterns, relationships, locations, travel, and
private commitments.

## Last Governance Review

Product Owner: Approved on 2026-07-03. Time Zone Scheduler selected as the
next live app for the Destination Framework.
Astra: Approved on 2026-07-03. Journey Progress 70 / 100 accepted.
Codex: Drafted destination and identified governance discussion points.

Status:

Approved
