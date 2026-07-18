# Travel Itinerary Builder Story

## Purpose

Travel Itinerary Builder helps a signed-in Ansiversa user plan private trips in one place. The app records trip-level itinerary information, organizes the trip by day, and stores scheduled activities with locations, categories, notes, and booking references.

## Workflow

The first workflow route is `/travel-itinerary-builder/plan`. Users create an itinerary, open its detail page, add itinerary days inside the approved date range, and add activities to each day. The Categories workflow manages reusable activity categories. The Insights workflow summarizes the user's itinerary count, days, activities, status mix, upcoming trips, and recent trips.

## User Journey

1. The user opens the overview and selects `Explore`.
2. The user lands on the protected Plan page.
3. The user creates an itinerary with trip name, destination, date range, status, purpose, and notes.
4. The user opens the itinerary detail page.
5. The user adds days and scheduled activities.
6. The user reviews planning coverage on Insights.

## Database Design

The module uses an isolated database configured by `TRAVEL_ITINERARY_BUILDER_DATABASE_URL`.

Tables:

- `TravelItineraries`: user-owned trip records.
- `TravelItineraryDays`: day records owned through an itinerary.
- `TravelActivities`: scheduled activities owned through an itinerary day.
- `TravelActivityCategories`: user-owned reusable category records.

Itinerary deletion cascades to days and activities. Day deletion cascades to activities. Category deletion is restricted by service logic while activities reference the category. Activity category foreign keys use `SET NULL` if database-level deletion happens outside the service path.

## API Design

The router exposes authenticated endpoints under `/api/v1/travel-itinerary-builder`.

List and dashboard endpoints return lightweight summaries. Detail endpoints return complete itinerary records with nested days and activities for view/edit workflows. Create and update schemas are explicit and reject extra fields.

## Business Rules

- Itinerary names must be unique per user, case-insensitively.
- End date cannot be before start date.
- Existing days must remain inside the itinerary date range when a trip is edited.
- Day dates must be inside the itinerary date range.
- A trip cannot have two days for the same date.
- Activity end time must be after start time when both are provided.
- A day cannot contain duplicate activities with the same title and start time.
- Categories are unique per user and cannot be deleted while activities use them.
- Cross-account access returns a safe not-found response.

## Shared Components Used

The frontend uses the Ansiversa shell, generated API client, Zustand store, `AvAppOverviewPage`, `AvAuthenticatedPageState`, `AvFormDrawer`, `AvRecordActions`, `AvPagination`, `AvInlineFeedback`, `AvCardEmptyState`, `AvPageHeader`, and shared cards.

## Performance Considerations

List responses avoid nested day/activity details. Detail records load nested data only when the user opens an itinerary. Indexes support owner-scoped status, start-date, destination, updated-date, day lookup, activity ordering, and category lookup patterns.

## Current Status

The module is real Workflow Ready, `comingSoon`, and `version: null`. It is awaiting a separate Astra certification assignment. It has not been promoted.

## Known Limitations

- No map integration.
- No reservation email import.
- No collaborative trip planning.
- No file attachments.
- No offline mobile export.
- No AI trip generation.

## Future Enhancements

Possible future improvements include map links, document attachment support, reservation parsing, collaborative planning, budget linkage, packing-list linkage, and AI-assisted itinerary suggestions after the approved AI roadmap begins.

## Current Implementation

The backend lives under `app/modules/travel_itinerary_builder`. The frontend lives under `src/modules/travel-itinerary-builder`. The app is data-backed, protected, and all workflow routes render real product behavior.
