# Digital Document Vault Destination

## Document Status

Approved for Live promotion on 2026-07-14 after Astra review, Partner approval, production migration verification, production upload-fix verification, and manual browser verification.

## Destination Status

Approved v1.0

## Destination

Digital Document Vault should become a private personal document shelf inside Ansiversa. The mature product helps users upload important files, organize them with searchable metadata, review expiry context, and retrieve or replace files when needed.

The destination is intentionally personal and bounded. It is not a government portal, identity wallet, legal vault, cloud-drive client, external verification system, notarization tool, or official renewal service.

The destination is always `100 / 100`. The current approved Journey Progress is `20 / 100`.

## Mature Workflow

1. Upload a supported document file.
2. Add title, category, document type, description, tags, and optional issue or expiry dates.
3. Search and filter documents by metadata and review file details.
4. Replace stale files, edit metadata, download files, or delete records.
5. Manage categories and review counts.
6. Review storage, category, type, expiry, and recent upload insights.

## V1 Product Boundary

- Owner-scoped documents and categories.
- Upload support for PDF, JPG, PNG, and DOCX.
- Metadata edit separate from file replacement.
- Category CRUD with deletion blocked when documents exist.
- Search and filters for title, category, tags, document type, and expiry state.
- Dashboard and insights summaries.
- No external document verification.
- No cloud-drive sync.
- No government integration.
- No identity-provider integration beyond the platform's normal authentication.
- No OCR, AI extraction, or file content indexing.

## Destination Metrics

- Users can retrieve an uploaded document with minimal navigation.
- Metadata remains editable without requiring file re-upload.
- Category deletion protects attached documents.
- Owner isolation prevents cross-user access.
- Overview CTA enters the document workflow directly.
- App remains consistent with the Ansiversa shell and shared UI patterns.

## Journey Progress

Current Position: 20 / 100

Current Journey Progress: 20 / 100

V1 creates the private vault foundation with owner-scoped category management, document upload, metadata edit, replacement, download, delete, search/filter, storage and expiry insights, production migration, and verified production upload/download behavior. Remaining maturity includes managed object storage, previews, storage quotas, governed reminders, richer import/export, and any future AI-assisted tagging only after privacy governance approval.

## Future Enhancements

- Browser preview for supported file types.
- Storage quota and retention policy surfaced at platform level.
- Optional reminders tied to expiry metadata.
- Optional import/export package after platform storage policy approval.
- AI-assisted tagging or extraction only after explicit privacy and governance approval.
- V2 should migrate file bytes to managed object storage while retaining metadata, object keys, checksums, storage provider, and retention state in the database.

## Current Implementation

The current implementation stores owner-scoped categories and document metadata in isolated `Categories` and `Documents` tables. V1 stores supported file content as base64 text in the app database to support the production libSQL driver. Downloads decode the stored payload back to the original bytes.

The first workflow route is `/digital-document-vault/documents`. Catalog status is approved for live release at version `1.0.0`.

## Governance Notes

Astra: Approved on 2026-07-14.

Partner: Approved Digital Document Vault live promotion after production upload fix and manual workflow verification.

Codex: Ran production-configured isolated database migration, verified schema/indexes/version table, verified upload/download/replace/delete smoke behavior, synced overview metadata, and prepared live promotion metadata.
