# Bill Splitter Story
## Purpose and workflow
Authenticated users follow `Create bill → Add participants → Add items → Allocate → Record paid amounts → Review` from `/bill-splitter/bills` and direct bill detail routes.
## Database and APIs
The isolated `Bills`, `BillParticipants`, `BillItems`, and `BillItemAllocations` tables are owner scoped through the parent bill. Protected APIs provide dashboard, bill CRUD/search/filters/pagination, participant CRUD, item CRUD, and replace-all allocation.
## Calculation rules
The backend is authoritative and uses two-decimal `Decimal` math backed by `NUMERIC(14,2)`. Line total is quantity × unit price. Total is subtotal − discount + tax + service charge + tip. Discount cannot exceed subtotal. Equal splits use integer cents and give remainder cents in participant sort order. Custom amounts must equal the line exactly. Bill adjustments use the same deterministic distribution, so participant shares reconcile exactly to total. Paid amount cannot exceed share; settled bills require zero outstanding balances.
## UI and shared resources
Overview Explore opens `/bills`. Responsive Bills and Bill Detail use generated contracts, Zustand, shared store helpers, authenticated state, headers, cards, feedback, empty states, `AvFormDrawer`, `AvRecordActions`/`AvConfirmDialog`, and pagination. Detail manages participants, items, allocation modes, totals, shares, and recorded settlements.
## Status and limitations
Workflow Ready / Level 3, `comingSoon`, version `null`, destination pending, authenticated E2E unavailable. No settlement history, payment processing, banking, OCR, exchange conversion, accounting integration, tax advice, or AI.
