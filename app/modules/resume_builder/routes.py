from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.resume_builder.db import get_resume_builder_db
from app.modules.resume_builder.schemas import (
    ResumeBuilderDashboardResponse,
    ResumeBuilderReviewResponse,
    ResumeItemCreateRequest,
    ResumeItemListResponse,
    ResumeItemResponse,
    ResumeItemUpdateRequest,
    ResumePreviewResponse,
    ResumeProjectCreateRequest,
    ResumeProjectListResponse,
    ResumeProjectResponse,
    ResumeProjectUpdateRequest,
    ResumeSectionCreateRequest,
    ResumeSectionListResponse,
    ResumeSectionResponse,
    ResumeSectionUpdateRequest,
)
from app.modules.resume_builder.service import (
    create_item,
    create_project,
    create_section,
    delete_item,
    delete_project,
    delete_section,
    get_dashboard,
    get_preview,
    get_review,
    list_items,
    list_projects,
    list_sections,
    update_item,
    update_project,
    update_section,
)

router = APIRouter()


@router.get("/dashboard", response_model=ResumeBuilderDashboardResponse)
def get_resume_builder_dashboard(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_resume_builder_db)],
) -> ResumeBuilderDashboardResponse:
    return get_dashboard(db, current_user)


@router.get("/projects", response_model=ResumeProjectListResponse)
def get_resume_projects(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_resume_builder_db)],
) -> ResumeProjectListResponse:
    return ResumeProjectListResponse(items=list_projects(db, current_user))


@router.post(
    "/projects",
    response_model=ResumeProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_resume_project(
    payload: ResumeProjectCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_resume_builder_db)],
) -> ResumeProjectResponse:
    return create_project(db, current_user, payload)


@router.put("/projects/{project_id}", response_model=ResumeProjectResponse)
def update_resume_project(
    project_id: Annotated[str, Path(min_length=1, max_length=80)],
    payload: ResumeProjectUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_resume_builder_db)],
) -> ResumeProjectResponse:
    return update_project(db, current_user, project_id, payload)


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume_project(
    project_id: Annotated[str, Path(min_length=1, max_length=80)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_resume_builder_db)],
) -> None:
    delete_project(db, current_user, project_id)


@router.get("/sections", response_model=ResumeSectionListResponse)
def get_resume_sections(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_resume_builder_db)],
) -> ResumeSectionListResponse:
    return ResumeSectionListResponse(items=list_sections(db, current_user))


@router.post(
    "/sections",
    response_model=ResumeSectionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_resume_section(
    payload: ResumeSectionCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_resume_builder_db)],
) -> ResumeSectionResponse:
    return create_section(db, current_user, payload)


@router.put("/sections/{section_id}", response_model=ResumeSectionResponse)
def update_resume_section(
    section_id: Annotated[str, Path(min_length=1, max_length=80)],
    payload: ResumeSectionUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_resume_builder_db)],
) -> ResumeSectionResponse:
    return update_section(db, current_user, section_id, payload)


@router.delete("/sections/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume_section(
    section_id: Annotated[str, Path(min_length=1, max_length=80)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_resume_builder_db)],
) -> None:
    delete_section(db, current_user, section_id)


@router.get("/items", response_model=ResumeItemListResponse)
def get_resume_items(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_resume_builder_db)],
) -> ResumeItemListResponse:
    return ResumeItemListResponse(items=list_items(db, current_user))


@router.post(
    "/items",
    response_model=ResumeItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_resume_item(
    payload: ResumeItemCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_resume_builder_db)],
) -> ResumeItemResponse:
    return create_item(db, current_user, payload)


@router.put("/items/{item_id}", response_model=ResumeItemResponse)
def update_resume_item(
    item_id: Annotated[str, Path(min_length=1, max_length=80)],
    payload: ResumeItemUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_resume_builder_db)],
) -> ResumeItemResponse:
    return update_item(db, current_user, item_id, payload)


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume_item(
    item_id: Annotated[str, Path(min_length=1, max_length=80)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_resume_builder_db)],
) -> None:
    delete_item(db, current_user, item_id)


@router.get("/preview", response_model=ResumePreviewResponse)
def get_resume_preview(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_resume_builder_db)],
    project_id: Annotated[
        str | None,
        Query(alias="projectId", min_length=1, max_length=80),
    ] = None,
) -> ResumePreviewResponse:
    return get_preview(db, current_user, project_id)


@router.get("/review", response_model=ResumeBuilderReviewResponse)
def get_resume_review(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_resume_builder_db)],
) -> ResumeBuilderReviewResponse:
    return get_review(db, current_user)
