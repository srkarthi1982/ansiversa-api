from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.exam.models import ExamAnswer, ExamAttempt, ExamPaper, ExamQuestion
from app.modules.exam.schemas import (
    ExamAttemptAnswersRequest,
    ExamAttemptResponse,
    ExamOption,
    ExamPaperCreateRequest,
    ExamPaperResponse,
    ExamPaperUpdateRequest,
    ExamQuestionCreateRequest,
    ExamQuestionResponse,
    ExamQuestionUpdateRequest,
    ExamReviewQuestionResponse,
    ExamReviewResponse,
)


def _question_count(db: Session, paper_id: str) -> int:
    return int(
        db.execute(
            select(func.count()).select_from(ExamQuestion).where(
                ExamQuestion.paper_id == paper_id
            )
        ).scalar_one()
    )


def _paper_response(db: Session, paper: ExamPaper) -> ExamPaperResponse:
    return ExamPaperResponse(
        id=paper.id,
        title=paper.title,
        subject=paper.subject,
        duration_minutes=paper.duration_minutes,
        description=paper.description,
        question_count=_question_count(db, paper.id),
        created_at=paper.created_at,
        updated_at=paper.updated_at,
    )


def _get_owned_paper(db: Session, user: User, paper_id: str) -> ExamPaper:
    paper = db.get(ExamPaper, paper_id)
    if not paper or paper.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam paper was not found.",
        )

    return paper


def _get_owned_question(db: Session, user: User, question_id: str) -> ExamQuestion:
    question = db.get(ExamQuestion, question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam question was not found.",
        )
    _get_owned_paper(db, user, question.paper_id)

    return question


def _get_owned_attempt(db: Session, user: User, attempt_id: str) -> ExamAttempt:
    attempt = db.get(ExamAttempt, attempt_id)
    if not attempt or attempt.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam attempt was not found.",
        )

    return attempt


def _list_questions(db: Session, paper_id: str) -> list[ExamQuestion]:
    return list(
        db.execute(
            select(ExamQuestion)
            .where(ExamQuestion.paper_id == paper_id)
            .order_by(ExamQuestion.created_at.asc())
        )
        .scalars()
        .all()
    )


def _list_answers(db: Session, attempt_id: str) -> list[ExamAnswer]:
    return list(
        db.execute(
            select(ExamAnswer)
            .where(ExamAnswer.attempt_id == attempt_id)
            .order_by(ExamAnswer.created_at.asc())
        )
        .scalars()
        .all()
    )


def _answer_text(question: ExamQuestion, option: ExamOption | None) -> str | None:
    if option == "A":
        return question.option_a
    if option == "B":
        return question.option_b
    if option == "C":
        return question.option_c
    if option == "D":
        return question.option_d

    return None


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)


def _is_attempt_expired(attempt: ExamAttempt, paper: ExamPaper) -> bool:
    started_at = _as_utc(attempt.started_at)
    expires_at = started_at + timedelta(minutes=paper.duration_minutes)

    return datetime.now(timezone.utc) > expires_at


def list_papers(db: Session, user: User) -> list[ExamPaperResponse]:
    papers = list(
        db.execute(
            select(ExamPaper)
            .where(ExamPaper.user_id == user.id)
            .order_by(ExamPaper.updated_at.desc(), ExamPaper.title.asc())
        )
        .scalars()
        .all()
    )

    return [_paper_response(db, paper) for paper in papers]


def create_paper(
    db: Session,
    user: User,
    payload: ExamPaperCreateRequest,
) -> ExamPaperResponse:
    paper = ExamPaper(
        user_id=user.id,
        title=payload.title,
        subject=payload.subject,
        duration_minutes=payload.duration_minutes,
        description=payload.description,
    )
    db.add(paper)
    db.commit()
    db.refresh(paper)

    return _paper_response(db, paper)


def get_paper_detail(
    db: Session,
    user: User,
    paper_id: str,
) -> tuple[ExamPaperResponse, list[ExamQuestion]]:
    paper = _get_owned_paper(db, user, paper_id)
    questions = _list_questions(db, paper.id)

    return _paper_response(db, paper), questions


