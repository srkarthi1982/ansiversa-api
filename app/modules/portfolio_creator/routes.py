from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.portfolio_creator.db import get_portfolio_creator_db
from app.modules.portfolio_creator.schemas import (
    PortfolioCreatorDashboardResponse,
    PortfolioProfileCreateRequest,
    PortfolioProfileListResponse,
    PortfolioProfileResponse,
    PortfolioProfileUpdateRequest,
    PortfolioProjectCreateRequest,
    PortfolioProjectListResponse,
    PortfolioProjectResponse,
    PortfolioProjectUpdateRequest,
    PortfolioPublishSettingCreateRequest,
    PortfolioPublishSettingListResponse,
    PortfolioPublishSettingResponse,
    PortfolioPublishSettingUpdateRequest,
    PortfolioSkillCreateRequest,
    PortfolioSkillListResponse,
    PortfolioSkillResponse,
    PortfolioSkillUpdateRequest,
)
from app.modules.portfolio_creator.service import (
    create_profile,
    create_project,
    create_publish_setting,
    create_skill,
    delete_profile,
    delete_project,
    delete_publish_setting,
    delete_skill,
    get_dashboard,
    list_profiles,
    list_projects,
    list_publish_settings,
    list_skills,
    update_profile,
    update_project,
    update_publish_setting,
    update_skill,
)

router = APIRouter()


@router.get("/dashboard", response_model=PortfolioCreatorDashboardResponse)
def get_portfolio_creator_dashboard(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_portfolio_creator_db)],
) -> PortfolioCreatorDashboardResponse:
    return get_dashboard(db, current_user)


@router.get("/profiles", response_model=PortfolioProfileListResponse)
def get_portfolio_profiles(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_portfolio_creator_db)],
) -> PortfolioProfileListResponse:
    return PortfolioProfileListResponse(items=list_profiles(db, current_user))


@router.post(
    "/profiles",
    response_model=PortfolioProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_portfolio_profile(
    payload: PortfolioProfileCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_portfolio_creator_db)],
) -> PortfolioProfileResponse:
    return create_profile(db, current_user, payload)


@router.put("/profiles/{profile_id}", response_model=PortfolioProfileResponse)
def update_portfolio_profile(
    profile_id: Annotated[int, Path(gt=0)],
    payload: PortfolioProfileUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_portfolio_creator_db)],
) -> PortfolioProfileResponse:
    return update_profile(db, current_user, profile_id, payload)


@router.delete("/profiles/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_portfolio_profile(
    profile_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_portfolio_creator_db)],
) -> None:
    delete_profile(db, current_user, profile_id)


@router.get("/projects", response_model=PortfolioProjectListResponse)
def get_portfolio_projects(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_portfolio_creator_db)],
) -> PortfolioProjectListResponse:
    return PortfolioProjectListResponse(items=list_projects(db, current_user))


@router.post(
    "/projects",
    response_model=PortfolioProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_portfolio_project(
    payload: PortfolioProjectCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_portfolio_creator_db)],
) -> PortfolioProjectResponse:
    return create_project(db, current_user, payload)


@router.put("/projects/{project_id}", response_model=PortfolioProjectResponse)
def update_portfolio_project(
    project_id: Annotated[int, Path(gt=0)],
    payload: PortfolioProjectUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_portfolio_creator_db)],
) -> PortfolioProjectResponse:
    return update_project(db, current_user, project_id, payload)


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_portfolio_project(
    project_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_portfolio_creator_db)],
) -> None:
    delete_project(db, current_user, project_id)


@router.get("/skills", response_model=PortfolioSkillListResponse)
def get_portfolio_skills(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_portfolio_creator_db)],
) -> PortfolioSkillListResponse:
    return PortfolioSkillListResponse(items=list_skills(db, current_user))


@router.post(
    "/skills",
    response_model=PortfolioSkillResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_portfolio_skill(
    payload: PortfolioSkillCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_portfolio_creator_db)],
) -> PortfolioSkillResponse:
    return create_skill(db, current_user, payload)


@router.put("/skills/{skill_id}", response_model=PortfolioSkillResponse)
def update_portfolio_skill(
    skill_id: Annotated[int, Path(gt=0)],
    payload: PortfolioSkillUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_portfolio_creator_db)],
) -> PortfolioSkillResponse:
    return update_skill(db, current_user, skill_id, payload)


@router.delete("/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_portfolio_skill(
    skill_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_portfolio_creator_db)],
) -> None:
    delete_skill(db, current_user, skill_id)


@router.get("/publish", response_model=PortfolioPublishSettingListResponse)
def get_portfolio_publish_settings(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_portfolio_creator_db)],
) -> PortfolioPublishSettingListResponse:
    return PortfolioPublishSettingListResponse(items=list_publish_settings(db, current_user))


@router.post(
    "/publish",
    response_model=PortfolioPublishSettingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_portfolio_publish_setting(
    payload: PortfolioPublishSettingCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_portfolio_creator_db)],
) -> PortfolioPublishSettingResponse:
    return create_publish_setting(db, current_user, payload)


@router.put("/publish/{setting_id}", response_model=PortfolioPublishSettingResponse)
def update_portfolio_publish_setting(
    setting_id: Annotated[int, Path(gt=0)],
    payload: PortfolioPublishSettingUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_portfolio_creator_db)],
) -> PortfolioPublishSettingResponse:
    return update_publish_setting(db, current_user, setting_id, payload)


@router.delete("/publish/{setting_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_portfolio_publish_setting(
    setting_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_portfolio_creator_db)],
) -> None:
    delete_publish_setting(db, current_user, setting_id)
