from __future__ import annotations

import json
import re
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.modules.assistant.schemas import AssistantAction
from app.modules.assistant.tools import AssistantToolContext, AssistantToolDefinition, AssistantToolResult
from app.modules.quiz.db import QuizSessionLocal
from app.modules.quiz.models import Platform, QuizAttempt, Result, Roadmap, Subject, Topic


QUIZ_APP_SLUG = "quiz"
QUIZ_RESULT_LIMIT = 5
QUIZ_TOPIC_EVIDENCE_MIN_ATTEMPTS = 2
QuizSessionFactory = Callable[[], Session]


@dataclass(frozen=True)
class QuizResultSummary:
    platform_name: str
    subject_name: str
    topic_name: str
    roadmap_name: str
    score_percent: int
    completed_at: datetime


def build_quiz_astra_tools(
    *,
    session_factory: sessionmaker[Session] | QuizSessionFactory = QuizSessionLocal,
) -> tuple[AssistantToolDefinition, ...]:
    return (
        _tool(
            "get_quiz_progress_summary",
            "Returns a bounded authenticated summary of the user's Quiz activity and scores.",
            ("quiz_progress_summary", "quiz_attempt_count", "quiz_average_score"),
            lambda context, arguments: execute_quiz_progress_summary(context, arguments, session_factory),
            {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
            {
                "type": "object",
                "properties": {
                    "attemptCount": {"type": "integer"},
                    "completedAttemptCount": {"type": "integer"},
                    "averageScorePercent": {"type": "number"},
                    "lastAttemptAt": {"type": "string"},
                    "platformsStarted": {"type": "integer"},
                    "platformsCompleted": {"type": "integer"},
                },
                "required": [
                    "attemptCount",
                    "completedAttemptCount",
                    "averageScorePercent",
                    "lastAttemptAt",
                    "platformsStarted",
                    "platformsCompleted",
                ],
                "additionalProperties": False,
            },
        ),
        _tool(
            "get_completed_quiz_platforms",
            "Returns Quiz platforms where the authenticated user has submitted results.",
            ("completed_quiz_platforms", "quiz_platform_completion"),
            lambda context, arguments: execute_completed_quiz_platforms(context, arguments, session_factory),
            {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
            {
                "type": "object",
                "properties": {
                    "completedPlatforms": {"type": "array"},
                    "completedCount": {"type": "integer"},
                },
                "required": ["completedPlatforms", "completedCount"],
                "additionalProperties": False,
            },
        ),
        _tool(
            "get_recent_quiz_attempts",
            "Returns a bounded list of the authenticated user's recent submitted Quiz attempts.",
            ("recent_quiz_attempts", "latest_quiz_attempt"),
            lambda context, arguments: execute_recent_quiz_attempts(context, arguments, session_factory),
            {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "minimum": 1, "maximum": QUIZ_RESULT_LIMIT},
                },
                "additionalProperties": False,
            },
            {
                "type": "object",
                "properties": {
                    "attempts": {"type": "array"},
                },
                "required": ["attempts"],
                "additionalProperties": False,
            },
        ),
        _tool(
            "get_quiz_topic_performance",
            "Returns strongest and weakest Quiz topic summaries when enough submitted evidence exists.",
            ("quiz_topic_performance", "quiz_weakest_topic", "quiz_strongest_topic", "quiz_revision_topic"),
            lambda context, arguments: execute_quiz_topic_performance(context, arguments, session_factory),
            {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
            {
                "type": "object",
                "properties": {
                    "strongestTopics": {"type": "array"},
                    "weakestTopics": {"type": "array"},
                    "minimumAttemptEvidence": {"type": "integer"},
                },
                "required": ["strongestTopics", "weakestTopics", "minimumAttemptEvidence"],
                "additionalProperties": False,
            },
        ),
        _tool(
            "recommend_next_quiz_platform",
            "Recommends a deterministic next Quiz platform from the user's submitted Quiz progress.",
            ("recommend_next_quiz_platform", "continue_quiz_work"),
            lambda context, arguments: execute_recommend_next_quiz_platform(context, arguments, session_factory),
            {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
            {
                "type": "object",
                "properties": {
                    "confirmedCompleted": {"type": "array"},
                    "recommendedNext": {"type": "array"},
                    "alternatives": {"type": "array"},
                },
                "required": ["confirmedCompleted", "recommendedNext", "alternatives"],
                "additionalProperties": False,
            },
        ),
    )


def execute_quiz_progress_summary(
    context: AssistantToolContext,
    arguments: dict[str, Any],
    session_factory: sessionmaker[Session] | QuizSessionFactory = QuizSessionLocal,
) -> AssistantToolResult:
    _ = arguments
    if context.user is None:
        return _denied_result("get_quiz_progress_summary")
    with session_factory() as db:
        attempt_count = _attempt_count(db, context.user.id)
        result_rows = _result_summaries(db, context.user.id, limit=100)
        completed_count = len(result_rows)
        average = _average_score(result_rows)
        last_attempt_at = _last_attempt_at(db, context.user.id)
        platforms_started = _distinct_attempt_platform_count(db, context.user.id)
        platforms_completed = len({row.platform_name for row in result_rows})

    if attempt_count == 0:
        return AssistantToolResult(
            tool_name="get_quiz_progress_summary",
            source_app=QUIZ_APP_SLUG,
            status="empty",
            data=_progress_data(0, 0, 0.0, "", 0, 0),
            summary_facts=("You have not started Quiz attempts yet.",),
            actions=_quiz_actions(context),
            metadata={"resultCount": 0},
        )
    return AssistantToolResult(
        tool_name="get_quiz_progress_summary",
        source_app=QUIZ_APP_SLUG,
        status="success",
        data=_progress_data(
            attempt_count,
            completed_count,
            average,
            last_attempt_at.isoformat() if last_attempt_at else "",
            platforms_started,
            platforms_completed,
        ),
        summary_facts=(
            f"You have started {attempt_count} Quiz attempt{'s' if attempt_count != 1 else ''}.",
            f"You have completed {completed_count} submitted Quiz attempt{'s' if completed_count != 1 else ''}.",
            f"Your average submitted score is {average:.1f}%.",
        ),
        actions=_quiz_actions(context),
        metadata={"resultCount": 1, "attemptCount": attempt_count},
    )


def execute_completed_quiz_platforms(
    context: AssistantToolContext,
    arguments: dict[str, Any],
    session_factory: sessionmaker[Session] | QuizSessionFactory = QuizSessionLocal,
) -> AssistantToolResult:
    _ = arguments
    if context.user is None:
        return _denied_result("get_completed_quiz_platforms")
    with session_factory() as db:
        rows = _completed_platform_rows(db, context.user.id)
    items = [
        {
            "name": name,
            "completedAt": completed_at.isoformat() if completed_at else "",
            "submittedResultCount": count,
        }
        for name, completed_at, count in rows[:QUIZ_RESULT_LIMIT]
    ]
    if not items:
        facts = ("You do not have submitted Quiz platform results yet.",)
        status = "empty"
    else:
        names = ", ".join(item["name"] for item in items)
        facts = (f"You have submitted results in {len(rows)} Quiz platform{'s' if len(rows) != 1 else ''}: {names}.",)
        status = "success"
    return AssistantToolResult(
        tool_name="get_completed_quiz_platforms",
        source_app=QUIZ_APP_SLUG,
        status=status,
        data={"completedPlatforms": items, "completedCount": len(rows)},
        summary_facts=facts,
        actions=_quiz_actions(context),
        metadata={"resultCount": len(items), "totalCount": len(rows)},
    )


def execute_recent_quiz_attempts(
    context: AssistantToolContext,
    arguments: dict[str, Any],
    session_factory: sessionmaker[Session] | QuizSessionFactory = QuizSessionLocal,
) -> AssistantToolResult:
    if context.user is None:
        return _denied_result("get_recent_quiz_attempts")
    limit = max(1, min(int(arguments.get("limit") or QUIZ_RESULT_LIMIT), QUIZ_RESULT_LIMIT))
    with session_factory() as db:
        rows = _result_summaries(db, context.user.id, limit=limit)
    attempts = [
        {
            "platform": row.platform_name,
            "subject": row.subject_name,
            "topic": row.topic_name,
            "roadmap": row.roadmap_name,
            "scorePercent": row.score_percent,
            "completedAt": row.completed_at.isoformat(),
        }
        for row in rows
    ]
    if not attempts:
        facts = ("You do not have submitted Quiz attempts yet.",)
        status = "empty"
    else:
        latest = attempts[0]
        facts = (
            f"Your latest submitted Quiz attempt was {latest['platform']} / {latest['topic']} with {latest['scorePercent']}%.",
        )
        status = "success"
    return AssistantToolResult(
        tool_name="get_recent_quiz_attempts",
        source_app=QUIZ_APP_SLUG,
        status=status,
        data={"attempts": attempts},
        summary_facts=facts,
        actions=_quiz_actions(context),
        metadata={"resultCount": len(attempts)},
    )


def execute_quiz_topic_performance(
    context: AssistantToolContext,
    arguments: dict[str, Any],
    session_factory: sessionmaker[Session] | QuizSessionFactory = QuizSessionLocal,
) -> AssistantToolResult:
    _ = arguments
    if context.user is None:
        return _denied_result("get_quiz_topic_performance")
    with session_factory() as db:
        rows = _result_summaries(db, context.user.id, limit=100)
    grouped: dict[str, list[int]] = defaultdict(list)
    for row in rows:
        grouped[row.topic_name].append(row.score_percent)
    eligible = [
        {
            "topic": topic,
            "averageScorePercent": round(sum(scores) / len(scores), 1),
            "attemptCount": len(scores),
        }
        for topic, scores in grouped.items()
        if len(scores) >= QUIZ_TOPIC_EVIDENCE_MIN_ATTEMPTS
    ]
    eligible.sort(key=lambda item: (item["averageScorePercent"], item["topic"]))
    weakest = eligible[:3]
    strongest = list(reversed(eligible[-3:]))
    if not eligible:
        facts = ("There is not enough repeated Quiz topic evidence yet to identify strongest or weakest topics.",)
        status = "empty"
    else:
        facts = (
            f"Your strongest Quiz topic is {strongest[0]['topic']} at {strongest[0]['averageScorePercent']}%.",
            f"Your weakest Quiz topic is {weakest[0]['topic']} at {weakest[0]['averageScorePercent']}%.",
        )
        status = "success"
    return AssistantToolResult(
        tool_name="get_quiz_topic_performance",
        source_app=QUIZ_APP_SLUG,
        status=status,
        data={
            "strongestTopics": strongest,
            "weakestTopics": weakest,
            "minimumAttemptEvidence": QUIZ_TOPIC_EVIDENCE_MIN_ATTEMPTS,
        },
        summary_facts=facts,
        actions=_quiz_actions(context),
        metadata={"resultCount": len(strongest) + len(weakest)},
    )


def execute_recommend_next_quiz_platform(
    context: AssistantToolContext,
    arguments: dict[str, Any],
    session_factory: sessionmaker[Session] | QuizSessionFactory = QuizSessionLocal,
) -> AssistantToolResult:
    _ = arguments
    if context.user is None:
        return _denied_result("recommend_next_quiz_platform")
    with session_factory() as db:
        completed = _completed_platform_rows(db, context.user.id)
        all_platforms = list(
            db.execute(select(Platform).where(Platform.is_active.is_(True)).order_by(Platform.id.asc())).scalars().all()
        )
    completed_names = [name for name, _, _ in completed]
    completed_set = set(completed_names)
    recommended = [
        {
            "platform": platform.name,
            "reasonCode": "NEXT_ACTIVE_PLATFORM",
            "reason": "This is an active Quiz platform without a submitted result yet.",
        }
        for platform in all_platforms
        if platform.name not in completed_set
    ][:3]
    alternatives = [
        {
            "platform": name,
            "reasonCode": "CONTINUE_COMPLETED_PLATFORM",
            "reason": "You already have submitted results here and can continue improving the score.",
        }
        for name in completed_names[:2]
    ]
    if recommended:
        facts = (f"Recommended next Quiz platform: {recommended[0]['platform']}.",)
        status = "success"
    elif alternatives:
        facts = (f"You have submitted results for all visible Quiz platforms in this dataset. Continue improving {alternatives[0]['platform']}.",)
        status = "success"
    else:
        facts = ("No active Quiz platform recommendation is available yet.",)
        status = "empty"
    return AssistantToolResult(
        tool_name="recommend_next_quiz_platform",
        source_app=QUIZ_APP_SLUG,
        status=status,
        data={
            "confirmedCompleted": completed_names[:QUIZ_RESULT_LIMIT],
            "recommendedNext": recommended,
            "alternatives": alternatives,
        },
        summary_facts=facts,
        actions=_quiz_actions(context),
        metadata={"resultCount": len(recommended) + len(alternatives)},
    )


def _tool(
    name: str,
    description: str,
    intents: tuple[str, ...],
    handler: Callable[[AssistantToolContext, dict[str, Any]], AssistantToolResult],
    input_schema: dict[str, Any],
    output_schema: dict[str, Any],
) -> AssistantToolDefinition:
    return AssistantToolDefinition(
        name=name,
        description=description,
        source_app=QUIZ_APP_SLUG,
        input_schema=input_schema,
        output_schema=output_schema,
        handler=handler,
        requires_authentication=True,
        read_only=True,
        timeout_seconds=2.0,
        visibility="authenticated",
        deterministic_intents=intents,
        max_result_items=QUIZ_RESULT_LIMIT,
        owner_scoped=True,
        permission_scope="owner",
        version="1.0.0",
        enabled=True,
        deprecated=False,
        documentation_path="app/modules/quiz/astra-ai.md",
    )


def _progress_data(
    attempt_count: int,
    completed_count: int,
    average: float,
    last_attempt_at: str,
    platforms_started: int,
    platforms_completed: int,
) -> dict[str, Any]:
    return {
        "attemptCount": attempt_count,
        "completedAttemptCount": completed_count,
        "averageScorePercent": round(average, 1),
        "lastAttemptAt": last_attempt_at,
        "platformsStarted": platforms_started,
        "platformsCompleted": platforms_completed,
    }


def _denied_result(tool_name: str) -> AssistantToolResult:
    return AssistantToolResult(
        tool_name=tool_name,
        source_app=QUIZ_APP_SLUG,
        status="denied",
        summary_facts=("Authentication is required.",),
    )


def _quiz_actions(context: AssistantToolContext) -> tuple[AssistantAction, ...]:
    route = "/quiz/play" if "/quiz/play" in context.allowed_routes else "/quiz"
    if route not in context.allowed_routes:
        return ()
    return (AssistantAction(type="app", label="Open Quiz", route=route),)


def _attempt_count(db: Session, user_id: str) -> int:
    return int(db.scalar(select(func.count()).select_from(QuizAttempt).where(QuizAttempt.user_id == user_id)) or 0)


def _distinct_attempt_platform_count(db: Session, user_id: str) -> int:
    return int(
        db.scalar(
            select(func.count(func.distinct(QuizAttempt.platform_id))).where(QuizAttempt.user_id == user_id)
        )
        or 0
    )


def _last_attempt_at(db: Session, user_id: str) -> datetime | None:
    return db.scalar(
        select(QuizAttempt.created_at)
        .where(QuizAttempt.user_id == user_id)
        .order_by(QuizAttempt.created_at.desc(), QuizAttempt.id.desc())
        .limit(1)
    )


def _completed_platform_rows(db: Session, user_id: str) -> list[tuple[str, datetime | None, int]]:
    rows = db.execute(
        select(
            Platform.name,
            func.max(Result.created_at).label("completed_at"),
            func.count(Result.id).label("result_count"),
        )
        .join(Result, Result.platform_id == Platform.id)
        .where(Result.user_id == user_id, Platform.is_active.is_(True))
        .group_by(Platform.id, Platform.name)
        .order_by(func.max(Result.created_at).desc(), Platform.name.asc())
    ).all()
    return [(str(name), completed_at, int(count)) for name, completed_at, count in rows]


def _result_summaries(db: Session, user_id: str, *, limit: int) -> list[QuizResultSummary]:
    rows = db.execute(
        select(
            Result.mark,
            Result.responses_json,
            Result.created_at,
            Platform.name.label("platform_name"),
            Subject.name.label("subject_name"),
            Topic.name.label("topic_name"),
            Roadmap.name.label("roadmap_name"),
        )
        .outerjoin(Platform, Platform.id == Result.platform_id)
        .outerjoin(Subject, Subject.id == Result.subject_id)
        .outerjoin(Topic, Topic.id == Result.topic_id)
        .outerjoin(Roadmap, Roadmap.id == Result.roadmap_id)
        .where(Result.user_id == user_id)
        .order_by(Result.created_at.desc(), Result.id.desc())
        .limit(limit)
    ).all()
    summaries: list[QuizResultSummary] = []
    for mark, responses_json, created_at, platform_name, subject_name, topic_name, roadmap_name in rows:
        total = _response_count(responses_json)
        if total <= 0:
            continue
        summaries.append(
            QuizResultSummary(
                platform_name=str(platform_name or "Unknown Platform"),
                subject_name=str(subject_name or "Unknown Subject"),
                topic_name=str(topic_name or "Unknown Topic"),
                roadmap_name=str(roadmap_name or "Unknown Roadmap"),
                score_percent=round((int(mark) / total) * 100),
                completed_at=created_at,
            )
        )
    return summaries


def _average_score(rows: list[QuizResultSummary]) -> float:
    if not rows:
        return 0.0
    return sum(row.score_percent for row in rows) / len(rows)


def _response_count(value: str) -> int:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return 0
    return len(parsed) if isinstance(parsed, list) else 0
