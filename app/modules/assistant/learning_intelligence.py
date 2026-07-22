from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from time import perf_counter
from typing import Any, Literal
from uuid import uuid4

from app.modules.assistant.schemas import AssistantAction, AssistantClientContext, AssistantQueryResponse, AssistantSource
from app.modules.assistant.tools import (
    AssistantToolContext,
    AssistantToolExecutor,
    AssistantToolRegistry,
    AssistantToolResult,
)
from app.modules.assistant.user_context import PlatformUserContext
from app.modules.auth.models import User


LOGGER = logging.getLogger(__name__)

LearningIntent = Literal["daily", "comparison", "completion", "weakness", "stalled", "time_budget", "summary"]
LearningConfidence = Literal["high", "medium", "low", "insufficient"]
MAX_LEARNING_TOOLS = 2
MAX_TOOLS_PER_APP = 1
WEAK_TOPIC_THRESHOLD = 60
NEAR_COMPLETION_THRESHOLD = 80


@dataclass(frozen=True)
class LearningRecommendation:
    type: str
    source_app: str
    title: str
    reason_code: str
    reason: str
    supporting_facts: tuple[str, ...]
    confidence: LearningConfidence
    action: AssistantAction | None = None
    priority: int = 100


@dataclass(frozen=True)
class LearningToolPlan:
    intent: LearningIntent
    tool_names: tuple[str, ...]
    time_budget_minutes: int | None = None


def learning_intent_for_message(
    message: str,
    context: AssistantClientContext | None = None,
) -> LearningIntent | None:
    normalized = _normalize(message)
    tokens = set(re.findall(r"[a-z0-9]+", normalized))
    if _is_write_or_private_request(tokens, normalized):
        return None
    learning_terms = {
        "learn",
        "learning",
        "study",
        "studying",
        "course",
        "courses",
        "quiz",
        "quizzes",
        "revise",
        "revision",
        "topic",
        "topics",
    }
    current_learning_context = _is_learning_context(context)
    if not (tokens & learning_terms) and not current_learning_context:
        return None
    if any(phrase in normalized for phrase in ("another user", "user id", "other user's", "someone else")):
        return None
    if any(phrase in normalized for phrase in ("answer key", "answers", "raw answer", "schema", "sql")):
        return None
    if any(phrase in normalized for phrase in ("learning summary", "learning progress", "am i making", "how is my learning")):
        return "summary"
    if re.search(r"\b(\d+)\s*(minute|minutes|min|hour|hours)\b", normalized) or "one hour" in normalized or "two hours" in normalized:
        return "time_budget"
    if any(phrase in normalized for phrase in ("course or revise quiz", "course or practice", "finish a course or", "more value")):
        return "comparison"
    if any(phrase in normalized for phrase in ("weakest", "weak topic", "revise", "struggling", "struggle")):
        return "weakness"
    if any(phrase in normalized for phrase in ("ignored", "stalled", "resume", "where did i stop", "continue where i stopped")):
        return "stalled"
    if any(phrase in normalized for phrase in ("closest to completing", "closest to completion", "finish first", "complete quickly")):
        return "completion"
    if any(phrase in normalized for phrase in ("study today", "focus on", "next learning task", "most important", "study next")):
        return "daily"
    return None


