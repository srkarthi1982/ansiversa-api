# Job Tracker

## Purpose

Job Tracker helps users organize job listings, job applications, application insights, and application history during a job search.

## Workflow

The V1 workflow moves through jobs, applications, insights, and history. Jobs hold the opportunity details. Applications belong to jobs and track pipeline status. Insights capture recommendations and priorities. History records application events, summaries, and next steps.

## User Journey

A signed-in user creates a job listing, adds an application for that role, records insights about next actions or fit, and logs history as the application progresses.

## Database Design

The app uses an isolated `JOB_TRACKER_DATABASE_URL` database. Tables are `JobListings`, `JobApplications`, `ApplicationInsights`, and `ApplicationHistory`. Every record includes `ownerId` and `platformId`. Child records use indexed foreign keys for job and application relationships.

## API Design

The module is mounted at `/api/v1/job-tracker`. Dashboard and list endpoints return lightweight summaries. Detail endpoints return complete editable records. Create and update DTOs are separate for jobs, applications, and insights. History records support create, list, detail, and delete.

## Shared Components Used

The backend follows shared FastAPI routing, auth dependency, SQLAlchemy session timing, Pydantic schema, repository/service separation, and isolated Alembic migration patterns used by Ansiversa mini apps.

## Performance Considerations

Phase-1 indexes cover owner-scoped lists, job-linked applications, application-linked insights/history, status filters, priority filters, follow-up dates, and history timelines. Long text fields are excluded from text indexes.

## Current Status

The backend V1 foundation is implemented and remains `comingSoon`.

## Known Limitations

The backend stores manual job-search records only. It does not scrape job boards, send reminders, parse resumes, or generate AI recommendations.

## Future Enhancements

Future versions may add reminder notifications, job board imports, resume matching, interview integrations, and job-search analytics.

## Current Implementation

Current implementation includes isolated database configuration, models, schemas, repository functions, service functions, authenticated routes, migration files, overview metadata, and module story documentation.
