# Emergency Contacts Organizer Destination

## Destination Vision

Emergency Contacts Organizer should become a private quick-reference workspace for important contacts. Its mature form helps users keep essential family, medical, school, workplace, roadside, insurance, and local assistance contacts organized and easy to find.

## Current Readiness State

Status: workflow ready for evening manual verification  
Destination status: not approved  
Destination reviewed at: null  
Live promotion: not performed

## Core Workflows

- Create, view, edit, and delete emergency contacts.
- Group contacts by default or custom categories.
- Search and filter contacts.
- Mark contacts as favourite or primary.
- Use direct `tel:` and `mailto:` actions where contact data exists.
- Review totals, favourite contacts, category distribution, and missing-information signals.

## Feature Boundaries

The app organizes contact information only. It does not contact emergency services, dispatch help, verify public emergency numbers, monitor crises, provide medical or legal advice, track location, or guarantee assistance.

## Data Ownership Model

Contacts and categories are private records scoped to the authenticated owner. A user must not read, update, or delete another user's records. Future integrations must go through approved APIs rather than direct database access.

## Safety Limitations

The UI and documentation must avoid fear-based copy and emergency-response promises. Users remain responsible for verifying official local emergency numbers and contacting appropriate services outside Ansiversa.

## UX Expectations

- First workflow page opens to contacts.
- Favourite and primary contacts are easy to see.
- Phone numbers are prominent and support direct manual dialing.
- Empty states are calm and practical.
- Mobile layout remains readable under narrow widths.

## Acceptance Criteria

- Protected routes exist for contacts, categories, and insights.
- Backend APIs enforce owner scoping.
- Contact CRUD, category CRUD, favourite/primary actions, search/filter, details, and insights work.
- Overview CTA routes to `/emergency-contacts-organizer/contacts`.
- App remains `comingSoon`, version `null`, destination not approved.

## Readiness Checklist

- [x] Product workflow implemented.
- [x] Backend module and migration created.
- [x] Frontend workflow created.
- [x] Overview metadata updated.
- [x] Mandatory documentation created.
- [ ] Evening manual verification completed.
- [ ] Partner/Astra approval granted.
- [ ] Live promotion completed.
