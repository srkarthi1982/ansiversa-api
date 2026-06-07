import json
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
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
    QuizAttemptQuestionResponse,
    QuizAttemptRequest,
    QuizAttemptResponse,
    QuizAttemptReviewResponse,
    QuizAttemptSubmitRequest,
    QuizAttemptSubmitResponse,
)


ADMIN_ROLE_ID = 1
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
    if index is not None and index < 26:
        return chr(ord("A") + index)

    return fallback.strip()


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


def _attempt_questions(db: Session, attempt_id: int) -> list[Question]:
    return list(
        db.execute(
            select(Question)
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

    statement = select(Question).where(
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

    questions = _attempt_questions(db, attempt.id)
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
                correct_answer=_answer_label(correct_index, question.answer_key),
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
