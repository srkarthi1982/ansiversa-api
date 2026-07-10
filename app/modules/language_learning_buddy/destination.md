# Language Learning Buddy Destination

## Purpose

Language Learning Buddy should mature into Ansiversa's practical personal language-practice log: a place to build vocabulary, record practice attempts, and review progress without requiring external AI, social feeds, browser storage, or separate language-learning accounts.

## Destination Status

Approved v1.0

## Journey Progress

Current Position: 35 / 100
Destination: 100 / 100
Remaining Journey: 65 / 100

This estimate describes product maturity, not feature completion. V1 has owner-scoped vocabulary and practice persistence, protected frontend routes, and clean API boundaries. The remaining journey includes spaced repetition, richer review views, import/export, optional reminders, and carefully governed AI or pronunciation support only if approved later.

## Mature Product Direction

The mature product should help users maintain a trustworthy record of language learning effort. It should stay manual, transparent, and lightweight unless Partner/Astra approve a more advanced learning engine.

## Core Capabilities

- Create, edit, and delete vocabulary records.
- Group vocabulary by language, category, and difficulty.
- Record dated practice sessions with result, confidence, and notes.
- Review vocabulary totals, language coverage, mastered items, weekly practice, and recent sessions.
- Keep all records owner-scoped inside the dedicated module database.
- Keep list responses lightweight and detail responses complete.

## Trust Boundaries

Language Learning Buddy is not a full language course, translation engine, AI tutor, speech-recognition app, certification product, classroom LMS, or social learning network. Any future AI, pronunciation, or generated lesson capability must be opt-in, reviewed, and clearly separated from the current manual tracking workflow.

## Ecosystem Fit

Language Learning Buddy can later connect with Study Planner, Goal Tracker, Daily Word Challenge, Dictionary+, and Course Tracker through approved APIs. It must not directly own or mutate other apps' records.

## Current V1 Position

V1 is approved live with Vocabulary, Practice, and Progress routes, owner-scoped persistence, generated API types, and an isolated production migration. It does not include external AI, generated lessons, speech recognition, pronunciation scoring, spaced repetition, imports, exports, reminders, collaboration, or cross-app automation.

## Future Enhancements

- Spaced repetition scheduling.
- Import/export for vocabulary lists.
- Optional reminder workflow after governance review.
- Richer progress charts by language and category.
- Approved cross-app summaries with Study Planner or Goal Tracker.
- Governed AI practice prompts only after safety, privacy, and trust review.

## Governance Notes

Astra: Approved on 2026-07-10.

Partner: Approved Language Learning Buddy live promotion after manual workflow verification.

Codex: Ran production-configured isolated database migration, verified schema/indexes, synced destination metadata, and prepared live promotion metadata.
