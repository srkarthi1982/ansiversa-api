import json
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, load_only

from app.core.config import settings
from app.modules.auth.constants import ADMIN_ROLE_ID
from app.modules.auth.models import User
from app.modules.quiz.models import (
    Platform,
    Question,
    QuizAttempt,
    QuizAttemptQuestion,
    Result,
    Roadmap,
    Subject,
    Topic,
)
from app.modules.quiz.schemas import (
    QuizAttemptHistoryItemResponse,
    QuizAttemptHistoryListResponse,
    QuizAttemptQuestionResponse,
    QuizAttemptRequest,
    QuizAttemptResponse,
    QuizAttemptReviewResponse,
    QuizAttemptSubmitRequest,
    QuizAttemptSubmitResponse,
    QuizResultDetailResponse,
    QuizResultHistoryItemResponse,
    QuizResultHistoryListResponse,
)


PAID_PLAN_STATUSES = {"active", "trialing"}
FREE_PLAN_NAMES = {"", "free", "none"}


def _not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Quiz attempt not found.",
    )


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)


def _is_entitled_to_difficult_level(user: User) -> bool:
    if user.role_id == ADMIN_ROLE_ID:
        return True

    plan = (user.plan or "").strip().lower()
    plan_status = (user.plan_status or "").strip().lower()
    return plan not in FREE_PLAN_NAMES and plan_status in PAID_PLAN_STATUSES


def _normalize_options(value: str | list[Any] | dict[str, Any]) -> list[str]:
    parsed: Any = value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return []

    values = list(parsed.values()) if isinstance(parsed, dict) else parsed
    if not isinstance(values, list):
        return []

    options: list[str] = []
    for item in values:
        if isinstance(item, str):
            normalized = item.strip()
        elif isinstance(item, (int, float, bool)):
            normalized = str(item)
        else:
            normalized = ""
        if normalized:
            options.append(normalized)

    return options


def _answer_index(options: list[str], answer: str) -> int | None:
    normalized = answer.strip()
    if not normalized:
        return None

    if normalized.lstrip("-").isdigit():
        numeric = int(normalized)
        if 0 <= numeric < len(options):
            return numeric
        if 1 <= numeric <= len(options):
            return numeric - 1

    if len(normalized) == 1 and normalized.isalpha():
        alpha_index = ord(normalized.upper()) - ord("A")
        if 0 <= alpha_index < len(options):
            return alpha_index

    lowered = normalized.casefold()
    for index, option in enumerate(options):
        if option.strip().casefold() == lowered:
            return index

    return None


def _answer_label(index: int | None, fallback: str) -> str:
    if index is not None and 0 <= index < 26:
        return chr(ord("A") + index)

    return fallback.strip()


def _answer_text(options: list[str], index: int | None) -> str | None:
    return options[index] if index is not None and 0 <= index < len(options) else None


def _parse_responses(value: str) -> list[dict[str, int]]:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return []

    if not isinstance(parsed, list):
        return []

    responses: list[dict[str, int]] = []
    for item in parsed:
        if (
            isinstance(item, dict)
            and isinstance(item.get("id"), int)
            and isinstance(item.get("a"), int)
            and isinstance(item.get("s"), int)
        ):
            responses.append({"id": item["id"], "a": item["a"], "s": item["s"]})

    return responses


def _percentage(score: int, total: int) -> int:
    return round((score / total) * 100) if total > 0 else 0


def _safe_question(question: Question) -> QuizAttemptQuestionResponse:
    return QuizAttemptQuestionResponse(
        id=question.id,
        question_text=question.question_text,
        options=_normalize_options(question.options_json),
        level=question.level,  # type: ignore[arg-type]
    )


def _validate_taxonomy(db: Session, payload: QuizAttemptRequest) -> None:
    platform = db.get(Platform, payload.platform_id)
    subject = db.get(Subject, payload.subject_id)
    topic = db.get(Topic, payload.topic_id)
    roadmap = db.get(Roadmap, payload.roadmap_id)

    if not platform:
        raise HTTPException(status_code=400, detail="Platform not found.")
    if not subject or subject.platform_id != payload.platform_id:
        raise HTTPException(status_code=400, detail="Subject does not belong to platform.")
    if (
        not topic
        or topic.platform_id != payload.platform_id
        or topic.subject_id != payload.subject_id
    ):
        raise HTTPException(
            status_code=400,
            detail="Topic does not belong to platform and subject.",
        )
    if (
        not roadmap
        or roadmap.platform_id != payload.platform_id
        or roadmap.subject_id != payload.subject_id
        or roadmap.topic_id != payload.topic_id
    ):
        raise HTTPException(
            status_code=400,
            detail="Roadmap does not belong to platform, subject, and topic.",
        )


