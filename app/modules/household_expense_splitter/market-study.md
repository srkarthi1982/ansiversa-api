# Household Expense Splitter Market Study

## Document Status

- App: Household Expense Splitter
- App #: 076
- Slug: `household-expense-splitter`
- Market Version: 1
- Created: 2026-07-14
- Last Reviewed: 2026-07-14
- Next Review: 2026-10-14
- Status: Research only

## Purpose

This study captures public market patterns around shared household expense splitting. It informs Ansiversa product thinking but does not define implementation commitments.

## Problem Statement

Families, couples, roommates, and shared living groups often need a simple way to record who paid for a shared cost, who participated, and whether anyone has paid another member back. Spreadsheets and chat threads work for small cases but become hard to audit when expenses, repayments, and participants change over time.

## Target Users

- Roommates splitting groceries, utilities, repairs, rent-adjacent purchases, and supplies.
- Couples or families who share everyday household costs.
- Shared living groups that settle up periodically outside the app.
- People who want a lightweight shared-cost ledger without banking or accounting features.

## Competitor Landscape

- Splitwise focuses on shared expenses, balances, groups, categorization, equal and unequal splits, settlements, and optional payment integrations.
- Tricount emphasizes group expenses, equal/custom splits, clear balances, and settlement suggestions for roommates, trips, and couples.
- Settle Up and similar apps provide group expense tracking, debt simplification, and settlement flows.
- Newer competitors increasingly add AI assistants, photo receipt handling, travel features, imports, and payment-related functionality.

## Common Market Features

- Members or group participants.
- Expenses with payer, category, date, amount, notes, and participants.
- Equal, exact/manual, percentage, or share-based split methods.
- Running balances and settlement recording.
- Recent activity and summaries by member/category.
- Optional exports, multi-currency, receipt images, recurring bills, and payment integrations in broader products.

## User Love Signals

- Users value clear balances and who-owes-whom summaries.
- Equal and exact/manual splits cover many household cases.
- Settlement recording keeps the ledger useful even when payment happens elsewhere.
- Category summaries help explain why balances changed.
- Low-friction entry matters more than formal accounting structure.

## Complaints And Friction

- Payment integrations can confuse users when they only need a record.
- Too many split types can slow simple household entry.
- Receipt/OCR workflows create privacy and data-retention concerns.
- Finance-style products can feel too formal for roommates and families.
- Free tiers often limit activity history, exports, or group features.

## Pricing And Paywall Observations

- Consumer shared-expense tools commonly offer free basic splitting with paid upgrades for receipt scanning, advanced currencies, exports, unlimited usage, or premium support.
- Payment integrations may be region-specific and outside the core ledger.
- Ansiversa V1 should avoid paywall-shaped complexity and stay focused on owner-scoped household records.

## AI Trends

- Some newer tools promote AI assistants, receipt parsing, and automated categorization.
- V1 intentionally excludes AI, OCR, receipt scanning, and automated financial interpretation.

## UX Patterns Worth Studying

- Start with members before expense entry.
- Keep payer, participants, split method, and amount close together.
- Show balances in plain language rather than accounting terms.
- Separate settlement recording from actual payment processing.
- Keep category and member summaries simple.

## Ansiversa Opportunities

- Provide a private household sharing workspace inside the Ansiversa shell.
- Keep the scope narrower than finance apps: members, expenses, settlements, insights.
- Avoid banking, payment, receipt, OCR, invoice, tax, subscription, payroll, ecommerce, and AI workflows.
- Make manual splits precise while keeping equal splits fast.

## Avoid List

- Do not copy competitor wording, screens, templates, proprietary settlement algorithms, or brand patterns.
- Do not integrate payments, bank sync, cards, wallets, invoices, receipts, OCR, taxes, payroll, subscriptions, or AI.
- Do not imply financial advice, accounting correctness, or legal debt enforcement.

## Product Questions

- Should V2 support recurring household costs, or would that overlap with Subscription Manager?
- Should exports be added after the review workflow matures?
- Should multi-currency ever be supported, or should this remain a single household-currency ledger?
- Should simplified repayment suggestions be added after more usage data exists?

## Sources

- Splitwise: https://www.splitwise.com/
- Splitwise Google Play listing: https://play.google.com/store/apps/details?id=com.Splitwise.SplitwiseMobile
- Tricount: https://tricount.com/en-us/
- Tricount Google Play listing: https://play.google.com/store/apps/details?id=com.tribab.tricount.android
- Tricount roommate expense guidance: https://tricount.com/en-us/blog/managing-shared-expenses-as-roommates

## Review Notes

- 2026-07-14: Initial market study created during App #076 development.

## Revision History

- v1: Initial public-market scan and Ansiversa opportunity framing.
