from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.interview_coach.db import get_interview_coach_db
from app.modules.interview_coach.schemas import (
    InterviewAnswerCreateRequest,
    InterviewAnswerListResponse,
    InterviewAnswerResponse,
    InterviewAnswerUpdateRequest,
    InterviewCoachDashboardResponse,
    InterviewQuestionCreateRequest,
    InterviewQuestionListResponse,
    InterviewQuestionResponse,
    InterviewQuestionUpdateRequest,
    InterviewReviewCreateRequest,
    InterviewReviewListResponse,
    InterviewReviewResponse,
    InterviewSessionCreateRequest,
    InterviewSessionListResponse,
    InterviewSessionResponse,
    InterviewSessionUpdateRequest,
)
from app.modules.interview_coach.service import (
    create_answer,
    create_question,
    create_review,
    create_session,
    delete_question,
    delete_session,
    get_dashboard,
    list_answers,
    list_questions,
    list_reviews,
    list_sessions,
    update_answer,
    update_question,
    update_session,
)

router = APIRouter()


@router.get("/dashboard", response_model=InterviewCoachDashboardResponse)
def get_interview_coach_dashboard(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_interview_coach_db)],
) -> InterviewCoachDashboardResponse:
    return get_dashboard(db, current_user)


@router.get("/sessions", response_model=InterviewSessionListResponse)
def get_interview_sessions(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_interview_coach_db)],
) -> InterviewSessionListResponse:
    return InterviewSessionListResponse(items=list_sessions(db, current_user))


@router.post(
    "/sessions",
    response_model=InterviewSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_interview_session(
    payload: InterviewSessionCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_interview_coach_db)],
) -> InterviewSessionResponse:
    return create_session(db, current_user, payload)


@router.put("/sessions/{session_id}", response_model=InterviewSessionResponse)
def update_interview_session(
    session_id: Annotated[int, Path(gt=0)],
    payload: InterviewSessionUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_interview_coach_db)],
) -> InterviewSessionResponse:
    return update_session(db, current_user, session_id, payload)


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interview_session(
    session_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_interview_coach_db)],
) -> None:
    delete_session(db, current_user, session_id)


@router.get("/questions", response_model=InterviewQuestionListResponse)
def get_interview_questions(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_interview_coach_db)],
) -> InterviewQuestionListResponse:
    return InterviewQuestionListResponse(items=list_questions(db, current_user))


@router.post(
    "/questions",
    response_model=InterviewQuestionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_interview_question(
    payload: InterviewQuestionCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_interview_coach_db)],
) -> InterviewQuestionResponse:
    return create_question(db, current_user, payload)


@router.put("/questions/{question_id}", response_model=InterviewQuestionResponse)
def update_interview_question(
    question_id: Annotated[int, Path(gt=0)],
    payload: InterviewQuestionUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_interview_coach_db)],
) -> InterviewQuestionResponse:
    return update_question(db, current_user, question_id, payload)


@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interview_question(
    question_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_interview_coach_db)],
) -> None:
    delete_question(db, current_user, question_id)


@router.get("/answers", response_model=InterviewAnswerListResponse)
def get_interview_answers(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_interview_coach_db)],
) -> InterviewAnswerListResponse:
    return InterviewAnswerListResponse(items=list_answers(db, current_user))


@router.post(
    "/answers",
    response_model=InterviewAnswerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_interview_answer(
    payload: InterviewAnswerCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_interview_coach_db)],
) -> InterviewAnswerResponse:
    return create_answer(db, current_user, payload)


@router.put("/answers/{answer_id}", response_model=InterviewAnswerResponse)
def update_interview_answer(
    answer_id: Annotated[int, Path(gt=0)],
    payload: InterviewAnswerUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_interview_coach_db)],
) -> InterviewAnswerResponse:
    return update_answer(db, current_user, answer_id, payload)


@router.get("/reviews", response_model=InterviewReviewListResponse)
def get_interview_reviews(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_interview_coach_db)],
) -> InterviewReviewListResponse:
    return InterviewReviewListResponse(items=list_reviews(db, current_user))


@router.post(
    "/reviews",
    response_model=InterviewReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_interview_review(
    payload: InterviewReviewCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_interview_coach_db)],
) -> InterviewReviewResponse:
    return create_review(db, current_user, payload)
