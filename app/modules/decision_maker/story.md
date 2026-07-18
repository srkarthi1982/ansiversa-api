# Decision Maker Story

## Purpose and user journey

Decision Maker is a private structured-thinking aid. An authenticated user creates a decision, adds at least two active options and one active criterion, rates each active pair, reviews transparent scores, selects any active option, records an outcome/reflection, revisits when needed, and may archive the record. The user—not the score—owns the final judgment.

The shared overview enters `/decision-maker/decisions`. Protected list and detail/workspace routes provide loading, empty, filtered-empty, error, missing/inaccessible, and archived read-only states. Every create/edit workflow uses `AvFormDrawer`; destructive actions use `AvRecordActions` and its shared `AvConfirmDialog`.

## Database and ownership

The isolated database owns `Decisions`, `DecisionOptions`, `DecisionCriteria`, and `DecisionRatings`, with custom version table `decision_maker_alembic_version`. Cascades remove nested records with a deleted decision. Unique constraints protect option names, criterion names, and rating pairs. Every nested operation first resolves the owner-scoped parent decision.

## Scoring rules

The scenario scale is 1–5 or 1–10 and cannot change after ratings exist. Active positive weights normalize proportionally. Higher-is-better uses `rating / maximum`; lower-is-better uses `(maximum + 1 - rating) / maximum`. The backend sums normalized weight × normalized rating and reports a two-decimal percentage using `Decimal` and `ROUND_HALF_UP`.

Only active options with every active criterion rated receive scores and ranks. Incomplete options show completion but no score. Equal two-decimal scores share a rank; sort order/name/ID provide display stability only. Contributions explain each criterion. A lower-ranked option may be selected neutrally.

## State and deletion rules

Evaluating requires two active options and one active criterion. Decided requires a complete matrix and selected active option; `decidedAt` is synchronized. Decided evaluations require an explicit move to revisiting before nested changes. Archived decisions are restore-only until restored: metadata, nested records, ratings, and deletion are blocked while archived. Cancelled decisions need no selection. A selected option cannot be deleted. Option/criterion deletion removes dependent ratings transactionally and recalculates results. Decision deletion cascades all nested records after the record is restored if it was archived.

## API, lists, and performance

Stable operations provide dashboard, paginated/searchable/filterable lightweight decision summaries, owner-scoped detail/update/delete, nested option/criterion CRUD, transactional rating-matrix upsert, and rating deletion. Detail responses provide full edit/view fields. Default presentation prioritizes evaluating/revisiting, nearest target date, then recent updates. Query indexes cover user/status/type/target, nested ordering, and ratings.

## Current status and limitations

The implementation targets Workflow Ready Level 3 while remaining `comingSoon`, version `null`, destination approval pending. Production migration `20260716_0009_decision_maker` is applied and verified. No AI recommendation, external research, random choice, voting, collaboration, sharing, integration, professional advice, or outcome guarantee exists. Authenticated browser E2E, manual acceptance, and live promotion require separate approval.