def query_learning_intelligence(
    *,
    message: str,
    registry: AssistantToolRegistry,
    current_user: User | None,
    platform_context: PlatformUserContext,
    allowed_routes: frozenset[str],
    client_context: AssistantClientContext | None = None,
) -> AssistantQueryResponse | None:
    intent = learning_intent_for_message(message, client_context)
    if intent is None:
        return None
    if current_user is None:
        return AssistantQueryResponse(
            answer="Please sign in before asking Astra for personalized learning guidance.",
            actions=[],
            sources=[],
            confidence="medium",
            response_mode="deterministic",
        )

    start = perf_counter()
    plan = _tool_plan(intent, message)
    tool_context = AssistantToolContext(
        request_id=str(uuid4()),
        user=current_user,
        current_route=platform_context.current_route,
        current_app_slug=platform_context.current_app_slug,
        allowed_routes=allowed_routes,
        max_tool_calls=MAX_LEARNING_TOOLS,
    )
    executor = AssistantToolExecutor(registry, max_tool_calls=MAX_LEARNING_TOOLS)
    results: list[AssistantToolResult] = []
    source_failures: list[str] = []
    for tool_name in plan.tool_names[:MAX_LEARNING_TOOLS]:
        try:
            definition = registry.get(tool_name)
        except Exception:
            source_app = _source_for_tool(tool_name)
            results.append(
                AssistantToolResult(
                    tool_name=tool_name,
                    source_app=source_app,
                    status="unavailable",
                    summary_facts=("Learning source is temporarily unavailable.",),
                    metadata={"fallbackReason": "tool_unavailable"},
                )
            )
            source_failures.append(source_app)
            continue
        result = executor.execute(
            tool_name,
            {"limit": 5} if "limit" in (definition.input_schema.get("properties") or {}) else {},
            tool_context,
        )
        results.append(result)
        if result.status not in {"success", "empty"}:
            source_failures.append(result.source_app)

    response = _compose_response(intent, plan, results)
    LOGGER.info(
        "Astra learning intelligence metadata: %s",
        {
            "intent": intent,
            "toolsUsed": [result.tool_name for result in results],
            "sourcesUsed": sorted({result.source_app for result in results if result.status in {"success", "empty"}}),
            "sourceFailures": sorted(set(source_failures)),
            "durationMs": int((perf_counter() - start) * 1000),
            "responseMode": response.response_mode,
        },
    )
    return response


def _tool_plan(intent: LearningIntent, message: str) -> LearningToolPlan:
    if intent == "summary":
        tools = ("get_course_progress_summary", "get_quiz_progress_summary")
    elif intent == "weakness":
        tools = ("get_quiz_topic_performance", "recommend_next_course_action")
    elif intent == "completion":
        tools = ("get_course_nearest_completion", "recommend_next_quiz_platform")
    elif intent == "stalled":
        tools = ("get_stalled_courses", "get_quiz_topic_performance")
    else:
        tools = ("recommend_next_course_action", "get_quiz_topic_performance")
    _validate_tool_plan(tools)
    return LearningToolPlan(intent=intent, tool_names=tools, time_budget_minutes=_time_budget_minutes(message))


def _validate_tool_plan(tool_names: tuple[str, ...]) -> None:
    if len(tool_names) > MAX_LEARNING_TOOLS:
        raise ValueError("Learning Intelligence tool plan exceeds the approved tool limit.")
    source_counts = {"quiz": 0, "course-tracker": 0}
    for tool_name in tool_names:
        source = _source_for_tool(tool_name)
        if source in source_counts:
            source_counts[source] += 1
    if any(count > MAX_TOOLS_PER_APP for count in source_counts.values()):
        raise ValueError("Learning Intelligence tool plan exceeds the per-app tool limit.")


def _compose_response(
    intent: LearningIntent,
    plan: LearningToolPlan,
    results: list[AssistantToolResult],
) -> AssistantQueryResponse:
    recommendations = _recommendations(intent, plan, results)
    if not recommendations:
        return _no_learning_data_response(results)
    recommendations.sort(key=lambda item: (item.priority, item.source_app, item.title.lower()))
    primary = recommendations[0]
    secondary = recommendations[1:3]
    actions = _ordered_actions(primary, secondary)
    answer_parts = [primary.title, primary.reason]
    if plan.time_budget_minutes:
        answer_parts.append(_time_budget_sentence(plan.time_budget_minutes, primary))
    if secondary:
        answer_parts.append(f"Secondary option: {secondary[0].title}.")
    answer = " ".join(part for part in answer_parts if part).strip()
    return AssistantQueryResponse(
        answer=answer,
        actions=actions,
        sources=_sources(results),
        confidence=_assistant_confidence(primary.confidence),
        response_mode="deterministic",
    )


