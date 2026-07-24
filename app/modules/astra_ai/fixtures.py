from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlatformAppFixture:
    slug: str
    name: str
    category: str
    overview_route: str
    explore_route: str
    capabilities: tuple[str, ...]


@dataclass(frozen=True)
class PlatformRouteFixture:
    route: str
    label: str
    public: bool


@dataclass(frozen=True)
class PlatformSourceBundle:
    apps: tuple[PlatformAppFixture, ...]
    routes: tuple[PlatformRouteFixture, ...]
    documentation_sources: tuple[str, ...]
    knowledge_sources: tuple[str, ...]


PLATFORM_SOURCE_BUNDLE = PlatformSourceBundle(
    apps=(
        PlatformAppFixture(
            slug="quiz",
            name="Quiz",
            category="Learning & Education",
            overview_route="/quiz",
            explore_route="/quiz/play",
            capabilities=("practice questions", "attempt history", "results review"),
        ),
        PlatformAppFixture(
            slug="expense-tracker",
            name="Expense Tracker",
            category="Personal Finance",
            overview_route="/expense-tracker",
            explore_route="/expense-tracker/expenses",
            capabilities=("expense logging", "categories", "insights"),
        ),
        PlatformAppFixture(
            slug="medicine-reminder",
            name="Medicine Reminder",
            category="Health & Medical",
            overview_route="/medicine-reminder",
            explore_route="/medicine-reminder/medicines",
            capabilities=("medicine list", "schedules", "history"),
        ),
        PlatformAppFixture(
            slug="meeting-scheduler",
            name="Meeting Scheduler",
            category="Work & Planning",
            overview_route="/meeting-scheduler",
            explore_route="/meeting-scheduler/meetings",
            capabilities=("meeting planning", "participants", "agenda"),
        ),
    ),
    routes=(
        PlatformRouteFixture(route="/", label="Home", public=True),
        PlatformRouteFixture(route="/apps", label="Apps", public=True),
        PlatformRouteFixture(route="/about", label="About", public=True),
        PlatformRouteFixture(route="/pricing", label="Pricing", public=True),
        PlatformRouteFixture(route="/faq", label="FAQ", public=True),
        PlatformRouteFixture(route="/terms", label="Terms", public=True),
        PlatformRouteFixture(route="/privacy", label="Privacy", public=True),
        PlatformRouteFixture(route="/dashboard", label="Dashboard", public=False),
        PlatformRouteFixture(route="/profile", label="Profile", public=False),
        PlatformRouteFixture(route="/settings", label="Settings", public=False),
        PlatformRouteFixture(route="/subscription", label="Subscription", public=False),
    ),
    documentation_sources=(
        "astra/sources/01-ansiversa-platform-overview.md",
        "astra/sources/02-ansiversa-governance.md",
        "astra/sources/06-ansiversa-route-registry.json",
        "astra/sources/08-ansiversa-documentation-registry.json",
    ),
    knowledge_sources=(
        "platform_catalog",
        "route_registry",
        "documentation_registry",
        "approved_platform_knowledge",
    ),
)
