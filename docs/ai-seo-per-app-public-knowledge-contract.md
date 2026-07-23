# Ansiversa Per-App Public Knowledge Contract

**Contract:** AI SEO Per-App Public Knowledge
**Contract Version:** 1
**Status:** Approved
**Created:** 2026-07-23
**Approved:** 2026-07-23
**Task:** SEO-002
**Scope:** Specification only
**Architecture Reviewer:** Astra — Approved with incorporated refinements
**Product Owner:** Karthikeyan Ramalingam — Approved

This contract defines what Ansiversa may say publicly about each application
and how every claim remains attributable, reviewable, current, and safe.

It is implementation-independent. It does not change the Canonical AI Knowledge
Registry, compiler, publisher, frontend, metadata, rendering, or production.

---

# Governing Law

## AI SEO Engineering Law #1

> Every public claim must have exactly one approved source of truth.

The contract applies this law at field and list-item level. A claim may have
supporting evidence in several documents, but exactly one source is
authoritative for its published value.

---

# Contract Goals

The contract must:

- give every app one stable public entity identity;
- separate public product truth from research, aspiration, and internal detail;
- make ownership and provenance deterministic;
- prevent marketing or generated content from outrunning implementation;
- make conflicts fail visibly;
- support canonical pages and machine projections from the same record;
- preserve the fixed 100-app catalog and App #101 prohibition; and
- remain independent of SEO-003's rendering technology.

---

# Logical Public App Entity

The logical entity is named `PublicAppEntityV1`.

```text
PublicAppEntityV1
├── contractVersion
├── identity
├── classification
├── lifecycle
├── content
├── relationships
├── discovery
└── governance
```

Physical storage, serialization, registry migration, and public projection
shapes remain future implementation decisions.

---

# Field Classes

| Class | Meaning |
|---|---|
| Required | Every public app must provide a valid current value |
| Conditional | Required when its stated condition is true |
| Optional | May be omitted without inventing a placeholder |
| Platform-owned | Platform governance approves the authoritative value |
| App-owned | The application owner approves the authoritative value |
| Derived | Deterministically computed from approved fields |
| Generated | Projection/build metadata; never authored as a product claim |
| Governance-only | Required for control but omitted from public projection unless separately approved |
| Prohibited | Must never enter the entity or its public projections |

Missing optional data stays absent. The compiler must not invent copy to make a
record appear complete.

---

# Version 1 Schema

## Root

| Field | Type | Requirement | Visibility | Owner |
|---|---|---|---|---|
| `contractVersion` | integer | Required; exactly `1` | Public | Platform |
| `identity` | object | Required | Public | Platform |
| `classification` | object | Required | Public | Platform |
| `lifecycle` | object | Required | Public | Platform |
| `content` | object | Required | Public | Mixed by field |
| `relationships` | object | Required | Public | Platform with app proposals |
| `discovery` | object | Required | Public | Mixed by field |
| `governance` | object | Required | Governance-only | Platform |

## Identity

| Field | Type / bound | Requirement | Authority |
|---|---|---|---|
| `appId` | stable string, 80 | Required and unique | Catalog registry |
| `number` | integer, 1–100 | Required and unique | Catalog registry |
| `name` | string, 120 | Required | Catalog registry |
| `slug` | lowercase route slug, 100 | Required and unique | Route registry |
| `canonicalUrl` | HTTPS URL, 240 | Derived and required | Canonical domain + `overviewRoute` |
| `overviewRoute` | canonical absolute path, 140 | Required and unique | Route registry |
| `exploreRoute` | canonical absolute path, 180 | Conditional when a current workflow route exists | Route registry |

`appId` is permanent across wording changes. A replacement within the fixed
catalog requires a separately governed identity decision.

Replacement and retirement rules:

- a retired `appId` is never silently reassigned;
- a replacement receives its own permanent `appId`;
- reuse or reassignment of a catalog slot/number requires a separate governance
  decision;
- a replacement must not inherit claims, provenance, reviews, or lifecycle
  history from the retired entity; and
- historical redirects and archival representations belong to a later
  contract.

## Classification

| Field | Type / bound | Requirement | Authority |
|---|---|---|---|
| `entityType` | enum | Required; `software_application` | Contract |
| `categoryId` | stable string, 80 | Required | Catalog registry |
| `categoryName` | string, 120 | Derived and required | Approved category registry |
| `platformId` | stable string, 80 | Required; `ansiversa` | Contract |

