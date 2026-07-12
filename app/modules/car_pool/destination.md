# Car Pool Destination

## App Name

Car Pool

## Destination Status

Approved v1.0

## Final Product Vision

Car Pool should become Ansiversa's trusted coordination workspace for people who share rides with known or semi-known groups. Its destination is structured carpool planning, seat/request clarity, and accountability without becoming a public transportation marketplace by default.

## Target Users

- Commuters coordinating repeated workplace or school routes.
- Families and small groups sharing local rides.
- Students or community members arranging planned trips.
- Users who need a private record of ride participation and requests.

## Core User Problems

- Carpooling breaks down when route details, seat counts, pickup notes, request state, and cancellation context are scattered across chats or memory.
- Users need a calm workspace that records what was planned without pretending the software can guarantee real-world trust or safety.
- Joined trips and passenger requests need visible status so users can distinguish planned, left, completed, pending, approved, and rejected activity.
- Seat availability needs to remain clear before users attempt local join actions.

## Final Capabilities

- Create, edit, duplicate, search, filter, paginate, and delete ride records.
- Track route, departure time, return time, meeting point, vehicle, driver, seats, price reference, recurrence, status, visibility, and notes.
- Create local passenger trip records only for joinable rides with available seats.
- Review upcoming and past local trips, then leave trip records when plans change.
- Create, edit, delete, approve, reject, and filter passenger requests.
- Track request names, requested seats, pickup notes, messages, request dates, response notes, and status.
- Review deterministic insights for total rides, seats offered, seats filled, completed trips, cancellation rate, pending/approved/rejected requests, recently updated rides, and weekly activity.
- Keep list responses lightweight and detail endpoints complete.
- Support accessible responsive workflows inside the Ansiversa shell.

## Advanced Capabilities

- Trusted-circle sharing for known groups after architecture approval.
- Recurring ride templates and improved recurring ride review.
- Reminder and calendar export support after notification/calendar governance approval.
- Cancellation history and clearer participation audit trails.
- Route notes and pickup-point templates without live routing or dispatch.
- Cross-app links to Travel Itinerary Builder, Trip Cost Calculator, Work Log Tracker, and Expense Tracker through approved APIs.

## AI Opportunities

- Summarize repeated ride patterns from user-entered records.
- Draft polite request responses that remain user-reviewed.
- Detect incomplete ride details, such as missing meeting point or unclear seat count.
- Generate simple weekly activity summaries.

AI must remain optional, user-reviewed, and clearly separated from driver verification, safety guarantees, person scoring, live matching, and automated approval decisions.

## Ecosystem Connections

Car Pool can later connect with Travel Itinerary Builder, Trip Cost Calculator, Work Log Tracker, Expense Tracker, calendar workflows, and notification services through approved APIs. It must not directly own or mutate records in those apps.

## Weekly Return Value

Users return before repeated commutes or shared trips to check route details, seat availability, joined passengers, pending requests, and recent changes.

## Success Criteria

- Users can record ride plans quickly.
- Seat counts and request status remain clear.
- Upcoming and past trips are easy to distinguish.
- Cancellation and completion signals are visible.
- The app remains honest about its local coordination boundary.

## Journey Progress

Current Position: 26 / 100
Destination: 100 / 100
Remaining Journey: 74 / 100

This estimate describes product maturity, not feature completion. Workflow Ready V1 includes ride CRUD, duplicate, search, filters, pagination, local trip join/leave, request workflow, deterministic insights, owner-scoped APIs, isolated database storage, overview routing, production database migration, manual QA verification, and a My Trips guard that prevents full rides from being selected for local joins. The remaining journey includes trusted sharing, reminders, integrations, richer recurring ride handling, improved audit trails, and stronger governance around safety-sensitive features.

## Future Version Ideas

- V1.1: Recurring ride templates and pickup-point presets.
- V1.2: Exportable ride summary for known groups.
- V1.3: Reminder and calendar export support after governance approval.
- V2: Approved trusted-circle sharing.
- V2+: AI-assisted ride pattern summaries under strict safety and claims governance.

## Non Goals

- Do not become a public rideshare marketplace.
- Do not provide payments, escrow, reimbursement processing, or fee calculation.
- Do not provide driver verification, background checks, identity guarantees, or safety guarantees.
- Do not provide live GPS tracking, dispatch, navigation, or route optimization.
- Do not provide chat, emergency response, insurance handling, or legal compliance automation.
- Do not automate passenger acceptance or score people.

## Guiding Principles

- Carpool planning should stay useful without pretending to guarantee real-world trust.
- Seat and request state should be clear before users coordinate outside the app.
- Local trip participation should remain user-controlled.
- Advanced reminders, integrations, and AI must be opt-in and approved.
- Safety-sensitive features require explicit Partner/Astra architecture approval.

## Governance Notes

Astra: Approved on 2026-07-12.

Partner: Approved Car Pool live promotion after manual workflow verification and My Trips join UX fix.

Codex: Ran production-configured isolated database migration, verified schema/indexes/foreign keys, synced overview metadata, fixed the full-ride join default, and prepared live promotion metadata.
