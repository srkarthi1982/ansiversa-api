from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.creative_title_generator.db import CreativeTitleGeneratorBase


class TitleProject(CreativeTitleGeneratorBase):
    __tablename__ = "TitleProjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    topic: Mapped[str] = mapped_column(Text, nullable=False)
    audience: Mapped[str | None] = mapped_column(String(160), nullable=True)
    language: Mapped[str | None] = mapped_column(String(80), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="draft", server_default="draft", nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    generated_titles: Mapped[list["GeneratedTitle"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    jobs: Mapped[list["TitleJob"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class GeneratedTitle(CreativeTitleGeneratorBase):
    __tablename__ = "GeneratedTitles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    project_id: Mapped[int] = mapped_column("projectId", Integer, ForeignKey("TitleProjects.id"), index=True, nullable=False)
    generated_title: Mapped[str] = mapped_column("generatedTitle", String(220), nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    score: Mapped[int] = mapped_column(Integer, default=82, server_default="82", nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)

    project: Mapped[TitleProject] = relationship(back_populates="generated_titles")


class TitleJob(CreativeTitleGeneratorBase):
    __tablename__ = "TitleJobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    project_id: Mapped[int] = mapped_column("projectId", Integer, ForeignKey("TitleProjects.id"), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="completed", server_default="completed", nullable=False)
    provider: Mapped[str] = mapped_column(String(80), default="placeholder", server_default="placeholder", nullable=False)
    generation_type: Mapped[str] = mapped_column("generationType", String(40), default="blog", server_default="blog", nullable=False)
    started_at: Mapped[datetime] = mapped_column("startedAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column("completedAt", DateTime(timezone=True), nullable=True)

    project: Mapped[TitleProject] = relationship(back_populates="jobs")
