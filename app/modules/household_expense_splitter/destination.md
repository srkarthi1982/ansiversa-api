# Household Expense Splitter Destination

## Document Status

Approved for Live promotion on 2026-07-15 after Astra review, Partner approval, production migration verification, production smoke verification, and manual browser verification.

## Destination Status

Approved v1.0

## Destination

Household Expense Splitter should become a lightweight private shared-living ledger inside Ansiversa. Its mature form helps a household record shared costs, understand member balances, and record settlements made outside the platform.

The destination is intentionally bounded. It is not a finance app, accounting system, banking app, invoicing platform, payment gateway, budgeting system, business expense tracker, OCR tool, receipt scanner, payroll system, tax product, subscription manager, or AI product.

The destination is always `100 / 100`. The current approved Journey Progress is `20 / 100`.

## Mature Workflow

1. Create household members.
2. Record shared expenses with payer, category, date, participants, and split method.
3. Use equal or manual split amounts.
4. Record settlements between members.
5. Review simple summaries for spending, balances, recent activity, and outstanding amounts.

## Product Boundaries

- Owner-scoped household records only.
- No payment processing, bank sync, receipts, OCR, AI, invoices, tax, payroll, barcode, ecommerce, or subscriptions.
- Settlements are records only; actual payments happen outside Ansiversa.

## Journey Progress

Current Position: 20 / 100

Current Journey Progress: 20 / 100

V1 creates the private household expense splitter foundation with owner-scoped member management, expense CRUD, equal and manual split validation, archive/restore, permanent delete, settlement CRUD, search, filters, sorting, dashboard metrics, insights, production migration, and verified production workflow behavior. Remaining maturity includes optional CSV export, governed settlement suggestions, recurring household expense templates only if they do not overlap with Subscription Manager, and multi-currency only after explicit product governance approval.

## Future Enhancements

- Optional CSV export after review.
- Simplified settlement suggestions if approved.
- Recurring household expense templates only if they do not overlap with Subscription Manager.
- Multi-currency only after explicit product governance approval.

## Current Implementation

The current implementation stores owner-scoped members, expenses, expense participants, and settlements in isolated `Members`, `Expenses`, `ExpenseParticipants`, and `Settlements` tables. It supports create, edit, archive, restore, permanent delete, equal split, manual split validation, settlement tracking, search, filters, sorting, dashboard metrics, and insights.

The first workflow route is `/household-expense-splitter/members`. Catalog status is approved for live release at version `1.0.0`.

## Governance Notes

Astra: Approved on 2026-07-15.

Partner: Approved Household Expense Splitter live promotion after owner-review browser verification.

Codex: Ran production-configured isolated database migration, verified schema/indexes/version table, verified CRUD/equal split/manual split/archive/restore/delete/search/filter/dashboard/insights smoke behavior, synced overview metadata, and prepared live promotion metadata.
