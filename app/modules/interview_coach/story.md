# Interview Coach Backend Story

## Purpose

Interview Coach owns the persistent preparation records for interview practice: sessions, questions, answers, and readiness reviews. The backend exists to keep a user's preparation history structured around interview targets and to enforce ownership across every child record.

## Workflow

The backend supports a Sessions -> Questions -> Practice Answers -> Reviews workflow. Sessions are the parent records. Questions belong to sessions, answers belong to questions and sessions, and reviews summarize readiness for a session.

## User Journey

An authenticated user creates an interview session for a role and interview type, adds practice questions, writes answers with confidence ratings, and records review feedback with strengths, improvements, and next steps. The dashboard returns the user's preparation state and aggregate counters so the frontend can resume the active session quickly.

## Database Design

The module uses four persistent tables:

* `InterviewSessions` stores the interview target, role, company, interview type, target date, and status.
* `InterviewQuestions` stores ordered prompts under a session.
* `InterviewAnswers` stores answer text, confidence, and answer status under a question and session.
* `InterviewReviews` stores readiness score, strengths, improvements, and next steps under a session.

`ownerId` indexes support user-owned dashboard and list queries. `sessionId` and `questionId` indexes support parent lookups for questions, answers, and reviews. Large answer and review text fields are not indexed because the current product does not provide text search.

## API Design

The router exposes `/api/v1/interview-coach/dashboard`, sessions CRUD, questions CRUD, answer create/update/list, and review create/list routes. Request schemas separate create and update behavior so update payloads do not require create-only parent IDs. Response models include only the fields the current frontend needs, including counts such as question, answer, and review totals.

## Shared Components Used

The module uses the shared FastAPI module pattern: isolated database dependency, SQLAlchemy models, Pydantic schemas, thin routes, service-owned business logic, current-user authentication, owner-scoped access checks, and generated OpenAPI contracts for the frontend.

## Performance Considerations

The dashboard provides coordinated session, question, answer, review, and counter data in one request because the frontend pages operate on the same selected-session context. Indexes match the current query paths for owner lists and parent-child navigation. The backend does not create speculative text-search indexes for answer or review text.

## Current Status

The backend implementation is live at version `1.0.0`. The parent Apps catalog stores Interview Coach as `active` with `launchStatus = live`.

## Known Limitations

V1 supports written practice and manual review records. It does not include video practice, audio capture, speech scoring, automated interviewer simulation, recruiter collaboration, or calendar scheduling.

## Future Enhancements

Future versions may add AI-generated questions, voice practice, timed mock interviews, readiness trend analytics, job-description imports, and external calendar reminders.

## Current Implementation

Current version: `1.0.0`

Implemented:

* Isolated Interview Coach backend module
* `InterviewSessions` persistence
* `InterviewQuestions` persistence
* `InterviewAnswers` persistence
* `InterviewReviews` persistence
* Dashboard route with preparation counters
* Session and question CRUD routes
* Answer create/update/list routes
* Review create/list routes
* Owner-scoped service access
* Query-pattern indexes for owner, session, and question lookups
* Current-state story documentation