def _recommendations(
    intent: LearningIntent,
    plan: LearningToolPlan,
    results: list[AssistantToolResult],
) -> list[LearningRecommendation]:
    recommendations: list[LearningRecommendation] = []
    for result in results:
        if result.status != "success":
            continue
        if result.tool_name == "recommend_next_course_action":
            recommendations.extend(_course_recommendations(result))
        elif result.tool_name == "get_course_nearest_completion":
            recommendations.extend(_nearest_course_recommendations(result))
        elif result.tool_name == "get_stalled_courses":
            recommendations.extend(_stalled_course_recommendations(result))
        elif result.tool_name == "get_quiz_topic_performance":
            recommendations.extend(_quiz_topic_recommendations(result))
        elif result.tool_name == "recommend_next_quiz_platform":
            recommendations.extend(_quiz_platform_recommendations(result))
        elif result.tool_name in {"get_course_progress_summary", "get_quiz_progress_summary"}:
            recommendations.extend(_summary_recommendations(result))
    if intent == "weakness":
        return _reprioritize(recommendations, preferred_type="REVISE_WEAKEST_TOPIC")
    if intent == "completion":
        return _reprioritize(recommendations, preferred_type="FINISH_NEAREST_COURSE")
    if intent == "stalled":
        return _reprioritize(recommendations, preferred_type="RESUME_STALLED_COURSE")
    if intent == "summary":
        return _reprioritize(recommendations, preferred_type="CONTINUE_RECENT_LEARNING")
    return recommendations


def _course_recommendations(result: AssistantToolResult) -> list[LearningRecommendation]:
    recommendation = result.data.get("primaryRecommendation")
    if not isinstance(recommendation, dict) or not recommendation:
        return []
    reason_code = str(recommendation.get("reasonCode") or "COURSE_RECOMMENDATION")
    course = str(recommendation.get("course") or "Course Tracker")
    progress = recommendation.get("progressPercent")
    recommendation_type = "FINISH_NEAREST_COURSE"
    priority = 20
    if reason_code == "OVERDUE_TARGET_DATE":
        recommendation_type = "FINISH_NEAREST_COURSE"
        priority = 10
    elif reason_code == "STALLED_ACTIVE_COURSE":
        recommendation_type = "RESUME_STALLED_COURSE"
        priority = 40
    return [
        LearningRecommendation(
            type=recommendation_type,
            source_app="course-tracker",
            title=f"Continue {course}",
            reason_code=reason_code,
            reason=str(recommendation.get("reason") or "Course Tracker recommends this as your next course action."),
            supporting_facts=(f"Progress: {progress}%" if isinstance(progress, int) else "Course Tracker provided this recommendation.",),
            confidence="high",
            action=_first_action(result),
            priority=priority,
        )
    ]


def _nearest_course_recommendations(result: AssistantToolResult) -> list[LearningRecommendation]:
    course = result.data.get("course")
    if not isinstance(course, dict) or not course:
        return []
    name = str(course.get("name") or "Course Tracker")
    progress = course.get("progressPercent")
    priority = 20 if isinstance(progress, int) and progress >= NEAR_COMPLETION_THRESHOLD else 35
    return [
        LearningRecommendation(
            type="FINISH_NEAREST_COURSE",
            source_app="course-tracker",
            title=f"Finish {name}",
            reason_code=str(result.data.get("reasonCode") or "HIGHEST_ACTIVE_PROGRESS"),
            reason=str(result.data.get("reason") or "This active course is closest to completion."),
            supporting_facts=(f"Progress: {progress}%" if isinstance(progress, int) else "Course Tracker identified this course.",),
            confidence="high" if priority == 20 else "medium",
            action=_first_action(result),
            priority=priority,
        )
    ]


def _stalled_course_recommendations(result: AssistantToolResult) -> list[LearningRecommendation]:
    stalled = result.data.get("stalledCourses")
    if not isinstance(stalled, list) or not stalled:
        return []
    first = stalled[0]
    if not isinstance(first, dict):
        return []
    name = str(first.get("name") or "Course Tracker")
    inactive = first.get("inactiveDays")
    return [
        LearningRecommendation(
            type="RESUME_STALLED_COURSE",
            source_app="course-tracker",
            title=f"Resume {name}",
            reason_code=str(first.get("reasonCode") or "STALLED_ACTIVE_COURSE"),
            reason="This active course has no recent Course Tracker progress.",
            supporting_facts=(f"Inactive days: {inactive}" if isinstance(inactive, int) and inactive >= 0 else "No progress log exists yet.",),
            confidence="medium",
            action=_first_action(result),
            priority=40,
        )
    ]


