# Price Checker Destination

## App Name

Price Checker

## Destination Status

Approved v1.0

## Final Product Vision

Price Checker should become Ansiversa's trusted private purchase-decision
companion: a browser-first place to compare manually entered prices, understand
possible savings, and make calmer buying decisions without turning Ansiversa
into a marketplace, scraper, coupon engine, affiliate platform, or shopping
surveillance product.

At maturity, Price Checker should help users answer practical questions like
"Is this price better than before?", "Where have I seen this item cheaper?",
"Which category am I spending attention on?", and "Does this deal actually
help me?" The product should improve purchase confidence through clarity,
manual control, and local insight, not through automated store crawling or
pressure to buy.

The mature product should feel useful before a purchase, during comparison, and
after reviewing saved analyses. It should remain lightweight, private, and
honest about the fact that manually entered prices are decision aids, not
verified live market data.
Its market-informed position is a user-owned price decision log: data source,
last-checked context, shipping/tax notes, coupons, membership assumptions, and
manual-entry limits should stay visible so users understand why a comparison is
or is not trustworthy.

## Target Users

- Shoppers comparing prices across stores before buying.
- Families tracking recurring purchase decisions.
- Students and budget-conscious users checking whether a deal is meaningful.
- Small business owners comparing supplies or equipment prices manually.
- Ansiversa users who want private purchase notes without shopping accounts.
- Privacy-conscious users who do not want shopping behavior synced to a
  backend service.

## Core User Problems

- Users often remember that a price changed, but not by how much.
- Discounts can be misleading without previous-price context.
- Shipping, taxes, coupons, memberships, condition, seller, and region can make
  two prices look comparable when they are not.
- Shopping comparisons are scattered across notes, screenshots, carts, and
  memory.
- Many shopping tools rely on tracking, affiliate links, scraping, alerts, or
  behavioral data collection.
- Users need simple local records without creating another shopping account.
- Purchase decisions benefit from category, store, and savings insight, but can
  become manipulative if the app pushes users toward transactions.

## Final Capabilities

- Create manual price analyses with product name, store, category, current
  price, previous price, and notes.
- Estimate savings or price increase when previous-price context is available.
- Save, search, filter, edit, duplicate, delete, and clear local analyses.
- Show local insights such as total products, average price, highest and lowest
  prices, estimated savings, frequent stores, recent analyses, and category
  patterns.
- Support clear empty, loading, success, error, and delete confirmation states.
- Provide optional currency labels or simple currency support after governance
  review.
- Offer import/export for browser-local backup and portability.
- Help users compare manually entered prices without claiming live verification.
- Capture source, last-checked time, shipping/tax/coupon notes, and other
  assumptions when users need stronger comparison context.
- Provide keyboard-friendly analysis creation and review workflows.
- Keep all shopping notes and price records local by default.
- Make privacy and manual-data limitations visible.

## Advanced Capabilities

- Unit-price comparison for groceries, supplies, and recurring purchases.
- Source-confidence and last-checked indicators for user-entered or imported
  prices.
- Browser-local wish list or watch list for manual review.
- Optional local reminders to recheck an item after a user-defined time.
- Local import/export of analyses for backup or device movement.
- Currency and region labeling without turning into exchange-rate trading.
- Duplicate-product detection across local analyses.
- Visual trend summaries based only on user-entered records.
- Explicit handoffs to budget or expense tools after user action.
- Trusted API integrations only after privacy, legal, accuracy, and platform
  review.

## AI Opportunities

- Explain whether a price change looks meaningful based on user-entered data.
- Suggest clearer notes, categories, or comparison criteria.
- Help users understand unit prices, sale wording, and discount math.
- Identify possible false-discount patterns in local records.
- Summarize saved analyses into practical purchase considerations.
- Suggest questions to ask before buying, such as warranty, shipping, or
  recurring cost checks.

AI features must not receive shopping history, product names, store names,
notes, or purchase intent by default. Any AI handoff must be explicit,
privacy-reviewed, and clear about what local data is being sent.

## Ecosystem Connections

- Expense Tracker: receive approved purchase records or spending notes after an
  explicit handoff.
- Budget Planner: help users decide whether a planned purchase fits a budget.
- Savings Goal Planner: compare purchases against savings goals before buying.
- Shopping List: share manually reviewed items only through explicit user
  action if that app exists or is later introduced.
