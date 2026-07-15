# Emergency Contacts Organizer Story

## Purpose

Emergency Contacts Organizer gives authenticated users a private place to store and quickly access important contact information. It exists for practical recordkeeping, not emergency response.

## Workflow

Users open the Contacts page, create contact records, assign categories, mark favourites or primary contacts, and review summaries. Categories provide default household and assistance groups while still allowing user-managed custom records.

## User Journey

A parent records family, pediatrician, school, and caregiver contacts so the information is not scattered across notes and messages.

A resident saves local police, fire and rescue, insurance, building support, and roadside assistance numbers for quick reference.

A traveller records assistance, insurance, hotel, and local support contacts before departure.

A user under time pressure opens the app, searches or filters the contact list, and taps the visible phone or email action manually.

## Database Design

The isolated app database owns two tables:

- `Categories`: owner-scoped category records with name, description, sort order, system/default flag, and timestamps.
- `Contacts`: owner-scoped contact records with category, name, relationship, phone, email, location, address, notes, priority, favourite and primary flags, and timestamps.

The Alembic version table is `emergency_contacts_organizer_alembic_version`.

## API Design

The API is mounted at `/api/v1/emergency-contacts-organizer` and provides:

- `GET /dashboard`
- `GET /insights`
- CRUD for `/categories`
- CRUD for `/contacts`
- Favourite/unfavourite contact actions
- Primary/unprimary contact actions

Routes are protected with the shared authenticated user dependency and all private data is owner-scoped.

## Shared Components Used

The frontend uses the shared overview page, authenticated page state, page header, cards, inline feedback, empty state, drawer, confirmation dialog, record actions, pagination, and form drawer components.

## Performance Considerations

List responses are lightweight and detail records are loaded when the user opens or edits a contact. Indexes support owner queries, category filtering, favourite/primary filtering, priority ordering, and updated-time review.

## Current Status

The app is approved live at version `1.0.0` after Astra review, Partner approval, production-configured isolated database migration verification, production Apps row promotion, overview metadata sync, and manual browser workflow verification. Destination metadata is synced at `20 / 100`, status `approved`, reviewed on `2026-07-15`.

## Known Limitations

V1 does not support sharing, exports, file attachments, background reminders, public emergency-number verification, location tracking, or automated emergency calls.

## Future Enhancements

- Optional export or print sheet after approval.
- Review reminders through the platform notification layer.
- Approved cross-app links to health, family, travel, or document apps.

## Current Implementation

The backend follows the current FastAPI, SQLAlchemy 2, service/repository, and isolated Alembic pattern. The frontend follows the current React, TypeScript, Zustand, React Router, generated API client, and shared-component mini-app pattern. The production catalog row is `active` / `live` / `1.0.0`.
