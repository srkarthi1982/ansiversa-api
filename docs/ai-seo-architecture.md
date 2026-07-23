# Ansiversa AI SEO Architecture

**Status:** Approved
**Created:** 2026-07-23
**Iteration:** Iteration 2 — AI SEO Architecture
**Scope:** Discovery and specification only
**Architecture Reviewer:** Astra — Approved 2026-07-23
**Product Owner:** Karthikeyan Ramalingam — Approved 2026-07-23

SEO-001 is complete, SEO-002 Contract V1 is Frozen, and SEO-003's Hybrid
Governed Pre-rendering architecture is Accepted and Frozen. These architecture
approvals do not authorize runtime implementation, crawler submission, metadata
changes, or production changes.

---

# Vision

Ansiversa should be understandable as one trusted platform, fourteen coherent
categories, and exactly one hundred focused solution apps by people, search
engines, answer engines, and future machine consumers.

AI SEO means governed public knowledge architecture:

```text
Approved product truth
    ↓
Canonical knowledge model
    ↓
Human-visible canonical pages
    ↓
Standard discovery and structured data
    ↓
Optional machine-readable projections
    ↓
Measured indexing, citations, and factual accuracy
```

It does not mean writing hidden content for bots, mass-generating pages,
guaranteeing rankings, or publishing internal product memory.

---

# Current Foundation

AI SEO is not greenfield. The repository already contains:

- a deterministic Canonical AI Knowledge Registry;
- exactly 100 public app records and 14 categories;
- visibility and current/future separation;
- source traceability and secret scanning;
- Assistant retrieval parity;
- public knowledge JSON and schema.org JSON-LD;
- `llms.txt` and `llms-full.txt`;
- an AI sitemap and robots hints;
- canonical-domain deployment rewrites;
- public artifact drift checks; and
- a read-only production smoke verifier.

These assets remain the foundation. Iteration 2 must extend them rather than
create a second AI SEO registry or publishing pipeline.

---

# Evidence-Based Gap

The canonical public website is currently a React SPA:

- `index.html` supplies one platform-wide description and Open Graph set;
- route changes update `document.title` in the browser;
- app routes do not emit route-specific canonical links in initial HTML;
- app routes do not emit route-specific metadata in initial HTML;
- route-specific JSON-LD is published as a separate graph, not embedded in the
  corresponding visible page; and
- the AI sitemap is useful as a generated inventory but does not replace a
  conventional canonical sitemap and crawlable linked HTML.

Some crawlers render JavaScript, but the architecture must not depend on every
search or answer engine executing the SPA correctly.

The next major architectural requirement is therefore:

> Every indexable public entity must have one canonical, crawlable,
> human-visible representation whose visible claims and structured metadata
> derive from the same approved knowledge record.

---

# Principles

## AI SEO Engineering Law #1

> Every public claim must have exactly one approved source of truth.

Every compiled claim must retain field-level provenance to its approved source.
When sources conflict, compilation must fail for review rather than select a
claim silently.

## AI SEO Engineering Law #2

> Every published artifact must be reproducible from one immutable approved
> revision.

Every public release must preserve enough immutable revision identity to
reproduce and explain its visible and machine-readable output. A mutable
“latest” source is not an approved release input.

## Truth Before Reach

Discoverability never permits claims beyond current approved product truth.

## One Knowledge Compiler

All generated public projections come from the Canonical AI Knowledge Registry.
Frontend and backend must not independently invent app facts.

## Human And Machine Parity

Structured data and machine exports must describe content visible on the
canonical page. Hidden machine-only claims are prohibited.

## Standards First

Canonical HTML, internal links, robots controls, ordinary sitemaps, HTTP
correctness, and valid structured data are the primary discovery layer.
Vendor-specific or emerging files are additive and evidence-rated.

## Public By Approval

Source availability does not imply publication. Only explicitly approved
public fields may enter public pages or artifacts.

## Generated Does Not Mean Unreviewed

Generation removes duplication. It does not remove human ownership, approval,
or validation.

## Discovery Is Not A Guarantee