- Discount Calculator: support math-focused discount checks without Price
  Checker absorbing every calculator responsibility.
- Markdown Editor: export comparison notes into a private shopping or research
  note.
- AI Notes Summarizer: summarize selected purchase notes only after explicit
  user action.

## Weekly Return Value

Users return weekly when checking recurring purchases, comparing sale prices,
planning household spending, reviewing whether a deal is meaningful, or looking
back at saved analyses before buying. Price Checker earns repeat use by helping
users feel less rushed and more informed.

The mature product should make shopping decisions calmer, not louder. It should
help users compare, reflect, and decide without nudging them into marketplaces,
ads, affiliate funnels, or automated tracking.

## Success Criteria

- Users can create and review manual price analyses quickly.
- Savings and price-change calculations are clear and trustworthy.
- Saved analyses remain local by default.
- Users understand that prices are manually entered and not live-verified.
- Users can distinguish observed prices, assumptions, and user-entered notes
  from any automated or AI-assisted interpretation.
- Search, filters, duplication, editing, deletion, and insights support real
  repeat use.
- Import/export, currency support, reminders, or integrations preserve privacy
  and user control.
- The app does not drift into scraping, affiliate marketing, coupons,
  marketplace listings, or automated purchase behavior.
- The product helps users make better decisions without increasing shopping
  pressure.

## Journey Progress

Current Position: 76 / 100
Destination: 100 / 100
Remaining Journey: 24 / 100

This estimate describes product maturity, not feature completion. Price Checker
already has a strong live V1 with manual analyses, browser-local persistence,
search, filtering, editing, duplication, deletion, clearing, insights, and no
backend runtime. The remaining journey is mostly decision-quality maturity:
clearer manual-data limits, import/export, optional currency labeling,
unit-price support, lightweight local reminders, accessibility polish, and
careful governance around any API integration, alerting, or AI assistance.

## Future Version Ideas

- V1.1: Improve savings explanations, validation, delete confirmation, and
  manual-data privacy messaging.
- V1.2: Add import/export, currency labels, and richer category/store insights.
- V1.3: Add unit-price comparison and duplicate-product detection.
- V1.4: Add explicit handoffs to Expense Tracker, Budget Planner, Savings Goal
  Planner, or Markdown Editor.
- V2: Consider optional price alerts, trusted API integrations, or AI purchase
  summaries only after governance review and destination update.

## Non Goals

Price Checker is not intended to become:

- A shopping marketplace.
- A store crawler or scraper.
- A coupon platform.
- An affiliate marketing engine.
- A URL shortener or tracking-link platform.
- A live price-monitoring service by default.
- A checkout, cart, or automated purchasing tool.
- A financial or investment advice product.
- A competitor intelligence or retail surveillance platform.
- A product review marketplace.
- A browser extension or automated shopping agent by default.

These directions should remain out of scope unless the destination itself is
reviewed and intentionally changed.

## Guiding Principles

Every Price Checker feature should:

- Preserve browser-local privacy by default.
- Improve purchase clarity without increasing shopping pressure.
- Be honest about manually entered data.
- Make price source, last-checked time, and comparison assumptions visible.
- Help users compare prices, savings, and context calmly.
- Avoid hidden tracking, affiliate incentives, and behavioral profiling.
- Keep integrations explicit and user-controlled.
- Prefer decision support over transaction capture.
- Avoid scraping, marketplace, coupon, and alert-platform drift.

## Governance Notes

This destination is aspirational. It describes the target product direction,
not the current implementation and not an authorization to build every feature
now.

destination.md is not a promise of what will be built next. It is a
description of what the product could ultimately become if time, user value,
and platform direction remain aligned.

Product owner and Astra review are required before accepting, prioritizing, or
implementing any destination item. Particular care is needed before approving
price alerts, shopping APIs, currency normalization, AI purchase suggestions,
import/export, reminders, or cross-app handoffs because shopping data can reveal
personal habits, finances, household needs, location patterns, and purchase
intent.

## Last Governance Review

Product Owner:
Astra: Approved on 2026-07-03. Journey Progress 76 / 100 accepted.
Codex: Drafted destination and identified governance discussion points.

Status:

Approved