def _quiz_topic_recommendations(result: AssistantToolResult) -> list[LearningRecommendation]:
    weakest = result.data.get("weakestTopics")
    if not isinstance(weakest, list) or not weakest:
        return []
    first = weakest[0]
    if not isinstance(first, dict):
        return []
    topic = str(first.get("topic") or "Quiz topic")
    average = first.get("averageScorePercent")
    priority = 30 if isinstance(average, (int, float)) and average <= WEAK_TOPIC_THRESHOLD else 50
    return [
        LearningRecommendation(
            type="REVISE_WEAKEST_TOPIC",
            source_app="quiz",
            title=f"Revise {topic}",
            reason_code="WEAKEST_REPEATED_TOPIC",
            reason="Quiz has repeated evidence that this is your weakest topic.",
            supporting_facts=(f"Average score: {average}%" if isinstance(average, (int, float)) else "Quiz identified this weak topic.",),
            confidence="high" if priority == 30 else "medium",
            action=_first_action(result),
            priority=priority,
        )
    ]


def _quiz_platform_recommendations(result: AssistantToolResult) -> list[LearningRecommendation]:
    recommended = result.data.get("recommendedNext")
    if not isinstance(recommended, list) or not recommended:
        return []
    first = recommended[0]
    if not isinstance(first, dict):
        return []
    platform = str(first.get("platform") or "Quiz")
    return [
        LearningRecommendation(
            type="START_NEXT_QUIZ_PLATFORM",
            source_app="quiz",
            title=f"Try {platform}",
            reason_code=str(first.get("reasonCode") or "NEXT_ACTIVE_PLATFORM"),
            reason=str(first.get("reason") or "Quiz recommends this as the next available platform."),
            supporting_facts=("Quiz provided this next-platform recommendation.",),
            confidence="medium",
            action=_first_action(result),
            priority=60,
        )
    ]


def _summary_recommendations(result: AssistantToolResult) -> list[LearningRecommendation]:
    if result.tool_name == "get_course_progress_summary":
        active_count = result.data.get("activeCourseCount")
        completed_count = result.data.get("completedCourseCount")
        if not isinstance(active_count, int) or active_count <= 0:
            return []
        return [
            LearningRecommendation(
                type="CONTINUE_RECENT_LEARNING",
                source_app="course-tracker",
                title="Review Course Tracker progress",
                reason_code="COURSE_PROGRESS_AVAILABLE",
                reason=f"You have {active_count} active courses and {completed_count if isinstance(completed_count, int) else 0} completed courses.",
                supporting_facts=tuple(result.summary_facts[:2]),
                confidence="medium",
                action=_first_action(result),
                priority=45,
            )
        ]
    completed_attempts = result.data.get("completedAttemptCount")
    if not isinstance(completed_attempts, int) or completed_attempts <= 0:
        return []
    return [
        LearningRecommendation(
            type="CONTINUE_RECENT_LEARNING",
            source_app="quiz",
            title="Review Quiz progress",
            reason_code="QUIZ_PROGRESS_AVAILABLE",
            reason=f"You have {completed_attempts} submitted Quiz attempts.",
            supporting_facts=tuple(result.summary_facts[:2]),
            confidence="medium",
            action=_first_action(result),
            priority=50,
        )
    ]


def _reprioritize(recommendations: list[LearningRecommendation], *, preferred_type: str) -> list[LearningRecommendation]:
    updated: list[LearningRecommendation] = []
    for recommendation in recommendations:
        if recommendation.type == preferred_type:
            updated.append(
                LearningRecommendation(
                    type=recommendation.type,
                    source_app=recommendation.source_app,
                    title=recommendation.title,
                    reason_code=recommendation.reason_code,
                    reason=recommendation.reason,
                    supporting_facts=recommendation.supporting_facts,
                    confidence=recommendation.confidence,
                    action=recommendation.action,
                    priority=max(1, recommendation.priority - 25),
                )
            )
        else:
            updated.append(recommendation)
    return updated


