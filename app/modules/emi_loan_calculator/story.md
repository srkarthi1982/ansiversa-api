# EMI / Loan Calculator Story

## Purpose

EMI / Loan Calculator helps authenticated users estimate loan repayments, understand interest cost, compare scenarios, and inspect an amortization schedule. It exists as a planning tool inside the Ansiversa shell, not as a lender, broker, credit-score service, or financial adviser.

## Workflow

Users enter a loan amount, annual interest rate, duration, duration unit, monthly repayment frequency, optional start date, processing fee, extra monthly payment, and display currency. The calculator returns EMI, principal, interest, total repayment, total cost, installment count, payoff date, interest ratio, extra-payment savings, and a full schedule. Users can save scenarios, edit them later, duplicate them, delete them, compare saved or temporary scenarios, and review insights.

## User Journey

The first real workflow route is `/emi-loan-calculator/calculator`. Users calculate a scenario first, then optionally save it. Saved scenarios live under `/saved-loans`, comparison under `/compare`, and summary insights under `/insights`.

## Database Design

The app owns an isolated `LoanScenarios` table in the EMI / Loan Calculator database. Records are owner-scoped by `userId` and store scenario inputs plus calculated summary fields:

- loan amount, annual interest rate, duration, duration unit, repayment frequency
- start date, processing fee, extra payment, currency code
- calculated EMI, total interest, total repayment, overall cost, payoff date, installment count, interest ratio
- created and updated timestamps

Indexes cover owner list queries, created/updated sorting, EMI sorting, total-interest sorting, and payoff-date review.

## API Design

The router is mounted at `/api/v1/emi-loan-calculator`.

Endpoints:

- `POST /calculate`
- `GET /dashboard`
- `GET /scenarios`
- `POST /scenarios`
- `GET /scenarios/{scenario_id}`
- `PUT /scenarios/{scenario_id}`
- `POST /scenarios/{scenario_id}/duplicate`
- `DELETE /scenarios/{scenario_id}`

List and dashboard responses return scenario summaries only. Detail responses include a dynamically calculated amortization schedule. Update payloads are independent from create payloads and do not include parent IDs.

## Shared Components Used

The frontend uses the shared Ansiversa shell, generated API client, `AvAuthenticatedPageState`, `AvPageHeader`, `AvInlineFeedback`, `AvCardEmptyState`, `AvPagination`, `AvFormDrawer`, `AvRecordActions`, confirmation dialog helpers, shared cards, and Zustand store helpers.

## Performance Considerations

Amortization schedules are not stored in the database and are not included in dashboard responses. The service caps generated schedules at 600 monthly installments. Saved list and dashboard payloads stay lightweight while detail and calculation responses provide complete schedule data only when needed.

## Current Status

Approved live at version `1.0.0`. Catalog status is `active` / `live`, destination metadata is approved at `20 / 100` with `destination_reviewed_at` set to `2026-07-14`, and the production-configured isolated database migration is verified at Alembic head `20260714_0001_emi_loan_calculator`.

## Known Limitations

- Monthly repayment frequency only.
- No CSV/PDF export.
- No lender-rate feed or bank integration.
- No currency conversion.
- No AI explanation.
- Payoff dates assume the first installment is one month after the supplied start date.

## Future Enhancements

- CSV export for amortization schedules.
- Richer comparison charts.
- Optional annual schedule grouping.
- Print-friendly schedule review.
- Governance-approved AI explanation, if Partner/Astra approve financial guardrails.

## Current Implementation

The backend uses Decimal-safe reducing-balance EMI calculations, zero-interest handling, final payment adjustment, owner-scoped CRUD, and deterministic schedule generation. The frontend provides Calculator, Saved Loans, Compare, and Insights routes using app-local services and store state.