def update_paper(
    db: Session,
    user: User,
    paper_id: str,
    payload: ExamPaperUpdateRequest,
) -> ExamPaperResponse:
    paper = _get_owned_paper(db, user, paper_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(paper, field, value)
    db.commit()
    db.refresh(paper)

    return _paper_response(db, paper)


def delete_paper(db: Session, user: User, paper_id: str) -> None:
    paper = _get_owned_paper(db, user, paper_id)
    question_ids = select(ExamQuestion.id).where(ExamQuestion.paper_id == paper.id)
    attempt_ids = select(ExamAttempt.id).where(ExamAttempt.paper_id == paper.id)
    db.execute(delete(ExamAnswer).where(ExamAnswer.attempt_id.in_(attempt_ids)))
    db.execute(delete(ExamAnswer).where(ExamAnswer.question_id.in_(question_ids)))
    db.execute(delete(ExamAttempt).where(ExamAttempt.paper_id == paper.id))
    db.execute(delete(ExamQuestion).where(ExamQuestion.paper_id == paper.id))
    db.delete(paper)
    db.commit()


def list_questions(db: Session, user: User, paper_id: str) -> list[ExamQuestion]:
    paper = _get_owned_paper(db, user, paper_id)
    return _list_questions(db, paper.id)


def create_question(
    db: Session,
    user: User,
    paper_id: str,
    payload: ExamQuestionCreateRequest,
) -> ExamQuestion:
    paper = _get_owned_paper(db, user, paper_id)
    question = ExamQuestion(
        paper_id=paper.id,
        question_text=payload.question_text,
        option_a=payload.option_a,
        option_b=payload.option_b,
        option_c=payload.option_c,
        option_d=payload.option_d,
        correct_option=payload.correct_option,
        explanation=payload.explanation,
        marks=payload.marks,
    )
    db.add(question)
    db.commit()
    db.refresh(question)

    return question


def update_question(
    db: Session,
    user: User,
    question_id: str,
    payload: ExamQuestionUpdateRequest,
) -> ExamQuestion:
    question = _get_owned_question(db, user, question_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(question, field, value)
    db.commit()
    db.refresh(question)

    return question


def delete_question(db: Session, user: User, question_id: str) -> None:
    question = _get_owned_question(db, user, question_id)
    db.execute(delete(ExamAnswer).where(ExamAnswer.question_id == question.id))
    db.delete(question)
    db.commit()


def start_attempt(db: Session, user: User, paper_id: str) -> ExamAttemptResponse:
    paper = _get_owned_paper(db, user, paper_id)
    questions = _list_questions(db, paper.id)
    if not questions:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Add at least one question before starting an exam attempt.",
        )

    attempt = ExamAttempt(
        user_id=user.id,
        paper_id=paper.id,
        total_questions=len(questions),
        total_marks=sum(question.marks for question in questions),
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return _attempt_response(db, user, attempt)


def get_attempt(db: Session, user: User, attempt_id: str) -> ExamAttemptResponse:
    attempt = _get_owned_attempt(db, user, attempt_id)
    return _attempt_response(db, user, attempt)


def save_answers(
    db: Session,
    user: User,
    attempt_id: str,
    payload: ExamAttemptAnswersRequest,
) -> ExamAttemptResponse:
    attempt = _get_owned_attempt(db, user, attempt_id)
    if attempt.status == "submitted":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Submitted exam attempts cannot be changed.",
        )

    paper = _get_owned_paper(db, user, attempt.paper_id)
    if _is_attempt_expired(attempt, paper):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Exam attempt time has expired.",
        )

    submitted_question_ids = [answer.question_id for answer in payload.answers]
    submitted_question_id_set = set(submitted_question_ids)
    if len(submitted_question_ids) != len(submitted_question_id_set):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Answers contain duplicate questions.",
        )

    valid_question_ids = {
        question.id for question in _list_questions(db, paper.id)
    }
    for answer in payload.answers:
        if answer.question_id not in valid_question_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Answer contains a question outside this exam paper.",
            )
        existing = db.execute(
            select(ExamAnswer).where(
                ExamAnswer.attempt_id == attempt.id,
                ExamAnswer.question_id == answer.question_id,
            )
        ).scalar_one_or_none()
        if existing:
            existing.selected_option = answer.selected_option
            existing.is_correct = None
        else:
            db.add(
                ExamAnswer(
                    attempt_id=attempt.id,
                    question_id=answer.question_id,
                    selected_option=answer.selected_option,
                )
            )

    db.commit()

    return _attempt_response(db, user, attempt)


