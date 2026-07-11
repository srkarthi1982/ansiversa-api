# Language Learning Buddy Destination

## Purpose

Language Learning Buddy should mature into Ansiversa's practical personal language-practice log: a place to build vocabulary, record practice attempts, and review progress without requiring external AI, social feeds, browser storage, or separate language-learning accounts.

## Destination Status

Approved v1.0

## Final Product Vision

Language Learning Buddy should become Ansiversa's personal vocabulary and practice record: a lightweight workspace where users choose the words they care about, record short practice attempts, and review progress without requiring a full course platform, public leaderboard, speech engine, or AI tutor.

## Journey Progress

Current Position: 35 / 100
Destination: 100 / 100
Remaining Journey: 65 / 100

This estimate describes product maturity, not feature completion. V1 has owner-scoped vocabulary and practice persistence, protected frontend routes, and clean API boundaries. The remaining journey includes spaced repetition, richer review views, import/export, optional reminders, and carefully governed AI or pronunciation support only if approved later.

## Mature Product Direction

The mature product should help users maintain a trustworthy record of language learning effort. It should stay manual, transparent, and lightweight unless Partner/Astra approve a more advanced learning engine.

## Target Users

- Self-directed learners building vocabulary for travel, work, school, family, or personal interest.
- Users who want to track their own words rather than follow a full course.
- Learners who prefer short practice sessions and factual progress over social feeds.
- Ansiversa users who want language practice near Study Planner, Goal Tracker, Daily Word Challenge, and Dictionary+.

## Core User Problems

- Personal vocabulary often lives in notebooks, chats, screenshots, translation apps, and memory.
- Full lesson apps can feel rigid when users only need to practice their own words.
- AI tutors and speech tools may be too expensive, private, or overbuilt for simple tracking.
- Gamification can distract from retention when progress records are weak.
- Users need durable vocabulary and practice history without becoming an LMS.

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

## Weekly Return Value

Users return weekly to add words they encountered, run short practice sessions, review confidence and difficulty, and see whether language practice is continuing.

## Success Criteria

- Vocabulary capture is faster than maintaining a spreadsheet.
- Practice history shows effort without claiming fluency.
- Progress remains factual: counts, confidence, difficulty, and recent sessions.
- The app stays useful without generated lessons, speech scoring, or AI roleplay.
- Future spaced repetition or AI practice remains user-controlled and governed.

## Current V1 Position

V1 is approved live with Vocabulary, Practice, and Progress routes, owner-scoped persistence, generated API types, and an isolated production migration. It does not include external AI, generated lessons, speech recognition, pronunciation scoring, spaced repetition, imports, exports, reminders, collaboration, or cross-app automation.

## Future Enhancements

- Spaced repetition scheduling.
- Import/export for vocabulary lists.
- Optional reminder workflow after governance review.
- Richer progress charts by language and category.
- Approved cross-app summaries with Study Planner or Goal Tracker.
- Governed AI practice prompts only after safety, privacy, and trust review.

## Non Goals

- Do not claim fluency outcomes or guaranteed retention.
- Do not copy competitor lessons, exercises, prompts, or scoring models.
- Do not add public leaderboards or social competition by default.
- Do not turn the module into a classroom LMS.
- Do not send vocabulary or practice notes to AI by default.

## Guiding Principles

- The user chooses the vocabulary worth learning.
- Practice should be short, clear, and low-friction.
- Progress should be visible without pressure-heavy gamification.
- Advanced learning engines must be optional, transparent, and approved.

## Governance Notes

Astra: Approved on 2026-07-10.

Partner: Approved Language Learning Buddy live promotion after manual workflow verification.

Codex: Ran production-configured isolated database migration, verified schema/indexes, synced destination metadata, and prepared live promotion metadata.
