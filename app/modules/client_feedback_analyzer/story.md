# Client Feedback Analyzer

## Purpose

Client Feedback Analyzer helps users organize client profiles, collect feedback, identify actionable insights, and prepare summary reports.

## Workflow

The V1 workflow moves through clients, feedback, insights, and reports. Clients provide the owner-scoped context for feedback. Feedback records capture source comments, sentiment, rating, status, and tags. Insights turn feedback into prioritized actions. Reports summarize the review work.

## User Journey

A signed-in user creates a client profile, adds feedback for that client, records insights from one or more feedback items, and prepares reports for review or sharing.

## Database Design

The app uses an isolated `CLIENT_FEEDBACK_ANALYZER_DATABASE_URL` database. Tables are `ClientProfiles`, `ClientFeedback`, `FeedbackInsights`, and `FeedbackReports`. All records include `ownerId` and `platformId`. Child records use indexed foreign keys for client and feedback relationships.

## API Design

The module is mounted at `/api/v1/client-feedback-analyzer`. Dashboard and list endpoints return lightweight summaries. Detail endpoints return complete editable records. Create and update DTOs are separate. Service operations validate ownership and parent-child relationships before writes.

## Shared Components Used

The backend follows shared FastAPI routing, auth dependency, SQLAlchemy session timing, Pydantic schema, and isolated Alembic migration patterns used by Ansiversa mini apps.

## Performance Considerations

Phase-1 indexes cover owner-scoped lists, client-linked feedback and insights, sentiment/status filtering, priority/status filtering, and report review order. Long text fields are excluded from text indexes.

## Current Status

The backend V1 foundation is approved live at version `1.0.0`. The parent Apps catalog stores Client Feedback Analyzer as `active` with `launchStatus = live`.

## Known Limitations

The backend stores manual analysis records only. It does not generate AI insights or reports automatically.

## Future Enhancements

Future versions may add AI-assisted sentiment extraction, trend clustering, exportable reports, and richer dashboard analytics.

## Current Implementation

Current implementation includes isolated database configuration, models, schemas, service functions, authenticated routes, migration files, and module story documentation.