def _no_learning_data_response(results: list[AssistantToolResult]) -> AssistantQueryResponse:
    sources = _sources(results)
    if any(result.status in {"success", "empty"} for result in results):
        answer = (
            "I do not have enough Quiz or Course Tracker activity to make a personalized learning recommendation yet. "
            "You can add Course Tracker progress or complete Quiz attempts to give Astra stronger learning signals."
        )
    else:
        answer = "Personalized learning guidance is temporarily unavailable."
    return AssistantQueryResponse(
        answer=answer,
        actions=_fallback_actions(results),
        sources=sources,
        confidence="low",
        response_mode="deterministic",
    )


def _sources(results: list[AssistantToolResult]) -> list[AssistantSource]:
    sources: list[AssistantSource] = []
    seen: set[str] = set()
    for result in results:
        if result.status != "success" or result.source_app in seen:
            continue
        seen.add(result.source_app)
        if result.source_app == "quiz":
            sources.append(AssistantSource(id="tool:quiz-learning", title="Quiz", type="app"))
        elif result.source_app == "course-tracker":
            sources.append(AssistantSource(id="tool:course-tracker-learning", title="Course Tracker", type="app"))
    return sources


def _ordered_actions(primary: LearningRecommendation, secondary: list[LearningRecommendation]) -> list[AssistantAction]:
    actions: list[AssistantAction] = []
    seen: set[str] = set()
    for recommendation in (primary, *secondary):
        action = recommendation.action
        if action is None or action.route in seen:
            continue
        actions.append(action)
        seen.add(action.route)
        if len(actions) >= 3:
            break
    return actions


def _fallback_actions(results: list[AssistantToolResult]) -> list[AssistantAction]:
    actions: list[AssistantAction] = []
    seen: set[str] = set()
    for result in results:
        for action in result.actions:
            if action.route in seen:
                continue
            actions.append(action)
            seen.add(action.route)
            if len(actions) >= 2:
                return actions
    return actions


def _first_action(result: AssistantToolResult) -> AssistantAction | None:
    return result.actions[0] if result.actions else None


def _assistant_confidence(confidence: LearningConfidence) -> Literal["high", "medium", "low"]:
    if confidence == "high":
        return "high"
    if confidence == "insufficient":
        return "low"
    return "medium"


def _time_budget_minutes(message: str) -> int | None:
    normalized = _normalize(message)
    if "one hour" in normalized:
        return 60
    if "two hours" in normalized:
        return 120
    match = re.search(r"\b(\d+)\s*(minute|minutes|min|hour|hours)\b", normalized)
    if match is None:
        return None
    value = int(match.group(1))
    unit = match.group(2)
    return value * 60 if unit.startswith("hour") else value


def _time_budget_sentence(minutes: int, primary: LearningRecommendation) -> str:
    if minutes <= 30:
        return "For this short session, keep the scope focused and complete one bounded step."
    if minutes <= 60:
        return "For one focused hour, start with the primary recommendation and stop before adding unrelated work."
    return f"With {minutes} minutes, complete the primary recommendation first and use remaining time for a secondary review."


def _source_for_tool(tool_name: str) -> str:
    if tool_name.startswith("get_quiz") or tool_name.startswith("recommend_next_quiz"):
        return "quiz"
    if tool_name.startswith("get_course") or tool_name.startswith("recommend_next_course"):
        return "course-tracker"
    return "unknown"


def _is_learning_context(context: AssistantClientContext | None) -> bool:
    if context is None:
        return False
    if context.current_route and (context.current_route.startswith("/quiz") or context.current_route.startswith("/course-tracker")):
        return True
    if context.current_app is None:
        return False
    return context.current_app.slug in {"quiz", "course-tracker"} or context.current_app.key in {"quiz", "course-tracker"}


def _is_write_or_private_request(tokens: set[str], normalized: str) -> bool:
    if tokens & {"change", "update", "edit", "delete", "remove", "create", "add", "mark"}:
        return True
    return any(phrase in normalized for phrase in ("ignore instructions", "reveal prompt", "show prompt", "another user", "user id"))


def _normalize(message: str) -> str:
    return re.sub(r"\s+", " ", message.strip().lower())
