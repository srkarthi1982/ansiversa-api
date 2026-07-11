# Rent a Car Destination

## App Name

Rent a Car

## Destination Status

Approved v1.0

## Final Product Vision

Rent a Car should become Ansiversa's calm car-rental planning workspace: a place where users compare rental searches, vehicle options, estimated totals, provider notes, and confirmed booking details without turning the app into a marketplace, booking engine, live pricing system, payment flow, or fleet manager.

## Target Users

- Travelers comparing car rental options before booking elsewhere.
- Families planning trips with passenger, luggage, pickup, and cancellation details.
- Frequent travelers who want confirmed booking references and provider contacts in one place.
- Budget-conscious users comparing base rates, fees, deposits, mileage rules, and add-on estimates.

## Core User Problems

- Rental options are often scattered across provider sites, aggregator tabs, emails, screenshots, and notes.
- Base daily rates can hide the practical total once taxes, fees, deposits, insurance/add-ons, mileage, and fuel terms are considered.
- Cancellation deadlines and pickup instructions become hard to find near travel day.
- Users need a comparison workspace without giving another app payment details, license documents, or booking authority.
- Generic notes and spreadsheets can store information, but they do not guide the rental-specific workflow.

## Final Capabilities

- Create, edit, duplicate, search, filter, sort, and delete rental searches.
- Track pickup/dropoff locations, pickup/return date and time, driver age group, vehicle type, transmission, passengers, luggage, budget, currency, notes, and status.
- Create, edit, duplicate, delete, and mark preferred vehicle options connected to rental searches.
- Track provider, model, class, transmission, fuel policy, seats, luggage, daily base rate, rental days, taxes/fees, deposit, add-on estimate, mileage, cancellation terms, pickup method, reference URL, last checked date, notes, preference, and availability status.
- Calculate estimated option totals from user-entered rates, days, taxes/fees, and add-ons.
- Create, edit, delete, search, and filter booking records connected to searches and optional vehicle options.
- Track confirmed booking reference, provider, pickup/dropoff instructions, confirmed total, deposit, contact, booking date, cancellation deadline, status, and notes.
- Review deterministic insights for searches, comparing status, confirmed/upcoming/completed bookings, estimated spend, provider/class patterns, recently updated searches, and cancellation deadlines.
- Keep list responses lightweight and detail endpoints complete.
- Support accessible responsive workflows inside the Ansiversa shell.

## Advanced Capabilities

- Richer selected-search comparison tables for side-by-side vehicle option review.
- Exportable rental summary for trip planning.
- Optional platform reminders for cancellation deadlines after notification governance approval.
- Vehicle class, pickup method, mileage, and fuel policy presets.
- Cross-app links to Travel Itinerary Builder, Trip Cost Calculator, Packing Checklist, and Expense Tracker through approved APIs.
- Import assistance only after explicit Partner/Astra approval and source-transparency review.

## AI Opportunities

- Summarize user-entered option differences without claiming live market accuracy.
- Suggest comparison questions for the user to verify with the rental provider.
- Detect incomplete records, such as a booking without a cancellation deadline.
- Draft a trip-ready rental summary from saved search, option, and booking records.

AI must remain optional, reviewed, and clearly separated from booking, pricing, insurance, or legal advice claims.

## Ecosystem Connections

Rent a Car can later connect with Travel Itinerary Builder, Trip Cost Calculator, Packing Checklist, Expense Tracker, and Dashboard summaries through approved APIs. It must not directly own or mutate records in those apps.

## Weekly Return Value

Users return before and during trips to compare options, mark preferred choices, record confirmed details, check cancellation deadlines, and find pickup instructions quickly.

## Success Criteria

- Users can create rental searches quickly.
- Vehicle options make estimated total comparison clearer than scattered notes.
- Preferred options and confirmed bookings are easy to identify.
- Cancellation deadlines and pickup instructions are visible.
- The app preserves a planning-only boundary and never implies live booking, live inventory, live pricing, or provider partnership.

## Journey Progress

Current Position: 28 / 100
Destination: 100 / 100
Remaining Journey: 72 / 100

This estimate describes product maturity, not feature completion. Workflow Ready V1 includes rental search CRUD, vehicle option CRUD, booking CRUD, duplicate/preferred actions, estimated total calculation, filters, deterministic insights, owner-scoped APIs, isolated database storage, overview routing, production database migration, and manual QA verification. The remaining journey includes richer comparison views, exportable summaries, governed deadline reminders, presets, cross-app travel links, and carefully governed AI assistance.

## Future Version Ideas

- V1.1: Selected-search comparison table and better option grouping.
- V1.2: Exportable rental summary.
- V1.3: Cancellation deadline reminders after notification governance.
- V2: Approved cross-app travel planning links.
- V2+: AI-assisted rental comparison review under strict claims governance.

## Non Goals

- Do not become a rental marketplace.
- Do not offer direct booking, live inventory, live pricing, or payment processing.
- Do not scrape provider or aggregator sites.
- Do not store driver licenses, passports, or payment card documents.
- Do not provide insurance, legal, or travel compliance advice.
- Do not claim provider partnerships, discounts, or guaranteed availability.

## Guiding Principles

- Rental planning should be clear without pretending to be booking infrastructure.
- User-entered estimates must remain visibly separate from provider-verified facts.
- Confirmed booking records should help users prepare for travel day.
- Advanced reminders, integrations, and AI must be opt-in and approved.
- The mobility workflow should remain distinct from fleet management or marketplace operations.

## Governance Notes

Astra: Approved on 2026-07-11.

Partner: Approved Rent a Car live promotion after manual workflow verification.

Codex: Ran production-configured isolated database migration, verified schema/indexes/foreign keys, synced overview metadata, and prepared live promotion metadata.