## Lifecycle

| Field | Type / bound | Requirement | Authority |
|---|---|---|---|
| `status` | enum | Required | Catalog registry |
| `launchStatus` | enum | Required | Catalog registry |
| `version` | semantic version or null | Conditional; required for live apps | Catalog registry |
| `availability` | enum | Derived and required | Lifecycle mapping |
| `currentState` | enum | Derived and required | Lifecycle mapping |

Allowed contract values:

```text
status:
active | inactive | archived

launchStatus:
live | coming_soon | retired

availability:
publicly_available | announced | unavailable

currentState:
current | future | retired
```

Only `active + live + current` apps may publish current capability claims as
available. Iteration 2 preserves exactly 100 current public apps unless a
separate catalog governance decision changes a member while retaining the fixed
total.

## Content

| Field | Type / bound | Requirement | Authority |
|---|---|---|---|
| `purpose` | string, 40–500 | Required | Overview metadata |
| `shortDescription` | string, 40–240 | Required | Overview metadata |
| `intendedAudiences` | unique list, 1–8 items, 80/item | Required | Overview metadata |
| `userProblems` | unique list, 1–8 items, 240/item | Required | Overview metadata |
| `currentCapabilities` | unique list, 1–12 items, 240/item | Required | App `story.md`, approved current-capability section |
| `workflowSteps` | ordered list, 1–10 items, 120/item | Required | Overview metadata |
| `commonUseCases` | unique list, 0–10 items, 180/item | Optional | Overview metadata |
| `limitations` | unique list, 1–12 items, 240/item | Required | App `story.md` |
| `safetyNotes` | unique list, 0–12 items, 240/item | Conditional for regulated, professional, safety-sensitive, or AI-assisted claims | App `story.md` |
| `publicFaqs` | list of question/answer objects, maximum 12 | Optional | Approved app FAQ/public communication source |

Every capability must describe behavior available now. A missing limitations
list is not interpreted as "no limitations"; it is a contract failure requiring
app review.

FAQ bounds:

```text
question: 20–180 characters
answer:   20–600 characters
```

FAQs may clarify current behavior and limitations. They may not introduce a
capability absent from `currentCapabilities`.

## Relationships

| Field | Type | Requirement | Authority |
|---|---|---|---|
| `parentPlatform` | entity reference | Required; Ansiversa | Contract |
| `category` | entity reference | Required | Catalog/category registry |
| `relatedApps` | unique list, maximum 8 | Optional | Approved relationship rules |

Related-app entry:

| Field | Requirement |
|---|---|
| `appId` | Required existing public app ID |
| `relationshipType` | Required approved enum |
| `reasonCode` | Required approved bounded code |
| `displayReason` | Optional approved public wording |

Initial relationship types proposed for review:

```text
same_category
next_workflow
input_to
output_from
alternative_scope
complementary
```

Same-category membership may be derived. Semantic relationships require an
approved app proposal and platform validation. Popularity, user profiling, and
model-generated similarity are not relationship authorities.

## Discovery

| Field | Type / bound | Requirement | Authority |
|---|---|---|---|
| `aliases` | unique list, 1–12 items, 80/item | Required | App proposal, platform approval |
| `searchPhrases` | unique list, 0–16 items, 140/item | Optional derived projection | Approved content fields |
| `disambiguators` | unique list, 0–8 items, 120/item | Optional | App proposal, platform approval |
| `language` | BCP 47 tag | Required; initial value `en` | Platform |

Aliases must be names, common abbreviations, or truthful problem vocabulary.
They must not contain competitor trademarks for traffic capture, unsupported
features, guarantees, or repetitive keyword variants.

## Governance

| Field | Type | Requirement |
|---|---|---|
| `entityRevision` | content hash or immutable revision | Required |
| `approvedAt` | UTC timestamp | Required |
| `approvedByRole` | bounded role | Required |
| `reviewedAt` | UTC date | Required |
| `reviewDueAt` | UTC date | Required |
| `reviewOwnerRole` | bounded role | Required |
| `fieldProvenance` | map keyed by public field/item path | Required |
| `validationState` | enum | Required |

Public projections may expose only an approved role and a non-sensitive review
date. They must not expose internal actor/approver names, repository paths,
content hashes, source revisions, approval notes, conflict records, or internal
review assignments.

