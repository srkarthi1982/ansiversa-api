# Meeting Minutes AI Destination

## App Name

Meeting Minutes AI

## Destination Status

Approved v1.0

## Final Product Vision

Meeting Minutes AI should become Ansiversa's focused meeting follow-up
workspace: a place to capture meeting context, notes, action items, summaries,
decisions, risks, and review history without turning Ansiversa into a live
transcription platform, meeting recorder, conferencing product, surveillance
tool, or project-management replacement.

At maturity, Meeting Minutes AI should help users answer practical questions
like "What happened in this meeting?", "What decisions were made?", "Who owns
the next action?", "What risks need review?", and "What should be exported or
handed off?" The product should make meeting follow-up reviewable while keeping
audio, calendar, and task-system integrations explicit.

The mature product should serve professionals, students, teams, consultants,
and operators who need structured meeting documentation after or during a
meeting. It should improve accountability and clarity, not silently record or
monitor conversations.

## Target Users

- Professionals tracking meetings, decisions, and follow-ups.
- Consultants documenting client discussions.
- Teams organizing action items from recurring meetings.
- Students and educators summarizing group discussions.
- Operators turning meeting notes into tasks and risks.
- Ansiversa users who need meeting records without recording infrastructure.
- Founders, managers, and client-facing teams who need decisions and commitments preserved after recurring discussions.
- Privacy-conscious users who need manual or imported minutes before any recording workflow is considered.

## Core User Problems

- Meeting notes, transcripts, decisions, and action items often get scattered.
- Users need participants, context, notes, actions, summaries, decisions, and
  risks connected.
- Action items lose value if owners, due dates, and status are not visible.
- AI summaries can misstate decisions if source notes are not reviewable.
- Audio recording and live transcription introduce consent, privacy, and legal
  concerns.
- Meeting tools can drift into recording, conferencing, surveillance, calendar
  sync, and project-management scope.
- Transcripts and summaries can become unused archives unless decisions and action items become reviewable execution records.
- Speaker labels, timestamps, and implied commitments need correction and source traceability before sharing.

## Final Capabilities

- Create, edit, archive, and delete long-lived meeting records.
- Create and edit notes or transcript text under meetings.
- Create and edit action items with owner, due date, status, and meeting
  context.
- Create and edit summaries with decisions, risks, and review status.
- Keep dashboard and list responses lightweight with previews, counts, status,
  and timestamps.
- Load full note, transcript, summary, decision, and risk text only through
  detail endpoints where needed.
- Support AI-assisted summaries only from user-provided notes or transcripts
  after governance review.
- Support explicit task handoffs without becoming the task system.
- Preserve review before any summary, decision, or action is treated as final.

## Advanced Capabilities

- AI-assisted summaries from user-provided notes or imported transcripts.
- Action item extraction with visible source references.
- Calendar import only after permission and privacy review.
- External task export after explicit user action.
- Attendee tagging and role notes.
- Decision and risk dashboards.
- Source-linked summaries that distinguish transcript text, AI output, and user-edited minutes.
- Client-facing approval and export review for sensitive meeting summaries.
- Search over user-owned meeting records after index review.
- Transcript import without audio storage.
- Live recording or transcription only after separate consent and legal review.

## AI Opportunities

- Summarize notes or transcripts into decisions, risks, and action items.
- Identify unclear ownership or missing due dates.
- Draft follow-up emails from reviewed summaries.
- Suggest task handoffs to Project Tracker or Task Prioritizer.
- Highlight unresolved questions and risks.
- Compare recurring meeting summaries for pattern review.

AI features must not silently record, transcribe, or monitor meetings. Meeting
context, notes, transcripts, participants, action items, decisions, risks, and
summaries should be sent to an AI provider only through an approved backend path
with explicit governance, consent consideration, privacy handling, and clear
product messaging.

## Ecosystem Connections

- Task Prioritizer or Project Tracker: receive selected reviewed action items.
- Email Assistant: prepare follow-up emails from reviewed summaries.
- Client Feedback Analyzer: receive selected client feedback from meeting notes.
- Proposal Writer: reuse approved client meeting context after user action.
- Calendar tools: remain separate unless a governed integration is approved.
- Dashboard areas may show high-level counts without exposing meeting content.

