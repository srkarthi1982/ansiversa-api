"""add family task planner tables

Revision ID: 20260711_0001_family_task_planner
Revises:
Create Date: 2026-07-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260711_0001_family_task_planner"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


INDEXES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("FamilyTaskMembers_userId_status_name_idx", "FamilyTaskMembers", ("userId", "status", "name")),
    ("FamilyTaskCategories_userId_status_name_idx", "FamilyTaskCategories", ("userId", "status", "name")),
    ("FamilyTasks_userId_dueDate_idx", "FamilyTasks", ("userId", "dueDate")),
    ("FamilyTasks_userId_status_dueDate_idx", "FamilyTasks", ("userId", "status", "dueDate")),
    ("FamilyTasks_userId_memberId_dueDate_idx", "FamilyTasks", ("userId", "memberId", "dueDate")),
    ("FamilyTasks_userId_categoryId_dueDate_idx", "FamilyTasks", ("userId", "categoryId", "dueDate")),
    ("FamilyTasks_userId_completedAt_idx", "FamilyTasks", ("userId", "completedAt")),
    ("FamilyTasks_userId_updatedAt_idx", "FamilyTasks", ("userId", "updatedAt")),
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
    if "FamilyTaskMembers" not in table_names:
        op.create_table(
            "FamilyTaskMembers",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("name", sa.String(length=140), nullable=False),
            sa.Column("color", sa.String(length=40), nullable=True),
            sa.Column("avatar", sa.String(length=80), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_FamilyTaskMembers_userId", "FamilyTaskMembers", ["userId"])

    table_names = _table_names()
    if "FamilyTaskCategories" not in table_names:
        op.create_table(
            "FamilyTaskCategories",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("name", sa.String(length=140), nullable=False),
            sa.Column("color", sa.String(length=40), nullable=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_FamilyTaskCategories_userId", "FamilyTaskCategories", ["userId"])

    table_names = _table_names()
    if "FamilyTasks" not in table_names:
        op.create_table(
            "FamilyTasks",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("memberId", sa.String(length=36), nullable=True),
            sa.Column("categoryId", sa.String(length=36), nullable=True),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("priority", sa.String(length=40), server_default="medium", nullable=False),
            sa.Column("dueDate", sa.String(length=40), nullable=True),
            sa.Column("recurring", sa.String(length=40), server_default="none", nullable=False),
            sa.Column("status", sa.String(length=40), server_default="pending", nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("completedAt", sa.String(length=40), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["memberId"], ["FamilyTaskMembers.id"]),
            sa.ForeignKeyConstraint(["categoryId"], ["FamilyTaskCategories.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_FamilyTasks_userId", "FamilyTasks", ["userId"])
        op.create_index("ix_FamilyTasks_memberId", "FamilyTasks", ["memberId"])
        op.create_index("ix_FamilyTasks_categoryId", "FamilyTasks", ["categoryId"])

    for name, table_name, columns in INDEXES:
        _create_index(name, table_name, columns)


def downgrade() -> None:
    for name, table_name, _columns in reversed(INDEXES):
        _drop_index(name, table_name)

    table_names = _table_names()
    if "FamilyTasks" in table_names:
        op.drop_index("ix_FamilyTasks_categoryId", table_name="FamilyTasks")
        op.drop_index("ix_FamilyTasks_memberId", table_name="FamilyTasks")
        op.drop_index("ix_FamilyTasks_userId", table_name="FamilyTasks")
        op.drop_table("FamilyTasks")
    table_names = _table_names()
    if "FamilyTaskCategories" in table_names:
        op.drop_index("ix_FamilyTaskCategories_userId", table_name="FamilyTaskCategories")
        op.drop_table("FamilyTaskCategories")
    table_names = _table_names()
    if "FamilyTaskMembers" in table_names:
        op.drop_index("ix_FamilyTaskMembers_userId", table_name="FamilyTaskMembers")
        op.drop_table("FamilyTaskMembers")
