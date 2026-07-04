"""add project tracker tables

Revision ID: 20260704_0001
Revises:
Create Date: 2026-07-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260704_0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


INDEXES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("ProjectTrackerProjects_ownerId_updatedAt_title_idx", "ProjectTrackerProjects", ("ownerId", "updatedAt", "title")),
    ("ProjectTrackerProjects_ownerId_status_priority_idx", "ProjectTrackerProjects", ("ownerId", "status", "priority")),
    ("ProjectTrackerProjects_ownerId_dueDate_idx", "ProjectTrackerProjects", ("ownerId", "dueDate")),
    ("ProjectTrackerTasks_ownerId_projectId_updatedAt_idx", "ProjectTrackerTasks", ("ownerId", "projectId", "updatedAt")),
    ("ProjectTrackerTasks_ownerId_status_dueDate_idx", "ProjectTrackerTasks", ("ownerId", "status", "dueDate")),
    ("ProjectTrackerTasks_projectId_status_idx", "ProjectTrackerTasks", ("projectId", "status")),
    ("ProjectTrackerTasks_ownerId_priority_dueDate_idx", "ProjectTrackerTasks", ("ownerId", "priority", "dueDate")),
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
    if "ProjectTrackerProjects" not in table_names:
        op.create_table(
            "ProjectTrackerProjects",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("ownerName", sa.String(length=120), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="planning", nullable=False),
            sa.Column("priority", sa.String(length=40), server_default="medium", nullable=False),
            sa.Column("dueDate", sa.String(length=40), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_ProjectTrackerProjects_ownerId", "ProjectTrackerProjects", ["ownerId"])

    table_names = _table_names()
    if "ProjectTrackerTasks" not in table_names:
        op.create_table(
            "ProjectTrackerTasks",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("projectId", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("status", sa.String(length=40), server_default="todo", nullable=False),
            sa.Column("priority", sa.String(length=40), server_default="medium", nullable=False),
            sa.Column("dueDate", sa.String(length=40), nullable=True),
            sa.Column("estimateHours", sa.Float(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["projectId"], ["ProjectTrackerProjects.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_ProjectTrackerTasks_ownerId", "ProjectTrackerTasks", ["ownerId"])
        op.create_index("ix_ProjectTrackerTasks_projectId", "ProjectTrackerTasks", ["projectId"])

    for name, table_name, columns in INDEXES:
        _create_index(name, table_name, columns)


def downgrade() -> None:
    for name, table_name, _columns in reversed(INDEXES):
        _drop_index(name, table_name)

    table_names = _table_names()
    if "ProjectTrackerTasks" in table_names:
        op.drop_index("ix_ProjectTrackerTasks_projectId", table_name="ProjectTrackerTasks")
        op.drop_index("ix_ProjectTrackerTasks_ownerId", table_name="ProjectTrackerTasks")
        op.drop_table("ProjectTrackerTasks")
    table_names = _table_names()
    if "ProjectTrackerProjects" in table_names:
        op.drop_index("ix_ProjectTrackerProjects_ownerId", table_name="ProjectTrackerProjects")
        op.drop_table("ProjectTrackerProjects")
