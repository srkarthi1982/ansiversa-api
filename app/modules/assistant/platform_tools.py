from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.modules.assistant.schemas import AssistantAction
from app.modules.assistant.tools import (
    AssistantToolContext,
    AssistantToolDefinition,
    AssistantToolRegistry,
    AssistantToolResult,
)
from app.modules.course_tracker.astra_tools import build_course_tracker_astra_tools
from app.modules.favorites.service import list_user_favorites
from app.modules.quiz.astra_tools import build_quiz_astra_tools


FAVORITES_TOOL_NAME = "get_user_favorites_summary"
FAVORITES_RESULT_LIMIT = 5


def build_assistant_tool_registry(db: Session) -> AssistantToolRegistry:
    registry = AssistantToolRegistry()
    registry.register(get_user_favorites_summary_tool(db), owning_app="platform:favorites")
    for tool in build_quiz_astra_tools():
        registry.register(tool, owning_app="quiz")
    for tool in build_course_tracker_astra_tools():
        registry.register(tool, owning_app="course-tracker")
    return registry


def get_user_favorites_summary_tool(db: Session) -> AssistantToolDefinition:
    return AssistantToolDefinition(
        name=FAVORITES_TOOL_NAME,
        description=(
            "Returns a bounded summary of the authenticated user's favorite "
            "Ansiversa apps."
        ),
        source_app="platform:favorites",
        input_schema={
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": FAVORITES_RESULT_LIMIT,
                },
            },
            "additionalProperties": False,
        },
        output_schema={
            "type": "object",
            "properties": {
                "favoriteCount": {"type": "integer"},
                "favorites": {"type": "array"},
            },
            "required": ["favoriteCount", "favorites"],
            "additionalProperties": False,
        },
        handler=lambda context, arguments: execute_user_favorites_summary(
            db,
            context,
            arguments,
        ),
        requires_authentication=True,
        read_only=True,
        timeout_seconds=2.0,
        visibility="authenticated",
        deterministic_intents=("user_favorites_summary",),
        max_result_items=FAVORITES_RESULT_LIMIT,
        owner_scoped=True,
        permission_scope="owner",
        version="1.0.0",
        enabled=True,
        deprecated=False,
        documentation_path="docs/architecture/astra-tool-framework.md#demonstration-tool",
    )


def execute_user_favorites_summary(
    db: Session,
    context: AssistantToolContext,
    arguments: dict[str, Any],
) -> AssistantToolResult:
    if context.user is None:
        return AssistantToolResult(
            tool_name=FAVORITES_TOOL_NAME,
            source_app="platform:favorites",
            status="denied",
            summary_facts=("Authentication is required.",),
        )

    limit = int(arguments.get("limit") or FAVORITES_RESULT_LIMIT)
    limit = max(1, min(limit, FAVORITES_RESULT_LIMIT))
    favorites = list_user_favorites(db, context.user)
    bounded = favorites[:limit]
    favorite_items: list[dict[str, str]] = []
    actions: list[AssistantAction] = []

    for favorite in bounded:
        app = favorite.app
        route = _approved_app_route(app.slug, context.allowed_routes)
        item = {
            "slug": app.slug,
            "name": app.name,
            "route": route,
        }
        favorite_items.append(item)
        if route in context.allowed_routes and len(actions) < 3:
            actions.append(
                AssistantAction(
                    type="app",
                    label=f"Open {app.name}",
                    route=route,
                )
            )

    count = len(favorites)
    if count == 0:
        facts = ("You do not have favorite apps yet.",)
        status = "empty"
    else:
        displayed = ", ".join(item["name"] for item in favorite_items)
        facts = (
            f"You have {count} favorite app{'s' if count != 1 else ''}.",
            f"Showing {len(favorite_items)} favorite app{'s' if len(favorite_items) != 1 else ''}: {displayed}.",
        )
        status = "success"

    return AssistantToolResult(
        tool_name=FAVORITES_TOOL_NAME,
        source_app="platform:favorites",
        status=status,
        data={
            "favoriteCount": count,
            "favorites": favorite_items,
        },
        summary_facts=facts,
        actions=tuple(actions),
        metadata={
            "resultCount": len(favorite_items),
            "totalCount": count,
            "bounded": True,
        },
    )


def _approved_app_route(slug: str, allowed_routes: frozenset[str]) -> str:
    direct_route = f"/{slug}"
    if direct_route in allowed_routes:
        return direct_route
    prefix = f"/{slug}/"
    for route in sorted(allowed_routes):
        if route.startswith(prefix):
            return route
    return direct_route