The governed repository may retain decision records identifying accountable
people. That internal accountability does not make their identity a public app
claim.

---

# Field Provenance Contract

Every public scalar and every publishable list item must resolve to exactly one
provenance record:

```text
fieldPath
sourceType
repository
path
sectionOrKey
sourceRevision
authorityRole
approvalState
approvedAt
reviewOwnerRole
reviewedAt
reviewDueAt
visibility
derivationRule
```

Rules:

- `fieldPath` uses a stable JSON-pointer-style path.
- Capabilities, limitations, safety notes, FAQs, related apps, and every other
  publishable claim list receive item-level provenance. One source reference
  for an entire mixed list is insufficient.
- `sourceRevision` is content-addressed or an immutable repository revision.
- `derivationRule` is required only for derived/generated values.
- source paths and internal review metadata are governance-only by default.
- a public value without complete provenance fails compilation.
- two authoritative provenance records for one field fail compilation.

Supporting sources may be recorded separately as evidence. They never replace
the single authoritative provenance record.

---

# Ownership Matrix

| Field family | Value owner | Approval owner | Review owner |
|---|---|---|---|
| Stable ID, number, name, lifecycle, version, category | Platform catalog | Product Owner or delegated catalog authority | Platform catalog owner |
| Slug and canonical routes | Platform routing | Platform architecture | Frontend/platform route owner |
| Purpose, description, audiences, problems, workflow | App product | Product Owner/delegated app approval | App product owner |
| Current capabilities, limitations, safety | App implementation | App owner plus engineering verification | App engineering owner |
| FAQs and approved communication | App communication | Product/marketing approval after truth validation | App product/communication owner |
| Alias/disambiguation vocabulary | App proposal | Platform knowledge governance | Platform knowledge owner |
| Category/platform relations | Platform | Platform knowledge governance | Platform catalog owner |
| Semantic related-app relations | App proposal | Platform knowledge governance | Both affected app owners |
| Canonical URL and search phrases | Derived | Compiler contract | Platform knowledge owner |
| Provenance, revision, validation state | Generated governance | Platform knowledge governance | Platform knowledge owner |

An owner may delegate operational review, but the accountable role remains
recorded.

---

# Source Authority And Precedence

Precedence is field-specific. It is not permission to silently choose a value.

| Source | Authoritative fields | Supporting/checking role | Never authoritative for |
|---|---|---|---|
| Catalog registry | ID, number, name, category, lifecycle, version | Fixed-count and lifecycle validation | Marketing copy, capabilities, routes |
| Route registry | slug, overview route, explore route | Catalog slug/route consistency | Product claims |
| Overview metadata | purpose, description, audiences, problems, workflow, use cases | Visible-page wording baseline | Technical truth when contradicted by story |
| `story.md` | current capabilities, limitations, safety | Validates all current claims | Future roadmap or market demand |
| `marketing.md` | No direct V1 compiler authority; approved FAQ/communication candidate only | Wording proposals checked against authoritative truth | Identity, lifecycle, unsupported capabilities |
| `market-study.md` | No public-field authority | Research vocabulary candidate requiring explicit promotion | Product requirements or current claims |
| `destination.md` | Future-direction governance only | Non-goals and long-term review context | Current availability or current capabilities |

## Source-Specific Rules

### Catalog Registry

The finalized platform catalog is the sole authority for app identity and
lifecycle. A frontend route registry may not declare an app live independently.

### Route Registry

The canonical route registry is the sole route authority. Routes appearing in
documents or marketing copy are references and must match it.

### Overview Metadata

Overview metadata owns approved public presentation fields. It must be revised
when story-verified implementation makes its wording stale.

### `story.md`

`story.md` owns current implementation capability, limitation, and safety
truth. Only approved current-state sections participate. Changelogs and future
enhancements are excluded.

### `marketing.md`

`marketing.md` remains outside automatic parsing in Contract V1. SEO-008 must
define a typed promotion mechanism before any field becomes a compiler input.
Marketing may propose wording, but no `marketing.md` field enters the compiler
in V1. Marketing wording can never override identity, lifecycle, routes,
capability, limitation, or safety truth.

### `market-study.md`

Research remains internal and non-authoritative. Vocabulary or user questions
may enter public knowledge only through an explicit, reviewed promotion into an
authoritative field.

