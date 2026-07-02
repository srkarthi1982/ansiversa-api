from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.grammar_and_paraphrasing_assistant.db import GrammarAndParaphrasingAssistantBase


class GrammarProject(GrammarAndParaphrasingAssistantBase):
    __tablename__ = "GrammarProjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    original_text: Mapped[str] = mapped_column("originalText", Text, nullable=False)
    language: Mapped[str | None] = mapped_column(String(80), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="draft", server_default="draft", nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    results: Mapped[list["GrammarResult"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    jobs: Mapped[list["GrammarJob"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class GrammarResult(GrammarAndParaphrasingAssistantBase):
    __tablename__ = "GrammarResults"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    project_id: Mapped[int] = mapped_column("projectId", Integer, ForeignKey("GrammarProjects.id"), index=True, nullable=False)
    corrected_text: Mapped[str] = mapped_column("correctedText", Text, nullable=False)
    paraphrased_text: Mapped[str] = mapped_column("paraphrasedText", Text, nullable=False)
    tone: Mapped[str | None] = mapped_column(String(80), nullable=True)
    grammar_score: Mapped[int] = mapped_column("grammarScore", Integer, default=82, server_default="82", nullable=False)
    readability_score: Mapped[int] = mapped_column("readabilityScore", Integer, default=78, server_default="78", nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)

    project: Mapped[GrammarProject] = relationship(back_populates="results")


class GrammarJob(GrammarAndParaphrasingAssistantBase):
    __tablename__ = "GrammarJobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    project_id: Mapped[int] = mapped_column("projectId", Integer, ForeignKey("GrammarProjects.id"), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="completed", server_default="completed", nullable=False)
    provider: Mapped[str] = mapped_column(String(80), default="placeholder", server_default="placeholder", nullable=False)
    action: Mapped[str] = mapped_column(String(40), default="improve", server_default="improve", nullable=False)
    started_at: Mapped[datetime] = mapped_column("startedAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column("completedAt", DateTime(timezone=True), nullable=True)

    project: Mapped[GrammarProject] = relationship(back_populates="jobs")
