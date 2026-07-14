# Household Expense Splitter Destination

## Document Status

- App: Household Expense Splitter
- App #: 076
- Slug: `household-expense-splitter`
- Status: Draft destination for owner review
- Destination Status: pending
- Journey Progress: 0 / 100
- Created: 2026-07-14
- Last Reviewed: 2026-07-14

## Destination

Household Expense Splitter should become a lightweight private shared-living ledger inside Ansiversa. Its mature form helps a household record shared costs, understand member balances, and record settlements made outside the platform.

The destination is intentionally bounded. It is not a finance app, accounting system, banking app, invoicing platform, payment gateway, budgeting system, business expense tracker, OCR tool, receipt scanner, payroll system, tax product, subscription manager, or AI product.

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

Current progress remains `0 / 100` until Astra and Partner complete destination review. This implementation must not approve destination metadata or promote the app to live.

## Future Enhancements

- Optional CSV export after review.
- Simplified settlement suggestions if approved.
- Recurring household expense templates only if they do not overlap with Subscription Manager.
- Multi-currency only after explicit product governance approval.
