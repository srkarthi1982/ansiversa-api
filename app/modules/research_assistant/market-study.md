# Research Assistant Market Study

## Document Status

**Status:** Living Document

**Market Version:** 1

**Created:** 2026-07-05

**Last Reviewed:** 2026-07-05

**Next Review:** During the next scheduled product improvement cycle or whenever significant market changes occur.

**Purpose**

This document captures external market intelligence for this solution.

It is intended to help Product discussions and future planning.

This document does **not** define product requirements or implementation commitments.

All product decisions require Partner approval and are reflected separately in `destination.md`.

## Purpose

This document captures market intelligence for Research Assistant so future
product decisions can be grounded in public competitor patterns, research
workflow pain points, AI reliability concerns, and Ansiversa's platform
direction.

This is research only. It does not copy competitor wording, UI, ranking
methods, summaries, or proprietary flows, and it does not recommend immediate
implementation.

## Problem Statement

Researchers, students, analysts, and professionals face information overload.
They need to find credible sources, understand what those sources say, extract
useful claims, preserve citations, and decide what to read next. Search alone
is no longer enough; users want synthesis, evidence trails, and structured
notes without losing trust.

The central market tension is speed versus reliability. AI can accelerate
literature discovery and summarization, but weak sourcing, hallucinated claims,
and opaque ranking can damage trust.

## Target Users

- Students starting essays, projects, or literature reviews.
- Graduate students and researchers scanning academic papers.
- Professionals doing market, policy, product, or technical research.
- Writers collecting sources and citation notes.
- Founders and product teams studying competitors.
- Clinicians, scientists, and analysts needing evidence summaries.
- Users who need a lightweight research workspace without a full reference
  manager or institutional database.

## Competitor Landscape

### Direct Competitors

- Elicit: AI research assistant focused on scientific literature search,
  summaries, data extraction, reports, and paper chat across a large paper
  corpus.
- Consensus: AI academic search engine that synthesizes peer-reviewed
  literature and presents evidence-oriented answers.
- Semantic Scholar: Free AI-powered scholarly search and discovery tool from
  Ai2, with paper discovery, semantic ranking, reading lists, and research APIs.
- Perplexity: General AI answer engine with citations, web search, Pro search,
  spaces, and enterprise plans for research workflows.
- SciSpace, Paperguide, ResearchRabbit, Connected Papers, and Litmaps:
  literature discovery and paper-network tools that help users explore research
  relationships.
- Zotero, Mendeley, and EndNote: Reference-management tools that own citation
  libraries and research organization rather than AI synthesis first.

### Indirect Competitors

- Google Scholar and library databases for source discovery.
- General web search for broader non-academic research.
- Notes apps such as Notion, Obsidian, OneNote, and Google Docs used as manual
  research notebooks.
- PDF readers and annotation tools used for paper-level notes.
- Search APIs and institutional discovery services used by universities.

### AI-Based Alternatives

- ChatGPT, Claude, Gemini, and Perplexity can summarize sources, compare
  claims, draft outlines, and create research plans. Their flexibility is high,
  but users must manage source quality and citation verification.
- Deep research-style agents compete by producing reports, but users still need
  transparency about what was searched, what was skipped, and where claims came
  from.

## Common Market Features

- Natural-language research questions.
- Search across academic papers, web pages, or uploaded documents.
- Source cards with titles, authors, dates, abstracts, and citations.
- AI summaries and key finding extraction.
- Evidence tables and structured extraction columns.
- PDF import, full-text chat, and paper Q&A.
- Citation export or reference-manager integration.
- Reading lists, collections, folders, and saved searches.
- Related-paper discovery and citation graph exploration.
- Report generation from selected sources.
- Quality signals such as citation counts, publication type, recency, and
  systematic review flags.
- Collaboration for teams or institutions.

## What Users Appear to Love

- Saving time during early literature discovery.
- Getting a quick map of what research exists.
- Seeing citations attached to generated summaries.
- Extracting structured details from many papers.
- Chatting with a paper instead of manually scanning every section.
- Free or low-cost discovery tools such as Semantic Scholar.
- Perplexity-style cited answers for broad research questions.
- Ability to organize saved sources into collections.
- Research workflows that reduce tab chaos.

## Common Complaints / Friction

- AI summaries can be incomplete, overconfident, or wrong.
- Source coverage may be unclear or biased toward accessible papers.
- Paywalls limit full-text access even when a search result is found.
- Citation formatting and export can be inconsistent.
- Users may confuse generated synthesis with peer-reviewed consensus.
- Academic tools can feel too complex for non-researchers.
- General AI tools may cite weak sources or fabricate references if not
  constrained.
- Credit-based pricing can feel unpredictable for heavy research sessions.
- Users need auditability: what was searched, why a source was selected, and
  what evidence supports a conclusion.

## Pricing and Paywall Observations

