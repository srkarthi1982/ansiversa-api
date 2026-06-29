# Contract Generator Backend Story

## Purpose

Contract Generator stores owner-scoped contract workspaces, generated contract
documents, reusable clauses, and activity history for the Contract Generator
mini app.

## Workflow

The backend supports a protected workflow from projects to documents, clauses,
and history. Users create a project, create contract documents inside that
project, attach reusable clauses to documents, and log generation, review,
approval, signature, or export activity.

## User Journey

A signed-in user opens the app, creates a contract project for a client or
counterparty, drafts one or more contract documents, adds clauses to organize
the document structure, and records activity as the contract moves through
draft, review, approval, signature, and export.

## Database Design

The isolated Contract Generator database contains:

* `ContractProjects`
* `ContractDocuments`
* `ContractClauses`
* `ContractHistory`

Every table has an `ownerId` column. Documents belong to projects. Clauses
belong to documents. History entries can reference a project, a document, or
both.

## API Design

The module is mounted at `/api/v1/contract-generator`. Dashboard responses
return lightweight summaries for projects, documents, clauses, and history.
Detail endpoints return full editable project, document, or clause records.
Long document bodies and clause text are excluded from dashboard and list
responses.

## Shared Components Used

The backend follows the shared Ansiversa patterns for FastAPI routers,
Pydantic request and response schemas, SQLAlchemy models, isolated session
management, and owner-scoped service functions.

## Performance Considerations

The dashboard uses summary responses and avoids large text fields. Phase-1
indexes support owner-updated project and document lists, project-status
document filters, document-clause ordering, clause category filtering, and
owner/project/document history timelines.

## Current Status

The backend implementation is approved live at version `1.0.0`. The parent
Apps catalog stores Contract Generator as `active` with `launchStatus = live`.

## Known Limitations

The backend stores contract draft data and activity records. It does not provide
legal advice, automated legal review, signature execution, or external
signature integrations.

## Future Enhancements

Future versions can add template libraries, clause presets, export rendering,
approval workflows, signature integrations, and richer comparison tools.

## Current Implementation

The implementation includes isolated SQLAlchemy models, an isolated database
session, an isolated Alembic configuration, initial migration, CRUD routes for
projects/documents/clauses/history, dashboard summaries, detail responses for
editable records, owner checks for every record, and overview metadata for the
Contract Generator mini app.
