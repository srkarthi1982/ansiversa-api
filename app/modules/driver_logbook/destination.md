# Driver Logbook Destination

## Destination Status

Unapproved for live launch. The app remains `active` / `comingSoon` / `version = null`.

## Product Destination

Driver Logbook should be a personal driving journal for vehicle records, trip entries, odometer-based distance, purpose summaries, and driving history review.

## Principles

- Track user-entered trip data only.
- Keep records personal and informational.
- Calculate distance from odometer readings only when users provide both readings.
- Avoid navigation, GPS, fleet management, compliance, and certification claims.
- Keep all vehicles and trips owner scoped.

## V1 Scope

- Vehicle CRUD with archive and restore.
- Trip CRUD with archive and restore.
- Trip search, purpose/date/vehicle filters, sorting, and pagination.
- Distance derivation from start and end odometer readings.
- Dashboard totals for trips, distance, monthly distance, driving time, average distance, and vehicles.
- Insights for recent trips, longest trip, monthly distance, vehicle distance, and purpose summaries.

## Non Goals

- Official driving logbook replacement.
- Commercial driver hours certification.
- Regulatory compliance calculations.
- Navigation or GPS tracking.
- Fleet management systems.
- AI-generated trip reconstruction.

## Journey Progress

V1 is prepared for manual verification and must remain behind the coming-soon gate until explicit approval.
