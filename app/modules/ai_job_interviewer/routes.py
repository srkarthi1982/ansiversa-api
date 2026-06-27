from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.ai_job_interviewer.db import get_ai_job_interviewer_db
from app.modules.ai_job_interviewer.schemas import (
    AiJobInterviewAnswerCreateRequest,
    AiJobInterviewAnswerListResponse,
    AiJobInterviewAnswerResponse,
    AiJobInterviewAnswerUpdateRequest,
    AiJobInterviewerDashboardResponse,
    AiJobInterviewQuestionCreateRequest,
    AiJobInterviewQuestionListResponse,
    AiJobInterviewQuestionResponse,
    AiJobInterviewQuestionUpdateRequest,
    AiJobInterviewResultCreateRequest,
    AiJobInterviewResultListResponse,
    AiJobInterviewResultResponse,
    AiJobInterviewSessionCreateRequest,
    AiJobInterviewSessionListResponse,
    AiJobInterviewSessionResponse,
    AiJobInterviewSessionUpdateRequest,
)
from app.modules.ai_job_interviewer.service import (
    create_answer,
    create_question,
    create_result,
    create_session,
    delete_question,
    delete_session,
    get_dashboard,
    list_answers,
    list_questions,
    list_results,
    list_sessions,
    update_answer,
    update_question,
    update_session,
)

router = APIRouter()


@router.get("/dashboard", response_model=AiJobInterviewerDashboardResponse)
def get_ai_job_interviewer_dashboard(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_ai_job_interviewer_db)],
) -> AiJobInterviewerDashboardResponse:
    return get_dashboard(db, current_user)


@router.get("/sessions", response_model=AiJobInterviewSessionListResponse)
def get_interview_sessions(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_ai_job_interviewer_db)],
) -> AiJobInterviewSessionListResponse:
    return AiJobInterviewSessionListResponse(items=list_sessions(db, current_user))


@router.post(
    "/sessions",
    response_model=AiJobInterviewSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_interview_session(
    payload: AiJobInterviewSessionCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_ai_job_interviewer_db)],
) -> AiJobInterviewSessionResponse:
    return create_session(db, current_user, payload)


@router.put("/sessions/{session_id}", response_model=AiJobInterviewSessionResponse)
def update_interview_session(
    session_id: Annotated[int, Path(gt=0)],
    payload: AiJobInterviewSessionUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_ai_job_interviewer_db)],
) -> AiJobInterviewSessionResponse:
    return update_session(db, current_user, session_id, payload)


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interview_session(
    session_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_ai_job_interviewer_db)],
) -> None:
    delete_session(db, current_user, session_id)


@router.get("/questions", response_model=AiJobInterviewQuestionListResponse)
def get_interview_questions(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_ai_job_interviewer_db)],
) -> AiJobInterviewQuestionListResponse:
    return AiJobInterviewQuestionListResponse(items=list_questions(db, current_user))


@router.post(
    "/questions",
    response_model=AiJobInterviewQuestionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_interview_question(
    payload: AiJobInterviewQuestionCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_ai_job_interviewer_db)],
) -> AiJobInterviewQuestionResponse:
    return create_question(db, current_user, payload)


@router.put("/questions/{question_id}", response_model=AiJobInterviewQuestionResponse)
def update_interview_question(
    question_id: Annotated[int, Path(gt=0)],
    payload: AiJobInterviewQuestionUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_ai_job_interviewer_db)],
) -> AiJobInterviewQuestionResponse:
    return update_question(db, current_user, question_id, payload)


@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interview_question(
    question_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_ai_job_interviewer_db)],
) -> None:
    delete_question(db, current_user, question_id)


@router.get("/answers", response_model=AiJobInterviewAnswerListResponse)
def get_interview_answers(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_ai_job_interviewer_db)],
) -> AiJobInterviewAnswerListResponse:
    return AiJobInterviewAnswerListResponse(items=list_answers(db, current_user))


@router.post(
    "/answers",
    response_model=AiJobInterviewAnswerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_interview_answer(
    payload: AiJobInterviewAnswerCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_ai_job_interviewer_db)],
) -> AiJobInterviewAnswerResponse:
    return create_answer(db, current_user, payload)


@router.put("/answers/{answer_id}", response_model=AiJobInterviewAnswerResponse)
def update_interview_answer(
    answer_id: Annotated[int, Path(gt=0)],
    payload: AiJobInterviewAnswerUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_ai_job_interviewer_db)],
) -> AiJobInterviewAnswerResponse:
    return update_answer(db, current_user, answer_id, payload)


@router.get("/results", response_model=AiJobInterviewResultListResponse)
def get_interview_results(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_ai_job_interviewer_db)],
) -> AiJobInterviewResultListResponse:
    return AiJobInterviewResultListResponse(items=list_results(db, current_user))


@router.post(
    "/results",
    response_model=AiJobInterviewResultResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_interview_result(
    payload: AiJobInterviewResultCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_ai_job_interviewer_db)],
) -> AiJobInterviewResultResponse:
    return create_result(db, current_user, payload)
