# Language Learning Buddy Market Study

## Document Status

**Market Version:** 1

**Created:** 2026-07-10

**Last Reviewed:** 2026-07-10

**Next Review:** During the next scheduled product improvement cycle or whenever major language-learning app expectations change.

## Purpose

This document captures external market intelligence for Language Learning Buddy. It is research only and does not define product requirements or implementation commitments. Product decisions require Partner approval and are reflected separately in `destination.md`.

## Problem Statement

Language learners often collect words in notebooks, apps, flashcards, chats, screenshots, and memory. Many apps provide lessons or AI conversations, but users may still need a simple owner-scoped place to record the vocabulary they personally want to practice and track whether practice is happening.

## Target Users

- Self-directed learners building vocabulary for travel, work, school, family, or personal interest.
- Users who want manual records instead of an AI tutor or full course platform.
- Ansiversa users who want language practice near goals, study planning, and everyday productivity tools.

## Competitor Landscape

### Direct Alternatives

- Duolingo: Broad gamified language lessons with paid tiers and AI-enhanced features in Duolingo Max.
- Babbel: Structured paid language courses focused on practical conversation and subscription/lifetime pricing.
- Busuu: Lesson-based learning with community/native-speaker feedback and free-to-start positioning.
- Memrise: Scenario-based vocabulary and listening practice with native-speaker media and AI conversation features.

### Indirect Alternatives

- Spaced-repetition tools such as Anki-style flashcard systems.
- Notion, Google Sheets, notebooks, and generic habit trackers used as vocabulary logs.
- Dictionary and translation apps where users save words but do not always track practice history.

### AI-Based Alternatives

AI language-learning products increasingly offer roleplay, AI chat partners, generated practice, pronunciation/speaking support, and adaptive review. These can be valuable, but they raise higher trust, content-quality, and expectation risks. Ansiversa V1 should stay manual and factual.

## Common Market Features

- Lessons or guided learning paths.
- Vocabulary lists and review.
- Listening or speaking practice.
- Gamified streaks, XP, and reminders.
- Progress dashboards.
- Paid subscriptions for advanced features, ad-free experiences, or AI practice.

## User Love Signals

- Short daily sessions reduce friction.
- Visible progress and streaks encourage return visits.
- Native-speaker audio/video helps learners hear real usage.
- Practical phrases and categories help learners connect study to real needs.
- Simple review loops help users remember words over time.

## Complaints And Friction

- Lesson apps can feel rigid when users want to track their own vocabulary.
- AI features can feel expensive or overbuilt for simple practice tracking.
- Gamification can distract from actual retention.
- Some users want clearer ownership of personal notes, categories, and practice history.
- Speech and AI tools may create privacy, accuracy, or trust concerns.

## Pricing And Paywall Observations

Language-learning apps commonly use freemium models, subscriptions, annual discounts, family plans, or lifetime offers. Advanced review, ad-free use, full course access, and AI conversation features are often paid. Ansiversa can keep V1 aligned with platform value by focusing on manual vocabulary and practice records without creating a separate language-learning paywall.

## AI Trends

Duolingo Max includes AI-powered roleplay and video-call style practice. Memrise promotes AI Buddies and scenario-based conversation. Market direction is clearly moving toward AI conversation, but V1 should avoid external AI until Partner/Astra approve scope, safety, privacy, and positioning.

## UX Patterns Worth Studying

- First action starts a practice flow, not a settings-heavy setup.
- Progress is visible in compact summaries.
- Vocabulary is grouped by practical context.
- Review actions remain close to the word being practiced.
- Empty states guide users toward the first vocabulary record.

## Ansiversa Opportunities

- Position as a calm personal vocabulary and practice log, not a full course.
- Keep records owner-scoped in a dedicated database.
- Make the first workflow route Vocabulary so users control what they learn.
- Keep Progress factual: counts, recent sessions, confidence, and difficulty.
- Later integrate with Study Planner or Goal Tracker through approved APIs.

## Avoid List

- Do not copy competitor lessons, prompts, exercises, scoring models, or wording.
- Do not claim fluency outcomes or guaranteed retention.
- Do not add external AI, generated lessons, speech scoring, or browser storage in V1.
- Do not make social sharing or public leaderboards part of the default workflow.
- Do not turn the module into a full LMS.

## Product Questions

- Should V2 add spaced repetition scheduling?
- Which import/export formats are acceptable for user-owned vocabulary?
- Should reminders live inside this module or a future shared notification service?
- What governance is required before AI practice prompts or pronunciation support?

## Sources

- Duolingo Max help page: https://www.duolingo.com/help/what-is-duolingo-max
- Duolingo Max announcement: https://blog.duolingo.com/duolingo-max/
- Babbel pricing page: https://my.babbel.com/en/prices
- Babbel product site: https://www.babbel.com/
- Busuu product site: https://www.busuu.com/
- Busuu App Store page: https://apps.apple.com/us/app/busuu-language-learning-app/id379968583
- Memrise product site: https://www.memrise.com/
- Memrise Google Play page: https://play.google.com/store/apps/details?id=com.memrise.android.memrisecompanion
- Memrise app update article: https://www.memrise.com/blog/major-update-a-new-version-of-the-app-is-coming

## Review Notes

Created during Language Learning Buddy Workflow Ready development. Public sources were summarized in original words.

## Revision History

- 2026-07-10: Initial market study for Language Learning Buddy V1.
