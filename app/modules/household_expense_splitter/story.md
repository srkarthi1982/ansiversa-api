# Household Expense Splitter Story

## Purpose

Household Expense Splitter stores owner-scoped members, shared expenses, participants, manual/equal shares, and settlement records. It exists for households that need a simple private way to understand shared costs and repayments.

The app is not a finance app, accounting system, banking app, invoicing platform, payment gateway, budgeting system, business expense tracker, OCR tool, receipt scanner, payroll product, tax product, subscription manager, or AI workflow.

## Workflow

The workflow is:

```text
Overview
→ Members
→ Expenses
→ Settlements
→ Insights
```

## User Journey

1. The user opens the overview and chooses Explore.
2. The Members route lets the user create, edit, and delete household members when no linked records exist.
3. The Expenses route records shared expenses with payer, participants, equal/manual split, category, date, notes, archive/restore, and delete actions.
4. The Settlements route records repayments between members.
5. The Insights route summarizes total expenses, settlements, outstanding balances, member/category spend, recent expenses, and recent settlements.

## Database Design

The module uses an isolated database configured by `HOUSEHOLD_EXPENSE_SPLITTER_DATABASE_URL`.

Tables:

- `Members`: owner-scoped household members.
- `Expenses`: owner-scoped shared expense records.
- `ExpenseParticipants`: expense-member shares.
- `Settlements`: owner-scoped repayment records.

Indexes support owner lists, member lookups, category filters, archive filters, split-method filters, date sorting, and settlement lookups.

## API Design

Routes are mounted under:

```text
/api/v1/household-expense-splitter
```

Primary endpoints:

- `GET /dashboard`
- `GET /insights`
- member CRUD endpoints
- expense CRUD, archive, and restore endpoints
- settlement CRUD endpoints

List endpoints return lightweight summaries. Detail endpoints return notes for edit workflows.

## Shared Components Used

The backend follows the isolated mini-app module pattern:

- dedicated SQLAlchemy base and session factory
- owner-scoped dependencies
- repository/service/router separation
- OpenAPI operation IDs
- module-specific Alembic environment and version table

## Performance Considerations

V1 stores metadata only and intentionally excludes receipt files, OCR payloads, payment payloads, and AI output. Balance calculations run over owner-scoped records and remain lightweight for household-scale usage.

## Current Status

App #076 is implemented as Workflow Ready for Astra/Partner review. It remains `comingSoon` with `version: null` and no approved destination metadata.

## Known Limitations

- No payment processing, bank sync, OCR, receipt scanning, exports, recurring expenses, AI, or settlement recommendations.
- One owner controls the household workspace.
- Settlements are record-only and do not move money.

## Future Enhancements

- CSV export after review.
- Optional recurring household expense templates.
- Simplified settlement suggestions if approved.
- Multi-currency only after explicit governance approval.

## Current Implementation

The implementation provides owner-scoped member CRUD, expense CRUD with equal/manual splits, archive/restore/delete, settlement CRUD, search/filter/sort, dashboard, insights, overview metadata, migration, and lifecycle documentation.
