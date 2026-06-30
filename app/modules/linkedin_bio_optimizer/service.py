from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.linkedin_bio_optimizer.models import (
    BioTemplate,
    BioVersion,
    LinkedInProfile,
)
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

PREVIEW_LENGTH = 220


def _preview(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) <= PREVIEW_LENGTH:
        return value
    return f"{value[:PREVIEW_LENGTH].rstrip()}..."


def _not_found(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _get_owned_profile(db: Session, user: User, profile_id: int) -> LinkedInProfile:
    profile = db.get(LinkedInProfile, profile_id)
    if not profile or profile.owner_id != user.id:
        _not_found("LinkedIn profile was not found.")
    return profile


def _get_owned_template(db: Session, user: User, template_id: int) -> BioTemplate:
    template = db.get(BioTemplate, template_id)
    if not template or template.owner_id != user.id:
        _not_found("Bio template was not found.")
    return template


def _get_owned_version(db: Session, user: User, version_id: int) -> BioVersion:
    version = db.get(BioVersion, version_id)
    if not version or version.owner_id != user.id:
        _not_found("Bio version was not found.")
    return version


def _count_versions(db: Session, profile_id: int) -> int:
    return int(
        db.execute(
            select(func.count()).select_from(BioVersion).where(BioVersion.profile_id == profile_id)
        ).scalar_one()
    )


def _profile_summary_response(
    db: Session,
    profile: LinkedInProfile,
) -> LinkedInProfileSummaryResponse:
    return LinkedInProfileSummaryResponse(
        id=profile.id,
        platform_id=profile.platform_id,
        title=profile.title,
        industry=profile.industry,
        career_level=profile.career_level,
        target_role=profile.target_role,
        current_headline=profile.current_headline,
        optimized_bio_preview=_preview(profile.optimized_bio),
        keywords_preview=_preview(profile.keywords),
        tone=profile.tone,
        language=profile.language,
        version_count=_count_versions(db, profile.id),
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


def _profile_detail_response(
    db: Session,
    profile: LinkedInProfile,
) -> LinkedInProfileDetailResponse:
    summary = _profile_summary_response(db, profile)
    return LinkedInProfileDetailResponse(
        **summary.model_dump(),
        current_bio=profile.current_bio,
        optimized_bio=profile.optimized_bio,
        keywords=profile.keywords,
        notes=profile.notes,
    )


def _template_summary_response(template: BioTemplate) -> BioTemplateSummaryResponse:
    return BioTemplateSummaryResponse(
        id=template.id,
        platform_id=template.platform_id,
        name=template.name,
        industry=template.industry,
        career_level=template.career_level,
        template_preview=_preview(template.template),
        is_default=template.is_default,
        created_at=template.created_at,
        updated_at=template.updated_at,
    )


def _template_detail_response(template: BioTemplate) -> BioTemplateDetailResponse:
    summary = _template_summary_response(template)
    return BioTemplateDetailResponse(**summary.model_dump(), template=template.template)


def _version_summary_response(
    version: BioVersion,
    profile_title: str,
) -> BioVersionSummaryResponse:
    return BioVersionSummaryResponse(
        id=version.id,
        platform_id=version.platform_id,
        profile_id=version.profile_id,
        profile_title=profile_title,
        version_number=version.version_number,
        headline=version.headline,
        bio_preview=_preview(version.bio),
        change_summary_preview=_preview(version.change_summary),
        created_at=version.created_at,
    )


def _version_detail_response(
    version: BioVersion,
    profile_title: str,
) -> BioVersionDetailResponse:
    summary = _version_summary_response(version, profile_title)
    return BioVersionDetailResponse(
        **summary.model_dump(),
        bio=version.bio,
        change_summary=version.change_summary,
    )


def list_profiles(db: Session, user: User) -> list[LinkedInProfileSummaryResponse]:
    profiles = list(
        db.execute(
            select(LinkedInProfile)
            .where(LinkedInProfile.owner_id == user.id)
            .order_by(LinkedInProfile.updated_at.desc(), LinkedInProfile.title.asc())
        )
        .scalars()
        .all()
    )
    return [_profile_summary_response(db, profile) for profile in profiles]


def create_profile(
    db: Session,
    user: User,
    payload: LinkedInProfileCreateRequest,
) -> LinkedInProfileDetailResponse:
    profile = LinkedInProfile(owner_id=user.id, **payload.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return _profile_detail_response(db, profile)


def get_profile(db: Session, user: User, profile_id: int) -> LinkedInProfileDetailResponse:
    return _profile_detail_response(db, _get_owned_profile(db, user, profile_id))


def update_profile(
    db: Session,
    user: User,
    profile_id: int,
    payload: LinkedInProfileUpdateRequest,
) -> LinkedInProfileDetailResponse:
    profile = _get_owned_profile(db, user, profile_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return _profile_detail_response(db, profile)


def delete_profile(db: Session, user: User, profile_id: int) -> None:
    profile = _get_owned_profile(db, user, profile_id)
    db.execute(delete(BioVersion).where(BioVersion.profile_id == profile.id))
    db.delete(profile)
    db.commit()


def list_templates(db: Session, user: User) -> list[BioTemplateSummaryResponse]:
    templates = list(
        db.execute(
            select(BioTemplate)
            .where(BioTemplate.owner_id == user.id)
            .order_by(BioTemplate.is_default.desc(), BioTemplate.updated_at.desc(), BioTemplate.name.asc())
        )
        .scalars()
        .all()
    )
    return [_template_summary_response(template) for template in templates]


def create_template(
    db: Session,
    user: User,
    payload: BioTemplateCreateRequest,
) -> BioTemplateDetailResponse:
    template = BioTemplate(owner_id=user.id, **payload.model_dump())
    db.add(template)
    db.commit()
    db.refresh(template)
    return _template_detail_response(template)


def get_template(db: Session, user: User, template_id: int) -> BioTemplateDetailResponse:
    return _template_detail_response(_get_owned_template(db, user, template_id))


def update_template(
    db: Session,
    user: User,
    template_id: int,
    payload: BioTemplateUpdateRequest,
) -> BioTemplateDetailResponse:
    template = _get_owned_template(db, user, template_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(template, field, value)
    db.commit()
    db.refresh(template)
    return _template_detail_response(template)


def delete_template(db: Session, user: User, template_id: int) -> None:
    template = _get_owned_template(db, user, template_id)
    db.delete(template)
    db.commit()


def _next_version_number(db: Session, profile_id: int) -> int:
    current = db.execute(
        select(func.max(BioVersion.version_number)).where(BioVersion.profile_id == profile_id)
    ).scalar_one()
    return int(current or 0) + 1


def list_versions_by_profile(
    db: Session,
    user: User,
    profile_id: int,
) -> list[BioVersionSummaryResponse]:
    profile = _get_owned_profile(db, user, profile_id)
    versions = list(
        db.execute(
            select(BioVersion)
            .where(BioVersion.owner_id == user.id, BioVersion.profile_id == profile.id)
            .order_by(BioVersion.version_number.desc(), BioVersion.created_at.desc())
        )
        .scalars()
        .all()
    )
    return [_version_summary_response(version, profile.title) for version in versions]


def list_versions(db: Session, user: User) -> list[BioVersionSummaryResponse]:
    rows = db.execute(
        select(BioVersion, LinkedInProfile.title)
        .join(LinkedInProfile, LinkedInProfile.id == BioVersion.profile_id)
        .where(BioVersion.owner_id == user.id)
        .order_by(BioVersion.created_at.desc(), BioVersion.version_number.desc())
    ).all()
    return [_version_summary_response(version, profile_title) for version, profile_title in rows]


def create_version(
    db: Session,
    user: User,
    payload: BioVersionCreateRequest,
) -> BioVersionDetailResponse:
    profile = _get_owned_profile(db, user, payload.profile_id)
    version = BioVersion(
        owner_id=user.id,
        platform_id=payload.platform_id or profile.platform_id,
        profile_id=profile.id,
        version_number=payload.version_number or _next_version_number(db, profile.id),
        headline=payload.headline,
        bio=payload.bio,
        change_summary=payload.change_summary,
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    return _version_detail_response(version, profile.title)


def get_version(db: Session, user: User, version_id: int) -> BioVersionDetailResponse:
    version = _get_owned_version(db, user, version_id)
    profile = _get_owned_profile(db, user, version.profile_id)
    return _version_detail_response(version, profile.title)


def delete_version(db: Session, user: User, version_id: int) -> None:
    version = _get_owned_version(db, user, version_id)
    db.delete(version)
    db.commit()


def get_dashboard(db: Session, user: User) -> LinkedInBioOptimizerDashboardResponse:
    profiles = list_profiles(db, user)
    templates = list_templates(db, user)
    versions = list_versions(db, user)
    return LinkedInBioOptimizerDashboardResponse(
        profiles=profiles,
        templates=templates,
        versions=versions,
        profile_count=len(profiles),
        template_count=len(templates),
        version_count=len(versions),
        optimized_profile_count=sum(1 for profile in profiles if profile.optimized_bio_preview),
    )
