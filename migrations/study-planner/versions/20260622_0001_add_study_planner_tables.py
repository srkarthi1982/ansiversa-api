"""add_study_planner_tables

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

    if "StudyPlans" not in table_names:
        op.create_table(
            "StudyPlans",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("subject", sa.String(length=120), nullable=False),
            sa.Column("goal", sa.Text(), nullable=False),
            sa.Column("startDate", sa.Date(), nullable=False),
            sa.Column("targetDate", sa.Date(), nullable=False),
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
        op.create_index("ix_StudyPlans_ownerId", "StudyPlans", ["ownerId"])

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "StudyPlanTasks" not in table_names:
        op.create_table(
            "StudyPlanTasks",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("planId", sa.Integer(), nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("dueDate", sa.Date(), nullable=True),
            sa.Column("priority", sa.String(length=20), server_default="medium", nullable=False),
            sa.Column("status", sa.String(length=40), server_default="pending", nullable=False),
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
            sa.ForeignKeyConstraint(["planId"], ["StudyPlans.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_StudyPlanTasks_ownerId", "StudyPlanTasks", ["ownerId"])
        op.create_index("ix_StudyPlanTasks_planId", "StudyPlanTasks", ["planId"])

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "StudyLogs" not in table_names:
        op.create_table(
            "StudyLogs",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("planId", sa.Integer(), nullable=False),
            sa.Column("taskId", sa.Integer(), nullable=True),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("studyDate", sa.Date(), nullable=False),
            sa.Column("minutes", sa.Integer(), nullable=False),
            sa.Column("focus", sa.String(length=180), nullable=False),
            sa.Column("reflection", sa.Text(), nullable=True),
            sa.Column(
                "createdAt",
                sa.DateTime(timezone=True),
                server_default=sa.text("(CURRENT_TIMESTAMP)"),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["planId"], ["StudyPlans.id"]),
            sa.ForeignKeyConstraint(["taskId"], ["StudyPlanTasks.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_StudyLogs_ownerId", "StudyLogs", ["ownerId"])
        op.create_index("ix_StudyLogs_planId", "StudyLogs", ["planId"])
        op.create_index("ix_StudyLogs_taskId", "StudyLogs", ["taskId"])


def downgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())

    if "StudyLogs" in table_names:
        op.drop_index("ix_StudyLogs_taskId", table_name="StudyLogs")
        op.drop_index("ix_StudyLogs_planId", table_name="StudyLogs")
        op.drop_index("ix_StudyLogs_ownerId", table_name="StudyLogs")
        op.drop_table("StudyLogs")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "StudyPlanTasks" in table_names:
        op.drop_index("ix_StudyPlanTasks_planId", table_name="StudyPlanTasks")
        op.drop_index("ix_StudyPlanTasks_ownerId", table_name="StudyPlanTasks")
        op.drop_table("StudyPlanTasks")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "StudyPlans" in table_names:
        op.drop_index("ix_StudyPlans_ownerId", table_name="StudyPlans")
        op.drop_table("StudyPlans")
