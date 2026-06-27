from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from fastapi import HTTPException, status

from app.modules.auth.models import User
from app.modules.portfolio_creator.models import (
    PortfolioProfile,
    PortfolioProject,
    PortfolioPublishSetting,
    PortfolioSkill,
)
from app.modules.portfolio_creator.schemas import (
    PortfolioCreatorDashboardResponse,
    PortfolioProfileCreateRequest,
    PortfolioProfileResponse,
    PortfolioProfileUpdateRequest,
    PortfolioProjectCreateRequest,
    PortfolioProjectResponse,
    PortfolioProjectUpdateRequest,
    PortfolioPublishSettingCreateRequest,
    PortfolioPublishSettingResponse,
    PortfolioPublishSettingUpdateRequest,
    PortfolioSkillCreateRequest,
    PortfolioSkillResponse,
    PortfolioSkillUpdateRequest,
)


def _get_owned_profile(db: Session, user: User, profile_id: int) -> PortfolioProfile:
    profile = db.get(PortfolioProfile, profile_id)
    if not profile or profile.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio profile was not found.",
        )

    return profile


def _get_owned_project(db: Session, user: User, project_id: int) -> PortfolioProject:
    project = db.get(PortfolioProject, project_id)
    if not project or project.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio project was not found.",
        )

    return project


def _get_owned_skill(db: Session, user: User, skill_id: int) -> PortfolioSkill:
    skill = db.get(PortfolioSkill, skill_id)
    if not skill or skill.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio skill was not found.",
        )

    return skill


def _get_owned_publish_setting(
    db: Session,
    user: User,
    setting_id: int,
) -> PortfolioPublishSetting:
    setting = db.get(PortfolioPublishSetting, setting_id)
    if not setting or setting.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio publish setting was not found.",
        )

    return setting


def _count_projects(db: Session, profile_id: int) -> int:
    return int(
        db.execute(
            select(func.count()).select_from(PortfolioProject).where(
                PortfolioProject.profile_id == profile_id
            )
        ).scalar_one()
    )


def _count_skills(db: Session, profile_id: int) -> int:
    return int(
        db.execute(
            select(func.count()).select_from(PortfolioSkill).where(
                PortfolioSkill.profile_id == profile_id
            )
        ).scalar_one()
    )


def _count_publish_settings(db: Session, profile_id: int) -> int:
    return int(
        db.execute(
            select(func.count()).select_from(PortfolioPublishSetting).where(
                PortfolioPublishSetting.profile_id == profile_id
            )
        ).scalar_one()
    )


