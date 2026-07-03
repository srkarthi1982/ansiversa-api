# Smart Textbook Scanner Destination

## App Name

Smart Textbook Scanner

## Destination Status

Approved v1.0

## Final Product Vision

Smart Textbook Scanner should mature into a focused textbook-to-study-material
workspace that helps learners capture source pages, organize page text, extract
review notes, and understand study material more efficiently.

The product should support learning from user-provided material without
becoming a textbook library, piracy tool, OCR platform, file vault, homework
answer machine, or replacement for the original source.

At its destination, the app should help users move from source material to
reviewable notes while preserving source context, user accountability, and
respect for copyrighted learning content.

## Target Users

- Students working through textbook chapters.
- Self-learners extracting review notes from structured study material.
- Educators preparing focused references from provided teaching material.
- Professionals studying certification or technical manuals.
- Learners who want page-level notes connected to original source context.

## Core User Problems

- Textbook study often produces scattered notes without page context.
- Users need a structured way to move from pages to extracted review material.
- Manual study notes can lose the connection between source text and summary.
- Learners need review progress signals across multiple scans and pages.
- AI or OCR assistance can become risky if it hides errors or encourages
  unauthorized content ingestion.

## Final Capabilities

- Create owner-scoped textbook scan projects with subject, source, and goal.
- Organize pages under a scan with page numbers, status, and source text.
- Load full page text only when the workflow needs it.
- Create extracted notes tied to both scan and page.
- Preserve headings, key points, summaries, and note type metadata.
- Review extraction rate, active scans, reviewed scans, page counts, and recent
  notes.
- Maintain clear status for each page and scan.
- Support source-aware exports into study workflows.
- Keep user-provided source material private by default.
- Require review before extracted notes are reused elsewhere.

## Advanced Capabilities

- OCR-assisted text capture from user-uploaded images or PDFs.
- AI-assisted extraction with source-linked summaries and citations.
- Concept linking into Concept Explainer.
- Note handoff into AI Notes Summarizer or Study Planner.
- Export of reviewed notes into markdown, PDF, or flashcard-ready formats.
- Page-level confidence indicators for OCR or AI extraction.
- Duplicate detection for repeated page captures.
- Study progress analytics across subjects and scans.

## AI Opportunities

AI may eventually help extract, summarize, and organize study material, but it
must remain source-grounded and reviewable.

Potential AI support includes:

- Extracting key points from user-provided page text.
- Suggesting headings and study questions from a page.
- Explaining difficult passages while linking back to the source page.
- Detecting unclear or incomplete page text before extraction.
- Grouping extracted notes into concepts for later study.
- Producing confidence or review warnings when source text is insufficient.

AI must not ingest copyrighted books by default, claim perfect accuracy, bypass
user review, generate homework answers as truth, or create summaries detached
from user-provided source material.

## Ecosystem Connections

- Concept Explainer may receive selected concepts for deeper explanation.
- AI Notes Summarizer may summarize reviewed extracted notes.
- Study Planner may receive study tasks based on reviewed pages or concepts.
- Course Tracker may link scans to a course module.
- Memory Trainer may receive reviewed facts or prompts after user approval.
- Browser PDF Reader may provide explicit source text handoff if governance
  permits.

These connections should preserve source context and require user action.
Smart Textbook Scanner owns page-to-note extraction, not full learning
management or content libraries.

## Weekly Return Value

Users return as they work through chapters, add new pages, extract notes,
review recent material, and prepare study sessions from source-linked notes.

The weekly value comes from making textbook progress visible and reviewable
without separating notes from their source material.

## Success Criteria

- Users can create scans, organize pages, extract notes, and review progress in
  one focused workflow.
- Extracted notes remain connected to source pages.
- Long page text is loaded intentionally rather than bloating every list view.
- AI and OCR assistance, if added, remain explicit, source-grounded, and
  reviewable.
- The product respects user-provided material and avoids encouraging
  copyrighted content misuse.
- Ecosystem handoffs support learning without turning the app into an LMS,
  library, or answer engine.

## Journey Progress

Current Position: 59 / 100
Destination: 100 / 100
Remaining Journey: 41 / 100

This estimate describes product maturity, not feature completion.

Smart Textbook Scanner has a live scan, page, extracted-note, and review
workflow. Its remaining maturity journey is longer because the highest-value
future work involves OCR, AI extraction, source fidelity, copyright boundaries,
and learning handoffs that must be governed carefully.

## Future Version Ideas

- V1.1: Add improved page review and extraction status controls.
- V1.2: Add export of reviewed extracted notes.
- V1.3: Add Concept Explainer and Study Planner handoffs.
- V1.4: Add OCR import with explicit source and privacy controls.
- V2: Add governed AI extraction with source-linked explanations and review
  confidence.

## Non Goals

- Do not become a textbook piracy tool.
- Do not become a full-text textbook library.
- Do not become a document vault or file storage platform.
- Do not become a generic OCR infrastructure product.
- Do not become a homework answer generator.
- Do not replace Course Tracker, Study Planner, Concept Explainer, or AI Notes
  Summarizer.
- Do not ingest complete copyrighted books by default.
- Do not treat AI-extracted notes as authoritative without review.
- Do not hide source material or page context behind generated summaries.

## Guiding Principles

- Preserve source context from page to note.
- Treat extracted notes as study aids, not authoritative replacements.
- Keep user-provided material private by default.
- Require explicit user action for uploads, extraction, export, and handoff.
- Respect copyright and learning integrity.
- Make AI assistance source-grounded, transparent, and reviewable.
- Improve comprehension rather than compressing content blindly.

## Governance Notes

This document is aspirational and does not authorize immediate implementation.
Future work must be reviewed by Product Owner and Astra before development.

Any feature involving OCR, file upload, image storage, copyrighted content
handling, AI extraction, external content ingestion, or answer-generation
behavior requires explicit governance review before implementation.

## Last Governance Review

Product Owner: Approved on 2026-07-03 for live-app Destination Framework rollout.
Astra: Approved on 2026-07-03. Journey Progress 59 / 100 accepted.
Codex: Drafted destination v1.0 from current backend story, frontend story, and overview metadata.

Status: Approved
