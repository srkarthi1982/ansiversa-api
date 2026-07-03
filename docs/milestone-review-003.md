# Ansiversa Milestone Review #3 - Backend

Date: 2026-07-03

Scope: Backend platform review after 50 completed mini-apps. App #51 was not started.

Decision: Approved to continue App #51 after Partner/Astra accept the review findings. No backend blocker requires a pre-App #51 fix, but route registration, migration inventory, and story parity should be tightened before the next large batch.

## Summary

The backend platform remains structurally sound. FastAPI routing, parent modules, isolated mini-app databases, Alembic contexts, generated OpenAPI operation IDs, auth dependencies, owner-scoped services, and index coverage are enough to continue. The main risk is operational drift as more mini-app APIs are added manually.

## Findings

| Section | Status | Evidence | Recommendation | Action taken |
| --- | --- | --- | --- | --- |
| Shared services | Good | `app/core` owns config, database, security, OpenAPI IDs, and timing middleware. Parent modules cover auth, content, apps, favorites, notifications, profile, dashboard, admin, audit, FAQs, and contact. | Keep platform services in `app/core` and parent modules. Avoid mini-app-specific behavior in shared services. | Report only. |
| API contract consistency | Good | `app/main.py` uses `generate_operation_id`; module routes expose typed schemas and owner-scoped handlers; README documents OpenAPI and generated client expectations. | Keep route names stable. Consider module-specific OpenAPI exports once schema size becomes painful. | Report only. |
| Database naming | Good | Newer app models use app-specific table names and `ownerId`/foreign-key conventions; older apps still carry `userId` in some tables for legacy compatibility. | Do not rename legacy tables during the freeze. Document owner/user naming expectations for App #51 onward. | Report only. |
| Migrations | Watch | Repository has parent `alembic.ini` plus 35 isolated mini-app Alembic configs. There are more backend modules than migration-owning apps because local-only and non-persistent modules do not need databases. | Maintain an inventory mapping each completed app to: no DB, parent DB, or isolated DB. | Report only. |
| Indexes | Good | Migrations and models include owner/user indexes, foreign-key indexes, and several compound indexes for dashboard/list paths. Prior DB cleanup and metadata performance docs exist. | Continue indexing owner-scoped list/detail paths only; avoid speculative indexes. | Report only. |
| Unused tables | Watch | No database inspection was performed during the freeze; repository review cannot prove production table usage. Existing `db-cleanup-review-2026-06-22.md` documents prior cleanup review. | Run a production-safe table usage inventory separately before large migration work. | Report only. |
| Runtime performance | Good | GZip middleware and timing middleware are registered; route docs favor compact dashboard/list responses and detail endpoints for large editable records. | Keep long text/blob fields out of dashboard responses. Review timing data before adding new shared caches. | Report only. |
| Authentication and protected behavior | Good | Backend scans show mini-app routes reuse `get_current_user` or module `CurrentUser` dependency; admin routes layer admin checks on top. | Keep all user data routes protected and owner-scoped. Add route coverage checks to scaffolding. | Report only. |
| Navigation/API relation | Good | Frontend route slugs and backend route prefixes match current backend-backed apps; local-only apps intentionally do not all have API routers. | Keep backend route prefixes slug-aligned with frontend module slugs. | Report only. |
| UX/API state support | Good | API modules generally expose dashboard/list/detail CRUD shapes that support loading, empty, error, success, and delete confirmation flows on the frontend. | Preserve list/detail separation and explicit delete endpoints. | Report only. |
| `story.md` accuracy | Watch | Backend has 49 module stories versus 50 frontend stories; the mismatch is `clipboard-manager`, which is frontend local-only and has no backend module story. | Add an explicit "local-only/no backend story required" convention, or add a backend stub story for local-only completed apps. | Report only. |
| Weekly return value | Watch | Backend stories describe purpose, data model, API, and implementation status, but not a uniform weekly-return-value field. | Add the field to the backend story template where an app has backend ownership. | Report only. |
| Developer experience | Watch | `app/main.py` manually imports and registers each backend router; newer modules sometimes use `router.py` plus adapter `routes.py`, while older modules use `routes.py` directly. | Pick one route export convention and add a registry/scaffold check before scaling further. | Report only. |

## Backend Inventory

- Backend module folders with `story.md`: 49.
- Isolated mini-app Alembic configs: 35 plus parent `alembic.ini`.
- Overview metadata files in `app/modules/content/data/overview`: 101.
- Route registration remains explicit in `app/main.py`.
- App #51 freeze observation: no implementation work was performed; this review added documentation only.

## Validation

- `python -m compileall app` passed.
- `alembic current` was not available on PATH in the active shell.
- `python -m alembic current` failed in the active Python 3.14 environment because Alembic was not installed there.
- `.venv\Scripts\python.exe -m alembic current` initially reached Alembic but failed against the current environment database URL because the `sqlite.libsql` SQLAlchemy dialect could not be loaded in this environment.
- `$env:PARENT_DATABASE_URL='sqlite:///./ansiversa_api.db'; .\.venv\Scripts\python.exe -m alembic current` passed and reported `20260628_0001 (head)` for the local parent SQLite database.
- `git diff --check` passed.
