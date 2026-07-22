from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session, sessionmaker

from app.modules.assistant.schemas import AssistantAction
from app.modules.assistant.tools import AssistantToolContext, AssistantToolDefinition, AssistantToolResult
from app.modules.course_tracker.db import CourseTrackerSessionLocal
from app.modules.course_tracker.models import Course, CourseModule, CourseProgressLog
from app.modules.course_tracker.service import (
    COURSE_TRACKER_DUE_SOON_DAYS,
    COURSE_TRACKER_STALLED_DAYS,
    calculate_completion_rate,
)


COURSE_TRACKER_APP_SLUG = "course-tracker"
COURSE_TRACKER_RESULT_LIMIT = 5
CourseTrackerSessionFactory = Callable[[], Session]


@dataclass(frozen=True)
class CourseAstraSummary:
    title: str
    provider: str
    category: str | None
    status: str
    target_date: date | None
    updated_at: datetime
    module_count: int
    completed_module_count: int
    total_minutes: int
    last_progress_date: date | None

    @property
    def progress_percent(self) -> int:
        return calculate_completion_rate(self.module_count, self.completed_module_count)

    @property
    def inactive_days(self) -> int | None:
        if self.last_progress_date is None:
            return None
        return max(0, (date.today() - self.last_progress_date).days)


def build_course_tracker_astra_tools(
    *,
    session_factory: sessionmaker[Session] | CourseTrackerSessionFactory = CourseTrackerSessionLocal,
) -> tuple[AssistantToolDefinition, ...]:
    return (
        _tool(
            "get_course_progress_summary",
            "Returns a bounded authenticated summary of the user's Course Tracker progress.",
            ("course_progress_summary", "course_count_summary", "course_average_progress"),
            lambda context, arguments: execute_course_progress_summary(context, arguments, session_factory),
            _limit_schema(),
            {
                "type": "object",
                "properties": {
                    "courseCount": {"type": "integer"},
                    "activeCourseCount": {"type": "integer"},
                    "pausedCourseCount": {"type": "integer"},
                    "completedCourseCount": {"type": "integer"},
                    "averageProgressPercent": {"type": "number"},
                    "totalMinutes": {"type": "integer"},
                    "lastActivityAt": {"type": "string"},
                },
                "required": [
                    "courseCount",
                    "activeCourseCount",
                    "pausedCourseCount",
                    "completedCourseCount",
                    "averageProgressPercent",
                    "totalMinutes",
                    "lastActivityAt",
                ],
                "additionalProperties": False,
            },
        ),
        _tool(
            "get_active_courses",
            "Returns bounded active Course Tracker courses for the authenticated user.",
            ("active_courses", "current_courses", "unfinished_courses"),
            lambda context, arguments: execute_active_courses(context, arguments, session_factory),
            _limit_schema(),
            {
                "type": "object",
                "properties": {"courses": {"type": "array"}, "activeCount": {"type": "integer"}},
                "required": ["courses", "activeCount"],
                "additionalProperties": False,
            },
        ),
        _tool(
            "get_completed_courses",
            "Returns bounded completed Course Tracker courses for the authenticated user.",
            ("completed_courses", "course_completion_status"),
            lambda context, arguments: execute_completed_courses(context, arguments, session_factory),
            _limit_schema(),
            {
                "type": "object",
                "properties": {"completedCourses": {"type": "array"}, "completedCount": {"type": "integer"}},
                "required": ["completedCourses", "completedCount"],
                "additionalProperties": False,
            },
        ),
        _tool(
            "get_course_nearest_completion",
            "Identifies the active Course Tracker course closest to completion.",
            ("course_nearest_completion", "course_finish_first", "course_least_remaining"),
            lambda context, arguments: execute_course_nearest_completion(context, arguments, session_factory),
            {"type": "object", "properties": {}, "additionalProperties": False},
            {
                "type": "object",
                "properties": {"course": {"type": "object"}, "reasonCode": {"type": "string"}, "reason": {"type": "string"}},
                "required": ["course", "reasonCode", "reason"],
                "additionalProperties": False,
            },
        ),
        _tool(
            "get_stalled_courses",
            "Returns active Course Tracker courses with no recent progress.",
            ("stalled_courses", "ignored_course", "resume_course"),
            lambda context, arguments: execute_stalled_courses(context, arguments, session_factory),
            _limit_schema(),
            {
                "type": "object",
                "properties": {
                    "stalledCourses": {"type": "array"},
                    "stalledCount": {"type": "integer"},
                    "thresholdDays": {"type": "integer"},
                },
                "required": ["stalledCourses", "stalledCount", "thresholdDays"],
                "additionalProperties": False,
            },
        ),
        _tool(
            "get_course_deadline_summary",
            "Returns overdue and due-soon Course Tracker courses using target dates.",
            ("course_deadline_summary", "overdue_course_work", "course_due_soon"),
            lambda context, arguments: execute_course_deadline_summary(context, arguments, session_factory),
            _limit_schema(),
            {
                "type": "object",
                "properties": {
                    "overdueCount": {"type": "integer"},
                    "dueSoonCount": {"type": "integer"},
                    "courses": {"type": "array"},
                    "dueSoonDays": {"type": "integer"},
                },
                "required": ["overdueCount", "dueSoonCount", "courses", "dueSoonDays"],
                "additionalProperties": False,
            },
        ),
        _tool(
            "recommend_next_course_action",
            "Recommends a deterministic next Course Tracker action from real course data.",
            ("recommend_next_course_action", "continue_course_work", "study_next_course"),
            lambda context, arguments: execute_recommend_next_course_action(context, arguments, session_factory),
            {"type": "object", "properties": {}, "additionalProperties": False},
            {
                "type": "object",
                "properties": {
                    "primaryRecommendation": {"type": "object"},
                    "alternatives": {"type": "array"},
                },
                "required": ["primaryRecommendation", "alternatives"],
                "additionalProperties": False,
            },
        ),
    )


