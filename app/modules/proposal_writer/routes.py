from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.proposal_writer.db import get_proposal_writer_db
from app.modules.proposal_writer.schemas import (
    ProposalDraftCreateRequest,
    ProposalDraftDetailResponse,
    ProposalDraftUpdateRequest,
    ProposalHistoryCreateRequest,
    ProposalHistorySummaryResponse,
    ProposalProjectCreateRequest,
    ProposalProjectDetailResponse,
    ProposalProjectUpdateRequest,
    ProposalSectionCreateRequest,
    ProposalSectionDetailResponse,
    ProposalSectionUpdateRequest,
    ProposalWriterDashboardResponse,
)
from app.modules.proposal_writer.service import (
    create_draft,
    create_history_item,
    create_project,
    create_section,
    delete_draft,
    delete_history_item,
    delete_project,
    delete_section,
    get_dashboard,
    get_draft,
    get_project,
    get_section,
    update_draft,
    update_project,
    update_section,
)

router = APIRouter()


@router.get("/dashboard", response_model=ProposalWriterDashboardResponse)
def get_proposal_writer_dashboard(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_proposal_writer_db)],
) -> ProposalWriterDashboardResponse:
    return get_dashboard(db, current_user)


@router.post(
    "/projects",
    response_model=ProposalProjectDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_proposal_project(
    payload: ProposalProjectCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_proposal_writer_db)],
) -> ProposalProjectDetailResponse:
    return create_project(db, current_user, payload)


@router.get("/projects/{project_id}", response_model=ProposalProjectDetailResponse)
def get_proposal_project(
    project_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_proposal_writer_db)],
) -> ProposalProjectDetailResponse:
    return get_project(db, current_user, project_id)


@router.put("/projects/{project_id}", response_model=ProposalProjectDetailResponse)
def update_proposal_project(
    project_id: Annotated[int, Path(gt=0)],
    payload: ProposalProjectUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_proposal_writer_db)],
) -> ProposalProjectDetailResponse:
    return update_project(db, current_user, project_id, payload)


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_proposal_project(
    project_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_proposal_writer_db)],
) -> None:
    delete_project(db, current_user, project_id)


@router.post(
    "/sections",
    response_model=ProposalSectionDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_proposal_section(
    payload: ProposalSectionCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_proposal_writer_db)],
) -> ProposalSectionDetailResponse:
    return create_section(db, current_user, payload)


@router.get("/sections/{section_id}", response_model=ProposalSectionDetailResponse)
def get_proposal_section(
    section_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_proposal_writer_db)],
) -> ProposalSectionDetailResponse:
    return get_section(db, current_user, section_id)


@router.put("/sections/{section_id}", response_model=ProposalSectionDetailResponse)
def update_proposal_section(
    section_id: Annotated[int, Path(gt=0)],
    payload: ProposalSectionUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_proposal_writer_db)],
) -> ProposalSectionDetailResponse:
    return update_section(db, current_user, section_id, payload)


@router.delete("/sections/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_proposal_section(
    section_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_proposal_writer_db)],
) -> None:
    delete_section(db, current_user, section_id)


@router.post(
    "/drafts",
    response_model=ProposalDraftDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_proposal_draft(
    payload: ProposalDraftCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_proposal_writer_db)],
) -> ProposalDraftDetailResponse:
    return create_draft(db, current_user, payload)


@router.get("/drafts/{draft_id}", response_model=ProposalDraftDetailResponse)
def get_proposal_draft(
    draft_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_proposal_writer_db)],
) -> ProposalDraftDetailResponse:
    return get_draft(db, current_user, draft_id)


@router.put("/drafts/{draft_id}", response_model=ProposalDraftDetailResponse)
def update_proposal_draft(
    draft_id: Annotated[int, Path(gt=0)],
    payload: ProposalDraftUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_proposal_writer_db)],
) -> ProposalDraftDetailResponse:
    return update_draft(db, current_user, draft_id, payload)


@router.delete("/drafts/{draft_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_proposal_draft(
    draft_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_proposal_writer_db)],
) -> None:
    delete_draft(db, current_user, draft_id)


@router.post(
    "/history",
    response_model=ProposalHistorySummaryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_proposal_history_item(
    payload: ProposalHistoryCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_proposal_writer_db)],
) -> ProposalHistorySummaryResponse:
    return create_history_item(db, current_user, payload)


@router.delete("/history/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_proposal_history_item(
    history_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_proposal_writer_db)],
) -> None:
    delete_history_item(db, current_user, history_id)
