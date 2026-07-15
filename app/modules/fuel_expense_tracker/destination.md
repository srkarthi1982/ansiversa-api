# Fuel Expense Tracker Destination

## Destination Status

Unapproved for live launch. The app remains `active` / `comingSoon` / `version = null`.

## Product Destination

Fuel Expense Tracker should be a focused vehicle fuel purchase log with vehicle records, fuel entries, dashboard totals, and spending insights.

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

V1 is prepared for manual verification and must remain behind the coming-soon gate until explicit approval.
