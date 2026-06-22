from uuid import uuid4

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.resume_builder.db import ResumeBuilderBase


class ResumeProject(ResumeBuilderBase):
    __tablename__ = "ResumeProject"

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[str] = mapped_column("userId", Text, index=True, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    template_key: Mapped[str] = mapped_column("templateKey", Text, nullable=False)
    is_default: Mapped[bool] = mapped_column(
        "isDefault",
        Boolean,
        default=False,
        server_default=text("FALSE"),
        nullable=False,
    )
    photo_key: Mapped[str] = mapped_column(
        "photoKey",
        Text,
        default="",
        server_default="",
        nullable=False,
    )
    photo_url: Mapped[str] = mapped_column(
        "photoUrl",
        Text,
        default="",
        server_default="",
        nullable=False,
    )
    photo_updated_at: Mapped[str] = mapped_column(
        "photoUpdatedAt",
        Text,
        server_default=text("CURRENT_TIMESTAMP"),
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

    sections: Mapped[list["ResumeSection"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )


class ResumeSection(ResumeBuilderBase):
    __tablename__ = "ResumeSection"

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    project_id: Mapped[str] = mapped_column(
        "projectId",
        Text,
        ForeignKey("ResumeProject.id"),
        index=True,
        nullable=False,
    )
    key: Mapped[str] = mapped_column(Text, nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(
        "isEnabled",
        Boolean,
        default=True,
        server_default=text("TRUE"),
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

    project: Mapped[ResumeProject] = relationship(back_populates="sections")
    items: Mapped[list["ResumeItem"]] = relationship(
        back_populates="section",
        cascade="all, delete-orphan",
    )


class ResumeItem(ResumeBuilderBase):
    __tablename__ = "ResumeItem"

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    section_id: Mapped[str] = mapped_column(
        "sectionId",
        Text,
        ForeignKey("ResumeSection.id"),
        index=True,
        nullable=False,
    )
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    data: Mapped[str] = mapped_column(Text, nullable=False)
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

    section: Mapped[ResumeSection] = relationship(back_populates="items")
