"""add_lesson_builder_tables

Revision ID: 20260616_lesson_0001
Revises:
Create Date: 2026-06-16

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260616_lesson_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())

    if "LessonPlans" not in table_names:
        op.create_table(
            "LessonPlans",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("subject", sa.String(length=140), nullable=False),
            sa.Column("audience", sa.String(length=140), nullable=False),
            sa.Column("durationMinutes", sa.Integer(), nullable=False),
            sa.Column("objective", sa.Text(), nullable=False),
            sa.Column("status", sa.String(length=40), server_default="draft", nullable=False),
            sa.Column(
                "createdAt",
                sa.DateTime(timezone=True),
                server_default=sa.text("(CURRENT_TIMESTAMP)"),
                nullable=False,
            ),
            sa.Column(
                "updatedAt",
                sa.DateTime(timezone=True),
                server_default=sa.text("(CURRENT_TIMESTAMP)"),
                nullable=False,
            ),
            sa.Column("publishedAt", sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            "ix_LessonPlans_userId",
            "LessonPlans",
            ["userId"],
            unique=False,
        )

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "LessonSections" not in table_names:
        op.create_table(
            "LessonSections",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("lessonId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("sectionType", sa.String(length=60), nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("position", sa.Integer(), nullable=False),
            sa.Column(
                "createdAt",
                sa.DateTime(timezone=True),
                server_default=sa.text("(CURRENT_TIMESTAMP)"),
                nullable=False,
            ),
            sa.Column(
                "updatedAt",
                sa.DateTime(timezone=True),
                server_default=sa.text("(CURRENT_TIMESTAMP)"),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["lessonId"], ["LessonPlans.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            "ix_LessonSections_lessonId",
            "LessonSections",
            ["lessonId"],
            unique=False,
        )


def downgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())

    if "LessonSections" in table_names:
        op.drop_index("ix_LessonSections_lessonId", table_name="LessonSections")
        op.drop_table("LessonSections")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "LessonPlans" in table_names:
        op.drop_index("ix_LessonPlans_userId", table_name="LessonPlans")
        op.drop_table("LessonPlans")
