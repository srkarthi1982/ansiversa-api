from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.snippet_generator.db import SnippetGeneratorBase


class SnippetProject(SnippetGeneratorBase):
    __tablename__ = "SnippetProjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    language: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="draft", server_default="draft", nullable=False)
    goal: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    snippets: Mapped[list["Snippet"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    categories: Mapped[list["SnippetCategory"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class SnippetCategory(SnippetGeneratorBase):
    __tablename__ = "SnippetCategories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    project_id: Mapped[int] = mapped_column("projectId", Integer, ForeignKey("SnippetProjects.id"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(140), nullable=False)
    color: Mapped[str | None] = mapped_column(String(40), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    project: Mapped[SnippetProject] = relationship(back_populates="categories")
    snippets: Mapped[list["Snippet"]] = relationship(back_populates="category")


class Snippet(SnippetGeneratorBase):
    __tablename__ = "SnippetLibrary"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    project_id: Mapped[int] = mapped_column("projectId", Integer, ForeignKey("SnippetProjects.id"), index=True, nullable=False)
    category_id: Mapped[int | None] = mapped_column("categoryId", Integer, ForeignKey("SnippetCategories.id"), index=True, nullable=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    language: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="draft", server_default="draft", nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    snippet_text: Mapped[str | None] = mapped_column("snippetText", Text, nullable=True)
    usage_notes: Mapped[str | None] = mapped_column("usageNotes", Text, nullable=True)
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    project: Mapped[SnippetProject] = relationship(back_populates="snippets")
    category: Mapped[SnippetCategory | None] = relationship(back_populates="snippets")
    history: Mapped[list["SnippetHistory"]] = relationship(back_populates="snippet", cascade="all, delete-orphan")


class SnippetHistory(SnippetGeneratorBase):
    __tablename__ = "SnippetHistory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    snippet_id: Mapped[int] = mapped_column("snippetId", Integer, ForeignKey("SnippetLibrary.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    event_type: Mapped[str | None] = mapped_column("eventType", String(80), nullable=True)
    occurred_at: Mapped[str | None] = mapped_column("occurredAt", String(40), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    revision_notes: Mapped[str | None] = mapped_column("revisionNotes", Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    snippet: Mapped[Snippet] = relationship(back_populates="history")