def _attempt_questions(
    db: Session,
    attempt_id: int,
    *,
    include_review_fields: bool = False,
) -> list[Question]:
    columns = [Question.id, Question.question_text, Question.options_json]
    if include_review_fields:
        columns.extend([Question.answer_key, Question.explanation])
    else:
        columns.append(Question.level)

    return list(
        db.execute(
            select(Question)
            .options(load_only(*columns))
            .join(QuizAttemptQuestion, QuizAttemptQuestion.question_id == Question.id)
            .where(QuizAttemptQuestion.attempt_id == attempt_id)
            .order_by(QuizAttemptQuestion.position.asc())
        )
        .scalars()
        .all()
    )


def start_attempt(
    db: Session,
    user: User,
    payload: QuizAttemptRequest,
) -> QuizAttemptResponse:
    _validate_taxonomy(db, payload)
    if payload.level == "D" and not _is_entitled_to_difficult_level(user):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Difficult level requires an active paid plan.",
        )

    statement = select(Question).options(
        load_only(
            Question.id,
            Question.question_text,
            Question.options_json,
            Question.level,
        )
    ).where(
        Question.platform_id == payload.platform_id,
        Question.subject_id == payload.subject_id,
        Question.topic_id == payload.topic_id,
        Question.roadmap_id == payload.roadmap_id,
        Question.level == payload.level,
        Question.is_active.is_(True),
    )
    if payload.excluded_question_ids:
        statement = statement.where(Question.id.not_in(payload.excluded_question_ids))
    questions = list(
        db.execute(statement.order_by(func.random()).limit(payload.limit)).scalars().all()
    )
    if not questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active questions match the requested quiz.",
        )

    attempt = QuizAttempt(
        user_id=user.id,
        platform_id=payload.platform_id,
        subject_id=payload.subject_id,
        topic_id=payload.topic_id,
        roadmap_id=payload.roadmap_id,
        level=payload.level,
        expires_at=datetime.now(timezone.utc)
        + timedelta(hours=settings.QUIZ_ATTEMPT_EXPIRE_HOURS),
    )
    db.add(attempt)
    db.flush()
    db.add_all(
        QuizAttemptQuestion(
            attempt_id=attempt.id,
            question_id=question.id,
            position=position,
        )
        for position, question in enumerate(questions)
    )
    db.commit()

    return QuizAttemptResponse(
        attempt_id=attempt.id,
        questions=[_safe_question(question) for question in questions],
        total_questions=len(questions),
    )


def resume_attempt(db: Session, user: User, attempt_id: int) -> QuizAttemptResponse:
    attempt = db.get(QuizAttempt, attempt_id)
    if (
        not attempt
        or attempt.user_id != user.id
        or attempt.status != "in_progress"
        or _as_utc(attempt.expires_at) <= datetime.now(timezone.utc)
    ):
        raise _not_found()

    questions = _attempt_questions(db, attempt.id)
    if not questions:
        raise _not_found()

    return QuizAttemptResponse(
        attempt_id=attempt.id,
        questions=[_safe_question(question) for question in questions],
        total_questions=len(questions),
    )


def submit_attempt(
    db: Session,
    user: User,
    attempt_id: int,
    payload: QuizAttemptSubmitRequest,
) -> QuizAttemptSubmitResponse:
    attempt = db.get(QuizAttempt, attempt_id)
    if not attempt or attempt.user_id != user.id:
        raise _not_found()
    if attempt.status == "submitted" or attempt.submitted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Quiz attempt has already been submitted.",
        )
    if attempt.status != "in_progress" or _as_utc(attempt.expires_at) <= datetime.now(
        timezone.utc
    ):
        raise _not_found()

    questions = _attempt_questions(db, attempt.id, include_review_fields=True)
    answer_by_question_id: dict[int, str] = {}
    for answer in payload.answers:
        if answer.question_id in answer_by_question_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Each attempt question must be answered exactly once.",
            )
        answer_by_question_id[answer.question_id] = answer.selected_answer

    expected_ids = {question.id for question in questions}
    if set(answer_by_question_id) != expected_ids:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Submitted question IDs must match the attempt questions.",
        )

    score = 0
    legacy_responses: list[dict[str, int]] = []
    review: list[QuizAttemptReviewResponse] = []
    for question in questions:
        options = _normalize_options(question.options_json)
        correct_index = _answer_index(options, question.answer_key)
        selected_answer = answer_by_question_id[question.id]
        selected_index = _answer_index(options, selected_answer)
        if selected_index is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Selected answer is invalid for question {question.id}.",
            )
        is_correct = correct_index is not None and selected_index == correct_index
        score += int(is_correct)
        legacy_responses.append(
            {
                "id": question.id,
                "a": correct_index if correct_index is not None else -1,
                "s": selected_index if selected_index is not None else -1,
            }
        )
        review.append(
            QuizAttemptReviewResponse(
                question_id=question.id,
                question_text=question.question_text,
                options=options,
                selected_answer=_answer_label(selected_index, selected_answer),
                selected_answer_text=_answer_text(options, selected_index),
                correct_answer=_answer_label(correct_index, question.answer_key),
                correct_answer_text=_answer_text(options, correct_index),
                is_correct=is_correct,
                explanation=question.explanation,
            )
        )

    result = Result(
        user_id=user.id,
        platform_id=attempt.platform_id,
        subject_id=attempt.subject_id,
        topic_id=attempt.topic_id,
        roadmap_id=attempt.roadmap_id,
        level=attempt.level,
        responses_json=json.dumps(legacy_responses, separators=(",", ":")),
        mark=score,
    )
    db.add(result)
    db.flush()
    attempt.status = "submitted"
    attempt.submitted_at = datetime.now(timezone.utc)
    attempt.result_id = result.id
    db.add(attempt)
    db.commit()

    total = len(questions)
    return QuizAttemptSubmitResponse(
        result_id=result.id,
        score=score,
        total=total,
        percentage=round((score / total) * 100),
        review=review,
    )


