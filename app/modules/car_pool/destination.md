# Car Pool Destination

## Document Status

Status: Draft for Workflow Ready review  
Destination Progress: 26 / 100  
Destination Status: Workflow Ready  
Reviewed At: 2026-07-12

## Purpose

Car Pool should mature into a trusted coordination workspace for people who share rides with known or semi-known groups. Its destination is structured carpool planning and accountability, not becoming a public transportation marketplace by default.

## Mature Product Vision

At 100 / 100, Car Pool helps users plan recurring and one-time shared rides, understand who is joining, track seats and requests, reduce forgotten coordination details, and preserve a clear record of ride decisions. It should make carpooling easier to organize while keeping safety, consent, verification, and real-world confirmation explicit.

## Target Users

- Commuters coordinating repeated workplace or school routes.
- Families and small groups sharing local rides.
- Students or community members arranging planned trips.
- Users who need a private record of ride participation and requests.

## Core Problem

Carpooling breaks down when route details, seat counts, pickup notes, request state, and cancellation context are scattered across chats or memory. Users need a calm workspace that records what was planned without pretending the software can guarantee real-world trust or safety.

## Approved V1 Scope

- Ride records with route, departure, seat, meeting point, vehicle, price-reference, recurrence, status, and notes.
- Ride create, edit, delete, duplicate, search, filters, empty state, pagination, and confirmation dialogs.
- Local join and leave actions through passenger trip records.
- Request records with pending, approved, and rejected workflow.
- Insights for total rides, seats offered, seats filled, completed trips, cancellation rate, and weekly activity.
- Protected owner-scoped backend APIs and isolated database storage.

## Non-Goals

- No live public marketplace.
- No payments, escrow, reimbursement processing, or fee calculation.
- No driver verification, background checks, identity guarantees, or safety guarantees.
- No live GPS tracking, dispatch, navigation, or route optimization.
- No chat, emergency response, insurance handling, or legal compliance automation.

## Future Direction

Future approved versions may add trusted-circle ride sharing, recurring ride templates, reminders, calendar export, cancellation history, route notes, commuter analytics, notification workflows, and carefully governed AI summaries of repeated route behavior.

## AI and Integration Boundary

AI may eventually summarize patterns, draft polite request responses, or detect incomplete ride details. It must not score people, guarantee safety, automate acceptance, infer sensitive identity attributes, or replace user approval. Any external maps, calendars, notifications, or payments require explicit architecture approval.

## Success Criteria

- Users can record ride plans quickly.
- Seat counts and request status remain clear.
- Upcoming and past trips are easy to distinguish.
- Cancellation and completion signals are visible.
- The app remains honest about its local coordination boundary.

## Journey Progress Rationale

The Workflow Ready implementation establishes the core data model, protected workflow, CRUD foundation, local trip actions, request review, and deterministic insights. The remaining maturity requires trusted sharing, reminders, integrations, richer recurring ride handling, and stronger governance around safety-sensitive features.
