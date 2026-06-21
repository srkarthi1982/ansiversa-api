"""rebuild_lesson_plans_uuid_pk

Revision ID: 20260616_lesson_0003
Revises: 20260616_lesson_0002
Create Date: 2026-06-16

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260616_lesson_0003"
down_revision: str | None = "20260616_lesson_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _lesson_plans_id_type() -> str | None:
    inspector = sa.inspect(op.get_bind())
    if "LessonPlans" not in inspector.get_table_names():
        return None

    for column in inspector.get_columns("LessonPlans"):
        if column["name"] == "id":
            return str(column["type"]).upper()

    return None


def upgrade() -> None:
    id_type = _lesson_plans_id_type()
    if id_type is None or "INT" not in id_type:
        return

    lesson_count = op.get_bind().execute(
        sa.text('SELECT COUNT(*) FROM "LessonPlans"')
    ).scalar_one()
    if lesson_count:
        raise RuntimeError(
            "Cannot rebuild LessonPlans primary key while existing lessons are present."
        )

    indexes = {
        index["name"]
        for index in sa.inspect(op.get_bind()).get_indexes("LessonPlans")
    }
    if "ix_LessonPlans_userId" in indexes:
        op.drop_index("ix_LessonPlans_userId", table_name="LessonPlans")

    op.drop_table("LessonPlans")
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


def downgrade() -> None:
    lesson_count = op.get_bind().execute(
        sa.text('SELECT COUNT(*) FROM "LessonPlans"')
    ).scalar_one()
    if lesson_count:
        raise RuntimeError(
            "Cannot downgrade LessonPlans primary key while existing lessons are present."
        )

    indexes = {
        index["name"]
        for index in sa.inspect(op.get_bind()).get_indexes("LessonPlans")
    }
    if "ix_LessonPlans_userId" in indexes:
        op.drop_index("ix_LessonPlans_userId", table_name="LessonPlans")

    op.drop_table("LessonPlans")
    op.create_table(
        "LessonPlans",
        sa.Column("id", sa.Integer(), nullable=True),
        sa.Column("ownerId", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("subject", sa.Text(), nullable=True),
        sa.Column("gradeLevel", sa.Text(), nullable=True),
        sa.Column("overview", sa.Text(), nullable=True),
        sa.Column("durationMinutes", sa.Integer(), nullable=True),
        sa.Column("tags", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), server_default="draft", nullable=False),
        sa.Column(
            "createdAt",
            sa.Text(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updatedAt",
            sa.Text(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("userId", sa.String(length=36), nullable=True),
        sa.Column("audience", sa.String(length=140), nullable=True),
        sa.Column("objective", sa.Text(), nullable=True),
        sa.Column("publishedAt", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_LessonPlans_userId",
        "LessonPlans",
        ["userId"],
        unique=False,
    )
