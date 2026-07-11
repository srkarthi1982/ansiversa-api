# Daily Word Challenge Destination

## App Name

Daily Word Challenge

## Destination Status

Approved v1.0

## Final Product Vision

Daily Word Challenge should mature into a lightweight daily vocabulary routine
that helps users discover one focused word each day, explore a curated
vocabulary collection, mark words learned, and build consistent browser-local
progress.

The product should support daily vocabulary growth without becoming a full
dictionary, language course, quiz platform, social streak network, or
server-first learning tracker.

At its destination, Daily Word Challenge should remain simple: one daily word,
clear meaning and usage, local progress, and optional handoffs into deeper
vocabulary tools when the user chooses.

## Target Users

- Students building vocabulary through small daily practice.
- Writers exploring expressive words.
- Curious learners who want a short daily learning routine.
- Language learners who want lightweight exposure to new words.
- Casual puzzle players who enjoy a quick word ritual without competitive pressure.
- Teachers or coaches who may use daily vocabulary as a warm-up after content governance.
- Users who prefer local progress without account-backed tracking by default.

## Core User Problems

- Vocabulary learning is easier to sustain when the daily task is small.
- Users often forget words unless they can mark and revisit learned vocabulary.
- A daily challenge should not require an account, server scheduler, or social
  streak system.
- Daily word apps can drift into full dictionaries, quizzes, or gamified
  ranking platforms.
- Progress and streaks should motivate consistency without becoming pressure or
  surveillance.
- Daily challenge content must feel fair, original, and useful rather than obscure or clone-like.
- Generated vocabulary practice needs validation before it can be trusted as a daily ritual.

## Final Capabilities

- Select a deterministic word of the day from a curated vocabulary set.
- Show word, pronunciation, meaning, part of speech, difficulty, and example.
- Filter vocabulary by search text, difficulty, and learned status.
- Mark and unmark words as learned for the current date.
- Track local streaks using browser storage.
- Validate local progress before loading it.
- Reset current-day progress when needed.
- Preserve progress locally by default without backend runtime APIs.
- Integrate with Dictionary+ for deeper saved-word workflows.
- Support optional account-backed progress only after governance review.

## Advanced Capabilities

- Larger curated vocabulary sets.
- Difficulty progression based on local history.
- Dictionary+ saved-word handoff.
- Memory Trainer practice handoff for learned words.
- Optional reminders with explicit user control.
- Archive or practice mode separated from the daily challenge.
- Shareable completion summaries that do not reveal answers, only after product review.
- Account-backed streak sync with clear privacy rules.
- Review modes for previously learned words.
- Import of user-selected vocabulary lists.

## AI Opportunities

AI should be limited and reviewable because vocabulary content and learning
signals need accuracy and clear sourcing.

Potential AI support includes:

- Suggesting example sentences for reviewed words.
- Creating short non-authoritative memory prompts.
- Grouping words by theme or difficulty.
- Recommending review words from user-approved local progress.
- Explaining similar words when paired with Dictionary+ context.

AI must not invent authoritative definitions, replace licensed dictionary
sources, personalize learning by hidden profiling, or turn local progress into
server-side tracking without explicit consent.

## Ecosystem Connections

- Dictionary+ can store selected words for personal vocabulary lists.
- Memory Trainer can receive selected words for recall practice.
- Study Planner can schedule optional vocabulary review tasks.
- Concept Explainer can receive unfamiliar concepts only when the user chooses.
- Quiz can remain the assessment workflow instead of Daily Word Challenge
  becoming a quiz product.

Daily Word Challenge owns the daily word routine and local learned-state
progress. It should not absorb dictionary publishing, vocabulary libraries,
memory games, study planning, or quizzes.

## Weekly Return Value

Users return daily or weekly to discover new words, mark learned words, review
the curated list, maintain a streak, and send useful vocabulary to deeper
learning tools.

The weekly value is consistency through small daily effort, not competition or
heavy study management.

## Success Criteria

- Users can complete the daily word workflow quickly without signing into a
  separate learning system.
- Local progress and streak behavior remain predictable and transparent.
- Vocabulary content remains clear and reviewable.
- Challenge words and hints remain fair for the intended learner level.
- Curated daily content stays distinct from generated practice.
- The product complements Dictionary+, Memory Trainer, and Quiz without
  becoming those products.
- Optional sync, reminders, or AI features are explicit and governed.
- Progress remains private and browser-local by default.

## Journey Progress

Current Position: 69 / 100
Destination: 100 / 100
Remaining Journey: 31 / 100

This estimate describes product maturity, not feature completion.

Daily Word Challenge already has a live browser-local daily word, filtering,
learned-state, reset, and streak workflow. The remaining journey is about
larger word sets, Dictionary+ integration, review modes, optional reminders,
and carefully governed progress sync.

## Future Version Ideas

- V1.1: Expand curated vocabulary sets.
- V1.2: Add Dictionary+ saved-word handoff.
- V1.3: Add review mode for learned words.
- V1.4: Add optional reminders.
- V2: Add account-backed progress sync after privacy and governance review.

## Non Goals

- Do not become a full dictionary.
- Do not become a language course.
- Do not become a quiz platform.
- Do not become a social streak or leaderboard product.
- Do not copy Wordle-style, Connections-style, Spelling Bee-style, or other proprietary puzzle formats.
- Do not become a server-first learning tracker by default.
- Do not replace Dictionary+, Memory Trainer, Study Planner, or Quiz.
- Do not use AI-generated definitions as authoritative entries.
- Do not sync local progress without explicit user approval.
- Do not turn streaks into pressure, ranking, or surveillance.

## Guiding Principles

- Keep the daily routine small and repeatable.
- Preserve browser-local progress by default.
- Treat streaks as gentle continuity, not competition.
- Keep vocabulary content clear, sourced, and reviewable.
- Preserve a small daily ritual before adding archives, sharing, or personalization.
- Use ecosystem handoffs for deeper learning instead of expanding scope.
- Make AI and account sync optional, transparent, and governed.
- Favor consistency over gamification.

## Governance Notes

This document is aspirational and does not authorize immediate implementation.
Future work must be reviewed by Product Owner and Astra before development.

Any feature involving account-backed progress, reminders, external word
providers, AI-generated vocabulary content, Dictionary+ integration, practice
handoffs, or social streak behavior requires explicit governance review before
implementation.

## Last Governance Review

Product Owner: Approved on 2026-07-03 for live-app Destination Framework rollout.
Astra: Approved on 2026-07-03. Journey Progress 69 / 100 accepted.
Codex: Drafted destination v1.0 from current backend story, frontend story, and overview metadata.

Status: Approved
