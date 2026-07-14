# EMI / Loan Calculator Destination

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

Current Journey Progress: ready for owner assessment.

Destination status: not approved.

Reviewed at: not reviewed.

The app has a useful Workflow Ready V1 foundation with deterministic loan math, saved scenarios, comparison, insights, and schedule review. Remaining maturity includes manual browser review, possible schedule export, richer comparison visualization, accessibility polish, and future governance review for any AI explanation feature.

## Current Implementation

The current implementation stores only saved loan scenarios. Amortization schedules are calculated dynamically from scenario inputs and are not persisted. The first workflow route is `/emi-loan-calculator/calculator`. Catalog status remains `comingSoon`, and no release version is assigned.
