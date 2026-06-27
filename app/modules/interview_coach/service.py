from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from fastapi import HTTPException, status

from app.modules.auth.models import User
from app.modules.interview_coach.models import (
    InterviewAnswer,
    InterviewQuestion,
    InterviewReview,
    InterviewSession,
)
from app.modules.interview_coach.schemas import (
    InterviewAnswerCreateRequest,
    InterviewAnswerResponse,
    InterviewAnswerUpdateRequest,
    InterviewCoachDashboardResponse,
    InterviewQuestionCreateRequest,
    InterviewQuestionResponse,
    InterviewQuestionUpdateRequest,
    InterviewReviewCreateRequest,
    InterviewReviewResponse,
    InterviewSessionCreateRequest,
    InterviewSessionResponse,
    InterviewSessionUpdateRequest,
)


def _get_owned_session(db: Session, user: User, session_id: int) -> InterviewSession:
    session = db.get(InterviewSession, session_id)
    if not session or session.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session was not found.",
        )

    return session


def _get_owned_question(db: Session, user: User, question_id: int) -> InterviewQuestion:
    question = db.get(InterviewQuestion, question_id)
    if not question or question.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview question was not found.",
        )

    return question


def _get_owned_answer(db: Session, user: User, answer_id: int) -> InterviewAnswer:
    answer = db.get(InterviewAnswer, answer_id)
    if not answer or answer.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview answer was not found.",
        )

    return answer


def _count_questions(db: Session, session_id: int) -> int:
    return int(
        db.execute(
            select(func.count()).select_from(InterviewQuestion).where(
                InterviewQuestion.session_id == session_id
            )
        ).scalar_one()
    )


def _count_answers(db: Session, session_id: int) -> int:
    return int(
        db.execute(
            select(func.count()).select_from(InterviewAnswer).where(
                InterviewAnswer.session_id == session_id
            )
        ).scalar_one()
    )


def _count_reviews(db: Session, session_id: int) -> int:
    return int(
        db.execute(
            select(func.count()).select_from(InterviewReview).where(
                InterviewReview.session_id == session_id
            )
        ).scalar_one()
    )


def _session_response(db: Session, session: InterviewSession) -> InterviewSessionResponse:
    return InterviewSessionResponse(
        id=session.id,
        title=session.title,
        role_title=session.role_title,
        company_name=session.company_name,
        interview_type=session.interview_type,
        target_date=session.target_date,
        status=session.status,
        question_count=_count_questions(db, session.id),
        answered_count=_count_answers(db, session.id),
        review_count=_count_reviews(db, session.id),
        created_at=session.created_at,
        updated_at=session.updated_at,
    )


def _question_response(
    db: Session,
    question: InterviewQuestion,
    session_title: str,
) -> InterviewQuestionResponse:
    answer_count = int(
        db.execute(
            select(func.count()).select_from(InterviewAnswer).where(
                InterviewAnswer.question_id == question.id
            )
        ).scalar_one()
    )
    return InterviewQuestionResponse(
        id=question.id,
        session_id=question.session_id,
        session_title=session_title,
        prompt=question.prompt,
        category=question.category,
        position=question.position,
        has_answer=answer_count > 0,
        created_at=question.created_at,
        updated_at=question.updated_at,
    )


def _answer_response(
    answer: InterviewAnswer,
    question_prompt: str,
) -> InterviewAnswerResponse:
    return InterviewAnswerResponse(
        id=answer.id,
        session_id=answer.session_id,
        question_id=answer.question_id,
        question_prompt=question_prompt,
        answer_text=answer.answer_text,
        confidence=answer.confidence,
        status=answer.status,
        created_at=answer.created_at,
        updated_at=answer.updated_at,
    )


def _review_response(
    review: InterviewReview,
    session_title: str,
) -> InterviewReviewResponse:
    return InterviewReviewResponse(
        id=review.id,
        session_id=review.session_id,
        session_title=session_title,
        readiness_score=review.readiness_score,
        strengths=review.strengths,
        improvements=review.improvements,
        next_steps=review.next_steps,
        created_at=review.created_at,
        updated_at=review.updated_at,
    )


def list_sessions(db: Session, user: User) -> list[InterviewSessionResponse]:
    sessions = list(
        db.execute(
            select(InterviewSession)
            .where(InterviewSession.owner_id == user.id)
            .order_by(InterviewSession.updated_at.desc(), InterviewSession.title.asc())
        )
        .scalars()
        .all()
    )

    return [_session_response(db, session) for session in sessions]


