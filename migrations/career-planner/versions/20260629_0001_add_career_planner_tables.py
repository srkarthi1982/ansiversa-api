"""add_career_planner_tables

Revision ID: 20260629_0001
Revises:
Create Date: 2026-06-29

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260629_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


INDEXES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("CareerGoals_ownerId_updatedAt_title_idx", "CareerGoals", ("ownerId", "updatedAt", "title")),
    ("CareerGoals_ownerId_status_updatedAt_idx", "CareerGoals", ("ownerId", "status", "updatedAt")),
    ("CareerRoadmaps_ownerId_updatedAt_idx", "CareerRoadmaps", ("ownerId", "updatedAt")),
    ("CareerRoadmaps_goalId_sortOrder_idx", "CareerRoadmaps", ("goalId", "sortOrder")),
    ("CareerRoadmaps_goalId_status_idx", "CareerRoadmaps", ("goalId", "status")),
    ("CareerMilestones_ownerId_updatedAt_idx", "CareerMilestones", ("ownerId", "updatedAt")),
    ("CareerMilestones_roadmapId_sortOrder_idx", "CareerMilestones", ("roadmapId", "sortOrder")),
    ("CareerMilestones_roadmapId_status_idx", "CareerMilestones", ("roadmapId", "status")),
    ("CareerReviewHistory_ownerId_createdAt_idx", "CareerReviewHistory", ("ownerId", "createdAt")),
    ("CareerReviewHistory_goalId_createdAt_idx", "CareerReviewHistory", ("goalId", "createdAt")),
)


def _table_names() -> set[str]:
    return set(sa.inspect(op.get_bind()).get_table_names())


def _index_names(table_name: str) -> set[str]:
    return {index["name"] for index in sa.inspect(op.get_bind()).get_indexes(table_name)}


def _create_index(name: str, table_name: str, columns: tuple[str, ...]) -> None:
    if table_name not in _table_names() or name in _index_names(table_name):
        return
    op.create_index(name, table_name, list(columns), unique=False)


def _drop_index(name: str, table_name: str) -> None:
    if table_name not in _table_names() or name not in _index_names(table_name):
        return
    op.drop_index(name, table_name=table_name)


def upgrade() -> None:
    table_names = _table_names()

    if "CareerGoals" not in table_names:
        op.create_table(
            "CareerGoals",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("targetRole", sa.String(length=180), nullable=True),
            sa.Column("timeHorizon", sa.String(length=80), server_default="12 months", nullable=False),
            sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_CareerGoals_ownerId", "CareerGoals", ["ownerId"])

    table_names = _table_names()
    if "CareerRoadmaps" not in table_names:
        op.create_table(
            "CareerRoadmaps",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("goalId", sa.Integer(), nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("focusArea", sa.String(length=120), server_default="skills", nullable=False),
            sa.Column("status", sa.String(length=40), server_default="planned", nullable=False),
            sa.Column("summary", sa.Text(), nullable=True),
            sa.Column("sortOrder", sa.Integer(), server_default="0", nullable=False),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["goalId"], ["CareerGoals.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_CareerRoadmaps_ownerId", "CareerRoadmaps", ["ownerId"])
        op.create_index("ix_CareerRoadmaps_goalId", "CareerRoadmaps", ["goalId"])

    table_names = _table_names()
    if "CareerMilestones" not in table_names:
        op.create_table(
            "CareerMilestones",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("roadmapId", sa.Integer(), nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("dueDate", sa.String(length=40), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="todo", nullable=False),
            sa.Column("successMetric", sa.String(length=240), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("sortOrder", sa.Integer(), server_default="0", nullable=False),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["roadmapId"], ["CareerRoadmaps.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_CareerMilestones_ownerId", "CareerMilestones", ["ownerId"])
        op.create_index("ix_CareerMilestones_roadmapId", "CareerMilestones", ["roadmapId"])

    table_names = _table_names()
    if "CareerReviewHistory" not in table_names:
        op.create_table(
            "CareerReviewHistory",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("goalId", sa.Integer(), nullable=True),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("actionType", sa.String(length=60), server_default="reviewed", nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["goalId"], ["CareerGoals.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_CareerReviewHistory_ownerId", "CareerReviewHistory", ["ownerId"])
        op.create_index("ix_CareerReviewHistory_goalId", "CareerReviewHistory", ["goalId"])

    for name, table_name, columns in INDEXES:
        _create_index(name, table_name, columns)


def downgrade() -> None:
    for name, table_name, _columns in reversed(INDEXES):
        _drop_index(name, table_name)

    table_names = _table_names()
    if "CareerReviewHistory" in table_names:
        op.drop_index("ix_CareerReviewHistory_goalId", table_name="CareerReviewHistory")
        op.drop_index("ix_CareerReviewHistory_ownerId", table_name="CareerReviewHistory")
        op.drop_table("CareerReviewHistory")

    table_names = _table_names()
    if "CareerMilestones" in table_names:
        op.drop_index("ix_CareerMilestones_roadmapId", table_name="CareerMilestones")
        op.drop_index("ix_CareerMilestones_ownerId", table_name="CareerMilestones")
        op.drop_table("CareerMilestones")

    table_names = _table_names()
    if "CareerRoadmaps" in table_names:
        op.drop_index("ix_CareerRoadmaps_goalId", table_name="CareerRoadmaps")
        op.drop_index("ix_CareerRoadmaps_ownerId", table_name="CareerRoadmaps")
        op.drop_table("CareerRoadmaps")

    table_names = _table_names()
    if "CareerGoals" in table_names:
        op.drop_index("ix_CareerGoals_ownerId", table_name="CareerGoals")
        op.drop_table("CareerGoals")
