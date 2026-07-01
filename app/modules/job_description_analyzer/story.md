# Job Description Analyzer Backend Story

## Purpose

Job Description Analyzer helps authenticated users turn job postings into structured review records. The backend stores job descriptions, analysis summaries, extracted skill matches, and analysis history in an isolated mini-app database so career planning data stays owner-scoped and separate from parent platform data.

## Workflow

The API supports a Jobs -> Analysis -> Skills -> History workflow. A user saves a job description, creates an analysis for that description, records skill matches for the analysis, and logs review history as the analysis changes.

## User Journey

A signed-in user opens the app, imports or manually enters a job description, adds an analysis with match score, keywords, responsibilities, and recommendations, records skill matches, and logs follow-up notes or status changes.

## Database Design

The module owns four tables: `JobDescriptions`, `JobAnalyses`, `SkillMatches`, and `AnalysisHistory`. Each table includes `ownerId`, optional `platformId`, `createdAt`, and `updatedAt`. `JobAnalyses` belongs to `JobDescriptions`; `SkillMatches` and `AnalysisHistory` belong to `JobAnalyses`.

## API Design

The module is mounted at `/api/v1/job-description-analyzer`. Dashboard and list endpoints return lightweight summary responses with previews and counters. Detail endpoints return complete editable records. Create and update DTOs are separate, and update DTOs avoid create-only parent reassignment for analysis, skills, and history.

## Shared Components Used

The backend uses the shared auth dependency for current-user ownership, the shared timing session infrastructure, and the standard FastAPI router/service/repository layering used by current Platform Foundation V1 mini apps.

## Performance Considerations

Summary responses avoid returning large job description text, analysis bodies, evidence, recommendations, and next-step text. Phase-1 indexes cover owner-scoped lists, updated sorting, parent lookups, status dashboards, skill-match filters, and history timelines without indexing large text columns.

## Current Status

The backend is implemented as an isolated coming-soon mini-app API. The production isolated database migration is complete at revision `20260630_0001`, and the module is ready for manual QA without live promotion.

## Known Limitations

The current backend records analysis data supplied by the frontend. It does not call an AI model, parse uploaded files, or generate automatic match scores.

## Future Enhancements

Future versions may add AI-assisted extraction, resume comparison, keyword coverage scoring, exportable reports, integration with Resume Builder, and richer skill taxonomy support.

## Current Implementation

The module contains explicit models, schemas, repository functions, service ownership checks, protected routes, isolated database configuration, Alembic migration assets, and current story documentation for App #035.