def create_session(
    db: Session,
    user: User,
    payload: InterviewSessionCreateRequest,
) -> InterviewSessionResponse:
    session = InterviewSession(
        owner_id=user.id,
        title=payload.title,
        role_title=payload.role_title,
        company_name=payload.company_name,
        interview_type=payload.interview_type,
        target_date=payload.target_date,
        status="draft",
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return _session_response(db, session)


def update_session(
    db: Session,
    user: User,
    session_id: int,
    payload: InterviewSessionUpdateRequest,
) -> InterviewSessionResponse:
    session = _get_owned_session(db, user, session_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(session, field, value)
    db.commit()
    db.refresh(session)

    return _session_response(db, session)


def delete_session(db: Session, user: User, session_id: int) -> None:
    session = _get_owned_session(db, user, session_id)
    db.execute(delete(InterviewReview).where(InterviewReview.session_id == session.id))
    db.execute(delete(InterviewAnswer).where(InterviewAnswer.session_id == session.id))
    db.execute(delete(InterviewQuestion).where(InterviewQuestion.session_id == session.id))
    db.delete(session)
    db.commit()


def list_questions(db: Session, user: User) -> list[InterviewQuestionResponse]:
    rows = db.execute(
        select(InterviewQuestion, InterviewSession.title)
        .join(InterviewSession, InterviewSession.id == InterviewQuestion.session_id)
        .where(InterviewQuestion.owner_id == user.id)
        .order_by(InterviewQuestion.position.asc(), InterviewQuestion.updated_at.desc())
    ).all()

    return [_question_response(db, question, title) for question, title in rows]


def create_question(
    db: Session,
    user: User,
    payload: InterviewQuestionCreateRequest,
) -> InterviewQuestionResponse:
    session = _get_owned_session(db, user, payload.session_id)
    question = InterviewQuestion(
        owner_id=user.id,
        session_id=session.id,
        prompt=payload.prompt,
        category=payload.category,
        position=payload.position,
    )
    if session.status == "draft":
        session.status = "inProgress"
    db.add(question)
    db.commit()
    db.refresh(question)

    return _question_response(db, question, session.title)


def update_question(
    db: Session,
    user: User,
    question_id: int,
    payload: InterviewQuestionUpdateRequest,
) -> InterviewQuestionResponse:
    question = _get_owned_question(db, user, question_id)
    session = _get_owned_session(db, user, question.session_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(question, field, value)
    db.commit()
    db.refresh(question)

    return _question_response(db, question, session.title)


def delete_question(db: Session, user: User, question_id: int) -> None:
    question = _get_owned_question(db, user, question_id)
    db.execute(delete(InterviewAnswer).where(InterviewAnswer.question_id == question.id))
    db.delete(question)
    db.commit()


def list_answers(db: Session, user: User) -> list[InterviewAnswerResponse]:
    rows = db.execute(
        select(InterviewAnswer, InterviewQuestion.prompt)
        .join(InterviewQuestion, InterviewQuestion.id == InterviewAnswer.question_id)
        .where(InterviewAnswer.owner_id == user.id)
        .order_by(InterviewAnswer.updated_at.desc())
    ).all()

    return [_answer_response(answer, prompt) for answer, prompt in rows]


def create_answer(
    db: Session,
    user: User,
    payload: InterviewAnswerCreateRequest,
) -> InterviewAnswerResponse:
    question = _get_owned_question(db, user, payload.question_id)
    answer = InterviewAnswer(
        owner_id=user.id,
        session_id=question.session_id,
        question_id=question.id,
        answer_text=payload.answer_text,
        confidence=payload.confidence,
        status=payload.status,
    )
    session = _get_owned_session(db, user, question.session_id)
    if session.status == "draft":
        session.status = "inProgress"
    db.add(answer)
    db.commit()
    db.refresh(answer)

    return _answer_response(answer, question.prompt)


def update_answer(
    db: Session,
    user: User,
    answer_id: int,
    payload: InterviewAnswerUpdateRequest,
) -> InterviewAnswerResponse:
    answer = _get_owned_answer(db, user, answer_id)
    question = _get_owned_question(db, user, answer.question_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(answer, field, value)
    db.commit()
    db.refresh(answer)

    return _answer_response(answer, question.prompt)


def list_reviews(db: Session, user: User) -> list[InterviewReviewResponse]:
    rows = db.execute(
        select(InterviewReview, InterviewSession.title)
        .join(InterviewSession, InterviewSession.id == InterviewReview.session_id)
        .where(InterviewReview.owner_id == user.id)
        .order_by(InterviewReview.updated_at.desc())
    ).all()

    return [_review_response(review, title) for review, title in rows]


def create_review(
    db: Session,
    user: User,
    payload: InterviewReviewCreateRequest,
) -> InterviewReviewResponse:
    session = _get_owned_session(db, user, payload.session_id)
    review = InterviewReview(
        owner_id=user.id,
        session_id=session.id,
        readiness_score=payload.readiness_score,
        strengths=payload.strengths,
        improvements=payload.improvements,
        next_steps=payload.next_steps,
    )
    session.status = "completed"
    db.add(review)
    db.commit()
    db.refresh(review)

    return _review_response(review, session.title)


def get_dashboard(db: Session, user: User) -> InterviewCoachDashboardResponse:
    sessions = list_sessions(db, user)
    reviews = list_reviews(db, user)
    readiness_scores = [review.readiness_score for review in reviews]

    return InterviewCoachDashboardResponse(
        sessions=sessions,
        questions=list_questions(db, user),
        answers=list_answers(db, user),
        reviews=reviews,
        active_session_count=len(
            [session for session in sessions if session.status == "inProgress"]
        ),
        completed_session_count=len(
            [session for session in sessions if session.status == "completed"]
        ),
        answered_question_count=sum(session.answered_count for session in sessions),
        average_readiness_score=round(sum(readiness_scores) / len(readiness_scores))
        if readiness_scores
        else 0,
    )
