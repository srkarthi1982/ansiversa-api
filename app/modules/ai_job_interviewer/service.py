from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from fastapi import HTTPException, status

from app.modules.auth.models import User
from app.modules.ai_job_interviewer.models import (
    AiJobInterviewAnswer,
    AiJobInterviewQuestion,
    AiJobInterviewResult,
    AiJobInterviewSession,
)
from app.modules.ai_job_interviewer.schemas import (
    AiJobInterviewAnswerCreateRequest,
    AiJobInterviewAnswerResponse,
    AiJobInterviewAnswerUpdateRequest,
    AiJobInterviewerDashboardResponse,
    AiJobInterviewQuestionCreateRequest,
    AiJobInterviewQuestionResponse,
    AiJobInterviewQuestionUpdateRequest,
    AiJobInterviewResultCreateRequest,
    AiJobInterviewResultResponse,
    AiJobInterviewSessionCreateRequest,
    AiJobInterviewSessionResponse,
    AiJobInterviewSessionUpdateRequest,
)


def _get_owned_session(db: Session, user: User, session_id: int) -> AiJobInterviewSession:
    session = db.get(AiJobInterviewSession, session_id)
    if not session or session.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mock interview session was not found.",
        )

    return session


def _get_owned_question(db: Session, user: User, question_id: int) -> AiJobInterviewQuestion:
    question = db.get(AiJobInterviewQuestion, question_id)
    if not question or question.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mock interview question was not found.",
        )

    return question


def _get_owned_answer(db: Session, user: User, answer_id: int) -> AiJobInterviewAnswer:
    answer = db.get(AiJobInterviewAnswer, answer_id)
    if not answer or answer.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mock interview answer was not found.",
        )

    return answer


def _count_questions(db: Session, session_id: int) -> int:
    return int(
        db.execute(
            select(func.count()).select_from(AiJobInterviewQuestion).where(
                AiJobInterviewQuestion.session_id == session_id
            )
        ).scalar_one()
    )


def _count_answers(db: Session, session_id: int) -> int:
    return int(
        db.execute(
            select(func.count()).select_from(AiJobInterviewAnswer).where(
                AiJobInterviewAnswer.session_id == session_id
            )
        ).scalar_one()
    )


def _count_results(db: Session, session_id: int) -> int:
    return int(
        db.execute(
            select(func.count()).select_from(AiJobInterviewResult).where(
                AiJobInterviewResult.session_id == session_id
            )
        ).scalar_one()
    )


def _session_response(db: Session, session: AiJobInterviewSession) -> AiJobInterviewSessionResponse:
    return AiJobInterviewSessionResponse(
        id=session.id,
        title=session.title,
        role_title=session.role_title,
        company_name=session.company_name,
        experience_level=session.experience_level,
        interview_type=session.interview_type,
        target_date=session.target_date,
        status=session.status,
        question_count=_count_questions(db, session.id),
        answered_count=_count_answers(db, session.id),
        result_count=_count_results(db, session.id),
        created_at=session.created_at,
        updated_at=session.updated_at,
    )


