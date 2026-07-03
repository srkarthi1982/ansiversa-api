# Research Assistant Destination

## App Name

Research Assistant

## Destination Status

Approved v1.0

## Final Product Vision

Research Assistant should mature into a focused research organization
workspace that helps users define research topics, collect notes, preserve
references, review evidence, and move a topic from collection to completion.

The product should support disciplined thinking without becoming a web crawler,
source scraper, citation authority, academic writing service, or automated
research report generator.

At its destination, Research Assistant should help users keep a research
question, findings, sources, and status connected so the user can verify,
review, and reuse their own research context with confidence.

## Target Users

- Students organizing assignment, paper, or project research.
- Self-learners collecting sources and notes around a topic.
- Professionals preparing decisions, briefs, planning notes, or comparisons.
- Writers who need source context before drafting.
- Knowledge workers who need a simple research trail inside Ansiversa.

## Core User Problems

- Research notes and references are often scattered across bookmarks, files,
  documents, and memory.
- Users lose the connection between a finding and the source that supported it.
- Research can feel complete before evidence has been reviewed.
- Users need a lightweight status lifecycle without a full project management
  system.
- AI-assisted research can become risky if it hides sources or fabricates
  evidence.

## Final Capabilities

- Create owner-scoped research topics with title, question, summary, and
  status.
- Add ordered notes under each topic.
- Add references with source title, link, and contextual notes.
- Edit and delete topics, notes, and references.
- Track status across collecting, reviewing, and complete states.
- Load topic lists as summaries and topic details only when needed.
- Preserve the link between findings, references, and the guiding question.
- Support review views that distinguish notes, sources, and conclusions.
- Export or hand off reviewed research material to writing and summarization
  apps.
- Keep research material private and user-owned by default.

## Advanced Capabilities

- Citation formatting for user-provided references.
- Source import from explicit URLs, PDFs, or browser handoffs.
- Evidence quality indicators and missing-source warnings.
- AI synthesis drafts that always cite the source notes used.
- Topic comparison across saved research records.
- Research job tracking for governed long-running tasks.
- Export to markdown, PDF, or writing modules.
- Connection to AI Notes Summarizer and Proposal Writer for reviewed material.

## AI Opportunities

AI can help summarize, organize, and synthesize user-provided research, but it
must remain grounded in visible notes and references.

Potential AI support includes:

- Grouping notes into themes.
- Suggesting missing questions or weak evidence areas.
- Summarizing a topic from selected notes and references.
- Producing evidence-linked outlines for writing handoff.
- Checking whether claims have an attached reference.
- Explaining conflicting notes without hiding the original material.

AI must not crawl the web silently, invent references, fabricate evidence,
produce uncited claims as truth, or write final academic work on the user's
behalf without review.

## Ecosystem Connections

- AI Notes Summarizer can summarize reviewed research notes.
- Grammar and Paraphrasing Assistant can improve user-authored research text.
- Proposal Writer can receive reviewed business research context.
- Lesson Builder can use reviewed research as lesson preparation material.
- Book Summary Generator and Browser PDF Reader can provide explicit source
  handoffs when permitted.
- Concept Explainer can receive concepts discovered during research.

Research Assistant owns topic organization, notes, references, and status. It
should not absorb long-form writing, citation management, PDF reading,
summarization, or lesson authoring.

## Weekly Return Value

Users return while a topic is active to add findings, save references, review
evidence, update status, and prepare handoffs to writing or learning tools.

The weekly value is continuity: the user can resume research without losing the
question, source trail, or current status.

## Success Criteria

- Users can create, update, review, and complete research topics in one focused
  workflow.
- Notes and references remain connected to the selected topic.
- Topic lists stay lightweight while detail pages preserve full context.
- Status transitions help the user understand research maturity without
  pretending to validate truth.
- Any AI support remains source-grounded, explainable, and optional.
- Ecosystem handoffs preserve source context and user review.
- The product remains useful as a manual research workspace even without AI.

## Journey Progress

Current Position: 64 / 100
Destination: 100 / 100
Remaining Journey: 36 / 100

This estimate describes product maturity, not feature completion.

Research Assistant already has a live topic, note, reference, and status
workflow. The remaining journey is about evidence review, citation support,
source import, AI synthesis governance, and higher-quality ecosystem handoffs.

## Future Version Ideas

- V1.1: Add stronger research review and evidence coverage signals.
- V1.2: Add citation formatting for user-provided references.
- V1.3: Add export and handoff into writing and notes apps.
- V1.4: Add explicit source import with privacy and copyright controls.
- V2: Add governed AI synthesis grounded only in selected notes and references.

## Non Goals

- Do not become a web crawler.
- Do not become a source scraper.
- Do not become a citation authority or academic compliance tool.
- Do not become a full document editor.
- Do not become a ghostwriting or academic cheating tool.
- Do not generate uncited claims as truth.
- Do not replace AI Notes Summarizer, Browser PDF Reader, Lesson Builder, or
  writing apps.
- Do not ingest external sources without explicit user action.
- Do not treat AI synthesis as verified research.

## Guiding Principles

- Preserve the relationship between question, note, source, and conclusion.
- Treat references as user-provided evidence, not automatic truth.
- Keep research private and owner-scoped by default.
- Make AI source-grounded, reviewable, and optional.
- Support user judgment rather than replacing it.
- Prefer clear research continuity over broad automation.
- Let adjacent apps handle writing, summarization, PDF reading, and teaching.

## Governance Notes

This document is aspirational and does not authorize immediate implementation.
Future work must be reviewed by Product Owner and Astra before development.

Any feature involving AI synthesis, web import, browser capture, citation
formatting, PDF ingestion, external source retrieval, or automated research
jobs requires explicit governance review before implementation.

## Last Governance Review

Product Owner: Approved on 2026-07-03 for live-app Destination Framework rollout.
Astra: Approved on 2026-07-03. Journey Progress 64 / 100 accepted.
Codex: Drafted destination v1.0 from current backend story, frontend story, and overview metadata.

Status: Approved
