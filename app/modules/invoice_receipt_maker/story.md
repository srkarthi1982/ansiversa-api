# Invoice and Receipt Maker Backend Story

## Purpose

Invoice and Receipt Maker gives authenticated users an isolated backend for
organizing billing collections, creating invoice or receipt documents, adding
line items, and logging document activity. The module is owned by the
`invoice-receipt-maker` mini app and does not share persistence tables with
other mini apps.

## Workflow

The workflow starts with a project that represents a business/client billing
collection. Users create invoice or receipt documents inside a project, add line
items to calculate document totals, and record history entries for sending,
payment, export, or void activity.

## User Journey

A user enters from `/invoice-receipt-maker/projects`, creates a project with
business identity and currency, adds invoice or receipt documents for clients,
adds itemized charges, and records document activity in history. The backend
keeps every record owner-scoped so one user can only access their own projects,
documents, items, and logs.

## Database Design

The module owns four tables:

* `InvoiceReceiptProjects`
* `InvoiceReceiptDocuments`
* `InvoiceReceiptItems`
* `InvoiceReceiptHistory`

Every table has an `ownerId` column. Documents belong to projects. Items belong
to documents. History records may reference a project, a document, or both.
Document totals are stored on `InvoiceReceiptDocuments` and recalculated when
items are created, updated, or deleted.

## API Design

The router is mounted at `/api/v1/invoice-receipt-maker`. Dashboard responses
return lightweight project, document, item, and history summaries. Summary
responses use preview fields for long notes and descriptions. Detail endpoints
return full editable records for projects, documents, and items.

## Shared Components Used

The backend uses the shared authenticated user dependency, timed SQLAlchemy
session helpers, API timing engine registration, and the established isolated
mini-app Alembic pattern.

## Performance Considerations

The initial migration includes owner and workflow indexes for the dashboard and
route query patterns: owner-updated project/document/item lists, project-status
document filters, document item ordering, and owner/project/document history
feeds. Large text fields are not returned in dashboard payloads.

## Current Status

The backend module is implemented for workflow review. The app catalog remains
`status = active`, `launchStatus = comingSoon`, and `version = null`.

## Known Limitations

The backend stores invoice and receipt data and recalculates line-item totals,
but it does not generate PDFs, send emails, collect online payments, or manage
tax jurisdiction rules.

## Future Enhancements

Future versions may add PDF export, email sending, reusable business profiles,
payment tracking integrations, template branding, recurring invoices, and tax
rule helpers.

## Current Implementation

Current implementation includes an isolated SQLAlchemy base and session, a
dedicated Alembic config, a first migration for the four module tables, protected
CRUD routes for projects/documents/items/history, owner checks for every record,
dashboard summaries, detail responses for edit flows, item total calculations,
and overview metadata pointing Explore to `/invoice-receipt-maker/projects`.
