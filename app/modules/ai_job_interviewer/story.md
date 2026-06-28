# AI Job Interviewer Backend Story

## Purpose

AI Job Interviewer owns the persistent preparation records for job interview practice: sessions, questions, answers, and progress results. The backend exists to keep job-specific practice organized around authenticated users and to protect every child record through owner-scoped access.

## Workflow

The backend supports a Sessions -> Questions -> Answers -> Results workflow. Sessions are the parent records. Questions belong to sessions, answers belong to questions and sessions, and results summarize progress for a session.

## User Journey

An authenticated user creates an interview session for a role, company, experience level, interview type, and target date. The user adds ordered practice questions, records answers with confidence, and creates result feedback with a progress score, strengths, improvements, and next steps. The dashboard returns the user's interview practice state and aggregate counters for the frontend workspace.

## Database Design

The module uses four persistent tables:

* `AiJobInterviewSessions` stores the interview target, role, company, experience level, interview type, target date, and status.
* `AiJobInterviewQuestions` stores ordered prompts under a session.
* `AiJobInterviewAnswers` stores answer text, confidence, and answer status under a question and session.
* `AiJobInterviewResults` stores progress score, strengths, improvements, and next steps under a session.

`ownerId` indexes support user-owned dashboard and list queries. `sessionId` and `questionId` indexes support parent lookups for questions, answers, and results. Long answer and result text fields are not indexed because V1 does not provide text search.

## API Design

The router exposes `/api/v1/ai-job-interviewer/dashboard`, sessions CRUD, questions CRUD, answer create/update/list, and result create/list routes. Request schemas separate create and update behavior so update payloads do not require create-only parent IDs. Response models include only the current frontend fields, including counts such as question, answered, result, active session, completed session, answered question, and average progress metrics.

## Shared Components Used

The module uses the shared FastAPI module pattern: isolated database dependency, SQLAlchemy models, Pydantic schemas, thin routes, service-owned business logic, current-user authentication, owner-scoped access checks, and generated OpenAPI contracts for the frontend.

## Performance Considerations

The dashboard provides coordinated session, question, answer, result, and counter data in one request because the frontend pages operate on the same selected-session context. Indexes match the current query paths for owner lists and parent-child navigation. The backend avoids speculative text-search indexes for prompts, answers, strengths, improvements, and next steps.

## Current Status

The backend implementation is live at version `1.0.0`. The parent Apps catalog stores AI Job Interviewer as `active` with `launchStatus = live`.

## Known Limitations

V1 supports structured written practice and manual result records. It does not provide live video interviews, speech analysis, recruiter collaboration, job-board ingestion, automated conversation generation, or external scheduling.

## Future Enhancements

Future versions may add AI-generated question sets, voice/video practice, job-description tailoring, timed mock interviews, scheduler integrations, scoring analytics, and trend history.

## Current Implementation

Current version: `1.0.0`

Implemented:

* Isolated AI Job Interviewer backend module
* `AiJobInterviewSessions` persistence
* `AiJobInterviewQuestions` persistence
* `AiJobInterviewAnswers` persistence
* `AiJobInterviewResults` persistence
* Dashboard route with interview practice counters
* Session and question CRUD routes
* Answer create/update/list routes
* Result create/list routes
* Owner-scoped service access
* Query-pattern indexes for owner, session, and question lookups
* Current-state story documentation