Passing validation proves accessibility and consistency. It does not guarantee
crawling, indexing, ranking, citation, recommendation, or answer adoption.

---

# Knowledge Source Contract

The four-document lifecycle participates through explicit roles.

| Source | Role | Direct public source? | Allowed contribution |
|---|---|---:|---|
| `market-study.md` | Research evidence and vocabulary | No | Candidate user language, questions, and entity vocabulary after review |
| `destination.md` | Product direction | No | Approved identity and non-goals; future items remain excluded from current claims |
| `story.md` | Current implementation truth | No | Current capabilities, limitations, safety, and workflow after sanitization |
| `marketing.md` | Approved communication | Candidate, field-level only | Public descriptions, audience language, FAQs, campaigns, and media guidance after truth checks |
| overview metadata | Current public product presentation | Yes, governed input | Name, description, workflow, capabilities, audiences, routes |
| catalog/route registries | Canonical identity | Yes, governed input | Stable IDs, names, slugs, status, categories, canonical routes |

The registry compiler—not the public publisher—owns parsing, precedence,
visibility, conflict detection, and provenance.

Recommended precedence:

```text
Canonical identity and lifecycle
    catalog and route registries

Current capability truth
    approved overview + story

Approved public wording
    marketing, checked against current capability truth

Research vocabulary
    market study, manually promoted into approved public fields

Future direction
    destination, explicitly state=future and excluded from current publishing
```

Conflicts fail the build; the publisher must never silently choose the more
marketable claim.

---

# Responsibility Boundary

## Platform-Owned

- knowledge schema and compiler;
- source precedence, visibility, and provenance;
- canonical URL policy;
- public-page rendering contract;
- robots and crawler policy;
- sitemap and IndexNow policy;
- shared schema.org vocabulary;
- organization, website, catalog, category, and relationship graph;
- artifact generation;
- drift, privacy, and claim validation;
- webmaster-tool evidence and AI-answer monitoring; and
- deprecation and correction procedures.

## App-Owned

- app purpose and user problem;
- approved audiences and use cases;
- current capabilities and limitations;
- app safety and professional-boundary statements;
- app-specific FAQs;
- app relationships proposed for review;
- truthful marketing language; and
- freshness review when app behavior changes.

Apps provide governed facts. They do not choose crawler behavior, canonical
domains, schema versions, or publishing infrastructure.

---

# Target Architecture

## Layer 1 — Authored Product Memory

The four lifecycle documents, catalog identity, route registry, and overview
metadata remain maintained by accountable owners.

## Layer 2 — Canonical Knowledge Registry

Extend the existing registry only through a versioned contract. Candidate
public entity fields include:

- stable entity ID and type;
- name, short name, aliases, and disambiguators;
- canonical URL;
- category and parent platform;
- concise purpose;
- user problems and approved audiences;
- current capabilities and workflow;
- limitations, safety boundary, and availability;
- related entities with typed relationship reasons;
- approved FAQs;
- freshness/review metadata;
- visibility and lifecycle state;
- source references and content revisions; and
- schema/compiler version.

No user data, internal paths, credentials, unpublished roadmap claims,
competitor text, or arbitrary Markdown is permitted.

## Layer 3 — Canonical Public Representations

Every indexable entity requires:

- an HTTP 200 canonical URL;
- meaningful initial HTML without requiring client execution;
- unique title and description;
- one canonical link;
- visible H1 and concise current-purpose text;
- crawlable internal links;
- route-specific Open Graph/social metadata where appropriate;
- JSON-LD matching visible facts;
- correct not-found and redirect behavior; and
- no authenticated or personal content in the indexable representation.

The rendering mechanism—pre-rendering, SSR, static generation, or another
bounded approach—requires a separate architecture decision. Iteration 2 does
not preselect it.

## Layer 4 — Discovery Controls

- one conventional root sitemap for canonical indexable pages;
- optional sitemap segmentation for platform, categories, apps, and later
  approved editorial/media content;
- accurate `lastmod` derived from approved content revisions;
- robots policy by crawler purpose;
- canonical-domain redirects and duplicate control;
- Google Search Console and Bing Webmaster Tools governance;
- optional IndexNow notification for approved changed canonical URLs; and
- crawler/WAF verification using official user-agent and IP guidance where
  available.

