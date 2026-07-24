from __future__ import annotations

from app.modules.astra_ai.contracts import (
    AssistantRequest,
    PlatformAppSummary,
    PlatformContext,
    PlatformRouteSummary,
)
from app.modules.astra_ai.fixtures import PLATFORM_SOURCE_BUNDLE, PlatformSourceBundle


def resolve_platform_context(
    request: AssistantRequest,
    *,
    sources: PlatformSourceBundle = PLATFORM_SOURCE_BUNDLE,
) -> PlatformContext:
    """Resolve bounded platform context from approved platform-owned sources.

    Phase 1 deliberately accepts no database session and no filesystem path.
    Callers may provide a prebuilt approved source bundle for tests or future
    build-time integration, but the resolver never reaches into app databases.
    """

    categories = tuple(sorted({app.category for app in sources.apps}))
    return PlatformContext(
        apps=tuple(
            PlatformAppSummary(
                slug=app.slug,
                name=app.name,
                category=app.category,
                overview_route=app.overview_route,
                explore_route=app.explore_route,
                capabilities=app.capabilities,
            )
            for app in sorted(sources.apps, key=lambda item: item.slug)
        ),
        categories=categories,
        routes=tuple(
            PlatformRouteSummary(route=route.route, label=route.label, public=route.public)
            for route in sorted(sources.routes, key=lambda item: item.route)
        ),
        documentation_sources=sources.documentation_sources,
        knowledge_sources=sources.knowledge_sources,
        authentication_state="authenticated" if request.user_context.is_authenticated else "anonymous",
        authorization_boundary=(
            "authenticated-platform-context"
            if request.user_context.is_authenticated
            else "public-platform-context-only"
        ),
    )
