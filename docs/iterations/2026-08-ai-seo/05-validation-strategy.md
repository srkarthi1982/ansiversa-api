# Iteration 2 AI SEO Validation Strategy

**Status:** Proposed

This is the validation architecture for future approved tasks. No runtime
validation is claimed by this planning iteration.

---

# Evidence Tiers

## Tier 1 — Deterministic Build

- registry builds reproducibly;
- generated output has no drift;
- schemas and bounds pass;
- exactly 100 apps and 14 categories remain;
- visibility and secret scanning pass;
- every output field has provenance; and
- current/future separation passes.

## Tier 2 — Page And Protocol

- canonical URL returns expected status;
- initial HTML contains unique title, description, canonical, H1, and visible
  current product truth;
- JSON-LD matches visible content;
- redirects and not-found behavior are correct;
- sitemap/robots syntax and HTTP headers pass;
- internal links are crawlable; and
- no authenticated content appears in public output.

## Tier 3 — Deployment

- canonical web and API topology works;
- no SPA fallback is returned for machine artifacts;
- representative official crawler user agents are not accidentally blocked;
- cache and CORS policies are scoped correctly;
- production artifact/page parity passes; and
- rollback restores the previous safe state.

## Tier 4 — Provider Observation

- Search Console and Bing Webmaster Tools record crawl/index evidence;
- official structured-data validators pass where applicable;
- provider-exposed AI citation/referral reports are reviewed;
- manual governed query samples record answers and citations; and
- stale or inaccurate answers enter a correction workflow.

Tier 4 is observation, not deterministic acceptance evidence.

---

# Required Test Matrices

## SEO-002 Contract

- required/conditional/optional field behavior;
- enum, length, list, and strict-schema validation;
- unique ID, number, slug, canonical URL, and route;
- exactly one authoritative provenance record per public scalar/list item;
- authority-role and source-field compatibility;
- missing, duplicate, stale, and conflicting claims;
- current/future/retired lifecycle consistency;
- public/governance-only/prohibited visibility;
- relationship target and reason validation;
- deterministic derived values; and
- synthetic representative fixtures without user data.

## Entity Coverage

- platform;
- 14 categories;
- all 100 app overview routes;
- public platform pages;
- representative browser-local, backend-backed, AI-assisted, regulated, and
  professional-boundary apps.

## Viewports And Clients

- raw HTTP without JavaScript;
- rendered desktop and mobile browsers;
- accessibility tree/semantic headings;
- standard crawler user agents; and
- social metadata preview tools where approved.

## Consistency

For every entity:

```text
Authored approved truth
    =
Canonical registry
    =
Visible page
    =
Page metadata
    =
JSON-LD
    =
Sitemap identity
    =
Machine export
```

Any unsupported material mismatch fails validation.

---

# Documentation-Only Validation For This Iteration

- Markdown readability;
- relative links resolve;
- external claims cite first-party sources;
- statuses match the authorized lifecycle;
- no runtime, frontend, backend, migration, configuration, generated artifact,
  crawler rule, or production file changes;
- I1-024 remains Frozen but unauthorized; and
- no implementation or production approval is implied.
