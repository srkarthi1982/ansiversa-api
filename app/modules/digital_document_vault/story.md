# Digital Document Vault Story

## Purpose

Digital Document Vault stores personal document files together with searchable metadata. It exists for users who need a private, owner-scoped place to upload, organize, retrieve, replace, and delete important digital documents.

The app is for personal organization only. It does not integrate with government systems, cloud drives, identity providers, or external document verification services.

## Workflow

The workflow is:

```text
Overview
→ Documents
→ Categories
→ Insights
```

Documents are the primary workspace. Categories support organization. Insights summarize the vault.

## User Journey

1. The user opens the overview and chooses Explore.
2. The Documents route lets the user create a document by uploading a supported file and entering metadata.
3. Saved documents show file name, upload date, category, document type, file size, tags, and expiry state.
4. The user can edit metadata, replace the file, download the file, or delete the document.
5. The Categories route lets the user create, rename, and delete categories when no documents are attached.
6. The Insights route summarizes total documents, storage used, type/category distribution, expiry state, and recent uploads.

## Database Design

The module uses an isolated database configured by `DIGITAL_DOCUMENT_VAULT_DATABASE_URL`.

Tables:

- `Categories`: owner-scoped custom category names.
- `Documents`: owner-scoped document metadata and the uploaded file blob.

Document file payloads are stored in the isolated database in `fileBlob` as base64 text so the same code works with SQLite and the production libSQL driver. The metadata columns retain the original `fileName`, generated `storedFileName`, `mimeType`, `fileSize`, issue date, expiry date, and timestamps.

Indexes support owner lists, category filters, document type filters, expiry filters, uploaded sorting, and update sorting.

## API Design

Routes are mounted under:

```text
/api/v1/digital-document-vault
```

Primary endpoints:

- `GET /dashboard`
- `GET /documents`
- `POST /documents`
- `GET /documents/{document_id}`
- `PUT /documents/{document_id}`
- `POST /documents/{document_id}/replace-file`
- `GET /documents/{document_id}/download`
- `DELETE /documents/{document_id}`
- `GET /categories`
- `POST /categories`
- `PUT /categories/{category_id}`
- `DELETE /categories/{category_id}`

Create and replace use multipart upload. Metadata update uses JSON and does not accept file bytes. Download returns the stored bytes with the original file name.

## Shared Components Used

The backend follows the isolated mini-app module pattern:

- dedicated SQLAlchemy base and session factory
- owner-scoped dependencies
- repository/service/router separation
- OpenAPI operation IDs
- module-specific Alembic environment and version table

## Performance Considerations

V1 uses a 10 MB file-size limit to keep database-backed storage practical. List and dashboard responses return metadata only, never file blobs. File bytes are returned only from the download endpoint.

## Current Status

App #074 is implemented as Workflow Ready for owner review. It remains `comingSoon` with `version: null`.

## Known Limitations

- No browser file preview.
- No OCR or file-content search.
- No AI extraction or classification.
- No external backup, sync, sharing, or verification.
- Storage quotas are enforced only by per-file size in V1.

## Future Enhancements

- File preview support for common formats.
- Platform-level storage quotas and retention controls.
- Optional expiry reminders if approved.
- AI tagging or extraction only after explicit privacy governance approval.

## Current Implementation

The implementation provides owner-scoped category CRUD, document upload, metadata edit, file replacement, download, delete, search/filter, insights, overview metadata, migration, and lifecycle documentation.
