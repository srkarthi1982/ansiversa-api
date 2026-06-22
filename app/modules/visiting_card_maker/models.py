from uuid import uuid4

from sqlalchemy import ForeignKey, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.visiting_card_maker.db import VisitingCardMakerBase


class CardProfile(VisitingCardMakerBase):
    __tablename__ = "CardProfiles"

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[str] = mapped_column("userId", Text, index=True, nullable=False)
    profile_name: Mapped[str] = mapped_column(
        "profileName",
        String(120),
        default="",
        server_default="",
        nullable=False,
    )
    full_name: Mapped[str] = mapped_column("fullName", String(120), nullable=False)
    job_title: Mapped[str] = mapped_column(
        "jobTitle",
        String(120),
        default="",
        server_default="",
        nullable=False,
    )
    company_name: Mapped[str] = mapped_column(
        "companyName",
        String(140),
        default="",
        server_default="",
        nullable=False,
    )
    phone_number: Mapped[str] = mapped_column(
        "phoneNumber",
        String(60),
        default="",
        server_default="",
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        String(180),
        default="",
        server_default="",
        nullable=False,
    )
    website: Mapped[str] = mapped_column(
        String(180),
        default="",
        server_default="",
        nullable=False,
    )
    address: Mapped[str] = mapped_column(
        Text,
        default="",
        server_default="",
        nullable=False,
    )
    tagline: Mapped[str] = mapped_column(
        String(180),
        default="",
        server_default="",
        nullable=False,
    )
    created_at: Mapped[str] = mapped_column(
        "createdAt",
        Text,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    updated_at: Mapped[str] = mapped_column(
        "updatedAt",
        Text,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    designs: Mapped[list["CardDesign"]] = relationship(
        back_populates="profile",
        cascade="all, delete-orphan",
    )


class CardDesign(VisitingCardMakerBase):
    __tablename__ = "CardDesigns"

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[str] = mapped_column("userId", Text, index=True, nullable=False)
    profile_id: Mapped[str] = mapped_column(
        "profileId",
        Text,
        ForeignKey("CardProfiles.id"),
        index=True,
        nullable=False,
    )
    template_key: Mapped[str] = mapped_column(
        "templateKey",
        String(40),
        default="professional",
        server_default="professional",
        nullable=False,
    )
    created_at: Mapped[str] = mapped_column(
        "createdAt",
        Text,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    updated_at: Mapped[str] = mapped_column(
        "updatedAt",
        Text,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    profile: Mapped[CardProfile] = relationship(back_populates="designs")
