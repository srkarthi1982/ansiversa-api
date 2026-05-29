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
| Auth foundation | `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `GET /api/v1/auth/me` | Present but not equivalent to parent web sessions/schema |
| Apps catalog | `GET /api/v1/apps/`, `GET /api/v1/apps/{app_key}` | Partially present |
| Categories catalog | `GET /api/v1/categories/`, `GET /api/v1/categories/{category_key_or_slug}` | Partially present |

Important mismatch: the API auth module currently uses a lowercase `users` table model with `full_name`/`is_active`, while parent web uses `Users` with `name`, `roleId`, `status`, session cookie claims, Stripe fields, avatar fields, and geo fields. Do not expand auth until the API model is reconciled with the parent schema.

## Migration Map

| Web feature | Existing web file/action | Required API endpoint | Auth required | DB tables | Migration priority | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| API health/root | `ansiversa-api/app/main.py`, `app/modules/health/routes.py` | `GET /`, `GET /api/v1/health/` | No | None | Phase A | Already covered in API. Keep as platform checks. |
| Auth status | `ansiversa-api/app/modules/auth/routes.py` | `GET /api/v1/auth/status/` | No | None | Phase A | Already covered as readiness/status only. |
| Register account | `web/src/actions/auth.ts` `auth.register` | `POST /api/v1/auth/register` | No | `Users`, `Notifications` | Phase C | API has a register endpoint, but it is not parent-equivalent. Parent registration sets `Users.name`, `roleId`, geo fields, JWT cookie, welcome email, and notification. |
| Login session | `web/src/actions/auth.ts` `auth.login`; `web/src/lib/auth.ts`; `web/src/middleware.ts` | `POST /api/v1/auth/login`, later `POST /api/v1/auth/session` or cookie bridge | No | `Users`, `PaymentsSubscriptions` | Phase C | API returns bearer JWT only. Parent web creates `ans_session` cookie with role and billing claims. Cutover requires a deliberate web/mobile session contract. |
| Current user | `web/src/middleware.ts`; `web/src/lib/auth.ts`; `ansiversa-api/app/modules/auth/routes.py` `GET /me` | `GET /api/v1/auth/me` | Bearer/cookie | `Users`, `Roles`, `PaymentsSubscriptions` | Phase C | Existing API `/me` is partial. Parent current-user shape includes role, status, avatar, and entitlement context. |
| Change password | `web/src/actions/auth.ts` `auth.changePassword` | `POST /api/v1/auth/change-password` | Yes | `Users`, `Notifications` | Phase C | Must verify current password, rotate session, send email, create security notification. Keep action until session parity is proven. |
| Request password reset | `web/src/actions/auth.ts` `auth.requestPasswordReset`; `web/src/lib/password-reset.ts`; `web/src/lib/email.ts` | `POST /api/v1/auth/password-reset/request` | No | `Users`, `PasswordResetTokens` | Phase C | Includes rate limit by recent token count and email dispatch. Needs idempotent response to avoid account enumeration. |
| Reset password | `web/src/actions/auth.ts` `auth.resetPassword` | `POST /api/v1/auth/password-reset/confirm` | No | `Users`, `PasswordResetTokens` | Phase C | Must preserve token hashing, expiry, single-use behavior, and transactional update. |
| Public apps discovery | `web/src/actions/apps.ts` `apps.getAll`; `web/src/lib/discoveryAccess.ts` | `GET /api/v1/apps?query=...` | Optional | `Apps`, `Categories` | Phase A | API partially lists apps, but does not yet apply parent discovery grouping, metadata search, optional user-aware visibility/pricing gating, launch action labels, logo fallback, or capability details. |
| Public app detail | `ansiversa-api/app/modules/apps/routes.py` | `GET /api/v1/apps/{app_key}` | No | `Apps` | Phase A | Present. Must confirm whether key-only lookup is enough or slug lookup is needed for clients. |
| Public categories | `ansiversa-api/app/modules/apps/routes.py` | `GET /api/v1/categories/`, `GET /api/v1/categories/{key_or_slug}` | No | `Categories` | Phase A | Present. Parent admin list has counts/filtering that are not public requirements. |
| Favorites list | `web/src/actions/favorites.ts` `favorites.listFavorites` | `GET /api/v1/me/favorites` | Yes | `Favorites`, `Apps` | Phase C | Must reuse discovery gating: hide private/internal apps for non-admins and block pro apps for non-entitled users. |
| Add favorite | `web/src/actions/favorites.ts` `favorites.addFavorite` | `POST /api/v1/me/favorites` | Yes | `Favorites`, `Apps` | Phase C | Current action allows only legacy `Apps.status === "live"`. Future endpoint should reconcile with `launchStatus`/`visibility`/`pricingGate` rules before migration. |
| Remove favorite | `web/src/actions/favorites.ts` `favorites.removeFavorite` | `DELETE /api/v1/me/favorites/{app_id}` | Yes | `Favorites` | Phase C | Straightforward after auth/session dependency is stable. |
| Dashboard summary | `web/src/actions/dashboard.ts` `dashboard.summary`; `web/src/pages/dashboard.astro`; `web/src/dashboard/summaryRegistry.ts` | `GET /api/v1/me/dashboard` | Yes | `Users`, `Favorites`, `Apps`, `Notifications`, `Dashboard` | Phase C | Current dashboard combines favorites, unread notifications, recommendations, and mini-app summary registry rendering. API should return stable data only; rendering registry stays in web/components. |
| Quiz dashboard proxy | `web/src/actions/quiz.ts` `quiz.fetchDashboardSummary` | Deferred or `GET /api/v1/me/dashboard/apps/quiz` | Yes | `Apps`; remote quiz action | Phase F | Current parent action fetches the quiz app action server-side. Do not centralize until cross-app ownership boundaries are approved. |
| Mini-app activity webhooks | `web/src/pages/api/webhooks/*-activity.json.ts`; `web/src/lib/dashboard.ts` | `POST /api/v1/webhooks/{app_key}/activity` | Shared secret | `Dashboard` | Phase C | Existing app-specific validators cover `quiz`, `resume-builder`, `portfolio-creator`, `flashnote`, and `study-planner`. A generic endpoint is tempting but risky; keep per-app schemas or module validators. |
| Notifications list | `web/src/actions/notifications.ts` `notifications.listNotifications` | `GET /api/v1/me/notifications` | Yes | `Notifications` | Phase C | Current action caps at 50 newest. Include pagination before external clients depend on it. |
| Mark notification read | `web/src/actions/notifications.ts` `notifications.markNotificationRead` | `PATCH /api/v1/me/notifications/{id}` | Yes | `Notifications` | Phase C | Must scope update by current user. |
| Mark all notifications read | `web/src/actions/notifications.ts` `notifications.markAllNotificationsRead` | `POST /api/v1/me/notifications/mark-all-read` | Yes | `Notifications` | Phase C | Preserve unread-only update and updated count response. |
| Unread notification count | `web/src/pages/api/notifications/unread-count.ts`; `web/src/lib/notifications.ts` | `GET /api/v1/me/notifications/unread-count` | Yes | `Notifications` | Phase C | Existing route accepts cookie or bearer token for mini-apps. API should preserve bearer support. |
| Notification webhook | `web/src/pages/api/webhooks/notifications.json.ts`; `web/src/lib/notifications.ts` | `POST /api/v1/webhooks/notifications` | Shared secret | `Notifications` | Phase C | Preserve `X-Ansiversa-Signature` secret validation and app/type normalization. |
| Public FAQ list | `web/src/actions/faq.ts` `faq.list`; `web/src/pages/api/faqs.json.ts`; `web/src/pages/faq.astro` | `GET /api/v1/faqs?appKey=&q=&page=&pageSize=` | No | `Faqs` | Phase B | Public read API is safe after schema model is added. Preserve `appKey IS NULL` default for parent FAQ and app-specific filtering. |
| Admin FAQ CRUD | `web/src/actions/faq.ts` `faq.create/update/remove`; `web/src/pages/api/admin/faqs*.ts` | `POST/PATCH/DELETE /api/v1/admin/faqs...` | Admin | `Faqs`, `Users`, `AuditLogs` | Phase D | Requires admin dependency and audit logging first. |
| Settings profile | `web/src/actions/user.ts` `user.updateProfile`; `web/src/pages/settings.astro` | `PATCH /api/v1/me/profile` | Yes | `Users` | Phase C | Simple after parent session/user model parity. |
| Settings preferences | `web/src/actions/user.ts` `user.updatePreferences` | `PUT /api/v1/me/preferences` | Yes | `UserPreferences` | Phase C | Requires `UserPreferences` API model. Upsert behavior must remain. |
| Account avatar metadata | `web/src/actions/account.ts` `account.updateAvatar/removeAvatar` | `PUT /api/v1/me/avatar`, `DELETE /api/v1/me/avatar` | Yes | `Users` | Phase C | Metadata update is separate from binary upload. Preserve avatar fields and timestamps. |
| Media upload | `web/src/pages/api/media/upload.json.ts`; `web/src/lib/r2.ts` | `POST /api/v1/media/uploads` | Yes | `Users` optional metadata | Phase F | Uses R2 and image processing. Do not migrate until storage ownership, size limits, and client upload strategy are approved. |
| Admin apps list/meta | `web/src/actions/adminApps.ts` `adminApps.list/meta` | `GET /api/v1/admin/apps`, `GET /api/v1/admin/apps/meta` | Admin | `Apps`, `Categories`, `Users` | Phase D | API public apps routes do not replace admin list. Admin route needs filters, pagination, sort, category names, capabilities parsing, and registry normalization. |
| Admin apps create/update/delete | `web/src/actions/adminApps.ts` `adminApps.create/update/delete` | `POST/PATCH/DELETE /api/v1/admin/apps...` | Admin | `Apps`, `Categories`, `AuditLogs` | Phase D | Must preserve validation for key/slug conflicts, URL normalization, launch/visibility/pricing values, capabilities serialization, and audit events. |
| Admin categories list | `web/src/actions/adminCategories.ts` `adminCategories.list` | `GET /api/v1/admin/categories` | Admin | `Categories`, `Apps`, `Users` | Phase D | Public categories route is not enough. Admin list includes filters, sorting, pagination, and app counts. |
| Admin categories create/update/delete | `web/src/actions/adminCategories.ts` `adminCategories.create/update/delete` | `POST/PATCH/DELETE /api/v1/admin/categories...` | Admin | `Categories`, `Apps`, `AuditLogs` | Phase D | Delete must block when apps reference the category. Preserve `cat_` id convention unless Astra changes it. |
| Admin users list/create/update/delete | `web/src/actions/adminUsers.ts`; `web/src/pages/admin/users.astro` | `GET/POST/PATCH/DELETE /api/v1/admin/users...` | Admin | `Users`, `Roles`, `AuditLogs` | Phase D | API auth model mismatch blocks this. Parent admin users include role/status/location fields. |
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

- Public FAQ list: `GET /api/v1/faqs`.
- Possibly public app/category reads after Phase A parity is finished.

Safe does not mean schema-free. Add API models only after matching the parent `Faqs`, `Apps`, and `Categories` table names/fields.

## Phase C: Protected User APIs

- Current user/session shape.
- Profile, preferences, avatar metadata.
- Favorites list/add/remove.
- Dashboard data.
- Notifications list/read/unread count.
- Parent notification and activity webhooks authenticated by shared secret.
- Password change/reset flows.

Blocker: API auth must be reconciled with parent `Users`, `Roles`, cookie/bearer strategy, and entitlement claims before these move.

## Phase D: Admin APIs

- Admin apps registry CRUD.
- Admin categories CRUD.
- Admin users CRUD.
- Admin roles CRUD.
- Permissions dictionary.
- Admin FAQ CRUD.
- Audit log listing and central audit write helper.

Admin migration should start with a shared admin dependency and audit logging. Do not migrate write endpoints before audit logging exists in the API.

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

1. Reconcile API parent auth models with the real parent `Users`, `Roles`, and session requirements without changing web runtime.
2. Finish public catalog parity in the API while keeping Astro actions as callers/compatibility layer.
3. Add public FAQ read API.
4. Add protected user read APIs: `/me`, notifications unread count, favorites list.
5. Add dashboard read API after favorites/notifications contracts stabilize.
6. Add admin audit log model/helper, then admin read APIs, then admin write APIs.
7. Treat billing as a separate approved freeze task.

## Verification Notes

- This plan did not add runtime endpoints.
- This plan did not modify the parent `web` repo.
- Required verification for this documentation task: `python -m compileall app`.
