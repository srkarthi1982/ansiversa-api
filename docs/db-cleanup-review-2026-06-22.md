# DB Cleanup Review - 2026-06-22

Review scope: production database tables observed across the parent database and the 18 approved live apps.

No tables were deleted. No `DROP TABLE` statements were run. No deletion migrations were generated.

## Review Rules

| Classification | Meaning | Current action |
| --- | --- | --- |
| SAFE ZERO-ROW CANDIDATE | Table has zero rows and is not part of the expected current schema for that database. | Review for a future cleanup sprint. |
| ASTRO SNAPSHOT CANDIDATE | Table is an `_astro_db_snapshot` table created outside the current SQLAlchemy/Alembic app schema. | Review separately after confirming no tooling still depends on it. |
| NON-ZERO REVIEW REQUIRED | Table contains rows. | Export and review before any deletion decision. |
| DO NOT TOUCH | Table contains active platform/billing data or is otherwise outside mini-app cleanup scope. | Do not include in cleanup. |

Reference columns:

- `Backend model reference` means a current backend SQLAlchemy model references the table name. For parent DB duplicates, a note clarifies when the model reference belongs to a dedicated app DB, not the parent DB.
- `Migration reference` means current migration files mention the table name.

## SAFE ZERO-ROW CANDIDATE

| Database | Table | Rows | Backend model reference | Migration reference | Recommended action |
| --- | --- | ---: | --- | --- | --- |
| parent | `ConceptChecks` | 0 | Yes, but expected in dedicated `concept-explainer` DB only | Yes, parent legacy and dedicated migrations | Candidate for parent DB cleanup only; do not touch dedicated table. |
| parent | `ConceptJobs` | 0 | Yes, but expected in dedicated `concept-explainer` DB only | Yes, parent legacy and dedicated migrations | Candidate for parent DB cleanup only; do not touch dedicated table. |
| parent | `ConceptSteps` | 0 | Yes, but expected in dedicated `concept-explainer` DB only | Yes, parent legacy and dedicated migrations | Candidate for parent DB cleanup only; do not touch dedicated table. |
| parent | `Concepts` | 0 | Yes, but expected in dedicated `concept-explainer` DB only | Yes, parent legacy and dedicated migrations | Candidate for parent DB cleanup only; do not touch dedicated table. |
| parent | `FortuneFavorites` | 0 | No | No | Candidate for future zero-row cleanup. |
| parent | `FortuneSessions` | 0 | No | No | Candidate for future zero-row cleanup. |
| parent | `ResearchJobs` | 0 | Yes, but expected in dedicated `research-assistant` DB only | Yes, parent legacy and dedicated migrations | Candidate for parent DB cleanup only; do not touch dedicated table. |
| parent | `ResearchNotes` | 0 | Yes, but expected in dedicated `research-assistant` DB only | Yes, parent legacy and dedicated migrations | Candidate for parent DB cleanup only; do not touch dedicated table. |
| parent | `ResearchReferences` | 0 | Yes, but expected in dedicated `research-assistant` DB only | Yes, parent legacy and dedicated migrations | Candidate for parent DB cleanup only; do not touch dedicated table. |
| parent | `ResearchTopics` | 0 | Yes, but expected in dedicated `research-assistant` DB only | Yes, parent legacy and dedicated migrations | Candidate for parent DB cleanup only; do not touch dedicated table. |
| concept-explainer | `ConceptChecks_legacy_20260621` | 0 | No | No | Candidate for future zero-row cleanup. |
| concept-explainer | `ConceptJobs_legacy_20260621` | 0 | No | No | Candidate for future zero-row cleanup. |
| concept-explainer | `ConceptSteps_legacy_20260621` | 0 | No | No | Candidate for future zero-row cleanup. |
| lesson-builder | `LessonJobs` | 0 | No | No | Candidate for future zero-row cleanup. |
| lesson-builder | `LessonMaterials` | 0 | No | No | Candidate for future zero-row cleanup. |
| lesson-builder | `LessonObjectives` | 0 | No | No | Candidate for future zero-row cleanup. |
| lesson-builder | `LessonSteps` | 0 | No | No | Candidate for future zero-row cleanup. |
| lesson-builder | `Lessons` | 0 | No | No | Candidate for future zero-row cleanup. |
| quiz | `Bookmark` | 0 | No | No | Candidate for future zero-row cleanup. |
| smart-textbook-scanner | `ScanJobs` | 0 | No | No | Candidate for future zero-row cleanup. |
| smart-textbook-scanner | `TextbookDocuments` | 0 | No | No | Candidate for future zero-row cleanup. |
| smart-textbook-scanner | `TextbookHighlights` | 0 | No | No | Candidate for future zero-row cleanup. |
| study-planner | `Bookmark` | 0 | No | No | Candidate for future zero-row cleanup. |
| eco-habit-tracker | `HabitLogs` | 0 | No | No | Candidate for future zero-row cleanup. |
| json-formatter | `JsonFormatOperations` | 0 | No | No | Candidate for future zero-row cleanup. |
| json-formatter | `JsonSnippets` | 0 | No | No | Candidate for future zero-row cleanup. |
| json-formatter | `JsonTransformRecipes` | 0 | No | No | Candidate for future zero-row cleanup. |
| markdown-editor | `MarkdownDocumentVersions` | 0 | No | No | Candidate for future zero-row cleanup. |
| markdown-editor | `MarkdownDocuments` | 0 | No | No | Candidate for future zero-row cleanup. |
| mood-journal | `MoodJournalEntries` | 0 | No | No | Candidate for future zero-row cleanup. |
| mood-journal | `MoodPrompts` | 0 | No | No | Candidate for future zero-row cleanup. |
| password-generator | `GeneratedPasswords` | 0 | No | No | Candidate for future zero-row cleanup. |
| password-generator | `PasswordPresets` | 0 | No | No | Candidate for future zero-row cleanup. |
| qr-code-creator | `QrCodes` | 0 | No | No | Candidate for future zero-row cleanup. |
| qr-code-creator | `QrScanEvents` | 0 | No | No | Candidate for future zero-row cleanup. |

