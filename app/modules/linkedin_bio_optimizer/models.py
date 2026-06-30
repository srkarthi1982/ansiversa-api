from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.linkedin_bio_optimizer.db import LinkedinBioOptimizerBase


class LinkedInProfile(LinkedinBioOptimizerBase):
    __tablename__ = "LinkedInProfiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    industry: Mapped[str | None] = mapped_column(String(120), nullable=True)
    career_level: Mapped[str | None] = mapped_column("careerLevel", String(80), nullable=True)
    target_role: Mapped[str | None] = mapped_column("targetRole", String(180), nullable=True)
    current_headline: Mapped[str | None] = mapped_column("currentHeadline", String(220), nullable=True)
    current_bio: Mapped[str | None] = mapped_column("currentBio", Text, nullable=True)
    optimized_bio: Mapped[str | None] = mapped_column("optimizedBio", Text, nullable=True)
    keywords: Mapped[str | None] = mapped_column(Text, nullable=True)
    tone: Mapped[str | None] = mapped_column(String(80), nullable=True)
    language: Mapped[str | None] = mapped_column(String(80), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        "createdAt",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updatedAt",
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    versions: Mapped[list["BioVersion"]] = relationship(
        back_populates="profile",
        cascade="all, delete-orphan",
    )


class BioTemplate(LinkedinBioOptimizerBase):
    __tablename__ = "BioTemplates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    industry: Mapped[str | None] = mapped_column(String(120), nullable=True)
    career_level: Mapped[str | None] = mapped_column("careerLevel", String(80), nullable=True)
    template: Mapped[str] = mapped_column(Text, nullable=False)
    is_default: Mapped[bool] = mapped_column("isDefault", Boolean, default=False, server_default="0", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        "createdAt",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updatedAt",
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class BioVersion(LinkedinBioOptimizerBase):
    __tablename__ = "BioVersions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    profile_id: Mapped[int] = mapped_column(
        "profileId",
        Integer,
        ForeignKey("LinkedInProfiles.id"),
        index=True,
        nullable=False,
    )
    version_number: Mapped[int] = mapped_column("versionNumber", Integer, nullable=False)
    headline: Mapped[str | None] = mapped_column(String(220), nullable=True)
    bio: Mapped[str] = mapped_column(Text, nullable=False)
    change_summary: Mapped[str | None] = mapped_column("changeSummary", Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        "createdAt",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    profile: Mapped[LinkedInProfile] = relationship(back_populates="versions")