### `destination.md`

Destination content remains future or directional. It may validate non-goals
and supply separately marked future entities later, but it cannot populate
current app claims in V1.

---

# Current Versus Future Claims

Every claim is classified:

| State | Public current app entity |
|---|---|
| `current` | Allowed when authoritative, approved, visible, and fresh |
| `future` | Prohibited from current fields |
| `retired` | Removed from current capability projections; historical handling deferred |
| `unknown` | Compilation failure for required fields; omission for optional fields |

Words such as planned, upcoming, soon, intended, will, roadmap, target, and
future trigger review. They must not be normalized into current language.

An announced/coming-soon app requires a separate future-entity contract. It
must not masquerade as publicly available software.

---

# Visibility Rules

Allowed public information:

- approved product identity;
- canonical public routes;
- current lifecycle and availability;
- approved purpose and audience;
- current capability and workflow summaries;
- necessary limitations and safety boundaries;
- approved public relationships, aliases, and FAQs; and
- non-sensitive freshness indicators if later projected.

Governance-only information:

- source repository paths;
- internal review notes;
- approver identity beyond approved public roles;
- content hashes and compiler diagnostics;
- conflict records; and
- internal freshness escalation.

Default-deny information:

- authenticated or user-specific content;
- app database records or identifiers;
- internal/restricted documentation;
- unpublished roadmap;
- raw Markdown;
- source code and internal file topology in public output;
- infrastructure/provider configuration;
- vulnerabilities, secrets, tokens, cookies, headers, SQL, or stack traces;
- private analytics;
- competitor-derived wording; and
- model-generated claims without authoritative approval.

Visibility is field-level. A public source document does not make every section
public.

---

# Freshness And Review

| Field family | Maximum scheduled review | Event-triggered review |
|---|---:|---|
| Identity/routes/lifecycle/version | 365 days | Catalog, route, promotion, retirement, or version change |
| Purpose/description/audiences/problems/workflow | 180 days | Product or overview change |
| Capabilities/limitations/safety | 90 days | Runtime, API, UI, policy, dependency, or safety change |
| FAQs/aliases/disambiguators | 180 days | Communication, support, or terminology change |
| Relationships | 180 days | Category, workflow, availability, or related-app change |

Rules:

- event-triggered review overrides the scheduled interval;
- a required field past `reviewDueAt` fails release builds;
- a stale optional field is omitted rather than published;
- safety-critical stale fields block publication;
- automated hash changes identify review need but do not approve new truth; and
- freshness dates are derived from governed reviews, not file modification time.

---

# Conflict Policy

Compilation must fail when approved sources disagree materially.

Conflict classes:

```text
identity_conflict
route_conflict
lifecycle_conflict
category_conflict
current_capability_conflict
limitation_conflict
safety_conflict
visibility_conflict
future_current_conflict
provenance_conflict
freshness_conflict
relationship_conflict
```

Process:

1. detect and report bounded field paths, sources, and revisions;
2. emit no updated public artifact for the invalid entity;
3. preserve the last-known-approved artifact only when it is still current,
   safe, and permitted by an explicitly approved deployment policy;
4. assign resolution to the accountable source owners;
5. update the authoritative source, not a generated output;
6. record approval; and
7. rebuild and validate.

The compiler must not:

- use source order as an implicit tie-breaker;
- prefer newer file modification time;
- prefer longer or more marketable text;
- merge contradictory lists;
- ask a language model to reconcile claims; or
- downgrade a conflict to a warning for required/public fields.

Equivalent formatting differences may normalize only through an approved
deterministic rule.

---

# Entity Validity And Release Validity

## Entity Validation

Entity validation determines whether one app record is safe and complete.

An invalid entity:

- cannot publish a new artifact;
- may retain its last-known-approved artifact only when that artifact remains
  current and safe under an approved deployment policy; and
- cannot be silently repaired from a lower-authority source.

## Release Validation

Release validation determines whether the platform-wide package remains
coherent:

- exactly 100 current catalog members;
- unique permanent identities, numbers, slugs, and canonical routes;
- valid lifecycle combinations;
- category and relationship integrity;
- no critical public-truth conflict;
- no privacy, safety, or visibility failure; and
- deterministic package consistency.

The overall release fails when invalidity affects:

- identity;
- canonical routes;
- lifecycle;
- safety;
- privacy or visibility;
- category integrity;
- fixed-catalog integrity; or
- another cross-entity invariant.

