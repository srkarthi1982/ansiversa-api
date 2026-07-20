# Shared Notifications

`Notifications` is parent-platform infrastructure and the only notification persistence model. Records belong to one authenticated `Users.id`. List, count, read-one, and read-all operations always scope by that owner; missing and cross-account IDs both return a safe not-found result.

The API exposes bounded types (`info`, `reminder`, `due_soon`, `overdue`, `success`, `warning`, `system`) and never returns raw `metadataJson`. The service resolves approved active/public apps and emits actions only for canonical parent routes or routes beneath the declared source app slug. External, protocol-relative, malformed, traversal, query, and fragment routes are rejected or omitted.

Future approved apps call `create_notification(db, user_id=..., type=..., title=..., message=..., source_app_slug=..., action_route=..., action_label=..., metadata=...)`. No unrestricted publish endpoint exists. Tests use direct database setup; no fake production records or development seed endpoint are included.

Phase 1 supports in-app notifications only. Push, email, SMS, recurring scheduling, marketing, broadcasting, permanent analytics, and service-worker subscriptions are deferred.