def execute_course_progress_summary(
    context: AssistantToolContext,
    arguments: dict[str, Any],
    session_factory: sessionmaker[Session] | CourseTrackerSessionFactory = CourseTrackerSessionLocal,
) -> AssistantToolResult:
    _ = arguments
    if context.user is None:
        return _denied_result("get_course_progress_summary")
    with session_factory() as db:
        courses = _course_summaries(db, context.user.id)

    if not courses:
        return _empty_result("get_course_progress_summary", "You have not added any Course Tracker courses yet.", context)

    active_count = len([course for course in courses if course.status == "active"])
    paused_count = len([course for course in courses if course.status == "paused"])
    completed_count = len([course for course in courses if course.status == "completed"])
    average_progress = round(sum(course.progress_percent for course in courses) / len(courses), 1)
    total_minutes = sum(course.total_minutes for course in courses)
    last_activity = _latest_activity(courses)
    return AssistantToolResult(
        tool_name="get_course_progress_summary",
        source_app=COURSE_TRACKER_APP_SLUG,
        status="success",
        data={
            "courseCount": len(courses),
            "activeCourseCount": active_count,
            "pausedCourseCount": paused_count,
            "completedCourseCount": completed_count,
            "averageProgressPercent": average_progress,
            "totalMinutes": total_minutes,
            "lastActivityAt": last_activity.isoformat() if last_activity else "",
        },
        summary_facts=(
            f"You have {active_count} active Course Tracker course{'s' if active_count != 1 else ''}.",
            f"You have completed {completed_count} course{'s' if completed_count != 1 else ''}.",
            f"Your average Course Tracker progress is {average_progress:.1f}%.",
        ),
        actions=_course_tracker_actions(context),
        metadata={"resultCount": 1, "courseCount": len(courses)},
    )


def execute_active_courses(
    context: AssistantToolContext,
    arguments: dict[str, Any],
    session_factory: sessionmaker[Session] | CourseTrackerSessionFactory = CourseTrackerSessionLocal,
) -> AssistantToolResult:
    if context.user is None:
        return _denied_result("get_active_courses")
    limit = _limit(arguments)
    with session_factory() as db:
        courses = [course for course in _course_summaries(db, context.user.id) if course.status == "active"]
    courses.sort(key=lambda course: (-course.progress_percent, course.target_date or date.max, course.title.lower()))
    items = [_course_item(course) for course in courses[:limit]]
    if not items:
        return _empty_result("get_active_courses", "You do not have active Course Tracker courses yet.", context)
    return AssistantToolResult(
        tool_name="get_active_courses",
        source_app=COURSE_TRACKER_APP_SLUG,
        status="success",
        data={"courses": items, "activeCount": len(courses)},
        summary_facts=(f"You have {len(courses)} active Course Tracker course{'s' if len(courses) != 1 else ''}: {', '.join(item['name'] for item in items)}.",),
        actions=_course_tracker_actions(context),
        metadata={"resultCount": len(items), "totalCount": len(courses)},
    )


