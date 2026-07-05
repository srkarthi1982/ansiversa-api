"""add goal tracker tables

Revision ID: 20260705_0001_goal_tracker
Revises:
Create Date: 2026-07-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260705_0001_goal_tracker"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


INDEXES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("GoalTrackerGoals_userId_status_updatedAt_idx", "GoalTrackerGoals", ("userId", "status", "updatedAt")),
    ("GoalTrackerGoals_userId_priority_status_idx", "GoalTrackerGoals", ("userId", "priority", "status")),
    ("GoalTrackerGoals_userId_category_status_idx", "GoalTrackerGoals", ("userId", "category", "status")),
    ("GoalTrackerGoals_userId_targetDate_idx", "GoalTrackerGoals", ("userId", "targetDate")),
    ("GoalTrackerMilestones_userId_goalId_sortOrder_idx", "GoalTrackerMilestones", ("userId", "goalId", "sortOrder")),
    ("GoalTrackerMilestones_userId_status_updatedAt_idx", "GoalTrackerMilestones", ("userId", "status", "updatedAt")),
    ("GoalTrackerCheckIns_userId_goalId_checkInDate_idx", "GoalTrackerCheckIns", ("userId", "goalId", "checkInDate")),
    ("GoalTrackerCheckIns_userId_checkInDate_idx", "GoalTrackerCheckIns", ("userId", "checkInDate")),
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
    if "GoalTrackerGoals" not in table_names:
        op.create_table(
            "GoalTrackerGoals",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("category", sa.String(length=80), nullable=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("targetDate", sa.String(length=40), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
            sa.Column("priority", sa.String(length=40), server_default="medium", nullable=False),
            sa.Column("progressPercent", sa.Integer(), server_default="0", nullable=False),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_GoalTrackerGoals_userId", "GoalTrackerGoals", ["userId"])

    table_names = _table_names()
    if "GoalTrackerMilestones" not in table_names:
        op.create_table(
            "GoalTrackerMilestones",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("goalId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("targetDate", sa.String(length=40), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="pending", nullable=False),
            sa.Column("sortOrder", sa.Integer(), server_default="0", nullable=False),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["goalId"], ["GoalTrackerGoals.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_GoalTrackerMilestones_userId", "GoalTrackerMilestones", ["userId"])
        op.create_index("ix_GoalTrackerMilestones_goalId", "GoalTrackerMilestones", ["goalId"])

    table_names = _table_names()
    if "GoalTrackerCheckIns" not in table_names:
        op.create_table(
            "GoalTrackerCheckIns",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("goalId", sa.String(length=36), nullable=False),
            sa.Column("checkInDate", sa.String(length=40), nullable=False),
            sa.Column("progressPercent", sa.Integer(), nullable=False),
            sa.Column("note", sa.Text(), nullable=True),
            sa.Column("mood", sa.String(length=40), server_default="steady", nullable=False),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["goalId"], ["GoalTrackerGoals.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_GoalTrackerCheckIns_userId", "GoalTrackerCheckIns", ["userId"])
        op.create_index("ix_GoalTrackerCheckIns_goalId", "GoalTrackerCheckIns", ["goalId"])

    for name, table_name, columns in INDEXES:
        _create_index(name, table_name, columns)


def downgrade() -> None:
    for name, table_name, _columns in reversed(INDEXES):
        _drop_index(name, table_name)

    table_names = _table_names()
    if "GoalTrackerCheckIns" in table_names:
        op.drop_index("ix_GoalTrackerCheckIns_goalId", table_name="GoalTrackerCheckIns")
        op.drop_index("ix_GoalTrackerCheckIns_userId", table_name="GoalTrackerCheckIns")
        op.drop_table("GoalTrackerCheckIns")
    table_names = _table_names()
    if "GoalTrackerMilestones" in table_names:
        op.drop_index("ix_GoalTrackerMilestones_goalId", table_name="GoalTrackerMilestones")
        op.drop_index("ix_GoalTrackerMilestones_userId", table_name="GoalTrackerMilestones")
        op.drop_table("GoalTrackerMilestones")
    table_names = _table_names()
    if "GoalTrackerGoals" in table_names:
        op.drop_index("ix_GoalTrackerGoals_userId", table_name="GoalTrackerGoals")
        op.drop_table("GoalTrackerGoals")
