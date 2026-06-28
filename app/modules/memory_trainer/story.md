# Memory Trainer Backend Story

## Purpose

Memory Trainer gives authenticated users a persistent practice workflow for
custom memory games, active sessions, submitted rounds, and performance review.
The backend owns the generated round sequences, scoring, and performance records
so practice history is consistent across sessions.

## Workflow

The API supports a Games -> Sessions -> Rounds -> Performance workflow. Games
define the mode, difficulty, sequence length, and round count. Starting a
session creates the session and server-owned rounds. Users submit answers for
each round, then submit the session to calculate performance. Review and
progress endpoints expose the completed session and aggregate progress.

## User Journey

A user creates or selects a memory game, starts a session, studies each
sequence, submits the remembered answer and response time, completes all rounds,
and reviews accuracy plus average response time.

## Database Design

Memory Trainer uses an isolated mini-app database with four tables:

* `MemoryGames`
* `MemorySessions`
* `MemoryRounds`
* `MemoryPerformance`

`MemoryGames` is owner-scoped with `userId`. `MemorySessions` belongs to a game
and stores active/completed state. `MemoryRounds` belongs to a session and
stores the generated sequence, submitted answer, correctness, and response
time. `MemoryPerformance` is one-to-one with a completed session and stores the
aggregate score.

## API Design

The router is mounted at `/api/v1/memory-trainer`. Game endpoints support
create, read, update, delete, and list. Session endpoints start a game session,
load session detail, submit individual rounds, submit the completed session,
load review detail, and load progress aggregates. Round submission accepts the
user answer as a sequence array and normalizes it before scoring.

Service logic verifies the authenticated owner through the game/session before
returning or mutating records.

## Shared Components Used

The backend follows the shared Ansiversa FastAPI module pattern: isolated
database session, SQLAlchemy models, Pydantic schemas, thin routes,
service-owned logic, current-user auth, and owner-scoped access checks.

## Performance Considerations

The main query patterns are owner-scoped game lists, session lookup, round lookup
by session, and completed performance aggregation. User, game, session, and
parent foreign-key columns are indexed. Sequence and answer payloads are not
indexed.

## Current Status

The backend implementation is approved live at version `1.0.0`. The parent
Apps catalog stores Memory Trainer as `active` with `launchStatus = live`.

## Known Limitations

V1 supports user-owned practice games and session scoring. It does not include
public leaderboards, multiplayer play, adaptive difficulty, or shared game
templates.

## Future Enhancements

Future versions may add adaptive sequences, reusable templates, richer progress
analytics, scheduled practice, and shared learning challenges.

## Current Implementation

Current version: `1.0.0`

Implemented:

* Owner-scoped memory games
* Server-created practice sessions
* Round answer submission and scoring
* Session performance calculation
* Session review and progress APIs
* Current-state story documentation
