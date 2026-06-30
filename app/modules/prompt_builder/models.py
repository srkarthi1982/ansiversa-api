from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.prompt_builder.db import PromptBuilderBase


class PromptProject(PromptBuilderBase):
    __tablename__ = "PromptProjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    category: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="draft", server_default="draft", nullable=False)
    goal: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    prompts: Mapped[list["Prompt"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    templates: Mapped[list["PromptTemplate"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class Prompt(PromptBuilderBase):
    __tablename__ = "PromptLibrary"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    project_id: Mapped[int] = mapped_column("projectId", Integer, ForeignKey("PromptProjects.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    category: Mapped[str | None] = mapped_column(String(120), nullable=True)
    model_target: Mapped[str | None] = mapped_column("modelTarget", String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="draft", server_default="draft", nullable=False)
    prompt_text: Mapped[str | None] = mapped_column("promptText", Text, nullable=True)
    context_text: Mapped[str | None] = mapped_column("contextText", Text, nullable=True)
    output_format: Mapped[str | None] = mapped_column("outputFormat", Text, nullable=True)
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    project: Mapped[PromptProject] = relationship(back_populates="prompts")
    history: Mapped[list["PromptHistory"]] = relationship(back_populates="prompt", cascade="all, delete-orphan")


class PromptTemplate(PromptBuilderBase):
    __tablename__ = "PromptTemplates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    project_id: Mapped[int] = mapped_column("projectId", Integer, ForeignKey("PromptProjects.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    category: Mapped[str | None] = mapped_column(String(120), nullable=True)
    template_text: Mapped[str | None] = mapped_column("templateText", Text, nullable=True)
    usage_notes: Mapped[str | None] = mapped_column("usageNotes", Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    project: Mapped[PromptProject] = relationship(back_populates="templates")


class PromptHistory(PromptBuilderBase):
    __tablename__ = "PromptHistory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    prompt_id: Mapped[int] = mapped_column("promptId", Integer, ForeignKey("PromptLibrary.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    event_type: Mapped[str | None] = mapped_column("eventType", String(80), nullable=True)
    occurred_at: Mapped[str | None] = mapped_column("occurredAt", String(40), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    revision_notes: Mapped[str | None] = mapped_column("revisionNotes", Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    prompt: Mapped[Prompt] = relationship(back_populates="history")
