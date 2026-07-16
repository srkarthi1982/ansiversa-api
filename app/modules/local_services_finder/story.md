# Local Services Finder Story

## Purpose

Local Services Finder is App #099 (`local-services-finder`). It helps authenticated users maintain a private directory of trusted local service providers with categories, contact information, address fields, notes, personal ratings, preferred provider markers, last contacted dates, archive behavior, search, filters, pagination, and dashboard metrics.

## Workflow

The shared overview enters `/local-services-finder/providers`. Protected workflow routes provide the provider list, provider detail page, and category management. Users create categories, create and edit providers, mark providers preferred or not preferred, archive and restore providers, delete records through shared confirmations, and filter the list by category, preferred state, archived state, rating, and last-contacted date range.

## User Journey

A user creates categories such as Electrician, Plumber, Doctor, Pharmacy, Salon, Car Repair, Tutor, Lawyer, Accountant, Cleaning, or Other. The user adds known providers with business name, contact person, phone, alternate phone, email, website, address, city, area, notes, rating, preferred state, and last contacted date. The dashboard summarizes active providers, preferred providers, archived providers, recently contacted providers, and categories.

## Database Design

The isolated database uses `LOCAL_SERVICES_FINDER_DATABASE_URL` and custom version table `local_services_finder_alembic_version`.

Tables:

- `ServiceCategories`: owner-scoped categories with unique user/name protection, color, sort order, and timestamps.
- `ServiceProviders`: owner-scoped provider records with optional category, contact fields, address fields, notes, rating, preferred boolean, archived boolean, last contacted date, and timestamps.

Indexes cover user/category, user/archived, user/preferred, user/rating, user/last contacted, user/updated, and category sort query patterns.

## API Design

Routes live under `/api/v1/local-services-finder`.

- `GET /dashboard`
- `GET /providers`
- `POST /providers`
- `GET /providers/{id}`
- `PUT /providers/{id}`
- `DELETE /providers/{id}`
- `POST /providers/{id}/archive`
- `POST /providers/{id}/restore`
- `POST /providers/{id}/prefer`
- `POST /providers/{id}/unprefer`
- `GET /categories`
- `POST /categories`
- `PUT /categories/{id}`
- `DELETE /categories/{id}`

List and dashboard responses stay lightweight. Detail responses return the complete record needed for viewing and editing. Every operation resolves owner-scoped records and never trusts client-provided user identity.

## Shared Components Used

The frontend uses generated API types, the shared typed API client, Zustand, `AvAppOverviewPage`, `AvAuthenticatedPageState`, `AvPageHeader`, `AvFormDrawer`, `AvRecordActions`, `AvConfirmDialog`, `AvPagination`, `AvInlineFeedback`, shared cards, and empty states.

## Performance Considerations

List responses return only fields displayed by the list UI. Dashboard returns counts and recent summaries only. Pagination limits result size. Indexes match owner-scoped list, category, archived, preferred, rating, last-contacted, and updated-at query patterns.

## Current Status

Local Services Finder is Workflow Ready / Level 3 candidate, `comingSoon`, version `null`. Production-configured migration `20260716_0011_local_services_finder` is applied and verified for the isolated database. Authenticated browser E2E, Karthik manual acceptance, destination approval, and live promotion remain pending.

## Known Limitations

- No Google Maps, GPS, directions, or route planning.
- No public reviews or marketplace search.
- No booking, quote, payment, or lead-generation workflow.
- No third-party APIs.
- No AI recommendations.

## Future Enhancements

- Optional approved import/export.
- Contact follow-up reminders through shared platform notifications.
- Household sharing if approved.
- Contact history if a deeper workflow is approved.

## Current Implementation

The implementation provides protected CRUD for providers and categories, combined list filters, deterministic ordering, preferred markers, archive/restore behavior, duplicate provider protection within category, duplicate category protection, category delete protection, generated OpenAPI contracts, service tests, and shared frontend drawer/delete patterns.
