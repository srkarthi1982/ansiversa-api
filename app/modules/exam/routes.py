from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.exam.db import get_exam_db
from app.modules.exam.schemas import (
    ExamAttemptAnswersRequest,
    ExamAttemptResponse,
    ExamPaperCreateRequest,
    ExamPaperDetailResponse,
    ExamPaperListResponse,
    ExamPaperResponse,
    ExamPaperUpdateRequest,
    ExamQuestionCreateRequest,
    ExamQuestionListResponse,
    ExamQuestionResponse,
    ExamQuestionUpdateRequest,
    ExamReviewResponse,
)
from app.modules.exam.service import (
    create_paper,
    create_question,
    delete_paper,
    delete_question,
    get_attempt,
    get_paper_detail,
    get_review,
    list_papers,
    list_questions,
    save_answers,
    start_attempt,
    submit_attempt,
    update_paper,
    update_question,
)

router = APIRouter()


@router.get("/papers", response_model=ExamPaperListResponse)
def get_exam_papers(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_exam_db)],
) -> ExamPaperListResponse:
    return ExamPaperListResponse(items=list_papers(db, current_user))


@router.post("/papers", response_model=ExamPaperResponse, status_code=status.HTTP_201_CREATED)
def create_exam_paper(
    payload: ExamPaperCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_exam_db)],
) -> ExamPaperResponse:
    return create_paper(db, current_user, payload)


@router.get("/papers/{paper_id}", response_model=ExamPaperDetailResponse)
def get_exam_paper(
    paper_id: Annotated[str, Path(min_length=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_exam_db)],
) -> ExamPaperDetailResponse:
    paper, questions = get_paper_detail(db, current_user, paper_id)
    return ExamPaperDetailResponse(paper=paper, questions=questions)


@router.patch("/papers/{paper_id}", response_model=ExamPaperResponse)
def update_exam_paper(
    paper_id: Annotated[str, Path(min_length=1)],
    payload: ExamPaperUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_exam_db)],
) -> ExamPaperResponse:
    return update_paper(db, current_user, paper_id, payload)


@router.delete("/papers/{paper_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exam_paper(
    paper_id: Annotated[str, Path(min_length=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_exam_db)],
) -> None:
    delete_paper(db, current_user, paper_id)


@router.get("/papers/{paper_id}/questions", response_model=ExamQuestionListResponse)
def get_exam_questions(
    paper_id: Annotated[str, Path(min_length=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_exam_db)],
) -> ExamQuestionListResponse:
    return ExamQuestionListResponse(items=list_questions(db, current_user, paper_id))


@router.post(
    "/papers/{paper_id}/questions",
    response_model=ExamQuestionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_exam_question(
    paper_id: Annotated[str, Path(min_length=1)],
    payload: ExamQuestionCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_exam_db)],
) -> ExamQuestionResponse:
    return create_question(db, current_user, paper_id, payload)


@router.patch("/questions/{question_id}", response_model=ExamQuestionResponse)
def update_exam_question(
    question_id: Annotated[str, Path(min_length=1)],
    payload: ExamQuestionUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_exam_db)],
) -> ExamQuestionResponse:
    return update_question(db, current_user, question_id, payload)


@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exam_question(
    question_id: Annotated[str, Path(min_length=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_exam_db)],
) -> None:
    delete_question(db, current_user, question_id)


@router.post(
    "/papers/{paper_id}/attempts",
    response_model=ExamAttemptResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_exam_attempt(
    paper_id: Annotated[str, Path(min_length=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_exam_db)],
) -> ExamAttemptResponse:
    return start_attempt(db, current_user, paper_id)


@router.get("/attempts/{attempt_id}", response_model=ExamAttemptResponse)
def get_exam_attempt(
    attempt_id: Annotated[str, Path(min_length=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_exam_db)],
) -> ExamAttemptResponse:
    return get_attempt(db, current_user, attempt_id)


@router.post("/attempts/{attempt_id}/answers", response_model=ExamAttemptResponse)
def save_exam_attempt_answers(
    attempt_id: Annotated[str, Path(min_length=1)],
    payload: ExamAttemptAnswersRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_exam_db)],
) -> ExamAttemptResponse:
    return save_answers(db, current_user, attempt_id, payload)


@router.post("/attempts/{attempt_id}/submit", response_model=ExamReviewResponse)
def submit_exam_attempt(
    attempt_id: Annotated[str, Path(min_length=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_exam_db)],
) -> ExamReviewResponse:
    return submit_attempt(db, current_user, attempt_id)


@router.get("/attempts/{attempt_id}/review", response_model=ExamReviewResponse)
def get_exam_attempt_review(
    attempt_id: Annotated[str, Path(min_length=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_exam_db)],
) -> ExamReviewResponse:
    return get_review(db, current_user, attempt_id)
