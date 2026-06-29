from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.presentation_designer.db import get_presentation_designer_db
from app.modules.presentation_designer.schemas import (
    PresentationAssetCreateRequest,
    PresentationAssetDetailResponse,
    PresentationAssetUpdateRequest,
    PresentationDashboardResponse,
    PresentationProjectCreateRequest,
    PresentationProjectDetailResponse,
    PresentationProjectUpdateRequest,
    PresentationReviewHistoryCreateRequest,
    PresentationReviewHistoryDetailResponse,
    PresentationReviewHistorySummaryResponse,
    PresentationReviewHistoryUpdateRequest,
    PresentationSlideCreateRequest,
    PresentationSlideDetailResponse,
    PresentationSlideUpdateRequest,
)
from app.modules.presentation_designer.service import (
    create_asset,
    create_project,
    create_review_history_item,
    create_slide,
    delete_asset,
    delete_project,
    delete_review_history_item,
    delete_slide,
    get_asset,
    get_dashboard,
    get_project,
    get_review_history_item,
    get_slide,
    update_asset,
    update_project,
    update_review_history_item,
    update_slide,
)

router = APIRouter()


@router.get("/dashboard", response_model=PresentationDashboardResponse)
def get_presentation_dashboard(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_presentation_designer_db)],
) -> PresentationDashboardResponse:
    return get_dashboard(db, current_user)


@router.post(
    "/projects",
    response_model=PresentationProjectDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_presentation_project(
    payload: PresentationProjectCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_presentation_designer_db)],
) -> PresentationProjectDetailResponse:
    return create_project(db, current_user, payload)


@router.get("/projects/{project_id}", response_model=PresentationProjectDetailResponse)
def get_presentation_project(
    project_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_presentation_designer_db)],
) -> PresentationProjectDetailResponse:
    return get_project(db, current_user, project_id)


@router.put("/projects/{project_id}", response_model=PresentationProjectDetailResponse)
def update_presentation_project(
    project_id: Annotated[int, Path(gt=0)],
    payload: PresentationProjectUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_presentation_designer_db)],
) -> PresentationProjectDetailResponse:
    return update_project(db, current_user, project_id, payload)


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_presentation_project(
    project_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_presentation_designer_db)],
) -> None:
    delete_project(db, current_user, project_id)


@router.post(
    "/slides",
    response_model=PresentationSlideDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_presentation_slide(
    payload: PresentationSlideCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_presentation_designer_db)],
) -> PresentationSlideDetailResponse:
    return create_slide(db, current_user, payload)


@router.get("/slides/{slide_id}", response_model=PresentationSlideDetailResponse)
def get_presentation_slide(
    slide_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_presentation_designer_db)],
) -> PresentationSlideDetailResponse:
    return get_slide(db, current_user, slide_id)


@router.put("/slides/{slide_id}", response_model=PresentationSlideDetailResponse)
def update_presentation_slide(
    slide_id: Annotated[int, Path(gt=0)],
    payload: PresentationSlideUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_presentation_designer_db)],
) -> PresentationSlideDetailResponse:
    return update_slide(db, current_user, slide_id, payload)


@router.delete("/slides/{slide_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_presentation_slide(
    slide_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_presentation_designer_db)],
) -> None:
    delete_slide(db, current_user, slide_id)


@router.post(
    "/assets",
    response_model=PresentationAssetDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_presentation_asset(
    payload: PresentationAssetCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_presentation_designer_db)],
) -> PresentationAssetDetailResponse:
    return create_asset(db, current_user, payload)


@router.get("/assets/{asset_id}", response_model=PresentationAssetDetailResponse)
def get_presentation_asset(
    asset_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_presentation_designer_db)],
) -> PresentationAssetDetailResponse:
    return get_asset(db, current_user, asset_id)


@router.put("/assets/{asset_id}", response_model=PresentationAssetDetailResponse)
def update_presentation_asset(
    asset_id: Annotated[int, Path(gt=0)],
    payload: PresentationAssetUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_presentation_designer_db)],
) -> PresentationAssetDetailResponse:
    return update_asset(db, current_user, asset_id, payload)


@router.delete("/assets/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_presentation_asset(
    asset_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_presentation_designer_db)],
) -> None:
    delete_asset(db, current_user, asset_id)


@router.post(
    "/review",
    response_model=PresentationReviewHistorySummaryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_presentation_review_history_item(
    payload: PresentationReviewHistoryCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_presentation_designer_db)],
) -> PresentationReviewHistorySummaryResponse:
    return create_review_history_item(db, current_user, payload)


@router.get("/review/{review_id}", response_model=PresentationReviewHistoryDetailResponse)
def get_presentation_review_history_item(
    review_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_presentation_designer_db)],
) -> PresentationReviewHistoryDetailResponse:
    return get_review_history_item(db, current_user, review_id)


@router.put("/review/{review_id}", response_model=PresentationReviewHistoryDetailResponse)
def update_presentation_review_history_item(
    review_id: Annotated[int, Path(gt=0)],
    payload: PresentationReviewHistoryUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_presentation_designer_db)],
) -> PresentationReviewHistoryDetailResponse:
    return update_review_history_item(db, current_user, review_id, payload)


@router.delete("/review/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_presentation_review_history_item(
    review_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_presentation_designer_db)],
) -> None:
    delete_review_history_item(db, current_user, review_id)
