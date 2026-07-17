# Net Worth Tracker Story

## Purpose and workflow

Net Worth Tracker is a private manual planning record for assets and liabilities. Authenticated users create accounts, record authoritative balances, archive inactive accounts, capture immutable dated snapshots, and compare historical changes by currency. It is not banking, accounting, valuation, credit, tax, or investment-advice software.

## User journey and UI

The shared overview enters `/net-worth-tracker/accounts`. Protected routes cover accounts, account detail and balance history, snapshots, snapshot detail, and comparison. Create/edit workflows use `AvFormDrawer`; destructive workflows use `AvRecordActions` with `AvConfirmDialog`. Pages expose loading, empty, filtered-empty, error, missing/inaccessible, and archived read-only states in responsive cards.

## Database and calculation design

The isolated database owns `NetWorthAccounts`, `NetWorthBalanceEntries`, `NetWorthSnapshots`, and `NetWorthSnapshotItems`, with custom version table `net_worth_tracker_alembic_version`. Values use `Numeric(16,2)` and backend `Decimal` with `ROUND_HALF_UP`. Asset and liability balances are non-negative; liabilities are subtracted only during totals. Active included accounts contribute to per-currency totals. Negative net worth is valid.

Latest deterministic balance history is authoritative. Account balance edits append history; entry edits/deletes recalculate current balance. Account names are owner-scoped and case-insensitively unique. Archived accounts reject new history and metadata edits, allowing only a restore update back to active status, and are excluded from active totals. Accounts with history or snapshot references cannot be permanently deleted.

One snapshot is allowed per user/date. Snapshot creation transactionally copies active account identity, category, currency, inclusion flag, and balance. Captures never depend on later live account changes. Comparison calculates per-currency asset, liability, and net-worth differences; percentage is absent for a zero baseline and uses the absolute negative baseline safely. No conversion occurs.

## API and performance

Stable operations provide dashboard, paginated/filterable accounts, nested balance mutations, paginated/filterable snapshots, snapshot details/deletion, and comparison. Ownership is enforced at every parent and nested boundary. Query indexes cover user/status/type/currency, account/date history, snapshot dates, and snapshot-item currencies. Account ordering is active first then type and recent update; snapshots are newest first.

## Current status and limitations

The workflow is technically Level 3 while remaining `comingSoon`, version `null`, destination approval pending. The production-configured isolated migration is verified at `20260716_0008_net_worth_tracker`. No bank linking, imports, feeds, conversions, charts, exports, custom categories, advice, or official statements are included. Authenticated browser E2E, manual acceptance, and live promotion require separate approval.
