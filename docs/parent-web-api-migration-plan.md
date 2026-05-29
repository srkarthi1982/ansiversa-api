# Parent Web API Migration Plan

Date: 2026-05-29

Purpose: map the current parent `web` repo implementation to future `ansiversa-api` endpoints before adding more APIs.

This is a documentation-only inspection pass. Do not remove Astro actions during migration. Treat the parent `web` Astro DB schema as the source of truth until Astra/Karthikeyan approve each API cutover.

## Current API Coverage

`ansiversa-api` currently exposes:

| Area | Endpoint | Status |
| --- | --- | --- |
| Health | `GET /api/v1/health/` | Present |
| Auth status | `GET /api/v1/auth/status/` | Present |
| Auth foundation | `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `GET /api/v1/auth/me` | Partially addressed: model now aligns to parent `Users`/`Roles`; parent cookie/session parity remains deferred |
| Admin foundation | `GET /api/v1/admin/status` | Partially completed with reusable `roleId = 1` admin guard and status verification route; admin CRUD remains deferred |
| Audit foundation | None public | Completed as model/helper foundation with `AuditLogs` table and reusable write helper; audit listing and admin write integration remain deferred |
| Admin categories foundation | `GET/POST/PATCH/DELETE /api/v1/admin/categories...` | Completed as admin categories foundation aligned to parent Astro action behavior for pagination, sorting, status filtering, app counts, validation, duplicate blocking, delete blocking, and audit logging; parent web action remains unchanged |
| Apps catalog | `GET /api/v1/apps/`, `GET /api/v1/apps/{app_key}` | Partially present |
| Categories catalog | `GET /api/v1/categories/`, `GET /api/v1/categories/{category_key_or_slug}` | Partially present |
| Public FAQ foundation | `GET /api/v1/faqs` | Completed as public read foundation with published-only filtering, parent/app scoping, search, and pagination; admin FAQ CRUD remains deferred |
| Notifications foundation | `GET /api/v1/me/notifications`, `GET /api/v1/me/notifications/unread-count`, `PATCH /api/v1/me/notifications/{notification_id}`, `POST /api/v1/me/notifications/mark-all-read` | Completed as protected current-user foundation; webhooks remain deferred |
| Dashboard read foundation | `GET /api/v1/me/dashboard` | Partially completed as protected current-user read API; write APIs, webhooks, and cross-app summaries remain deferred |

Phase 9 correction: the previous lowercase `users`/`full_name`/`is_active` auth mismatch has been corrected in the API model. Auth now uses parent-compatible `Users` and `Roles` tables with `name`, `passwordHash`, `roleId`, and `status`. Parent web cookie/session parity, billing/session claims, and broader protected APIs remain deferred.

## Migration Map

| Web feature | Existing web file/action | Required API endpoint | Auth required | DB tables | Migration priority | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| API health/root | `ansiversa-api/app/main.py`, `app/modules/health/routes.py` | `GET /`, `GET /api/v1/health/` | No | None | Phase A | Already covered in API. Keep as platform checks. |
| Auth status | `ansiversa-api/app/modules/auth/routes.py` | `GET /api/v1/auth/status/` | No | None | Phase A | Already covered as readiness/status only. |
| Register account | `web/src/actions/auth.ts` `auth.register` | `POST /api/v1/auth/register` | No | `Users`, `Roles` | Phase C | API now stores `Users.name`, `passwordHash`, `roleId = 2`, and `status = active`; parent web cookie creation, geo capture, welcome email, and notification remain web-only. |
| Login session | `web/src/actions/auth.ts` `auth.login`; `web/src/lib/auth.ts`; `web/src/middleware.ts` | `POST /api/v1/auth/login`, later `POST /api/v1/auth/session` or cookie bridge | No | `Users` | Phase C | API now authenticates against `Users.passwordHash` and blocks non-`active` status. It still returns bearer JWT only; parent `ans_session` cookie parity remains deferred. |
| Current user | `web/src/middleware.ts`; `web/src/lib/auth.ts`; `ansiversa-api/app/modules/auth/routes.py` `GET /me` | `GET /api/v1/auth/me` | Bearer/cookie | `Users`, `Roles` | Phase C | API `/me` now returns safe parent-compatible fields (`id`, `email`, `name`, `roleId`, `status`, `plan`, `planStatus`, `countryCode`, `regionCode`, `city`, `timezone`, `avatarUrl`, `createdAt`, `updatedAt`). Entitlement joins and parent cookie support remain deferred. |
| Change password | `web/src/actions/auth.ts` `auth.changePassword` | `POST /api/v1/auth/change-password` | Yes | `Users`, `Notifications` | Phase C | Must verify current password, rotate session, send email, create security notification. Keep action until session parity is proven. |
| Request password reset | `web/src/actions/auth.ts` `auth.requestPasswordReset`; `web/src/lib/password-reset.ts`; `web/src/lib/email.ts` | `POST /api/v1/auth/password-reset/request` | No | `Users`, `PasswordResetTokens` | Phase C | Includes rate limit by recent token count and email dispatch. Needs idempotent response to avoid account enumeration. |
| Reset password | `web/src/actions/auth.ts` `auth.resetPassword` | `POST /api/v1/auth/password-reset/confirm` | No | `Users`, `PasswordResetTokens` | Phase C | Must preserve token hashing, expiry, single-use behavior, and transactional update. |
| Public apps discovery | `web/src/actions/apps.ts` `apps.getAll`; `web/src/lib/discoveryAccess.ts` | `GET /api/v1/apps?query=...` | Optional | `Apps`, `Categories` | Phase A | API partially lists apps, but does not yet apply parent discovery grouping, metadata search, optional user-aware visibility/pricing gating, launch action labels, logo fallback, or capability details. |
| Public app detail | `ansiversa-api/app/modules/apps/routes.py` | `GET /api/v1/apps/{app_key}` | No | `Apps` | Phase A | Present. Must confirm whether key-only lookup is enough or slug lookup is needed for clients. |
| Public categories | `ansiversa-api/app/modules/apps/routes.py` | `GET /api/v1/categories/`, `GET /api/v1/categories/{key_or_slug}` | No | `Categories` | Phase A | Present. Parent admin list has counts/filtering that are not public requirements. |
| Favorites list | `web/src/actions/favorites.ts` `favorites.listFavorites` | `GET /api/v1/me/favorites` | Yes | `Favorites`, `Apps` | Phase C | Completed as API foundation with current-user scoping, newest-first sorting, and safe app catalog response fields. Full discovery/pricing gating remains deferred. |
| Add favorite | `web/src/actions/favorites.ts` `favorites.addFavorite` | `POST /api/v1/me/favorites` | Yes | `Favorites`, `Apps` | Phase C | Completed as API foundation: app must exist and satisfy conservative public/live checks; duplicate adds are idempotent. Parent web action remains unchanged. |
| Remove favorite | `web/src/actions/favorites.ts` `favorites.removeFavorite` | `DELETE /api/v1/me/favorites/{app_id}` | Yes | `Favorites` | Phase C | Completed as API foundation with current-user scoping and clean `404` for missing user/app favorite relation. Parent web action remains unchanged. |
| Dashboard summary | `web/src/actions/dashboard.ts` `dashboard.summary`; `web/src/pages/dashboard.astro`; `web/src/dashboard/summaryRegistry.ts` | `GET /api/v1/me/dashboard` | Yes | `Users`, `Favorites`, `Apps`, `Notifications`, `Dashboard` | Phase C | Partially completed as read-only API foundation with current-user scoping, counts, recent apps, dashboard items, newest `lastActivityAt` ordering, and safe `summaryJson` parsing. Parent rendering registry, recommendations parity, webhooks, and cross-app summaries remain deferred. |
| Quiz dashboard proxy | `web/src/actions/quiz.ts` `quiz.fetchDashboardSummary` | Deferred or `GET /api/v1/me/dashboard/apps/quiz` | Yes | `Apps`; remote quiz action | Phase F | Current parent action fetches the quiz app action server-side. Do not centralize until cross-app ownership boundaries are approved. |
| Mini-app activity webhooks | `web/src/pages/api/webhooks/*-activity.json.ts`; `web/src/lib/dashboard.ts` | `POST /api/v1/webhooks/{app_key}/activity` | Shared secret | `Dashboard` | Phase C | Existing app-specific validators cover `quiz`, `resume-builder`, `portfolio-creator`, `flashnote`, and `study-planner`. A generic endpoint is tempting but risky; keep per-app schemas or module validators. |
| Notifications list | `web/src/actions/notifications.ts` `notifications.listNotifications` | `GET /api/v1/me/notifications` | Yes | `Notifications` | Phase C | Completed as API foundation with current-user scoping, newest-first sorting, safe response fields, and default limit 50. Parent web action remains unchanged. |
| Mark notification read | `web/src/actions/notifications.ts` `notifications.markNotificationRead` | `PATCH /api/v1/me/notifications/{id}` | Yes | `Notifications` | Phase C | Completed as API foundation with current-user scoping, read-state update, `readAt` timestamp, and clean `404` for missing/non-owned notifications. |
| Mark all notifications read | `web/src/actions/notifications.ts` `notifications.markAllNotificationsRead` | `POST /api/v1/me/notifications/mark-all-read` | Yes | `Notifications` | Phase C | Completed as API foundation with unread-only bulk update and affected count response. |
| Unread notification count | `web/src/pages/api/notifications/unread-count.ts`; `web/src/lib/notifications.ts` | `GET /api/v1/me/notifications/unread-count` | Yes | `Notifications` | Phase C | Completed as API foundation using bearer auth through existing current-user dependency. Parent cookie/session parity remains deferred. |
| Notification webhook | `web/src/pages/api/webhooks/notifications.json.ts`; `web/src/lib/notifications.ts` | `POST /api/v1/webhooks/notifications` | Shared secret | `Notifications` | Phase C | Deferred intentionally. Preserve `X-Ansiversa-Signature` secret validation and app/type normalization when approved later. |
| Public FAQ list | `web/src/actions/faq.ts` `faq.list`; `web/src/pages/api/faqs.json.ts`; `web/src/pages/faq.astro` | `GET /api/v1/faqs?appKey=&q=&page=&pageSize=` | No | `Faqs` | Phase B | Completed as public read foundation with real parent `Faqs` model, published-only filtering, `appKey IS NULL` parent default, app-specific filtering, audience filter, question/answer search, sorting, and pagination metadata. Parent web action remains unchanged. |
| Admin FAQ CRUD | `web/src/actions/faq.ts` `faq.create/update/remove`; `web/src/pages/api/admin/faqs*.ts` | `POST/PATCH/DELETE /api/v1/admin/faqs...` | Admin | `Faqs`, `Users`, `AuditLogs` | Phase D | Admin guard and audit helper now exist, but CRUD remains deferred until the exact admin FAQ contract is approved. |
| Settings profile | `web/src/actions/user.ts` `user.updateProfile`; `web/src/pages/settings.astro` | `GET/PATCH /api/v1/me/profile` | Yes | `Users` | Phase C | Completed as API foundation for safe profile read/update fields (`name`, `countryCode`, `regionCode`, `city`, `timezone`). Parent web action remains unchanged. |
| Settings preferences | `web/src/actions/user.ts` `user.updatePreferences` | `GET/PUT /api/v1/me/preferences` | Yes | `UserPreferences` | Phase C | Completed as API foundation with parent-compatible `UserPreferences` model and create-if-missing/upsert behavior. Parent web action remains unchanged. |
| Account avatar metadata | `web/src/actions/account.ts` `account.updateAvatar/removeAvatar` | `PUT /api/v1/me/avatar`, `DELETE /api/v1/me/avatar` | Yes | `Users` | Phase C | Metadata update is separate from binary upload. Preserve avatar fields and timestamps. |
| Media upload | `web/src/pages/api/media/upload.json.ts`; `web/src/lib/r2.ts` | `POST /api/v1/media/uploads` | Yes | `Users` optional metadata | Phase F | Uses R2 and image processing. Do not migrate until storage ownership, size limits, and client upload strategy are approved. |
| Admin apps list/meta | `web/src/actions/adminApps.ts` `adminApps.list/meta` | `GET /api/v1/admin/apps`, `GET /api/v1/admin/apps/meta` | Admin | `Apps`, `Categories`, `Users` | Phase D | API public apps routes do not replace admin list. Admin route needs filters, pagination, sort, category names, capabilities parsing, and registry normalization. |
| Admin apps create/update/delete | `web/src/actions/adminApps.ts` `adminApps.create/update/delete` | `POST/PATCH/DELETE /api/v1/admin/apps...` | Admin | `Apps`, `Categories`, `AuditLogs` | Phase D | Must preserve validation for key/slug conflicts, URL normalization, launch/visibility/pricing values, capabilities serialization, and audit events. |
| Admin categories list | `web/src/actions/adminCategories.ts` `adminCategories.list` | `GET /api/v1/admin/categories` | Admin | `Categories`, `Apps`, `Users` | Phase D | Completed as API foundation with `page`, `pageSize`, `q`, `status`, `sort`, `dir`, app counts, and web action sort options. Intentional API addition: `sortBy`/`sortDirection` aliases are accepted, and search also covers `description` per Phase 16 requirement. |
| Admin categories create/update/delete | `web/src/actions/adminCategories.ts` `adminCategories.create/update/delete` | `POST/PATCH/DELETE /api/v1/admin/categories...` | Admin | `Categories`, `Apps`, `AuditLogs` | Phase D | Completed as API foundation with `cat_` id validation, key/slug normalization, duplicate blocking, `updatedAt` updates, app-reference delete blocking, and audit actions (`admin.categories.create/update/status/delete`). Parent web action remains unchanged. |
| Admin users list/create/update/delete | `web/src/actions/adminUsers.ts`; `web/src/pages/admin/users.astro` | `GET/POST/PATCH/DELETE /api/v1/admin/users...` | Admin | `Users`, `Roles`, `AuditLogs` | Phase D | Auth model mismatch is addressed, but admin dependencies, role checks, location fields response design, and audit logging are still required before admin user APIs. |
| Admin roles CRUD | `web/src/actions/adminRoles.ts`; `web/src/pages/admin/roles.astro` | `GET/POST/PATCH/DELETE /api/v1/admin/roles...` | Admin | `Roles`, `Users`, `AuditLogs` | Phase D | Requires role/permission model in API. Preserve permission JSON contract. |
| Admin permissions dictionary | `web/src/lib/permissionsRegistry.ts`; `web/src/pages/admin/permissions.astro` | `GET /api/v1/admin/permissions` | Admin | None or `Roles` | Phase D | Mostly static registry today. Can be API-backed after roles are migrated. |
| Admin audit logs | `web/src/actions/adminAuditLogs.ts`; `web/src/lib/auditLog.ts` | `GET /api/v1/admin/audit-logs` | Admin | `AuditLogs`, `Users` | Phase D | Needed before admin writes move, because write endpoints must log centrally. |
| Stripe checkout | `web/src/actions/payments.ts` `payments.createCheckoutSession`; `web/src/lib/stripe.ts` | `POST /api/v1/billing/checkout-sessions` | Yes | `Users` | Phase E | Freeze-sensitive. Must preserve TEST-mode verified behavior and parent URLs. Do not add new billing features. |
| Stripe billing portal | `web/src/actions/payments.ts` `payments.createBillingPortalSession` | `POST /api/v1/billing/portal-sessions` | Yes | `Users` | Phase E | Requires customer creation/lookup and return URL parity. |
| Billing session refresh | `web/src/actions/payments.ts` `payments.refreshSession`; `web/src/lib/subscriptions.ts` | `POST /api/v1/billing/session-refresh` or keep in web | Yes | `Users`, `PaymentsSubscriptions` | Phase E | Tightly coupled to parent cookie claims. Likely stays in web until cookie/session strategy is finalized. |
| Stripe webhook | `web/src/pages/api/stripe/webhook.ts` | `POST /api/v1/billing/stripe/webhook` | Stripe signature | `Users`, `PaymentsSubscriptions`, `PaymentsEvents` | Phase E | Must preserve idempotent event storage, subscription upsert, customer/email linking, and cancel-at-period-end fields. |
| AI gateway ping/suggest | `web/src/pages/api/ai/ping.json.ts`, `web/src/pages/api/ai/suggest.json.ts`; `web/src/lib/ai/*` | `GET /api/v1/ai/ping`, `POST /api/v1/ai/suggest` | Suggest: yes | None, rate limit memory today | Phase F | Rate limiting is in-memory and feature allowlist is parent-owned. Defer until API auth/session and production rate limiting are designed. |
| Contact/email dispatch | `web/src/actions/contact.ts`; `web/src/pages/api/email/send.ts`; `web/src/lib/email.ts` | `POST /api/v1/contact` and/or `POST /api/v1/email/send` | Mixed | None | Phase F | Email webhook secrets and anti-abuse/rate limits need review before externalizing. |
| Fortune actions | `web/src/actions/fortune.ts` | Keep out of parent migration for now | Mixed | `FortuneSessions`, `FortuneFavorites` | Phase F | This is app/domain logic living in parent DB today. Needs ownership decision before API migration. |

## Phase A: Already Partially Covered

- Health/root: `GET /`, `GET /api/v1/health/`.
- Auth status: `GET /api/v1/auth/status/`.
- Apps catalog read: `GET /api/v1/apps/`, `GET /api/v1/apps/{app_key}`.
- Categories catalog read: `GET /api/v1/categories/`, `GET /api/v1/categories/{category_key_or_slug}`.

Before expanding Phase A, close the catalog parity gaps: optional query search, category grouping, discovery gating, launch action metadata, `logoKey` fallback, capabilities details, and slug lookup.

## Phase B: Safe Public APIs

- Public FAQ list foundation completed: `GET /api/v1/faqs`.
- Possibly public app/category reads after Phase A parity is finished.

Safe does not mean schema-free. Add API models only after matching the parent `Faqs`, `Apps`, and `Categories` table names/fields.

## Phase C: Protected User APIs

- Current user/session shape.
- Profile and preferences foundation completed; avatar metadata remains pending.
- Favorites list/add/remove foundation completed.
- Notifications list/read/unread count foundation completed; notification webhooks remain deferred.
- Dashboard read foundation partially completed; dashboard writes, activity webhooks, recommendations parity, and cross-app summary fetching remain deferred.
- Parent notification and activity webhooks authenticated by shared secret.
- Password change/reset flows.

Blocker update: API auth now uses parent `Users` and `Roles`; profile/preferences, favorites, notifications, and dashboard read foundations exist under `/api/v1/me`. Cookie/bearer strategy, entitlement claims, advanced discovery/pricing gating, dashboard write/webhook flows, cross-app dashboard aggregation, notification webhook processing, and avatar uploads still need approval before moving.

## Phase D: Admin APIs

- Admin foundation partially completed: `require_admin_user` checks active authenticated users and allows `roleId = 1`; `/api/v1/admin/status` exists for verification only.
- Audit logging foundation completed before admin writes: parent-compatible `AuditLogs` model/migration and reusable `write_audit_log(...)` helper exist.
- Admin categories foundation completed with parity to `adminCategories` Astro actions where applicable. API search additionally includes `description` to satisfy the Phase 16 API contract.
- Admin apps registry CRUD.
- Admin categories CRUD.
- Admin users CRUD.
- Admin roles CRUD.
- Permissions dictionary.
- Admin FAQ CRUD.
- Audit log listing and central audit write helper.

Admin migration now has the shared admin dependency and audit logging foundation. Do not migrate write endpoints before each admin module contract is approved.

## Phase E: Billing/Payment APIs

- Checkout session creation.
- Billing portal session creation.
- Stripe webhook.
- Subscription/session refresh.

Billing is in freeze. Only migrate after Astra/Karthikeyan approve the exact contract. Preserve TEST-mode behavior, idempotency, `PaymentsEvents`, `PaymentsSubscriptions`, and parent session refresh semantics.

## Phase F: Deferred/Risky APIs

- AI Gateway.
- Media/R2 upload.
- Contact/email dispatch.
- Fortune domain actions.
- Cross-app dashboard summary proxying, especially `quiz.fetchDashboardSummary`.
- Generic mini-app activity webhook abstraction.

These areas either touch external services, need rate limiting/storage ownership decisions, or cross app database boundaries. Keep them in web until contracts are explicit.

## Recommended Implementation Order

1. Finish parent session/cookie strategy design without changing web runtime.
2. Finish public catalog parity in the API while keeping Astro actions as callers/compatibility layer.
3. Add public FAQ read API.
4. Add the next approved protected user API only after auth/profile/favorites/notifications contracts are accepted.
5. Expand dashboard only after write/webhook contracts and cross-app ownership boundaries are approved.
6. Add approved admin read APIs, then admin write APIs only with explicit contracts and audit logging.
7. Treat billing as a separate approved freeze task.

## Verification Notes

- Phase 10 added protected profile/preferences runtime endpoints in `ansiversa-api`.
- Phase 10 did not modify the parent `web` repo.
- Phase 12 added protected notifications runtime endpoints in `ansiversa-api`.
- Phase 13 added the protected read-only dashboard foundation in `ansiversa-api`.
- Phase 14 added the public read-only FAQ foundation in `ansiversa-api`.
- Phase 15 added reusable admin guard/status verification plus `AuditLogs` model/helper foundation in `ansiversa-api`.
- Phase 16 added admin categories list/create/update/delete foundation in `ansiversa-api`.
- Admin Apps, admin users, admin roles, admin FAQ CRUD, audit log listing, permissions registry, dashboard write APIs, dashboard/activity webhooks, cross-app summaries, notification webhooks, and billing APIs remain intentionally deferred.