def _question_response(
    db: Session,
    question: AiJobInterviewQuestion,
    session_title: str,
) -> AiJobInterviewQuestionResponse:
    answer_count = int(
        db.execute(
            select(func.count()).select_from(AiJobInterviewAnswer).where(
                AiJobInterviewAnswer.question_id == question.id
            )
        ).scalar_one()
    )
    return AiJobInterviewQuestionResponse(
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
    answer: AiJobInterviewAnswer,
    question_prompt: str,
) -> AiJobInterviewAnswerResponse:
    return AiJobInterviewAnswerResponse(
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


def _result_response(
    result: AiJobInterviewResult,
    session_title: str,
) -> AiJobInterviewResultResponse:
    return AiJobInterviewResultResponse(
        id=result.id,
        session_id=result.session_id,
        session_title=session_title,
        progress_score=result.progress_score,
        strengths=result.strengths,
        improvements=result.improvements,
        next_steps=result.next_steps,
        created_at=result.created_at,
        updated_at=result.updated_at,
    )


def list_sessions(db: Session, user: User) -> list[AiJobInterviewSessionResponse]:
    sessions = list(
        db.execute(
            select(AiJobInterviewSession)
            .where(AiJobInterviewSession.owner_id == user.id)
            .order_by(AiJobInterviewSession.updated_at.desc(), AiJobInterviewSession.title.asc())
        )
        .scalars()
        .all()
    )

    return [_session_response(db, session) for session in sessions]


def create_session(
    db: Session,
    user: User,
    payload: AiJobInterviewSessionCreateRequest,
) -> AiJobInterviewSessionResponse:
    session = AiJobInterviewSession(
        owner_id=user.id,
        title=payload.title,
        role_title=payload.role_title,
        company_name=payload.company_name,
        experience_level=payload.experience_level,
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
    payload: AiJobInterviewSessionUpdateRequest,
) -> AiJobInterviewSessionResponse:
    session = _get_owned_session(db, user, session_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(session, field, value)
    db.commit()
    db.refresh(session)

    return _session_response(db, session)


def delete_session(db: Session, user: User, session_id: int) -> None:
    session = _get_owned_session(db, user, session_id)
    db.execute(delete(AiJobInterviewResult).where(AiJobInterviewResult.session_id == session.id))
    db.execute(delete(AiJobInterviewAnswer).where(AiJobInterviewAnswer.session_id == session.id))
    db.execute(delete(AiJobInterviewQuestion).where(AiJobInterviewQuestion.session_id == session.id))
    db.delete(session)
    db.commit()


def list_questions(db: Session, user: User) -> list[AiJobInterviewQuestionResponse]:
    rows = db.execute(
        select(AiJobInterviewQuestion, AiJobInterviewSession.title)
        .join(AiJobInterviewSession, AiJobInterviewSession.id == AiJobInterviewQuestion.session_id)
        .where(AiJobInterviewQuestion.owner_id == user.id)
        .order_by(AiJobInterviewQuestion.position.asc(), AiJobInterviewQuestion.updated_at.desc())
    ).all()

    return [_question_response(db, question, title) for question, title in rows]


def create_question(
    db: Session,
    user: User,
    payload: AiJobInterviewQuestionCreateRequest,
) -> AiJobInterviewQuestionResponse:
    session = _get_owned_session(db, user, payload.session_id)
    question = AiJobInterviewQuestion(
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
    payload: AiJobInterviewQuestionUpdateRequest,
) -> AiJobInterviewQuestionResponse:
    question = _get_owned_question(db, user, question_id)
    session = _get_owned_session(db, user, question.session_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(question, field, value)
    db.commit()
    db.refresh(question)

    return _question_response(db, question, session.title)


def delete_question(db: Session, user: User, question_id: int) -> None:
    question = _get_owned_question(db, user, question_id)
    db.execute(delete(AiJobInterviewAnswer).where(AiJobInterviewAnswer.question_id == question.id))
    db.delete(question)
    db.commit()


def list_answers(db: Session, user: User) -> list[AiJobInterviewAnswerResponse]:
    rows = db.execute(
        select(AiJobInterviewAnswer, AiJobInterviewQuestion.prompt)
        .join(AiJobInterviewQuestion, AiJobInterviewQuestion.id == AiJobInterviewAnswer.question_id)
        .where(AiJobInterviewAnswer.owner_id == user.id)
        .order_by(AiJobInterviewAnswer.updated_at.desc())
    ).all()

    return [_answer_response(answer, prompt) for answer, prompt in rows]


def create_answer(
    db: Session,
    user: User,
    payload: AiJobInterviewAnswerCreateRequest,
) -> AiJobInterviewAnswerResponse:
    question = _get_owned_question(db, user, payload.question_id)
    answer = AiJobInterviewAnswer(
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
    payload: AiJobInterviewAnswerUpdateRequest,
) -> AiJobInterviewAnswerResponse:
    answer = _get_owned_answer(db, user, answer_id)
    question = _get_owned_question(db, user, answer.question_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(answer, field, value)
    db.commit()
    db.refresh(answer)

    return _answer_response(answer, question.prompt)


def list_results(db: Session, user: User) -> list[AiJobInterviewResultResponse]:
    rows = db.execute(
        select(AiJobInterviewResult, AiJobInterviewSession.title)
        .join(AiJobInterviewSession, AiJobInterviewSession.id == AiJobInterviewResult.session_id)
        .where(AiJobInterviewResult.owner_id == user.id)
        .order_by(AiJobInterviewResult.updated_at.desc())
    ).all()

    return [_result_response(result, title) for result, title in rows]


def create_result(
    db: Session,
    user: User,
    payload: AiJobInterviewResultCreateRequest,
) -> AiJobInterviewResultResponse:
    session = _get_owned_session(db, user, payload.session_id)
    result = AiJobInterviewResult(
        owner_id=user.id,
        session_id=session.id,
        progress_score=payload.progress_score,
        strengths=payload.strengths,
        improvements=payload.improvements,
        next_steps=payload.next_steps,
    )
    session.status = "completed"
    db.add(result)
    db.commit()
    db.refresh(result)

    return _result_response(result, session.title)


def get_dashboard(db: Session, user: User) -> AiJobInterviewerDashboardResponse:
    sessions = list_sessions(db, user)
    results = list_results(db, user)
    progress_scores = [result.progress_score for result in results]

    return AiJobInterviewerDashboardResponse(
        sessions=sessions,
        questions=list_questions(db, user),
        answers=list_answers(db, user),
        results=results,
        active_session_count=len(
            [session for session in sessions if session.status == "inProgress"]
        ),
        completed_session_count=len(
            [session for session in sessions if session.status == "completed"]
        ),
        answered_question_count=sum(session.answered_count for session in sessions),
        average_progress_score=round(sum(progress_scores) / len(progress_scores))
        if progress_scores
        else 0,
    )
