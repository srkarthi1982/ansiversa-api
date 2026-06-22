from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.visiting_card_maker.models import CardDesign, CardProfile
from app.modules.visiting_card_maker.schemas import (
    CardCreateRequest,
    CardDesignResponse,
    CardProfileResponse,
    CardUpdateRequest,
    VisitingCardMakerDashboardResponse,
    VisitingCardResponse,
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _card_response(profile: CardProfile, design: CardDesign) -> VisitingCardResponse:
    updated_at = max(profile.updated_at, design.updated_at)

    return VisitingCardResponse(
        id=design.id,
        profile=CardProfileResponse.model_validate(profile),
        design=CardDesignResponse.model_validate(design),
        created_at=design.created_at,
        updated_at=updated_at,
    )


def _get_owned_card(
    db: Session,
    user: User,
    design_id: str,
) -> tuple[CardProfile, CardDesign]:
    row = db.execute(
        select(CardProfile, CardDesign)
        .join(CardDesign, CardDesign.profile_id == CardProfile.id)
        .where(CardDesign.id == design_id, CardDesign.user_id == user.id)
    ).one_or_none()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visiting card was not found.",
        )

    return row


def list_cards(db: Session, user: User) -> list[VisitingCardResponse]:
    rows = db.execute(
        select(CardProfile, CardDesign)
        .join(CardDesign, CardDesign.profile_id == CardProfile.id)
        .where(CardDesign.user_id == user.id)
        .order_by(CardDesign.updated_at.desc(), CardProfile.full_name.asc())
    ).all()

    return [_card_response(profile, design) for profile, design in rows]


def get_dashboard(db: Session, user: User) -> VisitingCardMakerDashboardResponse:
    cards = list_cards(db, user)

    return VisitingCardMakerDashboardResponse(
        cards=cards,
        selected_card=cards[0] if cards else None,
    )


def create_card(
    db: Session,
    user: User,
    payload: CardCreateRequest,
) -> VisitingCardResponse:
    profile = CardProfile(
        user_id=user.id,
        profile_name=payload.full_name,
        full_name=payload.full_name,
        job_title=payload.job_title,
        company_name=payload.company_name,
        phone_number=payload.phone_number,
        email=payload.email,
        website=payload.website,
        address=payload.address,
        tagline=payload.tagline,
    )
    db.add(profile)
    db.flush()

    design = CardDesign(
        user_id=user.id,
        profile_id=profile.id,
        template_key=payload.template_key,
    )
    db.add(design)
    db.commit()
    db.refresh(profile)
    db.refresh(design)

    return _card_response(profile, design)


def update_card(
    db: Session,
    user: User,
    design_id: str,
    payload: CardUpdateRequest,
) -> VisitingCardResponse:
    profile, design = _get_owned_card(db, user, design_id)
    values = payload.model_dump(exclude_unset=True)
    for field in (
        "full_name",
        "job_title",
        "company_name",
        "phone_number",
        "email",
        "website",
        "address",
        "tagline",
    ):
        if field in values:
            setattr(profile, field, values[field])
    if "full_name" in values:
        profile.profile_name = values["full_name"]
    if "template_key" in values:
        design.template_key = values["template_key"]

    timestamp = _now()
    profile.updated_at = timestamp
    design.updated_at = timestamp
    db.commit()
    db.refresh(profile)
    db.refresh(design)

    return _card_response(profile, design)


def duplicate_card(db: Session, user: User, design_id: str) -> VisitingCardResponse:
    profile, design = _get_owned_card(db, user, design_id)
    duplicate_profile = CardProfile(
        user_id=user.id,
        full_name=f"{profile.full_name} Copy",
        job_title=profile.job_title,
        company_name=profile.company_name,
        phone_number=profile.phone_number,
        email=profile.email,
        website=profile.website,
        address=profile.address,
        tagline=profile.tagline,
    )
    db.add(duplicate_profile)
    db.flush()

    duplicate_design = CardDesign(
        user_id=user.id,
        profile_id=duplicate_profile.id,
        template_key=design.template_key,
    )
    db.add(duplicate_design)
    db.commit()
    db.refresh(duplicate_profile)
    db.refresh(duplicate_design)

    return _card_response(duplicate_profile, duplicate_design)


def delete_card(db: Session, user: User, design_id: str) -> None:
    profile, design = _get_owned_card(db, user, design_id)
    db.execute(delete(CardDesign).where(CardDesign.id == design.id))
    db.delete(profile)
    db.commit()