- Semantic Scholar is positioned as a free AI-powered research discovery tool.
- Elicit uses free and paid tiers, with deeper research-agent, report, and
  extraction workflows behind paid plans.
- Consensus offers a free layer with higher search/deep-search limits on paid
  plans.
- Perplexity has consumer, enterprise, and API pricing; enterprise plans are
  positioned around secure, cited research for teams.
- Literature review tools often monetize through AI credits, extraction limits,
  full-text processing, collaboration, or institutional access.

Research tools can justify payment when they save hours and preserve evidence,
but opaque credits and unclear source coverage create friction.

## AI Capability Trends

- AI search is moving from keyword results to answer synthesis with citations.
- Literature tools increasingly generate evidence tables and reports.
- Paper chat and full-text Q&A are becoming common.
- Deep research agents are raising user expectations for end-to-end reports.
- Trust features matter: citations, source previews, uncertainty, and audit
  trails.
- Institutions are interested in privacy, data handling, and provenance because
  research material can be sensitive or unpublished.

## UX Patterns Worth Studying

- Start with a research question, then show source-backed findings.
- Separate "search results" from "AI synthesis" so users understand the layer.
- Keep citations visible near every generated claim.
- Let users save sources into a project-specific collection.
- Support extraction tables where users choose fields.
- Show confidence and limitations rather than a single authoritative answer.
- Provide a research trail: query, filters, sources considered, and notes.
- Keep source detail and note-taking close together.
- Allow exporting citations and summaries without losing structure.

## Opportunities for Ansiversa

- Build a calm, source-first research workspace for everyday users, not only
  academic specialists.
- Treat research projects, sources, notes, and summaries as long-lived records.
- Make "evidence before answer" a product principle.
- Add AI only with visible citations, uncertainty, and user review.
- Connect with AI Notes Summarizer, Smart Textbook Scanner, Markdown Editor,
  Lesson Builder, and Proposal Writer through approved APIs.
- Preserve lightweight list responses and detailed source views.
- Support practical market/product research as well as academic research.
- Avoid opaque scoring; instead show evidence quality dimensions users can
  understand.

## What Ansiversa Should Avoid

- Do not copy competitor source cards, report templates, wording, or synthesis
  layouts.
- Do not present AI output as research truth without source review.
- Do not fabricate citations or hide weak source quality.
- Do not silently send private uploaded documents to AI providers.
- Do not become a full institutional research database without approval.
- Do not overload V1 with citation graph complexity before basic source
  organization is excellent.
- Do not make generated reports irreversible; users should edit and verify.

## Product Questions for Future Review

- Should Research Assistant focus first on academic sources, web sources, or
  general project research?
- Should AI synthesis be allowed only from saved user-selected sources?
- What citation/export formats matter most for Ansiversa users?
- Should source quality be represented through explicit labels or a checklist?
- How should Research Assistant integrate with AI Notes Summarizer?
- Should uploaded PDFs be supported, and under what privacy rules?
- What audit trail is required before calling a feature "research assistant"?

## Sources

- Elicit official site: https://elicit.com/
- Elicit education page: https://elicit.com/industries/edu
- Elicit pricing review signal: https://manusights.com/blog/is-elicit-worth-it
- Consensus research search: https://consensus.app/search/
- Consensus GPT announcement: https://consensus.app/home/blog/introducing-researchgpt-by-consensus/
- Bentley University overview of Consensus: https://www.bentley.edu/library/in-the-know/what-is-consensus-ai
- Consensus review/pricing signal: https://effortlessacademic.com/consensus-ai-review-for-literature-reviews/
- Semantic Scholar official site: https://www.semanticscholar.org/
- Semantic Scholar product page: https://www.semanticscholar.org/product
- Semantic Scholar FAQ: https://www.semanticscholar.org/faq
- Perplexity Pro: https://www.perplexity.ai/pro
- Perplexity Enterprise pricing: https://www.perplexity.ai/enterprise/pricing
- University of Arizona AI research guide for Elicit: https://libguides.library.arizona.edu/ai-researchers/elicit
- NIH / PMC article on Semantic Scholar: https://pmc.ncbi.nlm.nih.gov/articles/PMC5764585/
- Elicit literature-search comparison study: https://pmc.ncbi.nlm.nih.gov/articles/PMC12483133/
- Researcher community discussion on Consensus: https://www.reddit.com/r/GradSchool/comments/125ho7u/whats_your_favourite_new_ai_tool_mine_is_consensus/

## Review Notes

- AI research tooling is changing quickly. Re-check source coverage, pricing,
  and data-handling terms before product planning.
- Academic search quality should be validated with real user workflows, not
  only vendor claims.
- Reddit and review posts are useful for friction signals but are not controlled
  research.
- This study should inform future Research Assistant planning only after Partner
  and Astra review.

## Revision History

| Date | Summary |
|------|---------|
| 2026-07-05 | Initial market study created. |
