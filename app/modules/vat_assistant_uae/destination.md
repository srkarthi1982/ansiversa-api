# VAT Assistant UAE Destination

## Document Status

Status: Draft
Destination Progress: 18 / 100
Destination Status: Draft
Reviewed At: 2026-07-12

## Purpose

VAT Assistant UAE should mature into a dependable private VAT preparation and review workspace for UAE businesses. Its destination is structured recordkeeping and review clarity, not official filing, tax advice, accounting automation, or guaranteed compliance.

## Mature Product Vision

At 100 / 100, VAT Assistant UAE helps users keep VAT registrations, return periods, transaction evidence, filing status, and review notes organized before external filing or professional review.

## Target Users

- UAE small businesses tracking VAT records.
- Founders preparing information for accountants or tax agents.
- Finance teams reviewing VAT periods and transaction-level VAT activity.
- Users who want a simple VAT record ledger inside the Ansiversa platform.

## Core Problem

VAT information often lives across invoices, spreadsheets, filing portals, reminders, and adviser conversations. Users need one focused workspace to organize the records they have entered without confusing it with official FTA filing or advice.

## Approved V1 Scope

- VAT registration CRUD, duplicate, search, status/type filters, KPI cards, empty states, and confirmation dialogs.
- VAT return CRUD, duplicate, filing status and period filters, KPI cards, and user-entered VAT amount tracking.
- Transaction CRUD, duplicate, transaction type and VAT rate filters, KPI cards, and transaction-level VAT amounts.
- Estimate-only insights for total registrations, filed returns, pending returns, output VAT, input VAT, net VAT payable, VAT by period, VAT by rate, and recent activity.
- Protected owner-scoped backend APIs and isolated database storage.

## Non-Goals

- No FTA or EmaraTax filing/submission.
- No tax, accounting, legal, audit, or compliance advice.
- No official eligibility, exemption, or registration determination.
- No invoice OCR, accounting integration, payment processing, or tax-agent workflow in V1.
- No claims that user-entered records are complete, compliant, or filing-ready.

## Future Direction

Future approved versions may add exportable schedules, document attachments, adviser review comments, audit trails, official reference links, reminder workflows, and governed import workflows.

## AI and Integration Boundary

AI may eventually summarize user-entered VAT records or identify missing fields after explicit user action. It must not infer filing obligations, submit returns, provide tax advice, or connect to FTA/EmaraTax/accounting systems without governance review.

## Success Criteria

- Users can create VAT registrations quickly.
- Users can track VAT return amounts and filing status.
- Users can record transaction-level VAT rate and VAT amount.
- Insights are clear but bounded as estimate-only recordkeeping.
- The app stays honest about official filing and professional review boundaries.

## Journey Progress Rationale

Workflow Ready V1 establishes the isolated data model, protected workflow, CRUD foundation, deterministic summaries, and owner-scoped storage. Remaining maturity requires exports, attachments, adviser review, audit trail, import workflows, and stronger governance around official filing-adjacent use.