Isolated non-critical optional-field failures may be omitted only under an
explicitly approved deployment policy. They must not become silent warnings or
permit a stale optional claim to be republished as new output.

Whole-build versus entity-isolation mechanics remain an implementation design,
but they must implement this validity boundary without weakening it.

---

# Validation Contract

## Structural

- exact contract version;
- required objects and fields;
- types, enums, lengths, and list bounds;
- no unknown fields in strict inputs;
- unique app ID, number, slug, canonical URL, and overview route;
- exactly 100 current catalog members;
- referenced categories/apps exist; and
- canonical routes remain internal, public, and valid.

## Provenance

- every public field/item has one authoritative record;
- authority matches the field ownership matrix;
- source path and section/key are allowlisted;
- source revision resolves;
- approval and review metadata exists;
- derived fields name a permitted deterministic rule; and
- governance-only provenance is omitted from public projections.

## Truth And Lifecycle

- current capabilities exist in current implementation truth;
- overview wording does not exceed story-verified capability;
- limitations are present;
- safety notes are present when conditionally required;
- future language does not enter current fields;
- live/version/status combinations are valid; and
- unavailable apps do not claim usable current workflows.

## Visibility And Privacy

- public allowlist only;
- no authenticated, internal, restricted, or personal content;
- no raw source document or arbitrary metadata;
- secret and infrastructure-pattern scanning;
- no internal path leakage in public projection; and
- no competitor-copy or keyword-stuffing patterns.

## Freshness And Conflict

- required fields are within review window;
- event-triggered reviews are complete;
- stale optional fields are omitted;
- no unresolved conflict exists;
- list items are deduplicated after normalization; and
- conflict reports contain no prohibited content.

## Representative Fixtures

Future implementation tests must include:

- Quiz: backend-backed learning app;
- Course Tracker: owner-scoped workflow app;
- JSON Formatter: browser-local utility;
- Research Assistant: name suggests AI but current capability is manual;
- Corporate Tax UAE: professional/regulatory boundary;
- First Aid Guide: safety-sensitive boundary;
- one content-generation app with explicit AI limitations; and
- one retired/replacement fixture that never alters the fixed total.

Fixtures are synthetic or public metadata only. No user records are used.

---

# Pass / Fail Criteria

Entity pass requires:

- all required fields valid;
- exactly one authoritative provenance record per public claim;
- no unresolved conflict;
- lifecycle/current/future consistency;
- freshness within policy;
- visibility and prohibited-field checks passing;
- relationships resolving to approved entities; and
- deterministic rebuild equality.

Release pass additionally requires:

- exactly 100 coherent current entities;
- unique platform-wide identities and routes;
- valid categories and cross-entity references;
- no critical identity/lifecycle/safety/privacy/fixed-catalog failure; and
- every invalid optional field handled only by an approved isolation policy.

Any entity failure blocks that entity from a new artifact. Any critical
cross-entity or public-trust failure blocks the release.

---

# Non-Goals

SEO-002 does not:

- modify or version the runtime registry schema;
- implement compiler parsing or validation;
- implement rendering or resolve SEO-003;
- define final schema.org types for SEO-004;
- change metadata, JSON-LD, sitemap, robots, routes, or frontend pages;
- parse `marketing.md`;
- publish market research or future direction;
- submit to crawlers or webmaster tools;
- create runtime APIs or migrations; or
- authorize production changes.

---

# Architecture Review Decisions

The Architecture Reviewer resolved the Contract V1 questions:

1. Core content fields, including limitations, remain mandatory.
2. `story.md` owns current capabilities, limitations, and safety.
3. Missing limitations block publication.
4. Initial freshness windows are 90/180/365 days by field family, with
   immediate event-triggered review.
5. Publishable claim lists require item-level provenance.
6. Related-app types remain bounded; popularity, profiling, and model-generated
   similarity are prohibited authorities.
7. Retired identities are permanent and replacements receive new identities.
8. `marketing.md` has no automatic Contract V1 compiler participation.
9. Entity and release validity follow the criticality policy above.
10. Governance details remain absent from public output except separately
    approved roles, review dates, or other non-sensitive freshness indicators.

Architecture Reviewer and Product Owner approval freeze Contract V1 and
SEO-002. Approval does not authorize implementation or production.
