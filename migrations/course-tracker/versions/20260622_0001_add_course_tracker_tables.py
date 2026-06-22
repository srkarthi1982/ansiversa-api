"""add_course_tracker_tables

Revision ID: 20260622_0001
Revises:
Create Date: 2026-06-22

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260622_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())

    if "Courses" not in table_names:
        op.create_table(
            "Courses",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("provider", sa.String(length=120), nullable=False),
            sa.Column("category", sa.String(length=120), nullable=True),
            sa.Column("goal", sa.Text(), nullable=False),
            sa.Column("startDate", sa.Date(), nullable=False),
            sa.Column("targetDate", sa.Date(), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
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
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_Courses_ownerId", "Courses", ["ownerId"])

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "CourseModules" not in table_names:
        op.create_table(
            "CourseModules",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("courseId", sa.Integer(), nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("sequence", sa.Integer(), server_default="1", nullable=False),
            sa.Column("status", sa.String(length=40), server_default="notStarted", nullable=False),
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
            sa.ForeignKeyConstraint(["courseId"], ["Courses.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_CourseModules_courseId", "CourseModules", ["courseId"])
        op.create_index("ix_CourseModules_ownerId", "CourseModules", ["ownerId"])

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "CourseProgressLogs" not in table_names:
        op.create_table(
            "CourseProgressLogs",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("courseId", sa.Integer(), nullable=False),
            sa.Column("moduleId", sa.Integer(), nullable=True),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("progressDate", sa.Date(), nullable=False),
            sa.Column("minutes", sa.Integer(), nullable=False),
            sa.Column("summary", sa.String(length=240), nullable=False),
            sa.Column("reflection", sa.Text(), nullable=True),
            sa.Column(
                "createdAt",
                sa.DateTime(timezone=True),
                server_default=sa.text("(CURRENT_TIMESTAMP)"),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["courseId"], ["Courses.id"]),
            sa.ForeignKeyConstraint(["moduleId"], ["CourseModules.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_CourseProgressLogs_courseId", "CourseProgressLogs", ["courseId"])
        op.create_index("ix_CourseProgressLogs_moduleId", "CourseProgressLogs", ["moduleId"])
        op.create_index("ix_CourseProgressLogs_ownerId", "CourseProgressLogs", ["ownerId"])


def downgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())

    if "CourseProgressLogs" in table_names:
        op.drop_index("ix_CourseProgressLogs_ownerId", table_name="CourseProgressLogs")
        op.drop_index("ix_CourseProgressLogs_moduleId", table_name="CourseProgressLogs")
        op.drop_index("ix_CourseProgressLogs_courseId", table_name="CourseProgressLogs")
        op.drop_table("CourseProgressLogs")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "CourseModules" in table_names:
        op.drop_index("ix_CourseModules_ownerId", table_name="CourseModules")
        op.drop_index("ix_CourseModules_courseId", table_name="CourseModules")
        op.drop_table("CourseModules")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "Courses" in table_names:
        op.drop_index("ix_Courses_ownerId", table_name="Courses")
        op.drop_table("Courses")
