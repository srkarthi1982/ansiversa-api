# Quiz Backend Story

## Purpose

Quiz gives authenticated users a server-graded practice workflow over the
existing Ansiversa question taxonomy. The backend owns taxonomy reads, attempt
creation, answer submission, result storage, and answer review reconstruction
so quiz scoring remains authoritative and cannot be manipulated by the browser.

## Workflow

The API supports a Taxonomy -> Attempt -> Submit -> Review workflow. Users
choose a platform, subject, topic, roadmap, and level; the backend selects
active questions for an attempt; the user submits answers; the backend grades
the attempt and returns a review with selected answers, correct answers, and
explanations.

## User Journey

A user enters `/quiz/play`, loads active taxonomy options, starts a ten-question
attempt, answers each question, submits once, then reviews the result. The
history APIs let the user revisit attempts and completed result detail from
`/quiz/attempts` and `/quiz/results`.

## Database Design

Quiz uses the isolated quiz database and maps the existing taxonomy tables:

* `Platform`
* `Subject`
* `Topic`
* `Roadmap`
* `Question`

User activity is stored in:

* `QuizAttempt`
* `QuizAttemptQuestion`
* `Result`

`QuizAttempt` stores the owner, selected taxonomy, level, status, expiry,
submission time, and linked result. `QuizAttemptQuestion` freezes the exact
question set and display order used by the attempt. `Result` stores the scored
submission and preserved response payload for review.

## API Design

The router is mounted at `/api/v1/quiz`. Taxonomy endpoints are paginated and
filterable so the frontend can progressively load active platforms, subjects,
topics, and roadmaps. Attempt creation returns question text and options only;
answer keys and explanations are withheld until submission or result review.

History endpoints return lightweight attempt/result summaries. Result detail
reconstructs the review view only when the user opens a saved result. Protected
routes use the current user and reject access to attempts or results owned by
another user.

## Shared Components Used

The backend follows the shared Ansiversa FastAPI module pattern: isolated
database session, SQLAlchemy models, Pydantic schemas, thin routes,
service-owned logic, current-user auth, and owner-scoped access checks.

## Performance Considerations

Quiz keeps the play path indexed around the real user-facing query pattern:
platform, subject, topic, roadmap, level, and active status. Attempt and result
history are paginated. Review detail loads the full answer explanation payload
only when the user asks to inspect a result.

## Current Status

The backend implementation is approved live at version `1.0.0`. The parent
Apps catalog stores Quiz as `active` with `launchStatus = live`.

## Known Limitations

V1 focuses on server-graded practice and answer review. It does not include
question authoring, adaptive learning, multiplayer play, or public leaderboards.

## Future Enhancements

Future versions may add adaptive question selection, richer performance
analytics, authoring workflows, spaced repetition, and cross-app learning
recommendations.

## Current Implementation

Current version: `1.0.0`

Implemented:

* Protected taxonomy list APIs
* Server-owned attempt creation and expiry
* Server-side answer grading
* Attempt and result history
* Result detail review with explanations
* Query-pattern index for the quiz play filter
* Current-state story documentation
