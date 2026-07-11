# Rent a Car Story

## Purpose

Rent a Car is App #063 in the Ansiversa Mobility & Travel category. It helps users plan rental searches, compare user-entered vehicle options, and keep confirmed booking references in one protected workspace.

## Workflow

The workflow starts at `/rent-a-car/searches` and continues through `/rent-a-car/vehicles`, `/rent-a-car/bookings`, and `/rent-a-car/insights`.

## User Journey

Users create a rental search with locations, dates, passenger/luggage needs, budget, and status. They add vehicle options found outside Ansiversa, compare estimated totals, mark a preferred option, and record confirmed booking details after booking with a provider. Insights summarize saved records and upcoming cancellation deadlines.

## Database Design

The backend uses an isolated Rent a Car database configured by `RENT_A_CAR_DATABASE_URL`. Tables are:

- `RentACarSearches`
- `RentACarVehicleOptions`
- `RentACarBookings`

Records are owner-scoped by `userId`. Vehicle options belong to searches. Bookings belong to searches and may reference a vehicle option. Search delete cascades its options and bookings. Vehicle option delete clears booking option references before removing the option.

## API Design

The router is mounted at `/api/v1/rent-a-car`. It exposes protected CRUD endpoints for searches, vehicle options, and bookings, plus duplicate and preferred-option actions. Dashboard responses return lightweight summaries and deterministic insight fields. Detail endpoints return full editable fields.

## Shared Components Used

The frontend uses the Ansiversa shell, protected page state, page headers, cards, shared form drawer, feedback stack, empty states, confirmation dialog, and record action buttons.

## Performance Considerations

List and dashboard payloads avoid long text fields by using previews. Indexes cover owner-scoped list queries, status/date filters, search foreign-key lookups, provider/class filters, and cancellation deadline queries.

## Current Status

Workflow Ready candidate. The app remains `active / comingSoon` with `version = null`. Live promotion has not been performed.

## Known Limitations

- No live pricing, availability, booking, payment, scraping, messaging, notifications, or external integrations.
- Prices and availability are user-entered planning references.
- Insurance/add-on fields are estimates only and do not provide advice.

## Future Enhancements

Future versions may improve selected-search comparison, exports, and approved notification support while preserving the planning-only boundary.

## Current Implementation

The implementation includes isolated backend models, Alembic migration `20260711_0001_rent_a_car`, protected owner-scoped routes, generated OpenAPI compatibility, and React workflow pages for Searches, Vehicles, Bookings, and Insights.
