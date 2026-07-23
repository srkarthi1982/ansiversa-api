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

- separate entity validity from release validity;
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

Entity validation proves one app record is safe and complete. Release
validation separately proves the package retains exactly 100 coherent apps,
unique identities/routes, valid lifecycle/category relationships, and no
critical truth, safety, privacy, or fixed-catalog conflict.

## Entity Coverage

- platform;
- 14 categories;
- all 100 app overview routes;
- public platform pages;
- representative browser-local, backend-backed, AI-assisted, regulated, and
  professional-boundary apps.

## SEO-003 Rendering Architecture

- raw route HTML contains unique approved truth without JavaScript;
- public routes are generated exactly once from an allowlisted manifest;
- private, authenticated, preview, and workflow routes are absent;
- manifest schema, revision, freshness, and digest fail closed;
- visible content, head metadata, canonical URL, structured projection, and
  hydration use the same entity revision;
- missing entities and critical Contract V1 conflicts block release;
- browser hydration produces no material mismatch;
- cache and deployment topology preserve the revision pair;
- production-shaped build time and artifact size stay bounded; and
- rollback restores the prior immutable HTML and manifest pair.

## SEO-004 Structured Knowledge Graph Profile

- graph profile version is explicit;
- emitted node types match the approved allowlist;
- every `@id` follows the stable ID policy;
- exactly 100 `SoftwareApplication` nodes exist;
- category and relationship edges resolve within the same graph release;
- every public graph property maps to SEO-002 authority and provenance;
- prohibited V1 properties are absent;
- aggregate graph and page-local graph bundles use the same immutable revision;
- page-local JSON-LD represents visible page content;
- invalid optional properties are omitted only under approved policy;
- blocker, critical, and major graph failures block V1 release;
- JSON-LD parses and uses the Schema.org context; and
- provider validation evidence is collected only after deployment approval.

## SEO-005 Compiler And Validation Pipeline

- source package inventory is allowlisted and revisioned;
- parsers are deterministic, bounded, and source-type specific;
- normalization does not invent claims or resolve conflicts by source order;
- SEO-002 authority and provenance validation pass;
- entity resolution preserves permanent identity and blocks App #101;
- entity and release validation are separate;
- blocker, critical, and major severities block V1 release unless a separately
  approved omission policy permits a narrower behavior;
- SEO-004 graph compilation passes before manifest generation;
- manifest schema, profile, contract, compiler, source, route, and digest
  metadata are present;
- aggregate graph, page bundles, metadata, and artifacts share one immutable
  revision;
- full compilation is deterministic;
- incremental compilation, if later implemented, still produces a complete
  immutable release package;
- stale-output, last-known-good, fallback, and rollback rules are validated;
- validation reports are generated without leaking governance-only or private
  content; and
- no request-time parsing, AI calls, user-data reads, or SEO regeneration occur.

## AI SEO Implementation Readiness Review

- SEO-001 through SEO-005 are frozen or completed;
- implementation is authorized after Astra approval and Product Owner decision;
- no SEO-006 is created;
- first implementation repository and commit boundary are defined;
- feature flags are disabled by default;
- current Knowledge publisher migration is staged through shadow generation;
- certification gates are explicit;
- rollback behavior is defined before production enablement; and
- production remains unchanged.

## AI SEO Implementation Phase 1

- Astra review approved commit `5f0f852`;
- compiler package remains disabled by default;
- package is not imported by runtime routes or application startup;
- Knowledge builder and publisher remain the only active public-truth path;
- source inventory output is deterministically ordered;
- stable serialization and digest helpers are deterministic;
- allowlisted source classification accepts only approved source shapes;
- validation fixtures reject unsupported visibility and unsafe data;
- focused tests pass; and
- generated public artifacts remain unchanged.

Phase 2 is completed and Frozen after Astra review.

## AI SEO Implementation Phase 2

- governance/scope review approved for commit `3136c41`;
- source-level Astra review approved correction commit `7ede8ae`;
- Phase 2 is completed and Frozen;
- parser accepts only allowlisted source inventory entries;
- JSON parsing is strict and structured;
- Markdown parsing extracts only bounded allowlisted sections;
- normalization covers text, slugs, routes, canonical URLs, enums, stable lists,
  and digest inputs;
- conflicts between authoritative values fail closed;
- validation findings use the approved severity model, with blocker, critical,
  and major findings blocking V1 release by default;
- entity resolution enforces exactly 100 apps and 14 categories;
- duplicate identities, App #101, and unresolved relationships block release;
- graph compilation enforces approved node types, allowed properties, stable
  IDs, deterministic ordering, and relationship resolution;
- graph compilation emits no manifest or public output after blocking
  validation failures;
- public manifest boundary failures suppress public render output;
- graph property allowlists apply to every supported node type;
- Internal Release Manifest keeps governance evidence internal;
- Public Render Manifest excludes source inventory, diagnostics, approver
  identities, rollback evidence, validation reports, internal paths, and
  secrets;
- validation reports are internal test outputs only;
- repeated pipeline runs produce equivalent serialized output;
- Knowledge registry and public artifact drift checks remain current; and
- production remains unchanged.

## AI SEO Implementation Phase 3

- Phase 3 is authorized and implemented;
- Astra source review requested adapter corrections;
- adapter corrections are implemented and approved;
- Phase 3 is completed and Frozen;
- current Knowledge publisher remains the active production publisher;
- shadow comparison operates on supplied in-memory snapshots only;
- Knowledge artifact snapshot conversion does not write or publish artifacts;
- comparison reports are internal only;
- Knowledge and compiler adapters emit the same canonical semantic comparison
  projection;
- system-specific release IDs remain outside parity payloads;
- entity, graph, manifest, metadata, canonical URL, digest, missing,
  unexpected, duplicate, ordering, and validation-severity differences are
  detected;
- duplicate comparable items and failed candidate validation fail closed;
- repeated comparisons against identical snapshots produce identical reports;
- real Knowledge-versus-compiler adapter parity has no structural false
  positives when public truth is equivalent;
- no public serving, API exposure, frontend integration, deployment change,
  runtime startup change, artifact replacement, or production behavior change
  occurs.

Phase 4 remains blocked until separate Product Owner authorization completes.

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