def execute_completed_courses(
    context: AssistantToolContext,
    arguments: dict[str, Any],
    session_factory: sessionmaker[Session] | CourseTrackerSessionFactory = CourseTrackerSessionLocal,
) -> AssistantToolResult:
    if context.user is None:
        return _denied_result("get_completed_courses")
    limit = _limit(arguments)
    with session_factory() as db:
        courses = [course for course in _course_summaries(db, context.user.id) if course.status == "completed"]
    courses.sort(key=lambda course: (course.updated_at, course.title.lower()), reverse=True)
    items = [
        {
            "name": course.title,
            "provider": course.provider,
            "category": course.category or "",
            "progressPercent": course.progress_percent,
            "completedAt": course.updated_at.isoformat(),
        }
        for course in courses[:limit]
    ]
    if not items:
        return AssistantToolResult(
            tool_name="get_completed_courses",
            source_app=COURSE_TRACKER_APP_SLUG,
            status="empty",
            data={"completedCourses": [], "completedCount": 0},
            summary_facts=("You have no completed Course Tracker courses yet.",),
            actions=_course_tracker_actions(context),
            metadata={"resultCount": 0},
        )
    return AssistantToolResult(
        tool_name="get_completed_courses",
        source_app=COURSE_TRACKER_APP_SLUG,
        status="success",
        data={"completedCourses": items, "completedCount": len(courses)},
        summary_facts=(f"You have completed {len(courses)} Course Tracker course{'s' if len(courses) != 1 else ''}: {', '.join(item['name'] for item in items)}.",),
        actions=_course_tracker_actions(context),
        metadata={"resultCount": len(items), "totalCount": len(courses)},
    )


def execute_course_nearest_completion(
    context: AssistantToolContext,
    arguments: dict[str, Any],
    session_factory: sessionmaker[Session] | CourseTrackerSessionFactory = CourseTrackerSessionLocal,
) -> AssistantToolResult:
    _ = arguments
    if context.user is None:
        return _denied_result("get_course_nearest_completion")
    with session_factory() as db:
        active = [course for course in _course_summaries(db, context.user.id) if course.status == "active"]
    active.sort(key=lambda course: (-course.progress_percent, course.target_date or date.max, course.title.lower()))
    if not active:
        return _empty_nearest_result(context)
    course = active[0]
    return AssistantToolResult(
        tool_name="get_course_nearest_completion",
        source_app=COURSE_TRACKER_APP_SLUG,
        status="success",
        data={
            "course": _course_item(course),
            "reasonCode": "HIGHEST_ACTIVE_PROGRESS",
            "reason": "This active course has the highest Course Tracker completion percentage.",
        },
        summary_facts=(f"{course.title} is your active Course Tracker course closest to completion at {course.progress_percent}%.",),
        actions=_course_tracker_actions(context),
        metadata={"resultCount": 1},
    )


def execute_stalled_courses(
    context: AssistantToolContext,
    arguments: dict[str, Any],
    session_factory: sessionmaker[Session] | CourseTrackerSessionFactory = CourseTrackerSessionLocal,
) -> AssistantToolResult:
    if context.user is None:
        return _denied_result("get_stalled_courses")
    limit = _limit(arguments)
    with session_factory() as db:
        active = [course for course in _course_summaries(db, context.user.id) if course.status == "active"]
    stalled = [
        course
        for course in active
        if course.inactive_days is None or course.inactive_days >= COURSE_TRACKER_STALLED_DAYS
    ]
    stalled.sort(
        key=lambda course: (
            -(course.inactive_days if course.inactive_days is not None else 9999),
            course.progress_percent,
            course.title.lower(),
        )
    )
    items = [
        {
            **_course_item(course),
            "inactiveDays": course.inactive_days if course.inactive_days is not None else -1,
            "reasonCode": "NO_PROGRESS_LOG" if course.inactive_days is None else "INACTIVE_THRESHOLD_REACHED",
        }
        for course in stalled[:limit]
    ]
    if not items:
        return AssistantToolResult(
            tool_name="get_stalled_courses",
            source_app=COURSE_TRACKER_APP_SLUG,
            status="empty",
            data={"stalledCourses": [], "stalledCount": 0, "thresholdDays": COURSE_TRACKER_STALLED_DAYS},
            summary_facts=(f"No active Course Tracker course has been inactive for {COURSE_TRACKER_STALLED_DAYS} days.",),
            actions=_course_tracker_actions(context),
            metadata={"resultCount": 0},
        )
    return AssistantToolResult(
        tool_name="get_stalled_courses",
        source_app=COURSE_TRACKER_APP_SLUG,
        status="success",
        data={"stalledCourses": items, "stalledCount": len(stalled), "thresholdDays": COURSE_TRACKER_STALLED_DAYS},
        summary_facts=(f"{items[0]['name']} is the clearest Course Tracker course to resume.",),
        actions=_course_tracker_actions(context),
        metadata={"resultCount": len(items), "totalCount": len(stalled)},
    )


