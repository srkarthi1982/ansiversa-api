from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.linkedin_bio_optimizer.db import get_linkedin_bio_optimizer_db
from app.modules.linkedin_bio_optimizer.schemas import (
    BioTemplateCreateRequest,
    BioTemplateDetailResponse,
    BioTemplateSummaryResponse,
    BioTemplateUpdateRequest,
    BioVersionCreateRequest,
    BioVersionDetailResponse,
    BioVersionSummaryResponse,
    LinkedInBioOptimizerDashboardResponse,
    LinkedInProfileCreateRequest,
    LinkedInProfileDetailResponse,
    LinkedInProfileSummaryResponse,
    LinkedInProfileUpdateRequest,
)
from app.modules.linkedin_bio_optimizer.service import (
    create_profile,
    create_template,
    create_version,
    delete_profile,
    delete_template,
    delete_version,
    get_dashboard,
    get_profile,
    get_template,
    get_version,
    list_profiles,
    list_templates,
    list_versions,
    list_versions_by_profile,
    update_profile,
    update_template,
)

router = APIRouter()


@router.get("/dashboard", response_model=LinkedInBioOptimizerDashboardResponse)
def get_linkedin_bio_dashboard(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_linkedin_bio_optimizer_db)],
) -> LinkedInBioOptimizerDashboardResponse:
    return get_dashboard(db, current_user)


@router.post(
    "/profiles",
    response_model=LinkedInProfileDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_linkedin_profile(
    payload: LinkedInProfileCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_linkedin_bio_optimizer_db)],
) -> LinkedInProfileDetailResponse:
    return create_profile(db, current_user, payload)


@router.get("/profiles", response_model=list[LinkedInProfileSummaryResponse])
def list_linkedin_profiles(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_linkedin_bio_optimizer_db)],
) -> list[LinkedInProfileSummaryResponse]:
    return list_profiles(db, current_user)


@router.get("/profiles/{profile_id}", response_model=LinkedInProfileDetailResponse)
def get_linkedin_profile(
    profile_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_linkedin_bio_optimizer_db)],
) -> LinkedInProfileDetailResponse:
    return get_profile(db, current_user, profile_id)


@router.put("/profiles/{profile_id}", response_model=LinkedInProfileDetailResponse)
def update_linkedin_profile(
    profile_id: Annotated[int, Path(gt=0)],
    payload: LinkedInProfileUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_linkedin_bio_optimizer_db)],
) -> LinkedInProfileDetailResponse:
    return update_profile(db, current_user, profile_id, payload)


@router.delete("/profiles/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_linkedin_profile(
    profile_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_linkedin_bio_optimizer_db)],
) -> None:
    delete_profile(db, current_user, profile_id)


@router.post(
    "/templates",
    response_model=BioTemplateDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_bio_template(
    payload: BioTemplateCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_linkedin_bio_optimizer_db)],
) -> BioTemplateDetailResponse:
    return create_template(db, current_user, payload)


@router.get("/templates", response_model=list[BioTemplateSummaryResponse])
def list_bio_templates(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_linkedin_bio_optimizer_db)],
) -> list[BioTemplateSummaryResponse]:
    return list_templates(db, current_user)


@router.get("/templates/{template_id}", response_model=BioTemplateDetailResponse)
def get_bio_template(
    template_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_linkedin_bio_optimizer_db)],
) -> BioTemplateDetailResponse:
    return get_template(db, current_user, template_id)


@router.put("/templates/{template_id}", response_model=BioTemplateDetailResponse)
def update_bio_template(
    template_id: Annotated[int, Path(gt=0)],
    payload: BioTemplateUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_linkedin_bio_optimizer_db)],
) -> BioTemplateDetailResponse:
    return update_template(db, current_user, template_id, payload)


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bio_template(
    template_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_linkedin_bio_optimizer_db)],
) -> None:
    delete_template(db, current_user, template_id)


@router.post(
    "/versions",
    response_model=BioVersionDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_bio_version(
    payload: BioVersionCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_linkedin_bio_optimizer_db)],
) -> BioVersionDetailResponse:
    return create_version(db, current_user, payload)


@router.get("/versions", response_model=list[BioVersionSummaryResponse])
def list_bio_versions(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_linkedin_bio_optimizer_db)],
) -> list[BioVersionSummaryResponse]:
    return list_versions(db, current_user)


@router.get("/profiles/{profile_id}/versions", response_model=list[BioVersionSummaryResponse])
def list_bio_versions_by_profile(
    profile_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_linkedin_bio_optimizer_db)],
) -> list[BioVersionSummaryResponse]:
    return list_versions_by_profile(db, current_user, profile_id)


@router.get("/versions/{version_id}", response_model=BioVersionDetailResponse)
def get_bio_version(
    version_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_linkedin_bio_optimizer_db)],
) -> BioVersionDetailResponse:
    return get_version(db, current_user, version_id)


@router.delete("/versions/{version_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bio_version(
    version_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_linkedin_bio_optimizer_db)],
) -> None:
    delete_version(db, current_user, version_id)
