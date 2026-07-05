"""add wellness and goal planner tables

Revision ID: 20260705_0001_wellness_goal
Revises:
Create Date: 2026-07-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260705_0001_wellness_goal"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


INDEXES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("WellnessAreas_ownerId_name_idx", "WellnessAreas", ("ownerId", "name")),
    ("WellnessAreas_ownerId_updatedAt_idx", "WellnessAreas", ("ownerId", "updatedAt")),
    ("WellnessGoals_ownerId_status_updatedAt_idx", "WellnessGoals", ("ownerId", "status", "updatedAt")),
    ("WellnessGoals_ownerId_areaId_status_idx", "WellnessGoals", ("ownerId", "areaId", "status")),
    ("WellnessGoals_ownerId_targetDate_idx", "WellnessGoals", ("ownerId", "targetDate")),
    ("WellnessGoals_ownerId_updatedAt_title_idx", "WellnessGoals", ("ownerId", "updatedAt", "title")),
    ("WellnessReflections_ownerId_reflectionDate_idx", "WellnessReflections", ("ownerId", "reflectionDate")),
    ("WellnessReflections_ownerId_goalId_reflectionDate_idx", "WellnessReflections", ("ownerId", "goalId", "reflectionDate")),
    ("WellnessReflections_ownerId_updatedAt_idx", "WellnessReflections", ("ownerId", "updatedAt")),
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
    if "WellnessAreas" not in table_names:
        op.create_table(
            "WellnessAreas",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("name", sa.String(length=120), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("color", sa.String(length=40), server_default="#2f6f73", nullable=False),
            sa.Column("icon", sa.String(length=60), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_WellnessAreas_ownerId", "WellnessAreas", ["ownerId"])

    table_names = _table_names()
    if "WellnessGoals" not in table_names:
        op.create_table(
            "WellnessGoals",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("areaId", sa.Integer(), nullable=True),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("targetDate", sa.String(length=40), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
            sa.Column("priority", sa.String(length=40), server_default="medium", nullable=False),
            sa.Column("progress", sa.Integer(), server_default="0", nullable=False),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["areaId"], ["WellnessAreas.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_WellnessGoals_ownerId", "WellnessGoals", ["ownerId"])
        op.create_index("ix_WellnessGoals_areaId", "WellnessGoals", ["areaId"])

    table_names = _table_names()
    if "WellnessReflections" not in table_names:
        op.create_table(
            "WellnessReflections",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("goalId", sa.Integer(), nullable=True),
            sa.Column("reflectionDate", sa.String(length=40), nullable=False),
            sa.Column("reflection", sa.Text(), nullable=False),
            sa.Column("mood", sa.String(length=40), server_default="steady", nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["goalId"], ["WellnessGoals.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_WellnessReflections_ownerId", "WellnessReflections", ["ownerId"])
        op.create_index("ix_WellnessReflections_goalId", "WellnessReflections", ["goalId"])

    for name, table_name, columns in INDEXES:
        _create_index(name, table_name, columns)


def downgrade() -> None:
    for name, table_name, _columns in reversed(INDEXES):
        _drop_index(name, table_name)

    table_names = _table_names()
    if "WellnessReflections" in table_names:
        op.drop_index("ix_WellnessReflections_goalId", table_name="WellnessReflections")
        op.drop_index("ix_WellnessReflections_ownerId", table_name="WellnessReflections")
        op.drop_table("WellnessReflections")
    table_names = _table_names()
    if "WellnessGoals" in table_names:
        op.drop_index("ix_WellnessGoals_areaId", table_name="WellnessGoals")
        op.drop_index("ix_WellnessGoals_ownerId", table_name="WellnessGoals")
        op.drop_table("WellnessGoals")
    table_names = _table_names()
    if "WellnessAreas" in table_names:
        op.drop_index("ix_WellnessAreas_ownerId", table_name="WellnessAreas")
        op.drop_table("WellnessAreas")
