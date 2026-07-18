# Travel Itinerary Builder Market Study

## Document Status

Research summary for App #046 initial Workflow Ready implementation.

## Market Version

1

## Created

2026-07-18

## Last Reviewed

2026-07-18

## Next Review

After certification or before a major product maturity pass.

## Purpose

Understand common travel itinerary planner expectations without copying competitor wording, screens, proprietary flows, or protected content.

## Problem Statement

Travel planning often spreads across notes, emails, maps, booking confirmations, group messages, and spreadsheets. Users need a lightweight way to keep dates, daily schedule items, locations, notes, and references together.

## Target Users

- Everyday travelers planning personal trips.
- Families coordinating vacation days.
- Business travelers organizing appointments and reservations.
- Users who want structure without a complex enterprise travel system.

## Competitor Landscape

- TripIt focuses on organizing travel reservations and itinerary details.
- Wanderlog focuses on collaborative trip planning, route planning, reservations, guides, and mobile access.
- Google Maps and Google Travel workflows influence user expectations around places, routes, flights, and travel discovery.
- AI travel planners increasingly shape expectations for generated itineraries and recommendation assistance.

## Common Market Features

- Trip-level date ranges.
- Day-by-day itinerary organization.
- Activities or places with times and locations.
- Notes and reservation references.
- Map or route support.
- Collaboration and sharing.
- Offline/mobile access.
- Imports from email or booking providers.

## User Love Signals

Users value having trip details in one place, reducing scattered notes, and being able to see the plan by day. Mobile access and easy reordering are common expectations in mature travel planners.

## Complaints And Friction

Common friction includes too much setup, paywalls around offline/export features, difficulty editing day plans quickly, map features that are too complex for simple trips, and apps that assume every trip needs collaboration.

## Pricing And Paywall Observations

Travel apps commonly keep basic itinerary creation free and reserve advanced sharing, offline, export, route optimization, or AI features for paid plans.

## AI Trends

AI travel planning is moving toward generated day plans, personalized recommendations, flight-deal discovery, and conversational refinement. Ansiversa should defer AI implementation until the approved AI roadmap begins.

## UX Patterns Worth Studying

- Start from a trip, then organize by days.
- Keep activities compact and scannable.
- Make dates and times visible without opening every record.
- Separate planning details from analytics.
- Keep advanced integrations optional.

## Ansiversa Opportunities

- Provide a simple private itinerary workflow inside the Ansiversa shell.
- Avoid overbuilding maps and booking integrations in V1.
- Support practical activity categorization and booking references.
- Later connect to packing, expense, and travel-cost apps if Partner/Astra approve cross-app maturity work.

## Avoid List

- Do not copy competitor UI or wording.
- Do not scrape bookings or emails without explicit approval.
- Do not store external credentials.
- Do not implement AI trip generation before the AI roadmap begins.
- Do not turn this into a booking marketplace.

## Product Questions

- Should mature versions support map URLs or full map integrations?
- Should itinerary sharing be added after account and permission governance matures?
- Should travel costs link to Trip Cost Calculator in a future cross-app workflow?

## Sources

- TripIt official site: https://www.tripit.com/web
- Wanderlog official site: https://wanderlog.com/
- Google Maps Help: https://support.google.com/maps/answer/7565193
- Google AI trip planning update: https://blog.google/products-and-platforms/products/search/agentic-plans-booking-travel-canvas-ai-mode/

## Review Notes

The V1 implementation intentionally focuses on private CRUD workflow readiness: itineraries, days, activities, categories, filters, pagination, protected access, and summary insights.

## Revision History

- 2026-07-18: Initial market study created for real Workflow Ready implementation.

