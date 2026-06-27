from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.portfolio_creator.db import PortfolioCreatorBase


class PortfolioProfile(PortfolioCreatorBase):
    __tablename__ = "PortfolioProfiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column(
        "ownerId",
        String(36),
        index=True,
        nullable=False,
    )
    display_name: Mapped[str] = mapped_column("displayName", String(140), nullable=False)
    headline: Mapped[str] = mapped_column(String(180), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str | None] = mapped_column(String(140), nullable=True)
    website_url: Mapped[str | None] = mapped_column("websiteUrl", String(240), nullable=True)
    status: Mapped[str] = mapped_column(
        String(40),
        default="draft",
        server_default="draft",
        nullable=False,
    )
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

    projects: Mapped[list["PortfolioProject"]] = relationship(
        back_populates="profile",
        cascade="all, delete-orphan",
    )
    skills: Mapped[list["PortfolioSkill"]] = relationship(
        back_populates="profile",
        cascade="all, delete-orphan",
    )
    publish_settings: Mapped[list["PortfolioPublishSetting"]] = relationship(
        back_populates="profile",
        cascade="all, delete-orphan",
    )


class PortfolioProject(PortfolioCreatorBase):
    __tablename__ = "PortfolioProjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(
        "profileId",
        Integer,
        ForeignKey("PortfolioProfiles.id"),
        index=True,
        nullable=False,
    )
    owner_id: Mapped[str] = mapped_column(
        "ownerId",
        String(36),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    project_url: Mapped[str | None] = mapped_column("projectUrl", String(240), nullable=True)
    role: Mapped[str | None] = mapped_column(String(140), nullable=True)
    position: Mapped[int] = mapped_column(Integer, default=1, server_default="1", nullable=False)
    status: Mapped[str] = mapped_column(
        String(40),
        default="draft",
        server_default="draft",
        nullable=False,
    )
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

    profile: Mapped[PortfolioProfile] = relationship(back_populates="projects")


class PortfolioSkill(PortfolioCreatorBase):
    __tablename__ = "PortfolioSkills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(
        "profileId",
        Integer,
        ForeignKey("PortfolioProfiles.id"),
        index=True,
        nullable=False,
    )
    owner_id: Mapped[str] = mapped_column(
        "ownerId",
        String(36),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    category: Mapped[str] = mapped_column(
        String(80),
        default="technical",
        server_default="technical",
        nullable=False,
    )
    proficiency: Mapped[str] = mapped_column(
        String(40),
        default="intermediate",
        server_default="intermediate",
        nullable=False,
    )
    position: Mapped[int] = mapped_column(Integer, default=1, server_default="1", nullable=False)
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

    profile: Mapped[PortfolioProfile] = relationship(back_populates="skills")


class PortfolioPublishSetting(PortfolioCreatorBase):
    __tablename__ = "PortfolioPublishSettings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(
        "profileId",
        Integer,
        ForeignKey("PortfolioProfiles.id"),
        index=True,
        nullable=False,
    )
    owner_id: Mapped[str] = mapped_column(
        "ownerId",
        String(36),
        index=True,
        nullable=False,
    )
    visibility: Mapped[str] = mapped_column(
        String(40),
        default="private",
        server_default="private",
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(String(120), nullable=False)
    theme: Mapped[str] = mapped_column(
        String(40),
        default="classic",
        server_default="classic",
        nullable=False,
    )
    is_published: Mapped[bool] = mapped_column(
        "isPublished",
        Boolean,
        default=False,
        server_default="0",
        nullable=False,
    )
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

    profile: Mapped[PortfolioProfile] = relationship(back_populates="publish_settings")
