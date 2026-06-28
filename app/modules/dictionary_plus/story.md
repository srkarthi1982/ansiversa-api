# Dictionary+ Backend Story

## Purpose

Dictionary+ gives authenticated users a vocabulary workspace for recording word
lookups, saving useful words, and organizing saved words into personal lists.
The backend owns the persistent vocabulary records so users can build a
long-term word library.

## Workflow

The API supports a Lookups -> Saved Words -> Word Lists workflow. Lookups store
word definitions and example details. Saved words can be created from a lookup
or entered manually. Word lists group saved word IDs into user-owned vocabulary
collections.

## User Journey

A user records a word lookup with definition, pronunciation, part of speech, and
example sentence. The user saves words worth keeping, deletes saved words when
needed, creates word lists, and toggles saved words into or out of those lists.

## Database Design

Dictionary+ uses an isolated mini-app database with three tables:

* `DictionaryLookups`
* `SavedWords`
* `WordLists`

All tables are owner-scoped with `userId`. `SavedWords.lookupId` optionally
links a saved word back to the lookup that produced it. `WordLists.savedWordIds`
stores an ordered JSON list of saved-word IDs for the current list membership.
Definitions and example sentences are large text fields and are not used as
index targets.

## API Design

The router is mounted at `/api/v1/dictionary-plus`. Lookup, saved-word, and
word-list endpoints are separated so the frontend can load the vocabulary
workspace in focused groups. Word payload schemas normalize whitespace, enforce
field lengths, and forbid unexpected fields. Word-list create and update schemas
deduplicate saved-word IDs before persistence.

Saved-word deletion also requires the frontend to remove the deleted ID from
word-list state so stale membership does not remain visible.

## Shared Components Used

The backend follows the shared Ansiversa FastAPI module pattern: isolated
database session, SQLAlchemy models, Pydantic schemas, thin routes,
service-owned logic, current-user auth, and owner-scoped access checks.

## Performance Considerations

The main query patterns are owner-scoped lookup history, saved-word lists, and
word-list lists ordered by recency. User ID columns are indexed. Definition and
example text are intentionally not indexed because V1 is not a full-text search
engine.

## Current Status

The backend implementation is approved live at version `1.0.0`. The parent
Apps catalog stores Dictionary+ as `active` with `launchStatus = live`.

## Known Limitations

V1 stores user-entered dictionary data and lists. It does not provide licensed
dictionary content, pronunciation audio, spaced repetition, or full-text
vocabulary search.

## Future Enhancements

Future versions may add dictionary-provider lookup, pronunciation audio,
practice scheduling, import/export, and Daily Word Challenge integration.

## Current Implementation

Current version: `1.0.0`

Implemented:

* Owner-scoped lookup history
* Saved words with optional lookup linkage
* Word lists with saved-word membership
* Word-list create, update, and delete workflow
* Saved-word create and delete workflow
* Current-state story documentation
