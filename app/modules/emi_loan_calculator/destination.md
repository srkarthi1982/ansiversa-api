# EMI / Loan Calculator Destination

## Document Status

Approved for Live promotion on 2026-07-14 after Astra review, Partner approval, production migration verification, and manual browser verification.

## Destination Status

Approved v1.0

## Destination

EMI / Loan Calculator should mature into Ansiversa's private loan-planning workspace for users who need to estimate repayment commitments, compare scenarios, and understand amortization without being pushed toward a lender or marketplace.

The destination is always `100 / 100`. The current approved Journey Progress is `20 / 100`.

## Purpose

EMI / Loan Calculator should become Ansiversa's private loan-planning workspace for users who need to estimate repayment commitments, compare scenarios, and understand amortization without being pushed toward a lender or marketplace.

## Mature Product Destination

The mature product should help users move from a loan question to a saved, reviewable repayment plan. It should remain deterministic, transparent, and planning-only. The app should make repayment tradeoffs understandable through EMI, interest, total repayment, payoff timing, extra-payment savings, and amortization schedules.

## Target Users

- Individuals comparing loan affordability.
- Families reviewing shared borrowing decisions.
- Small business owners planning repayments for equipment or working-capital loans.
- Users who want private scenario memory inside Ansiversa instead of one-off calculator pages.

## Core Principles

- Use standard reducing-balance EMI calculation.
- Treat saved scenarios as user-owned planning records.
- Keep list and dashboard payloads lightweight.
- Keep calculations transparent and repeatable.
- Display a planning-only financial disclaimer.
- Avoid regulated financial advice, lender offers, credit scoring, and approval prediction.

## Approved V1 Direction

V1 is intended to include:

- Calculator route with principal, annual rate, duration, duration unit, monthly repayment frequency, optional start date, processing fee, extra monthly payment, and currency context.
- Deterministic calculation response with EMI, total principal, total interest, total repayment, processing fee, overall cost, payoff date, interest ratio, savings, and schedule.
- Saved loan scenario CRUD.
- Scenario comparison using saved and temporary calculations.
- Saved-scenario insights.
- Owner-scoped backend storage in an isolated app database.

## Non-Goals

- No lender rates.
- No credit-score or approval prediction.
- No loan application flow.
- No broker, bank, or marketplace integration.
- No currency conversion.
- No financial-advice positioning.
- No OpenAI or AI integration in V1.

## Journey Progress

Current Position: 20 / 100

Current Journey Progress: 20 / 100

V1 establishes the deterministic repayment-planning foundation with EMI calculation, amortization schedule review, saved scenarios, scenario comparison, insights, owner-scoped storage, and explicit planning-only financial boundaries. Remaining maturity includes possible schedule export, richer comparison visualization, accessibility polish, and future governance review for any AI explanation feature.

## Current Implementation

The current implementation stores only saved loan scenarios. Amortization schedules are calculated dynamically from scenario inputs and are not persisted. The first workflow route is `/emi-loan-calculator/calculator`. Catalog status is approved for live release at version `1.0.0`.

## Governance Notes

Astra: Approved on 2026-07-14.

Partner: Approved EMI / Loan Calculator live promotion after manual workflow verification.

Codex: Ran production-configured isolated database migration, verified schema/indexes/version table, synced overview metadata, and prepared live promotion metadata.