def execute_course_deadline_summary(
    context: AssistantToolContext,
    arguments: dict[str, Any],
    session_factory: sessionmaker[Session] | CourseTrackerSessionFactory = CourseTrackerSessionLocal,
) -> AssistantToolResult:
    if context.user is None:
        return _denied_result("get_course_deadline_summary")
    limit = _limit(arguments)
    today = date.today()
    due_soon_end = today + timedelta(days=COURSE_TRACKER_DUE_SOON_DAYS)
    with session_factory() as db:
        active = [course for course in _course_summaries(db, context.user.id) if course.status == "active" and course.target_date is not None]
    deadline_courses = [
        {
            **_course_item(course),
            "dueDate": course.target_date.isoformat() if course.target_date else "",
            "deadlineStatus": "overdue" if course.target_date and course.target_date < today else "due_soon",
        }
        for course in active
        if course.target_date and course.target_date <= due_soon_end
    ]
    deadline_courses.sort(key=lambda item: (item["dueDate"], item["name"].lower()))
    overdue_count = len([item for item in deadline_courses if item["deadlineStatus"] == "overdue"])
    due_soon_count = len(deadline_courses) - overdue_count
    if not deadline_courses:
        return AssistantToolResult(
            tool_name="get_course_deadline_summary",
            source_app=COURSE_TRACKER_APP_SLUG,
            status="empty",
            data={"overdueCount": 0, "dueSoonCount": 0, "courses": [], "dueSoonDays": COURSE_TRACKER_DUE_SOON_DAYS},
            summary_facts=("You do not have overdue or due-soon active Course Tracker courses with target dates.",),
            actions=_course_tracker_actions(context),
            metadata={"resultCount": 0},
        )
    return AssistantToolResult(
        tool_name="get_course_deadline_summary",
        source_app=COURSE_TRACKER_APP_SLUG,
        status="success",
        data={
            "overdueCount": overdue_count,
            "dueSoonCount": due_soon_count,
            "courses": deadline_courses[:limit],
            "dueSoonDays": COURSE_TRACKER_DUE_SOON_DAYS,
        },
        summary_facts=(f"You have {overdue_count} overdue and {due_soon_count} due-soon Course Tracker course{'s' if overdue_count + due_soon_count != 1 else ''}.",),
        actions=_course_tracker_actions(context),
        metadata={"resultCount": min(len(deadline_courses), limit), "totalCount": len(deadline_courses)},
    )