## ASTRO SNAPSHOT CANDIDATE

| Database | Table | Rows | Backend model reference | Migration reference | Recommended action |
| --- | --- | ---: | --- | --- | --- |
| ai-notes-summarizer | `_astro_db_snapshot` | 1 | No | No | Review in Phase 2 after confirming no external tooling depends on Astro snapshots. |
| lesson-builder | `_astro_db_snapshot` | 3 | No | No | Review in Phase 2 after confirming no external tooling depends on Astro snapshots. |
| memory-trainer | `_astro_db_snapshot` | 1 | No | No | Review in Phase 2 after confirming no external tooling depends on Astro snapshots. |
| quiz | `_astro_db_snapshot` | 10 | No | No | Review in Phase 2 after confirming no external tooling depends on Astro snapshots. |
| daily-word-challenge | `_astro_db_snapshot` | 1 | No | No | Review in Phase 2 after confirming no external tooling depends on Astro snapshots. |
| eco-habit-tracker | `_astro_db_snapshot` | 5 | No | No | Review in Phase 2 after confirming no external tooling depends on Astro snapshots. |
| formula-finder | `_astro_db_snapshot` | 2 | No | No | Review in Phase 2 after confirming no external tooling depends on Astro snapshots. |
| json-formatter | `_astro_db_snapshot` | 1 | No | No | Review in Phase 2 after confirming no external tooling depends on Astro snapshots. |
| markdown-editor | `_astro_db_snapshot` | 1 | No | No | Review in Phase 2 after confirming no external tooling depends on Astro snapshots. |
| mood-journal | `_astro_db_snapshot` | 1 | No | No | Review in Phase 2 after confirming no external tooling depends on Astro snapshots. |
| password-generator | `_astro_db_snapshot` | 1 | No | No | Review in Phase 2 after confirming no external tooling depends on Astro snapshots. |
| qr-code-creator | `_astro_db_snapshot` | 1 | No | No | Review in Phase 2 after confirming no external tooling depends on Astro snapshots. |

## NON-ZERO REVIEW REQUIRED

| Database | Table | Rows | Backend model reference | Migration reference | Recommended action |
| --- | --- | ---: | --- | --- | --- |
| concept-explainer | `Concepts_legacy_20260621` | 4 | No | No | Export rows and review content before any cleanup decision. |
| dictionary-plus | `DictionaryEntries` | 2 | No | No | Export rows and review whether they are old seed/reference records. |
| quiz | `Faq` | 6 | No | No | Export rows and compare with parent `Faqs` before any cleanup decision. |
| quiz | `QuestionVerification` | 36 | No | No | Export rows and review whether verification history is still needed. |
| study-planner | `Faq` | 6 | No | No | Export rows and compare with parent `Faqs` before any cleanup decision. |
| daily-word-challenge | `DailyWords` | 2 | No | No | Export rows and compare with bundled frontend word data before any cleanup decision. |
| eco-habit-tracker | `Habits` | 8 | No | No | Export rows and compare with bundled frontend habit data before any cleanup decision. |
| formula-finder | `Formulas` | 3 | No | No | Export rows and compare with bundled frontend formula data before any cleanup decision. |

## DO NOT TOUCH

| Database | Table | Rows | Backend model reference | Migration reference | Recommended action |
| --- | --- | ---: | --- | --- | --- |
| parent | `PaymentsEvents` | 15 | No | No | Do not include in mini-app cleanup; contains billing/event data. |
| parent | `PaymentsSubscriptions` | 3 | No | No | Do not include in mini-app cleanup; contains billing/subscription data. |

## Recommended Cleanup Phases

1. Phase 1: Zero-row cleanup only, after Partner approval of an explicit table list.
2. Phase 2: `_astro_db_snapshot` cleanup only, after confirming no deployment or external database tooling depends on these snapshots.
3. Phase 3: Non-zero legacy tables only after export, review, and a separate deletion plan.

Do not delete any non-zero table in Phase 1.