Training crawlers, search crawlers, and user-triggered fetchers are separate
policy decisions. Allowing search discovery must not silently authorize model
training.

## Layer 5 — Machine Projections

Continue generating:

- public knowledge JSON;
- schema.org JSON-LD;
- public metadata JSON;
- `llms.txt`;
- `llms-full.txt`; and
- diagnostic inventory artifacts.

These are projections, not independent truth stores. `llms.txt` remains an
emerging convention and must not be presented as a universal indexing
standard.

## Layer 6 — Evidence And Operations

Measure separately:

- accessibility and HTTP correctness;
- canonical/indexing coverage;
- structured-data validity;
- freshness and registry drift;
- crawler access and errors;
- search impressions/clicks;
- AI citations/referrals where vendors expose them;
- factual-answer accuracy;
- stale or unsupported claims; and
- correction latency.

No metric should require scraping search-result pages contrary to provider
terms.

---

# Vendor Discovery Policy

| Surface | Primary supported path | Architecture position |
|---|---|---|
| Google Search, AI Overviews, Gemini-grounded discovery | Crawlable HTML, Googlebot, canonical URLs, sitemaps, structured data, Search Console | Standards-first; no special AI markup claim |
| ChatGPT Search | Crawlable public pages and `OAI-SearchBot` access | Search crawling separated from `GPTBot` training policy |
| Microsoft Bing and Copilot | Bing index, sitemap, canonical content, optional IndexNow, Bing Webmaster Tools | Standards plus freshness notification |
| Perplexity | Crawlable public pages and `PerplexityBot`; user-triggered access separately governed | Follow official crawler/IP guidance |
| Claude | Public-web discoverability and vendor controls | Exact crawler/control contract must be verified before implementation |
| Future systems | Open-web standards and governed public exports | Add vendor rules only with primary evidence |

Crawler names and behavior are operationally volatile. They belong in a
versioned crawler-policy registry with review dates, not hard-coded assumptions
inside app modules.

---

# Generated Versus Authored

Manually authored and approved:

- research;
- product direction;
- implementation truth;
- public messaging;
- safety and non-goals;
- FAQ answers;
- relationship intent; and
- crawler/training policy.

Deterministically generated:

- normalized registry records;
- canonical metadata;
- page-head projections;
- JSON-LD;
- sitemap entries;
- machine exports;
- drift reports;
- source revision hashes; and
- validation evidence.

Measured, never authored as truth:

- ranking;
- indexing;
- citations;
- referral traffic;
- answer accuracy observations; and
- crawler behavior.

---

# Scope

Iteration 2 architecture includes:

- current-state discovery audit;
- per-app public knowledge contract;
- public entity and relationship model;
- canonical rendering decision;
- structured-data profile;
- crawler and usage-control policy;
- sitemap and freshness strategy;
- source-document integration;
- validation and observability design; and
- implementation roadmap.

# Non-Goals

- implementing SSR, pre-rendering, or static generation;
- modifying frontend metadata;
- changing registry code or schema;
- changing robots or sitemaps;
- submitting URLs to providers;
- adding IndexNow;
- marketing automation;
- content generation;
- advertising;
- video generation;
- vector search, embeddings, or RAG;
- new apps or App #101;
- publishing future plans as current; and
- guaranteeing AI recommendations or rankings.

---

# Architecture Decisions Still Required

Before implementation:

1. Choose the canonical public rendering strategy.
2. Freeze the per-app AI SEO contract and schema version.
3. Decide whether `marketing.md` becomes a compiler input or supplies a
   separately approved public projection.
4. Define standard sitemap versus diagnostic AI-sitemap ownership.
5. Approve crawler search/training/user-fetch policies.
6. Preserve the accepted SEO-004 structured-data profile and validation rules.
7. Define content freshness ownership and stale-content blocking.
8. Define IndexNow scope, secrets, retries, and evidence.
9. Define webmaster-tool roles and evidence retention.
10. Define measurable success criteria without ranking guarantees.

No implementation should begin from this proposal alone.