def execute_recommend_next_course_action(
    context: AssistantToolContext,
    arguments: dict[str, Any],
    session_factory: sessionmaker[Session] | CourseTrackerSessionFactory = CourseTrackerSessionLocal,
) -> AssistantToolResult:
    _ = arguments
    if context.user is None:
        return _denied_result("recommend_next_course_action")
    with session_factory() as db:
        active = [course for course in _course_summaries(db, context.user.id) if course.status == "active"]
    if not active:
        return AssistantToolResult(
            tool_name="recommend_next_course_action",
            source_app=COURSE_TRACKER_APP_SLUG,
            status="empty",
            data={"primaryRecommendation": {}, "alternatives": []},
            summary_facts=("No active Course Tracker course is available for a next-action recommendation.",),
            actions=_course_tracker_actions(context),
            metadata={"resultCount": 0},
        )

    today = date.today()
    primary = _deadline_candidate(active, today) or _nearest_completion_candidate(active) or _stalled_candidate(active)
    alternatives = [
        _recommendation(course, reason_code)
        for course, reason_code in (
            (_nearest_completion_candidate(active), "NEAREST_COMPLETION"),
            (_stalled_candidate(active), "STALLED_ACTIVE_COURSE"),
        )
        if course is not None and (primary is None or course.title != primary.title)
    ][:2]
    reason_code = _recommendation_reason_code(primary, today) if primary is not None else "NO_ACTIVE_COURSE"
    recommendation = _recommendation(primary, reason_code) if primary is not None else {}
    facts = (
        (f"Continue {primary.title} next because {recommendation['reason'].lower()}",)
        if primary is not None
        else ("No Course Tracker recommendation is available yet.",)
    )
    return AssistantToolResult(
        tool_name="recommend_next_course_action",
        source_app=COURSE_TRACKER_APP_SLUG,
        status="success" if primary is not None else "empty",
        data={"primaryRecommendation": recommendation, "alternatives": alternatives},
        summary_facts=facts,
        actions=_course_tracker_actions(context),
        metadata={"resultCount": 1 + len(alternatives) if primary is not None else 0},
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
        source_app=COURSE_TRACKER_APP_SLUG,
        input_schema=input_schema,
        output_schema=output_schema,
        handler=handler,
        requires_authentication=True,
        read_only=True,
        timeout_seconds=2.0,
        visibility="authenticated",
        deterministic_intents=intents,
        max_result_items=COURSE_TRACKER_RESULT_LIMIT,
        owner_scoped=True,
        permission_scope="owner",
        version="1.0.0",
        enabled=True,
        deprecated=False,
        documentation_path="app/modules/course_tracker/astra-ai.md",
    )


def _limit_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {"limit": {"type": "integer", "minimum": 1, "maximum": COURSE_TRACKER_RESULT_LIMIT}},
        "additionalProperties": False,
    }


def _limit(arguments: dict[str, Any]) -> int:
    return max(1, min(int(arguments.get("limit") or COURSE_TRACKER_RESULT_LIMIT), COURSE_TRACKER_RESULT_LIMIT))


def _course_summaries(db: Session, user_id: str) -> list[CourseAstraSummary]:
    module_counts = (
        select(
            CourseModule.course_id.label("course_id"),
            func.count(CourseModule.id).label("module_count"),
            func.coalesce(func.sum(case((CourseModule.status == "completed", 1), else_=0)), 0).label(
                "completed_module_count"
            ),
        )
        .where(CourseModule.owner_id == user_id)
        .group_by(CourseModule.course_id)
        .subquery()
    )
    progress_totals = (
        select(
            CourseProgressLog.course_id.label("course_id"),
            func.coalesce(func.sum(CourseProgressLog.minutes), 0).label("total_minutes"),
            func.max(CourseProgressLog.progress_date).label("last_progress_date"),
        )
        .where(CourseProgressLog.owner_id == user_id)
        .group_by(CourseProgressLog.course_id)
        .subquery()
    )
    rows = db.execute(
        select(
            Course.title,
            Course.provider,
            Course.category,
            Course.status,
            Course.target_date,
            Course.updated_at,
            func.coalesce(module_counts.c.module_count, 0).label("module_count"),
            func.coalesce(module_counts.c.completed_module_count, 0).label("completed_module_count"),
            func.coalesce(progress_totals.c.total_minutes, 0).label("total_minutes"),
            progress_totals.c.last_progress_date,
        )
        .outerjoin(module_counts, module_counts.c.course_id == Course.id)
        .outerjoin(progress_totals, progress_totals.c.course_id == Course.id)
        .where(Course.owner_id == user_id)
        .order_by(Course.updated_at.desc(), Course.title.asc())
    ).all()
    summaries: list[CourseAstraSummary] = []
    for row in rows:
        summaries.append(
            CourseAstraSummary(
                title=str(row.title),
                provider=str(row.provider),
                category=str(row.category) if row.category else None,
                status=str(row.status),
                target_date=row.target_date,
                updated_at=row.updated_at,
                module_count=int(row.module_count or 0),
                completed_module_count=int(row.completed_module_count or 0),
                total_minutes=int(row.total_minutes or 0),
                last_progress_date=row.last_progress_date,
            )
        )
    return summaries


def _course_item(course: CourseAstraSummary) -> dict[str, Any]:
    return {
        "name": course.title,
        "provider": course.provider,
        "category": course.category or "",
        "status": course.status,
        "progressPercent": course.progress_percent,
        "moduleCount": course.module_count,
        "completedModuleCount": course.completed_module_count,
        "totalMinutes": course.total_minutes,
        "targetDate": course.target_date.isoformat() if course.target_date else "",
        "lastActivityAt": course.last_progress_date.isoformat() if course.last_progress_date else "",
    }


