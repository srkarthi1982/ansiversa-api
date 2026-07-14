# Home Inventory Manager Story

## Purpose

Home Inventory Manager stores owner-scoped household belongings records. It exists for users who need a private, lightweight way to track items, categories, rooms, quantities, values, warranty dates, condition, and notes.

The app is for personal household organization only. It does not provide ecommerce, warehouse, ERP, accounting, marketplace, insurance, barcode, AI, smart-home, photo, attachment, or receipt workflows.

## Workflow

The workflow is:

```text
Overview
→ Items
→ Categories
→ Insights
```

Items are the primary workspace. Categories support organization. Insights summarize the inventory.

## User Journey

1. The user opens the overview and chooses Explore.
2. The Items route lets the user create an item with category, room, quantity, purchase/value details, warranty date, condition, and notes.
3. Saved items can be searched, filtered, sorted, edited, archived, restored, or permanently deleted.
4. The Categories route lets the user create, rename, and delete categories when no items are attached.
5. The Insights route summarizes inventory count, estimated value, archived count, warranty attention, distributions, recent additions, and highest-value items.

## Database Design

The module uses an isolated database configured by `HOME_INVENTORY_MANAGER_DATABASE_URL`.

Tables:

- `Categories`: owner-scoped custom category names.
- `Items`: owner-scoped household inventory records.

Indexes support owner lists, category filters, room filters, condition filters, archive filters, warranty filters, estimated value sorting, purchase-date sorting, and update sorting.

## API Design

Routes are mounted under:

```text
/api/v1/home-inventory-manager
```

Primary endpoints:

- `GET /dashboard`
- `GET /insights`
- `GET /items`
- `POST /items`
- `GET /items/{item_id}`
- `PUT /items/{item_id}`
- `POST /items/{item_id}/archive`
- `POST /items/{item_id}/restore`
- `DELETE /items/{item_id}`
- `GET /categories`
- `POST /categories`
- `PUT /categories/{category_id}`
- `DELETE /categories/{category_id}`

List and dashboard endpoints return only fields required by the UI. Detail endpoints return notes for edit workflows.

## Shared Components Used

The backend follows the isolated mini-app module pattern:

- dedicated SQLAlchemy base and session factory
- owner-scoped dependencies
- repository/service/router separation
- OpenAPI operation IDs
- module-specific Alembic environment and version table

## Performance Considerations

V1 stores metadata only and intentionally excludes images, attachments, receipts, and AI payloads. List filtering happens over owner-scoped records and is backed by indexes for the primary query dimensions.

## Current Status

App #075 is implemented as Workflow Ready for Astra/Partner review. It remains `comingSoon` with `version: null` and no approved destination metadata.

## Known Limitations

- No images, attachments, receipts, barcode scanning, QR labels, import/export, or AI.
- No insurance integration or claim report generation.
- Estimated value is user-entered and informational.
- Warranty tracking is summary-only; no reminder notifications are sent in V1.

## Future Enhancements

- CSV import/export after review.
- Optional warranty reminders through a governed reminder system.
- Photo or receipt storage only after storage governance approval.
- AI-assisted item entry only after explicit privacy and accuracy governance approval.

## Current Implementation

The implementation provides owner-scoped category CRUD, item CRUD, archive/restore, permanent delete, search/filter/sort, dashboard, insights, overview metadata, migration, and lifecycle documentation.