def _profile_response(db: Session, profile: PortfolioProfile) -> PortfolioProfileResponse:
    return PortfolioProfileResponse(
        id=profile.id,
        display_name=profile.display_name,
        headline=profile.headline,
        summary=profile.summary,
        location=profile.location,
        website_url=profile.website_url,
        status=profile.status,
        project_count=_count_projects(db, profile.id),
        skill_count=_count_skills(db, profile.id),
        publish_count=_count_publish_settings(db, profile.id),
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


def _project_response(project: PortfolioProject, profile_name: str) -> PortfolioProjectResponse:
    return PortfolioProjectResponse(
        id=project.id,
        profile_id=project.profile_id,
        profile_name=profile_name,
        title=project.title,
        description=project.description,
        project_url=project.project_url,
        role=project.role,
        position=project.position,
        status=project.status,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def _skill_response(skill: PortfolioSkill, profile_name: str) -> PortfolioSkillResponse:
    return PortfolioSkillResponse(
        id=skill.id,
        profile_id=skill.profile_id,
        profile_name=profile_name,
        name=skill.name,
        category=skill.category,
        proficiency=skill.proficiency,
        position=skill.position,
        created_at=skill.created_at,
        updated_at=skill.updated_at,
    )


def _publish_setting_response(
    setting: PortfolioPublishSetting,
    profile_name: str,
) -> PortfolioPublishSettingResponse:
    return PortfolioPublishSettingResponse(
        id=setting.id,
        profile_id=setting.profile_id,
        profile_name=profile_name,
        visibility=setting.visibility,
        slug=setting.slug,
        theme=setting.theme,
        is_published=setting.is_published,
        created_at=setting.created_at,
        updated_at=setting.updated_at,
    )


def list_profiles(db: Session, user: User) -> list[PortfolioProfileResponse]:
    profiles = list(
        db.execute(
            select(PortfolioProfile)
            .where(PortfolioProfile.owner_id == user.id)
            .order_by(PortfolioProfile.updated_at.desc(), PortfolioProfile.display_name.asc())
        )
        .scalars()
        .all()
    )

    return [_profile_response(db, profile) for profile in profiles]


def create_profile(
    db: Session,
    user: User,
    payload: PortfolioProfileCreateRequest,
) -> PortfolioProfileResponse:
    profile = PortfolioProfile(
        owner_id=user.id,
        display_name=payload.display_name,
        headline=payload.headline,
        summary=payload.summary,
        location=payload.location,
        website_url=payload.website_url,
        status="draft",
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)

    return _profile_response(db, profile)


def update_profile(
    db: Session,
    user: User,
    profile_id: int,
    payload: PortfolioProfileUpdateRequest,
) -> PortfolioProfileResponse:
    profile = _get_owned_profile(db, user, profile_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)

    return _profile_response(db, profile)


def delete_profile(db: Session, user: User, profile_id: int) -> None:
    profile = _get_owned_profile(db, user, profile_id)
    db.execute(delete(PortfolioPublishSetting).where(PortfolioPublishSetting.profile_id == profile.id))
    db.execute(delete(PortfolioSkill).where(PortfolioSkill.profile_id == profile.id))
    db.execute(delete(PortfolioProject).where(PortfolioProject.profile_id == profile.id))
    db.delete(profile)
    db.commit()


def list_projects(db: Session, user: User) -> list[PortfolioProjectResponse]:
    rows = db.execute(
        select(PortfolioProject, PortfolioProfile.display_name)
        .join(PortfolioProfile, PortfolioProfile.id == PortfolioProject.profile_id)
        .where(PortfolioProject.owner_id == user.id)
        .order_by(PortfolioProject.position.asc(), PortfolioProject.updated_at.desc())
    ).all()

    return [_project_response(project, profile_name) for project, profile_name in rows]


def create_project(
    db: Session,
    user: User,
    payload: PortfolioProjectCreateRequest,
) -> PortfolioProjectResponse:
    profile = _get_owned_profile(db, user, payload.profile_id)
    project = PortfolioProject(
        owner_id=user.id,
        profile_id=profile.id,
        title=payload.title,
        description=payload.description,
        project_url=payload.project_url,
        role=payload.role,
        position=payload.position,
        status="draft",
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    return _project_response(project, profile.display_name)


def update_project(
    db: Session,
    user: User,
    project_id: int,
    payload: PortfolioProjectUpdateRequest,
) -> PortfolioProjectResponse:
    project = _get_owned_project(db, user, project_id)
    profile = _get_owned_profile(db, user, project.profile_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)

    return _project_response(project, profile.display_name)


def delete_project(db: Session, user: User, project_id: int) -> None:
    project = _get_owned_project(db, user, project_id)
    db.delete(project)
    db.commit()


def list_skills(db: Session, user: User) -> list[PortfolioSkillResponse]:
    rows = db.execute(
        select(PortfolioSkill, PortfolioProfile.display_name)
        .join(PortfolioProfile, PortfolioProfile.id == PortfolioSkill.profile_id)
        .where(PortfolioSkill.owner_id == user.id)
        .order_by(PortfolioSkill.position.asc(), PortfolioSkill.updated_at.desc())
    ).all()

    return [_skill_response(skill, profile_name) for skill, profile_name in rows]


def create_skill(
    db: Session,
    user: User,
    payload: PortfolioSkillCreateRequest,
) -> PortfolioSkillResponse:
    profile = _get_owned_profile(db, user, payload.profile_id)
    skill = PortfolioSkill(
        owner_id=user.id,
        profile_id=profile.id,
        name=payload.name,
        category=payload.category,
        proficiency=payload.proficiency,
        position=payload.position,
    )
    db.add(skill)
    db.commit()
    db.refresh(skill)

    return _skill_response(skill, profile.display_name)


def update_skill(
    db: Session,
    user: User,
    skill_id: int,
    payload: PortfolioSkillUpdateRequest,
) -> PortfolioSkillResponse:
    skill = _get_owned_skill(db, user, skill_id)
    profile = _get_owned_profile(db, user, skill.profile_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(skill, field, value)
    db.commit()
    db.refresh(skill)

    return _skill_response(skill, profile.display_name)


def delete_skill(db: Session, user: User, skill_id: int) -> None:
    skill = _get_owned_skill(db, user, skill_id)
    db.delete(skill)
    db.commit()


def list_publish_settings(db: Session, user: User) -> list[PortfolioPublishSettingResponse]:
    rows = db.execute(
        select(PortfolioPublishSetting, PortfolioProfile.display_name)
        .join(PortfolioProfile, PortfolioProfile.id == PortfolioPublishSetting.profile_id)
        .where(PortfolioPublishSetting.owner_id == user.id)
        .order_by(PortfolioPublishSetting.updated_at.desc())
    ).all()

    return [_publish_setting_response(setting, profile_name) for setting, profile_name in rows]


def create_publish_setting(
    db: Session,
    user: User,
    payload: PortfolioPublishSettingCreateRequest,
) -> PortfolioPublishSettingResponse:
    profile = _get_owned_profile(db, user, payload.profile_id)
    setting = PortfolioPublishSetting(
        owner_id=user.id,
        profile_id=profile.id,
        visibility=payload.visibility,
        slug=payload.slug,
        theme=payload.theme,
        is_published=payload.is_published,
    )
    if payload.is_published:
        profile.status = "published"
    db.add(setting)
    db.commit()
    db.refresh(setting)

    return _publish_setting_response(setting, profile.display_name)


def update_publish_setting(
    db: Session,
    user: User,
    setting_id: int,
    payload: PortfolioPublishSettingUpdateRequest,
) -> PortfolioPublishSettingResponse:
    setting = _get_owned_publish_setting(db, user, setting_id)
    profile = _get_owned_profile(db, user, setting.profile_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(setting, field, value)
    if setting.is_published:
        profile.status = "published"
    db.commit()
    db.refresh(setting)

    return _publish_setting_response(setting, profile.display_name)


def delete_publish_setting(db: Session, user: User, setting_id: int) -> None:
    setting = _get_owned_publish_setting(db, user, setting_id)
    db.delete(setting)
    db.commit()


def get_dashboard(db: Session, user: User) -> PortfolioCreatorDashboardResponse:
    profiles = list_profiles(db, user)
    projects = list_projects(db, user)
    publish_settings = list_publish_settings(db, user)

    return PortfolioCreatorDashboardResponse(
        profiles=profiles,
        projects=projects,
        skills=list_skills(db, user),
        publish_settings=publish_settings,
        draft_profile_count=len([profile for profile in profiles if profile.status == "draft"]),
        published_profile_count=len(
            [profile for profile in profiles if profile.status == "published"]
        ),
        featured_project_count=len(
            [project for project in projects if project.status == "featured"]
        ),
        published_portfolio_count=len(
            [setting for setting in publish_settings if setting.is_published]
        ),
    )