def _latest_activity(courses: list[CourseAstraSummary]) -> date | None:
    values: list[date] = []
    for course in courses:
        if course.last_progress_date is not None:
            values.append(course.last_progress_date)
        else:
            values.append(course.updated_at.date())
    return max(values) if values else None


def _deadline_candidate(courses: list[CourseAstraSummary], today: date) -> CourseAstraSummary | None:
    candidates = [course for course in courses if course.target_date is not None and course.target_date < today]
    candidates.sort(key=lambda course: (course.target_date or date.max, -course.progress_percent, course.title.lower()))
    return candidates[0] if candidates else None


def _nearest_completion_candidate(courses: list[CourseAstraSummary]) -> CourseAstraSummary | None:
    candidates = sorted(courses, key=lambda course: (-course.progress_percent, course.target_date or date.max, course.title.lower()))
    return candidates[0] if candidates else None


def _stalled_candidate(courses: list[CourseAstraSummary]) -> CourseAstraSummary | None:
    candidates = [
        course
        for course in courses
        if course.inactive_days is None or course.inactive_days >= COURSE_TRACKER_STALLED_DAYS
    ]
    candidates.sort(key=lambda course: (-(course.inactive_days if course.inactive_days is not None else 9999), course.title.lower()))
    return candidates[0] if candidates else None


def _recommendation_reason_code(course: CourseAstraSummary, today: date) -> str:
    if course.target_date is not None and course.target_date < today:
        return "OVERDUE_TARGET_DATE"
    if course.inactive_days is None or course.inactive_days >= COURSE_TRACKER_STALLED_DAYS:
        return "STALLED_ACTIVE_COURSE"
    return "NEAREST_COMPLETION"


def _recommendation(course: CourseAstraSummary, reason_code: str) -> dict[str, Any]:
    reasons = {
        "OVERDUE_TARGET_DATE": "this active course is past its target date.",
        "NEAREST_COMPLETION": "this active course has the highest completion percentage.",
        "STALLED_ACTIVE_COURSE": "this active course has no recent progress.",
    }
    return {
        "course": course.title,
        "actionType": "continue",
        "progressPercent": course.progress_percent,
        "reasonCode": reason_code,
        "reason": reasons.get(reason_code, "this active course is the next deterministic Course Tracker action."),
    }


def _empty_result(tool_name: str, fact: str, context: AssistantToolContext) -> AssistantToolResult:
    return AssistantToolResult(
        tool_name=tool_name,
        source_app=COURSE_TRACKER_APP_SLUG,
        status="empty",
        data={
            "courses": [],
            "activeCount": 0,
        }
        if tool_name == "get_active_courses"
        else {
            "courseCount": 0,
            "activeCourseCount": 0,
            "pausedCourseCount": 0,
            "completedCourseCount": 0,
            "averageProgressPercent": 0.0,
            "totalMinutes": 0,
            "lastActivityAt": "",
        },
        summary_facts=(fact,),
        actions=_course_tracker_actions(context),
        metadata={"resultCount": 0},
    )


def _empty_nearest_result(context: AssistantToolContext) -> AssistantToolResult:
    return AssistantToolResult(
        tool_name="get_course_nearest_completion",
        source_app=COURSE_TRACKER_APP_SLUG,
        status="empty",
        data={"course": {}, "reasonCode": "NO_ACTIVE_COURSE", "reason": "No active Course Tracker course is available."},
        summary_facts=("No active Course Tracker course is available for nearest-completion guidance.",),
        actions=_course_tracker_actions(context),
        metadata={"resultCount": 0},
    )


def _denied_result(tool_name: str) -> AssistantToolResult:
    return AssistantToolResult(
        tool_name=tool_name,
        source_app=COURSE_TRACKER_APP_SLUG,
        status="denied",
        summary_facts=("Authentication is required.",),
    )


def _course_tracker_actions(context: AssistantToolContext) -> tuple[AssistantAction, ...]:
    preferred = ("/course-tracker/courses", "/course-tracker")
    for route in preferred:
        if route in context.allowed_routes:
            return (AssistantAction(type="app", label="Open Course Tracker", route=route),)
    return ()
