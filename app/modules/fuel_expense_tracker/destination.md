# Fuel Expense Tracker Destination

## Document Status

Approved for Live promotion on 2026-07-15 after Astra review, Partner approval, production migration verification, production catalog verification, backend authentication fix verification, and manual browser verification.

## Destination Status

Approved v1.0

## Product Destination

Fuel Expense Tracker should be a focused vehicle fuel purchase log with vehicle records, fuel entries, dashboard totals, and spending insights.

The destination is always `100 / 100`. The current approved Journey Progress is `20 / 100`.

## Principles

- Track user-entered purchase and odometer data only.
- Keep fuel spending separate from vehicle maintenance and trip planning.
- Never present estimated fuel economy as a diagnostic result.
- Avoid repair recommendations and fuel savings guarantees.
- Keep all vehicles and entries owner scoped.

## V1 Scope

- Vehicle CRUD with archive and restore.
- Fuel entry CRUD with search, filters, sorting, and pagination.
- Derived unit price when the user does not enter one.
- Dashboard totals for cost, monthly cost, fuel quantity, average price, and estimated fuel economy.
- Insights for recent entries, monthly spend, vehicle spend, station counts, highest expense, and lowest expense.

## Non Goals

- Vehicle diagnostics.
- Connected-car telemetry.
- Repair or maintenance recommendations.
- Fuel economy guarantees.
- Receipt OCR.
- External fuel price APIs.

## Journey Progress

Current Position: 20 / 100

Current Journey Progress: 20 / 100

V1 creates the personal fuel expense foundation with owner-scoped vehicles, fuel entry CRUD, archive/restore actions, search/filter/sort controls, dashboard summaries, insights, production migration, database authentication fix verification, and verified production workflow behavior. Remaining maturity includes receipt attachments, CSV export, recurring vehicle defaults, and optional printable summaries after approval.

## Governance Notes

Astra: Approved on 2026-07-15.

Partner: Approved Fuel Expense Tracker live promotion after owner-review browser verification and backend authentication fix verification.

Codex: Fixed isolated database auth wiring, verified Turso connectivity, smoke-tested dashboard/vehicles/entries/insights behavior, synced overview metadata, promoted the production Apps row, synced destination metadata, and verified production catalog counts.