def list_attempt_history(
    db: Session,
    user: User,
    *,
    page: int,
    page_size: int,
) -> QuizAttemptHistoryListResponse:
    filters = (QuizAttempt.user_id == user.id,)
    total = db.scalar(select(func.count()).select_from(QuizAttempt).where(*filters)) or 0
    question_counts = (
        select(
            QuizAttemptQuestion.attempt_id,
            func.count().label("total_questions"),
        )
        .group_by(QuizAttemptQuestion.attempt_id)
        .subquery()
    )
    rows = db.execute(
        select(
            QuizAttempt,
            Result.mark.label("result_mark"),
            Platform.name.label("platform_name"),
            Subject.name.label("subject_name"),
            Topic.name.label("topic_name"),
            Roadmap.name.label("roadmap_name"),
            func.coalesce(question_counts.c.total_questions, 0).label(
                "total_questions"
            ),
        )
        .outerjoin(Result, Result.id == QuizAttempt.result_id)
        .outerjoin(Platform, Platform.id == QuizAttempt.platform_id)
        .outerjoin(Subject, Subject.id == QuizAttempt.subject_id)
        .outerjoin(Topic, Topic.id == QuizAttempt.topic_id)
        .outerjoin(Roadmap, Roadmap.id == QuizAttempt.roadmap_id)
        .outerjoin(
            question_counts,
            question_counts.c.attempt_id == QuizAttempt.id,
        )
        .where(*filters)
        .order_by(QuizAttempt.created_at.desc(), QuizAttempt.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return QuizAttemptHistoryListResponse(
        items=[
            QuizAttemptHistoryItemResponse(
                id=attempt.id,
                platform_id=attempt.platform_id,
                platform_name=platform_name or f"Platform {attempt.platform_id}",
                subject_id=attempt.subject_id,
                subject_name=subject_name or f"Subject {attempt.subject_id}",
                topic_id=attempt.topic_id,
                topic_name=topic_name or f"Topic {attempt.topic_id}",
                roadmap_id=attempt.roadmap_id,
                roadmap_name=roadmap_name or f"Roadmap {attempt.roadmap_id}",
                level=attempt.level,  # type: ignore[arg-type]
                status=attempt.status,
                result_id=attempt.result_id,
                score=result_mark,
                total_questions=total_questions,
                percentage=(
                    _percentage(result_mark, total_questions)
                    if result_mark is not None
                    else None
                ),
                created_at=attempt.created_at,
                submitted_at=attempt.submitted_at,
                expires_at=attempt.expires_at,
            )
            for (
                attempt,
                result_mark,
                platform_name,
                subject_name,
                topic_name,
                roadmap_name,
                total_questions,
            ) in rows
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


def list_result_history(
    db: Session,
    user: User,
    *,
    page: int,
    page_size: int,
) -> QuizResultHistoryListResponse:
    filters = (Result.user_id == user.id,)
    total = db.scalar(select(func.count()).select_from(Result).where(*filters)) or 0
    rows = db.execute(
        select(
            Result.id.label("result_id"),
            Result.platform_id,
            Result.subject_id,
            Result.topic_id,
            Result.roadmap_id,
            Result.level,
            Result.mark,
            Result.created_at,
            QuizAttempt.id.label("attempt_id"),
            QuizAttempt.submitted_at,
            Platform.name.label("platform_name"),
            Subject.name.label("subject_name"),
            Topic.name.label("topic_name"),
            Roadmap.name.label("roadmap_name"),
            func.coalesce(func.json_array_length(Result.responses_json), 0).label(
                "total_questions"
            ),
        )
        .outerjoin(QuizAttempt, QuizAttempt.result_id == Result.id)
        .outerjoin(Platform, Platform.id == Result.platform_id)
        .outerjoin(Subject, Subject.id == Result.subject_id)
        .outerjoin(Topic, Topic.id == Result.topic_id)
        .outerjoin(Roadmap, Roadmap.id == Result.roadmap_id)
        .where(*filters)
        .order_by(Result.created_at.desc(), Result.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return QuizResultHistoryListResponse(
        items=[
            QuizResultHistoryItemResponse(
                id=result_id,
                attempt_id=attempt_id,
                platform_id=platform_id,
                platform_name=platform_name or f"Platform {platform_id}",
                subject_id=subject_id,
                subject_name=subject_name or f"Subject {subject_id}",
                topic_id=topic_id,
                topic_name=topic_name or f"Topic {topic_id}",
                roadmap_id=roadmap_id,
                roadmap_name=roadmap_name or f"Roadmap {roadmap_id}",
                level=level,  # type: ignore[arg-type]
                score=mark,
                total_questions=total_questions,
                percentage=_percentage(mark, total_questions),
                created_at=created_at,
                submitted_at=submitted_at if submitted_at else created_at,
            )
            for (
                result_id,
                platform_id,
                subject_id,
                topic_id,
                roadmap_id,
                level,
                mark,
                created_at,
                attempt_id,
                submitted_at,
                platform_name,
                subject_name,
                topic_name,
                roadmap_name,
                total_questions,
            ) in rows
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


def get_result_detail(db: Session, user: User, result_id: int) -> QuizResultDetailResponse:
    row = db.execute(
        select(
            Result,
            QuizAttempt.id.label("attempt_id"),
            QuizAttempt.submitted_at,
            Platform.name.label("platform_name"),
            Subject.name.label("subject_name"),
            Topic.name.label("topic_name"),
            Roadmap.name.label("roadmap_name"),
        )
        .outerjoin(QuizAttempt, QuizAttempt.result_id == Result.id)
        .outerjoin(Platform, Platform.id == Result.platform_id)
        .outerjoin(Subject, Subject.id == Result.subject_id)
        .outerjoin(Topic, Topic.id == Result.topic_id)
        .outerjoin(Roadmap, Roadmap.id == Result.roadmap_id)
        .where(Result.id == result_id, Result.user_id == user.id)
    ).one_or_none()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz result not found.")

    (
        result,
        attempt_id,
        submitted_at,
        platform_name,
        subject_name,
        topic_name,
        roadmap_name,
    ) = row
    responses = _parse_responses(result.responses_json)
    question_ids = [response["id"] for response in responses]
    questions = {
        question.id: question
        for question in db.execute(
            select(Question)
            .options(
                load_only(
                    Question.id,
                    Question.question_text,
                    Question.options_json,
                    Question.answer_key,
                    Question.explanation,
                )
            )
            .where(Question.id.in_(question_ids))
        ).scalars()
    }
    review: list[QuizAttemptReviewResponse] = []
    for response in responses:
        question = questions.get(response["id"])
        if not question:
            continue
        options = _normalize_options(question.options_json)
        selected_index = response["s"]
        correct_index = response["a"]
        review.append(
            QuizAttemptReviewResponse(
                question_id=question.id,
                question_text=question.question_text,
                options=options,
                selected_answer=_answer_label(selected_index, ""),
                selected_answer_text=_answer_text(options, selected_index),
                correct_answer=_answer_label(correct_index, question.answer_key),
                correct_answer_text=_answer_text(options, correct_index),
                is_correct=correct_index >= 0 and selected_index == correct_index,
                explanation=question.explanation,
            )
        )

    total_questions = len(responses)
    return QuizResultDetailResponse(
        id=result.id,
        attempt_id=attempt_id,
        platform_id=result.platform_id,
        platform_name=platform_name or f"Platform {result.platform_id}",
        subject_id=result.subject_id,
        subject_name=subject_name or f"Subject {result.subject_id}",
        topic_id=result.topic_id,
        topic_name=topic_name or f"Topic {result.topic_id}",
        roadmap_id=result.roadmap_id,
        roadmap_name=roadmap_name or f"Roadmap {result.roadmap_id}",
        level=result.level,  # type: ignore[arg-type]
        score=result.mark,
        total_questions=total_questions,
        percentage=_percentage(result.mark, total_questions),
        created_at=result.created_at,
        submitted_at=submitted_at if submitted_at else result.created_at,
        review=review,
    )
