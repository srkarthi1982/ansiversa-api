from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.email_assistant.db import get_email_assistant_db
from app.modules.email_assistant.schemas import (
    EmailAssistantDashboardResponse,
    EmailDraftCreateRequest,
    EmailDraftResponse,
    EmailDraftUpdateRequest,
    EmailHistoryCreateRequest,
    EmailHistoryResponse,
    EmailHistoryUpdateRequest,
    EmailProjectCreateRequest,
    EmailProjectResponse,
    EmailProjectUpdateRequest,
    EmailTemplateCreateRequest,
    EmailTemplateResponse,
    EmailTemplateUpdateRequest,
)
from app.modules.email_assistant.service import (
    create_draft,
    create_history_item,
    create_project,
    create_template,
    delete_draft,
    delete_history_item,
    delete_project,
    delete_template,
    get_dashboard,
    update_draft,
    update_history_item,
    update_project,
    update_template,
)

router = APIRouter()


@router.get("/dashboard", response_model=EmailAssistantDashboardResponse)
def get_email_assistant_dashboard(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_email_assistant_db)],
) -> EmailAssistantDashboardResponse:
    return get_dashboard(db, current_user)


@router.post("/projects", response_model=EmailProjectResponse, status_code=status.HTTP_201_CREATED)
def create_email_project(
    payload: EmailProjectCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_email_assistant_db)],
) -> EmailProjectResponse:
    return create_project(db, current_user, payload)


@router.put("/projects/{project_id}", response_model=EmailProjectResponse)
def update_email_project(
    project_id: Annotated[int, Path(gt=0)],
    payload: EmailProjectUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_email_assistant_db)],
) -> EmailProjectResponse:
    return update_project(db, current_user, project_id, payload)


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_email_project(
    project_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_email_assistant_db)],
) -> None:
    delete_project(db, current_user, project_id)


@router.post("/drafts", response_model=EmailDraftResponse, status_code=status.HTTP_201_CREATED)
def create_email_draft(
    payload: EmailDraftCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_email_assistant_db)],
) -> EmailDraftResponse:
    return create_draft(db, current_user, payload)


@router.put("/drafts/{draft_id}", response_model=EmailDraftResponse)
def update_email_draft(
    draft_id: Annotated[int, Path(gt=0)],
    payload: EmailDraftUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_email_assistant_db)],
) -> EmailDraftResponse:
    return update_draft(db, current_user, draft_id, payload)


@router.delete("/drafts/{draft_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_email_draft(
    draft_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_email_assistant_db)],
) -> None:
    delete_draft(db, current_user, draft_id)


@router.post(
    "/templates",
    response_model=EmailTemplateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_email_template(
    payload: EmailTemplateCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_email_assistant_db)],
) -> EmailTemplateResponse:
    return create_template(db, current_user, payload)


@router.put("/templates/{template_id}", response_model=EmailTemplateResponse)
def update_email_template(
    template_id: Annotated[int, Path(gt=0)],
    payload: EmailTemplateUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_email_assistant_db)],
) -> EmailTemplateResponse:
    return update_template(db, current_user, template_id, payload)


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_email_template(
    template_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_email_assistant_db)],
) -> None:
    delete_template(db, current_user, template_id)


@router.post("/history", response_model=EmailHistoryResponse, status_code=status.HTTP_201_CREATED)
def create_email_history_item(
    payload: EmailHistoryCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_email_assistant_db)],
) -> EmailHistoryResponse:
    return create_history_item(db, current_user, payload)


@router.put("/history/{history_id}", response_model=EmailHistoryResponse)
def update_email_history_item(
    history_id: Annotated[int, Path(gt=0)],
    payload: EmailHistoryUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_email_assistant_db)],
) -> EmailHistoryResponse:
    return update_history_item(db, current_user, history_id, payload)


@router.delete("/history/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_email_history_item(
    history_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_email_assistant_db)],
) -> None:
    delete_history_item(db, current_user, history_id)
