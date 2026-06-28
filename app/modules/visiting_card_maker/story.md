# Visiting Card Maker Backend Story

## Purpose

Visiting Card Maker owns the persistent profile and design records behind the digital business card workflow. The backend exists to keep card content owner-scoped, reusable, editable, and safe to duplicate without exposing unrelated user data.

## Workflow

The backend supports the frontend's Create -> Creations -> Settings flow through card-oriented endpoints. A card is created from profile fields and a template key, updated as one user-facing record, duplicated into a new profile/design pair, listed for the dashboard, and deleted when no longer needed.

## User Journey

An authenticated user saves a card with professional contact information and a selected template. The same user can reload the dashboard, edit saved card content, duplicate an existing card for a variation, or delete a card. Every operation resolves records through owner-scoped service logic.

## Database Design

The module uses two persistent tables:

* `CardProfiles` stores owner-scoped profile content such as name, title, company, contact details, address, and tagline.
* `CardDesigns` stores the selected template for a profile through `profileId`.

`userId` indexes support user-owned list queries. `profileId` indexes support profile-to-design lookups when the service assembles card responses. Large text-style profile fields are not indexed because the current workflow does not search them.

## API Design

The router exposes `/api/v1/visiting-card-maker/dashboard`, `/cards`, `/cards/{card_id}`, and `/cards/{card_id}/duplicate`. The service presents one user-facing card response made from profile and design data. Create requires the profile fields plus `templateKey`; update accepts only editable profile and template fields; duplicate creates a new owned copy; delete removes the saved card.

## Shared Components Used

The module uses the shared FastAPI module pattern: isolated database dependency, SQLAlchemy models, Pydantic schemas, thin routes, service-owned business logic, current-user authentication, owner-scoped access checks, and generated OpenAPI contracts for the frontend.

## Performance Considerations

Dashboard and card list responses are lightweight because each card only includes profile and design fields required to render saved cards. Indexes match current query paths: owner card lists and profile/design joins. Image export is intentionally frontend-owned, so the backend does not store PNG blobs or generated binary files.

## Current Status

The backend implementation is live at version `1.0.0`. The parent Apps catalog stores Visiting Card Maker as `active` with `launchStatus = live`.

## Known Limitations

V1 stores card profile and template data only. It does not manage print orders, QR analytics, public hosted cards, binary exports, team brand kits, or template authoring.

## Future Enhancements

Future versions may add shareable card URLs, QR metadata, export audit records, brand presets, template versioning, and integration with Portfolio Creator.

## Current Implementation

Current version: `1.0.0`

Implemented:

* Isolated Visiting Card Maker backend module
* `CardProfiles` persistence
* `CardDesigns` persistence
* Dashboard and card CRUD routes
* Duplicate-card route
* Owner-scoped service access
* Query-pattern indexes for owner and profile lookups
* Current-state story documentation