def submit_attempt(db: Session, user: User, attempt_id: str) -> ExamReviewResponse:
    attempt = _get_owned_attempt(db, user, attempt_id)
    if attempt.status == "submitted":
        return get_review(db, user, attempt.id)

    questions = _list_questions(db, attempt.paper_id)
    answers = {answer.question_id: answer for answer in _list_answers(db, attempt.id)}
    score = 0
    correct_answers = 0
    for question in questions:
        answer = answers.get(question.id)
        if answer is None:
            continue
        is_correct = answer.selected_option == question.correct_option
        answer.is_correct = is_correct
        if is_correct:
            score += question.marks
            correct_answers += 1

    total_marks = sum(question.marks for question in questions)
    completed_at = datetime.now(timezone.utc)
    attempt.score = score
    attempt.percentage = round((score / total_marks) * 100) if total_marks else 0
    attempt.status = "submitted"
    attempt.submitted_at = completed_at
    db.commit()

    return _review_response(
        questions=questions,
        answers=answers,
        attempt=attempt,
        completed_at=completed_at,
        correct_answers=correct_answers,
    )


def get_review(db: Session, user: User, attempt_id: str) -> ExamReviewResponse:
    attempt = _get_owned_attempt(db, user, attempt_id)
    if attempt.status != "submitted" or attempt.submitted_at is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Submit the exam attempt before reviewing the score.",
        )

    questions = _list_questions(db, attempt.paper_id)
    answers = {answer.question_id: answer for answer in _list_answers(db, attempt.id)}
    correct_answers = sum(1 for answer in answers.values() if answer.is_correct)

    return _review_response(
        questions=questions,
        answers=answers,
        attempt=attempt,
        completed_at=attempt.submitted_at,
        correct_answers=correct_answers,
    )


def _attempt_response(
    db: Session,
    user: User,
    attempt: ExamAttempt,
) -> ExamAttemptResponse:
    paper, questions = get_paper_detail(db, user, attempt.paper_id)
    answers = {
        answer.question_id: answer.selected_option
        for answer in _list_answers(db, attempt.id)
    }

    return ExamAttemptResponse(
        id=attempt.id,
        paper=paper,
        questions=[ExamQuestionResponse.model_validate(question) for question in questions],
        answers=answers,
        total_questions=attempt.total_questions,
        total_marks=attempt.total_marks,
        started_at=attempt.started_at,
        submitted_at=attempt.submitted_at,
        status=attempt.status,
    )


def _review_response(
    *,
    questions: list[ExamQuestion],
    answers: dict[str, ExamAnswer],
    attempt: ExamAttempt,
    completed_at: datetime,
    correct_answers: int,
) -> ExamReviewResponse:
    total_marks = sum(question.marks for question in questions)
    score = attempt.score or 0
    review_questions = []
    for question in questions:
        answer = answers.get(question.id)
        selected_option = answer.selected_option if answer else None
        is_correct = bool(answer and answer.is_correct)
        review_questions.append(
            ExamReviewQuestionResponse(
                question_id=question.id,
                question_text=question.question_text,
                selected_option=selected_option,
                correct_option=question.correct_option,
                selected_answer=_answer_text(question, selected_option),
                correct_answer=_answer_text(question, question.correct_option) or "",
                explanation=question.explanation,
                is_correct=is_correct,
                marks=question.marks,
            )
        )

    return ExamReviewResponse(
        attempt_id=attempt.id,
        total_questions=len(questions),
        correct_answers=correct_answers,
        wrong_answers=len([question for question in questions if answers.get(question.id) and not answers[question.id].is_correct]),
        unanswered=len([question for question in questions if question.id not in answers]),
        score=score,
        total_marks=total_marks,
        percentage=round((score / total_marks) * 100) if total_marks else 0,
        completed_at=completed_at,
        questions=review_questions,
    )
