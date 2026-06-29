from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.presentation_designer.models import (
    PresentationAsset,
    PresentationProject,
    PresentationReviewHistoryItem,
    PresentationSlide,
)
from app.modules.presentation_designer.schemas import (
    PresentationAssetCreateRequest,
    PresentationAssetDetailResponse,
    PresentationAssetSummaryResponse,
    PresentationAssetUpdateRequest,
    PresentationDashboardResponse,
    PresentationProjectCreateRequest,
    PresentationProjectDetailResponse,
    PresentationProjectSummaryResponse,
    PresentationProjectUpdateRequest,
    PresentationReviewHistoryCreateRequest,
    PresentationReviewHistoryDetailResponse,
    PresentationReviewHistorySummaryResponse,
    PresentationReviewHistoryUpdateRequest,
    PresentationSlideCreateRequest,
    PresentationSlideDetailResponse,
    PresentationSlideSummaryResponse,
    PresentationSlideUpdateRequest,
)

PREVIEW_LENGTH = 220


def _preview(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) <= PREVIEW_LENGTH:
        return value
    return f"{value[:PREVIEW_LENGTH].rstrip()}..."


def _not_found(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _get_owned_project(db: Session, user: User, project_id: int) -> PresentationProject:
    project = db.get(PresentationProject, project_id)
    if not project or project.owner_id != user.id:
        _not_found("Presentation project was not found.")
    return project


def _get_owned_slide(db: Session, user: User, slide_id: int) -> PresentationSlide:
    slide = db.get(PresentationSlide, slide_id)
    if not slide or slide.owner_id != user.id:
        _not_found("Presentation slide was not found.")
    return slide


def _get_owned_asset(db: Session, user: User, asset_id: int) -> PresentationAsset:
    asset = db.get(PresentationAsset, asset_id)
    if not asset or asset.owner_id != user.id:
        _not_found("Presentation asset was not found.")
    return asset


def _get_owned_review_history_item(
    db: Session,
    user: User,
    review_id: int,
) -> PresentationReviewHistoryItem:
    review_item = db.get(PresentationReviewHistoryItem, review_id)
    if not review_item or review_item.owner_id != user.id:
        _not_found("Presentation review history item was not found.")
    return review_item


def _optional_owned_project(
    db: Session,
    user: User,
    project_id: int | None,
) -> PresentationProject | None:
    if project_id is None:
        return None
    return _get_owned_project(db, user, project_id)


def _count_slides(db: Session, project_id: int) -> int:
    return int(
        db.execute(
            select(func.count()).select_from(PresentationSlide).where(
                PresentationSlide.project_id == project_id
            )
        ).scalar_one()
    )


def _count_assets(db: Session, project_id: int) -> int:
    return int(
        db.execute(
            select(func.count()).select_from(PresentationAsset).where(
                PresentationAsset.project_id == project_id
            )
        ).scalar_one()
    )


def _project_summary_response(
    db: Session,
    project: PresentationProject,
) -> PresentationProjectSummaryResponse:
    return PresentationProjectSummaryResponse(
        id=project.id,
        title=project.title,
        audience=project.audience,
        theme=project.theme,
        status=project.status,
        slide_count=_count_slides(db, project.id),
        asset_count=_count_assets(db, project.id),
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def _project_detail_response(
    db: Session,
    project: PresentationProject,
) -> PresentationProjectDetailResponse:
    summary = _project_summary_response(db, project)
    return PresentationProjectDetailResponse(**summary.model_dump(), notes=project.notes)


def _slide_summary_response(
    slide: PresentationSlide,
    project_title: str,
) -> PresentationSlideSummaryResponse:
    return PresentationSlideSummaryResponse(
        id=slide.id,
        project_id=slide.project_id,
        project_title=project_title,
        title=slide.title,
        layout=slide.layout,
        headline=slide.headline,
        sort_order=slide.sort_order,
        created_at=slide.created_at,
        updated_at=slide.updated_at,
    )


def _slide_detail_response(
    slide: PresentationSlide,
    project_title: str,
) -> PresentationSlideDetailResponse:
    summary = _slide_summary_response(slide, project_title)
    return PresentationSlideDetailResponse(
        **summary.model_dump(),
        body=slide.body,
        speaker_notes=slide.speaker_notes,
    )


def _asset_summary_response(
    asset: PresentationAsset,
    project_title: str,
) -> PresentationAssetSummaryResponse:
    return PresentationAssetSummaryResponse(
        id=asset.id,
        project_id=asset.project_id,
        project_title=project_title,
        title=asset.title,
        asset_type=asset.asset_type,
        sort_order=asset.sort_order,
        created_at=asset.created_at,
        updated_at=asset.updated_at,
    )


def _asset_detail_response(
    asset: PresentationAsset,
    project_title: str,
) -> PresentationAssetDetailResponse:
    summary = _asset_summary_response(asset, project_title)
    return PresentationAssetDetailResponse(
        **summary.model_dump(),
        description=asset.description,
        source=asset.source,
    )


def _review_history_summary_response(
    review_item: PresentationReviewHistoryItem,
    project_title: str | None,
) -> PresentationReviewHistorySummaryResponse:
    return PresentationReviewHistorySummaryResponse(
        id=review_item.id,
        project_id=review_item.project_id,
        project_title=project_title,
        title=review_item.title,
        action_type=review_item.action_type,
        notes_preview=_preview(review_item.notes),
        created_at=review_item.created_at,
        updated_at=review_item.updated_at,
    )


def _review_history_detail_response(
    review_item: PresentationReviewHistoryItem,
    project_title: str | None,
) -> PresentationReviewHistoryDetailResponse:
    summary = _review_history_summary_response(review_item, project_title)
    return PresentationReviewHistoryDetailResponse(**summary.model_dump(), notes=review_item.notes)


def list_projects(db: Session, user: User) -> list[PresentationProjectSummaryResponse]:
    projects = list(
        db.execute(
            select(PresentationProject)
            .where(PresentationProject.owner_id == user.id)
            .order_by(PresentationProject.updated_at.desc(), PresentationProject.title.asc())
        )
        .scalars()
        .all()
    )
    return [_project_summary_response(db, project) for project in projects]


def create_project(
    db: Session,
    user: User,
    payload: PresentationProjectCreateRequest,
) -> PresentationProjectDetailResponse:
    project = PresentationProject(
        owner_id=user.id,
        title=payload.title,
        audience=payload.audience,
        theme=payload.theme,
        status=payload.status,
        notes=payload.notes,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return _project_detail_response(db, project)


def get_project(db: Session, user: User, project_id: int) -> PresentationProjectDetailResponse:
    return _project_detail_response(db, _get_owned_project(db, user, project_id))


def update_project(
    db: Session,
    user: User,
    project_id: int,
    payload: PresentationProjectUpdateRequest,
) -> PresentationProjectDetailResponse:
    project = _get_owned_project(db, user, project_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return _project_detail_response(db, project)


def delete_project(db: Session, user: User, project_id: int) -> None:
    project = _get_owned_project(db, user, project_id)
    db.execute(delete(PresentationSlide).where(PresentationSlide.project_id == project.id))
    db.execute(delete(PresentationAsset).where(PresentationAsset.project_id == project.id))
    db.execute(delete(PresentationReviewHistoryItem).where(PresentationReviewHistoryItem.project_id == project.id))
    db.delete(project)
    db.commit()


def list_slides(db: Session, user: User) -> list[PresentationSlideSummaryResponse]:
    rows = db.execute(
        select(PresentationSlide, PresentationProject.title)
        .join(PresentationProject, PresentationProject.id == PresentationSlide.project_id)
        .where(PresentationSlide.owner_id == user.id)
        .order_by(
            PresentationSlide.project_id.asc(),
            PresentationSlide.sort_order.asc(),
            PresentationSlide.updated_at.desc(),
        )
    ).all()
    return [_slide_summary_response(slide, project_title) for slide, project_title in rows]


def create_slide(
    db: Session,
    user: User,
    payload: PresentationSlideCreateRequest,
) -> PresentationSlideDetailResponse:
    project = _get_owned_project(db, user, payload.project_id)
    slide = PresentationSlide(
        project_id=project.id,
        owner_id=user.id,
        title=payload.title,
        layout=payload.layout,
        headline=payload.headline,
        body=payload.body,
        speaker_notes=payload.speaker_notes,
        sort_order=payload.sort_order,
    )
    db.add(slide)
    db.commit()
    db.refresh(slide)
    return _slide_detail_response(slide, project.title)


def get_slide(db: Session, user: User, slide_id: int) -> PresentationSlideDetailResponse:
    slide = _get_owned_slide(db, user, slide_id)
    project = _get_owned_project(db, user, slide.project_id)
    return _slide_detail_response(slide, project.title)


def update_slide(
    db: Session,
    user: User,
    slide_id: int,
    payload: PresentationSlideUpdateRequest,
) -> PresentationSlideDetailResponse:
    slide = _get_owned_slide(db, user, slide_id)
    project = _get_owned_project(db, user, slide.project_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(slide, field, value)
    db.commit()
    db.refresh(slide)
    return _slide_detail_response(slide, project.title)


def delete_slide(db: Session, user: User, slide_id: int) -> None:
    slide = _get_owned_slide(db, user, slide_id)
    db.delete(slide)
    db.commit()


def list_assets(db: Session, user: User) -> list[PresentationAssetSummaryResponse]:
    rows = db.execute(
        select(PresentationAsset, PresentationProject.title)
        .join(PresentationProject, PresentationProject.id == PresentationAsset.project_id)
        .where(PresentationAsset.owner_id == user.id)
        .order_by(
            PresentationAsset.project_id.asc(),
            PresentationAsset.sort_order.asc(),
            PresentationAsset.updated_at.desc(),
        )
    ).all()
    return [_asset_summary_response(asset, project_title) for asset, project_title in rows]


def create_asset(
    db: Session,
    user: User,
    payload: PresentationAssetCreateRequest,
) -> PresentationAssetDetailResponse:
    project = _get_owned_project(db, user, payload.project_id)
    asset = PresentationAsset(
        project_id=project.id,
        owner_id=user.id,
        title=payload.title,
        asset_type=payload.asset_type,
        description=payload.description,
        source=payload.source,
        sort_order=payload.sort_order,
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return _asset_detail_response(asset, project.title)


def get_asset(db: Session, user: User, asset_id: int) -> PresentationAssetDetailResponse:
    asset = _get_owned_asset(db, user, asset_id)
    project = _get_owned_project(db, user, asset.project_id)
    return _asset_detail_response(asset, project.title)


def update_asset(
    db: Session,
    user: User,
    asset_id: int,
    payload: PresentationAssetUpdateRequest,
) -> PresentationAssetDetailResponse:
    asset = _get_owned_asset(db, user, asset_id)
    project = _get_owned_project(db, user, asset.project_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(asset, field, value)
    db.commit()
    db.refresh(asset)
    return _asset_detail_response(asset, project.title)


def delete_asset(db: Session, user: User, asset_id: int) -> None:
    asset = _get_owned_asset(db, user, asset_id)
    db.delete(asset)
    db.commit()


def list_review_history(db: Session, user: User) -> list[PresentationReviewHistorySummaryResponse]:
    rows = db.execute(
        select(PresentationReviewHistoryItem, PresentationProject.title)
        .outerjoin(PresentationProject, PresentationProject.id == PresentationReviewHistoryItem.project_id)
        .where(PresentationReviewHistoryItem.owner_id == user.id)
        .order_by(PresentationReviewHistoryItem.created_at.desc())
    ).all()
    return [
        _review_history_summary_response(review_item, project_title)
        for review_item, project_title in rows
    ]


def create_review_history_item(
    db: Session,
    user: User,
    payload: PresentationReviewHistoryCreateRequest,
) -> PresentationReviewHistorySummaryResponse:
    project = _optional_owned_project(db, user, payload.project_id)
    review_item = PresentationReviewHistoryItem(
        project_id=project.id if project else None,
        owner_id=user.id,
        title=payload.title,
        action_type=payload.action_type,
        notes=payload.notes,
    )
    db.add(review_item)
    db.commit()
    db.refresh(review_item)
    return _review_history_summary_response(
        review_item,
        project.title if project else None,
    )


def get_review_history_item(
    db: Session,
    user: User,
    review_id: int,
) -> PresentationReviewHistoryDetailResponse:
    review_item = _get_owned_review_history_item(db, user, review_id)
    project = _optional_owned_project(db, user, review_item.project_id)
    return _review_history_detail_response(review_item, project.title if project else None)


def update_review_history_item(
    db: Session,
    user: User,
    review_id: int,
    payload: PresentationReviewHistoryUpdateRequest,
) -> PresentationReviewHistoryDetailResponse:
    review_item = _get_owned_review_history_item(db, user, review_id)
    project = _optional_owned_project(db, user, review_item.project_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(review_item, field, value)
    db.commit()
    db.refresh(review_item)
    return _review_history_detail_response(review_item, project.title if project else None)


def delete_review_history_item(db: Session, user: User, review_id: int) -> None:
    review_item = _get_owned_review_history_item(db, user, review_id)
    db.delete(review_item)
    db.commit()


def get_dashboard(db: Session, user: User) -> PresentationDashboardResponse:
    projects = list_projects(db, user)
    slides = list_slides(db, user)
    assets = list_assets(db, user)
    review_history = list_review_history(db, user)
    return PresentationDashboardResponse(
        projects=projects,
        slides=slides,
        assets=assets,
        review_history=review_history,
        draft_project_count=sum(1 for project in projects if project.status == "draft"),
        review_project_count=sum(1 for project in projects if project.status == "review"),
        ready_project_count=sum(1 for project in projects if project.status == "ready"),
    )
