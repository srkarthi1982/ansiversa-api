from __future__ import annotations

from app.modules.astra_ai.contracts import (
    AssistantRequest,
    PlatformAppSummary,
    PlatformContext,
    PlatformRouteSummary,
)
from app.modules.astra_ai.fixtures import (
    PlatformAppFixture,
    PlatformRouteFixture,
    PlatformSourceBundle,
)
from app.modules.knowledge.registry import KnowledgeRegistry

GOVERNED_KNOWLEDGE_SOURCE = "governed_knowledge_registry"


def build_governed_platform_source_bundle() -> PlatformSourceBundle:
    registry = KnowledgeRegistry.load()
    apps = tuple(
        PlatformAppFixture(
            slug=app["slug"],
            name=app["name"],
            category=app["category"],
            overview_route=app["overviewRoute"],
            explore_route=app["exploreRoute"],
            capabilities=tuple(app.get("currentCapabilities", ())[:12]),
        )
        for app in registry.apps({"public"})
    )
    route_map: dict[str, PlatformRouteFixture] = {}
    for page in registry.pages({"public"}):
        route = page["route"]
        route_map[route] = PlatformRouteFixture(
            route=route,
            label=page.get("name") or route,
            public=True,
        )
    for app in apps:
        route_map.setdefault(
            app.overview_route,
            PlatformRouteFixture(route=app.overview_route, label=app.name, public=True),
        )
        route_map.setdefault(
            app.explore_route,
            PlatformRouteFixture(route=app.explore_route, label=f"{app.name} workflow", public=False),
        )
    return PlatformSourceBundle(
        apps=apps,
        routes=tuple(route_map[route] for route in sorted(route_map)),
        documentation_sources=(
            "app/modules/knowledge/data/ansiversa-knowledge.json",
            "app/modules/knowledge/registry.py",
        ),
        knowledge_sources=(
            GOVERNED_KNOWLEDGE_SOURCE,
            "platform_catalog",
            "route_registry",
            "approved_platform_knowledge",
        ),
    )


def resolve_platform_context(
    request: AssistantRequest,
    *,
    sources: PlatformSourceBundle | None = None,
) -> PlatformContext:
    """Resolve bounded platform context from approved platform-owned sources.

    Phase 1 deliberately accepts no database session and no filesystem path.
    Callers may provide a prebuilt approved source bundle for tests or future
    build-time integration, but the resolver never reaches into app databases.
    """

    resolved_sources = sources or build_governed_platform_source_bundle()
    categories = tuple(sorted({app.category for app in resolved_sources.apps}))
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
            for app in sorted(resolved_sources.apps, key=lambda item: item.slug)
        ),
        categories=categories,
        routes=tuple(
            PlatformRouteSummary(route=route.route, label=route.label, public=route.public)
            for route in sorted(resolved_sources.routes, key=lambda item: item.route)
        ),
        documentation_sources=resolved_sources.documentation_sources,
        knowledge_sources=resolved_sources.knowledge_sources,
        authentication_state="authenticated" if request.user_context.is_authenticated else "anonymous",
        authorization_boundary=(
            "authenticated-platform-context"
            if request.user_context.is_authenticated
            else "public-platform-context-only"
        ),
    )
