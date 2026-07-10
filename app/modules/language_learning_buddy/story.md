# Language Learning Buddy Story

## Purpose

Language Learning Buddy gives authenticated users a focused workspace for building a vocabulary library, recording practice sessions, and reviewing learning progress. It is a manual practice tracker, not an AI tutor, generated lesson engine, translation service, or certification tool.

## Workflow

The protected workflow starts at `/language-learning-buddy/vocabulary`. Users create vocabulary, record practice sessions against saved vocabulary, and review progress.

## User Journey

A user creates a vocabulary item with word, translation, language, category, difficulty, and notes. The user records practice sessions with practice date, result, confidence, and notes. The Progress page summarizes vocabulary count, languages, practice count, weekly practice, recent sessions, and difficulty mix.

## Database Design

Language Learning Buddy uses an isolated database configured by `LANGUAGE_LEARNING_BUDDY_DATABASE_URL`. The module owns `LanguageVocabulary` and `LanguagePracticeSessions`. Every table stores `userId` for owner scoping. Practice sessions belong to vocabulary and are deleted with their parent vocabulary item.

## API Design

The router is mounted at `/api/v1/language-learning-buddy`. It exposes protected dashboard, vocabulary CRUD, and practice-session CRUD endpoints. Dashboard and list responses return lightweight summaries and previews. Detail endpoints return full editable fields. Practice-session update schemas intentionally exclude create-only `vocabularyId`, so editing a session does not support parent vocabulary reassignment.

## Shared Components Used

The frontend uses the platform shell, protected authenticated page state, `AvPageHeader`, `AvFeedbackStack`, `AvEmptyState`, `AvFormDrawer`, `AvRecordActions`, and shared card styling.

## Performance Considerations

Indexes cover owner-scoped lists, language and category filters, parent vocabulary lookups, practice dates, result filters, and updated-at ordering. Large text notes are not indexed. List responses use previews and counts instead of full notes.

## Current Status

Workflow Ready only. The backend has protected owner-scoped APIs, isolated migration `20260710_0001`, dashboard summaries, vocabulary CRUD, practice-session CRUD, lightweight/detail response separation, and generated frontend API contracts. The parent Apps catalog remains `active` / `comingSoon` with version `null`.

## Known Limitations

V1 does not include external AI, generated lessons, speech recognition, pronunciation scoring, spaced-repetition scheduling, reminders, imports, exports, collaboration, browser storage persistence, or cross-app automation. All vocabulary and practice records are manually entered.

## Future Enhancements

Future versions may add spaced-repetition scheduling, import/export, optional reminders, richer progress charts, and approved cross-app learning summaries. Any AI tutoring or generated practice requires separate governance and must remain opt-in and reviewable.

## Current Implementation

Language Learning Buddy is a DB-backed mini-app module with owner-scoped CRUD APIs, isolated migration files, lightweight response schemas, dashboard summary calculation, and protected frontend routes for Vocabulary, Practice, and Progress. The overview Explore CTA enters `/language-learning-buddy/vocabulary`. The parent Apps catalog stores Language Learning Buddy as `active` with `launchStatus = comingSoon` and `version = null`.
