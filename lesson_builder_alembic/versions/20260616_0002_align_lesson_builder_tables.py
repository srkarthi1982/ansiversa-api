"""align_lesson_builder_tables

Revision ID: 20260616_lesson_0002
Revises: 20260616_lesson_0001
Create Date: 2026-06-16

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260616_lesson_0002"
down_revision: str | None = "20260616_lesson_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _table_columns(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    if table_name not in inspector.get_table_names():
        return set()

    return {column["name"] for column in inspector.get_columns(table_name)}


def _table_indexes(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    if table_name not in inspector.get_table_names():
        return set()

    return {index["name"] for index in inspector.get_indexes(table_name)}


def upgrade() -> None:
    columns = _table_columns("LessonPlans")

    if "userId" not in columns:
        op.add_column("LessonPlans", sa.Column("userId", sa.String(length=36)))
    if "audience" not in columns:
        op.add_column("LessonPlans", sa.Column("audience", sa.String(length=140)))
    if "objective" not in columns:
        op.add_column("LessonPlans", sa.Column("objective", sa.Text()))
    if "publishedAt" not in columns:
        op.add_column("LessonPlans", sa.Column("publishedAt", sa.DateTime(timezone=True)))

    columns = _table_columns("LessonPlans")
    if "userId" in columns and "ownerId" in columns:
        op.execute(sa.text('UPDATE "LessonPlans" SET "userId" = "ownerId" WHERE "userId" IS NULL'))
    if "audience" in columns and "gradeLevel" in columns:
        op.execute(
            sa.text(
                'UPDATE "LessonPlans" '
                'SET "audience" = COALESCE("gradeLevel", \'General learners\') '
                'WHERE "audience" IS NULL'
            )
        )
    elif "audience" in columns:
        op.execute(
            sa.text(
                'UPDATE "LessonPlans" '
                'SET "audience" = \'General learners\' '
                'WHERE "audience" IS NULL'
            )
        )
    if "objective" in columns and "overview" in columns:
        op.execute(
            sa.text(
                'UPDATE "LessonPlans" '
                'SET "objective" = COALESCE("overview", \'Lesson objective\') '
                'WHERE "objective" IS NULL'
            )
        )
    elif "objective" in columns:
        op.execute(
            sa.text(
                'UPDATE "LessonPlans" '
                'SET "objective" = \'Lesson objective\' '
                'WHERE "objective" IS NULL'
            )
        )

    indexes = _table_indexes("LessonPlans")
    if "ix_LessonPlans_userId" not in indexes:
        op.create_index(
            "ix_LessonPlans_userId",
            "LessonPlans",
            ["userId"],
            unique=False,
        )


def downgrade() -> None:
    indexes = _table_indexes("LessonPlans")
    if "ix_LessonPlans_userId" in indexes:
        op.drop_index("ix_LessonPlans_userId", table_name="LessonPlans")

    columns = _table_columns("LessonPlans")
    for column_name in ("publishedAt", "objective", "audience", "userId"):
        if column_name in columns:
            op.drop_column("LessonPlans", column_name)