## Weekly Return Value

Users return weekly after meetings to capture notes, clarify ownership, review
decisions, update actions, and prepare follow-up communication. The weekly
value is reliable follow-up: meeting context, notes, action items, decisions,
risks, and summaries stay connected instead of being lost in scattered notes.

The mature product earns trust by documenting only what users intentionally
provide or import. It should not secretly record, infer attendance, monitor
conversations, or replace project management by default.

## Success Criteria

- Users can create, edit, review, and revisit meeting records easily.
- Notes, action items, summaries, decisions, and risks remain connected.
- Action items clearly show owner, status, and due date.
- Dashboard and list APIs stay lightweight while detail endpoints provide full
  content only where needed.
- Users understand whether summaries are manual, imported, or AI-assisted.
- Users can correct source notes, speaker context, decisions, and action items before export or handoff.
- Any AI summary, transcript import, calendar integration, task export, or live
  transcription is explicit and governance-reviewed.
- The product does not drift into recording, conferencing, surveillance,
  calendar ownership, or project-management replacement scope.

## Journey Progress

Current Position: 62 / 100
Destination: 100 / 100
Remaining Journey: 38 / 100

This estimate describes product maturity, not feature completion. Meeting
Minutes AI already has a strong live V1 with isolated backend storage,
meetings, notes, action items, summaries, owner-scoped APIs, lightweight
previews, detail endpoints, and protected frontend workflow pages. The
remaining journey is mostly follow-up-quality and governance maturity: AI
summaries, action extraction, task handoffs, calendar import, transcript import,
search, and careful review around consent, privacy, recording, and external
sync.

## Future Version Ideas

- V1.1: Improve action item filters, decision/risk review, and summary states.
- V1.2: Add task handoffs and follow-up email drafting.
- V1.3: Add transcript import and AI-assisted summaries after governance review.
- V1.4: Add meeting search, attendee tagging, and recurring-meeting patterns.
- V2: Consider calendar integration, external task sync, or live transcription
  only after governance review and destination update.

## Non Goals

Meeting Minutes AI is not intended to become:

- A live transcription service.
- A meeting recorder.
- A conferencing platform.
- A surveillance tool.
- A calendar application.
- A project management suite.
- A task system of record.
- A team chat product.
- A CRM activity logger by default.
- An unmanaged AI meeting agent.
- A conversation intelligence or employee coaching platform by default.
- A bot-first recording workflow without visible consent controls.

These directions should remain out of scope unless the destination itself is
reviewed and intentionally changed.

## Guiding Principles

Every Meeting Minutes AI feature should:

- Preserve meeting, note, action item, summary, decision, and risk context.
- Improve follow-up clarity without hidden recording or monitoring.
- Keep long meeting text out of dashboard and list payloads.
- Keep source transcript, AI summary, and user-edited minutes distinct.
- Treat AI, transcripts, calendar import, and task export as governed
  capabilities.
- Keep task and email handoffs explicit and user-controlled.
- Prefer focused handoffs to adjacent tools instead of absorbing their
  responsibilities.

## Governance Notes

This destination is aspirational. It describes the target product direction,
not the current implementation and not an authorization to build every feature
now.

destination.md is not a promise of what will be built next. It is a
description of what the product could ultimately become if time, user value,
and platform direction remain aligned.

Product owner and Astra review are required before accepting, prioritizing, or
implementing any destination item. Particular care is needed before approving
AI summaries, transcript import, live transcription, recording, calendar
integration, task sync, or cross-app automation because meeting records can
reveal client work, personnel matters, strategy, legal issues, financial plans,
health topics, and private decisions.

## Last Governance Review

Product Owner: Approved on 2026-07-03. Meeting Minutes AI selected as one of
the next five live apps for the Destination Framework.
Astra: Approved on 2026-07-03. Journey Progress 62 / 100 accepted.
Codex: Drafted destination and identified governance discussion points.

Status:

Approved
