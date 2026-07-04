"""add task prioritizer tables

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
    ("TaskPrioritizerTasks_ownerId_updatedAt_title_idx", "TaskPrioritizerTasks", ("ownerId", "updatedAt", "title")),
    ("TaskPrioritizerTasks_ownerId_status_category_idx", "TaskPrioritizerTasks", ("ownerId", "status", "category")),
    ("TaskPrioritizerTasks_ownerId_priorityScore_idx", "TaskPrioritizerTasks", ("ownerId", "priorityScore")),
    ("TaskPrioritizerTasks_ownerId_priorityLabel_dueDate_idx", "TaskPrioritizerTasks", ("ownerId", "priorityLabel", "dueDate")),
    ("TaskPrioritizerTasks_ownerId_dueDate_status_idx", "TaskPrioritizerTasks", ("ownerId", "dueDate", "status")),
    ("TaskPrioritizerTaskPriorities_ownerId_taskId_createdAt_idx", "TaskPrioritizerTaskPriorities", ("ownerId", "taskId", "createdAt")),
    ("TaskPrioritizerPriorityRules_ownerId_enabled_category_idx", "TaskPrioritizerPriorityRules", ("ownerId", "isEnabled", "category")),
    ("TaskPrioritizerPriorityHistory_ownerId_createdAt_idx", "TaskPrioritizerPriorityHistory", ("ownerId", "createdAt")),
    ("TaskPrioritizerPriorityHistory_ownerId_taskId_createdAt_idx", "TaskPrioritizerPriorityHistory", ("ownerId", "taskId", "createdAt")),
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
    if "TaskPrioritizerTasks" not in table_names:
        op.create_table(
            "TaskPrioritizerTasks",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("category", sa.String(length=40), server_default="work", nullable=False),
            sa.Column("status", sa.String(length=40), server_default="inbox", nullable=False),
            sa.Column("dueDate", sa.String(length=40), nullable=True),
            sa.Column("effort", sa.Integer(), server_default="3", nullable=False),
            sa.Column("impact", sa.Integer(), server_default="3", nullable=False),
            sa.Column("urgency", sa.Integer(), server_default="3", nullable=False),
            sa.Column("priorityScore", sa.Float(), server_default="0", nullable=False),
            sa.Column("priorityLabel", sa.String(length=40), server_default="medium", nullable=False),
            sa.Column("manualOverride", sa.Boolean(), server_default="0", nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_TaskPrioritizerTasks_ownerId", "TaskPrioritizerTasks", ["ownerId"])

    table_names = _table_names()
    if "TaskPrioritizerTaskPriorities" not in table_names:
        op.create_table(
            "TaskPrioritizerTaskPriorities",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("taskId", sa.Integer(), nullable=False),
            sa.Column("priorityScore", sa.Float(), nullable=False),
            sa.Column("priorityLabel", sa.String(length=40), nullable=False),
            sa.Column("source", sa.String(length=40), server_default="system", nullable=False),
            sa.Column("reason", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["taskId"], ["TaskPrioritizerTasks.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_TaskPrioritizerTaskPriorities_ownerId", "TaskPrioritizerTaskPriorities", ["ownerId"])
        op.create_index("ix_TaskPrioritizerTaskPriorities_taskId", "TaskPrioritizerTaskPriorities", ["taskId"])

    table_names = _table_names()
    if "TaskPrioritizerPriorityRules" not in table_names:
        op.create_table(
            "TaskPrioritizerPriorityRules",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=160), nullable=False),
            sa.Column("category", sa.String(length=40), nullable=True),
            sa.Column("impactWeight", sa.Float(), server_default="2", nullable=False),
            sa.Column("urgencyWeight", sa.Float(), server_default="2", nullable=False),
            sa.Column("effortWeight", sa.Float(), server_default="1", nullable=False),
            sa.Column("dueDateWeight", sa.Float(), server_default="2", nullable=False),
            sa.Column("isEnabled", sa.Boolean(), server_default="1", nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_TaskPrioritizerPriorityRules_ownerId", "TaskPrioritizerPriorityRules", ["ownerId"])

    table_names = _table_names()
    if "TaskPrioritizerPriorityHistory" not in table_names:
        op.create_table(
            "TaskPrioritizerPriorityHistory",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("taskId", sa.Integer(), nullable=True),
            sa.Column("actionType", sa.String(length=40), nullable=False),
            sa.Column("previousPriority", sa.String(length=40), nullable=True),
            sa.Column("newPriority", sa.String(length=40), nullable=True),
            sa.Column("priorityScore", sa.Float(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["taskId"], ["TaskPrioritizerTasks.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_TaskPrioritizerPriorityHistory_ownerId", "TaskPrioritizerPriorityHistory", ["ownerId"])
        op.create_index("ix_TaskPrioritizerPriorityHistory_taskId", "TaskPrioritizerPriorityHistory", ["taskId"])

    for name, table_name, columns in INDEXES:
        _create_index(name, table_name, columns)


def downgrade() -> None:
    for name, table_name, _columns in reversed(INDEXES):
        _drop_index(name, table_name)

    table_names = _table_names()
    if "TaskPrioritizerPriorityHistory" in table_names:
        op.drop_index("ix_TaskPrioritizerPriorityHistory_taskId", table_name="TaskPrioritizerPriorityHistory")
        op.drop_index("ix_TaskPrioritizerPriorityHistory_ownerId", table_name="TaskPrioritizerPriorityHistory")
        op.drop_table("TaskPrioritizerPriorityHistory")
    table_names = _table_names()
    if "TaskPrioritizerPriorityRules" in table_names:
        op.drop_index("ix_TaskPrioritizerPriorityRules_ownerId", table_name="TaskPrioritizerPriorityRules")
        op.drop_table("TaskPrioritizerPriorityRules")
    table_names = _table_names()
    if "TaskPrioritizerTaskPriorities" in table_names:
        op.drop_index("ix_TaskPrioritizerTaskPriorities_taskId", table_name="TaskPrioritizerTaskPriorities")
        op.drop_index("ix_TaskPrioritizerTaskPriorities_ownerId", table_name="TaskPrioritizerTaskPriorities")
        op.drop_table("TaskPrioritizerTaskPriorities")
    table_names = _table_names()
    if "TaskPrioritizerTasks" in table_names:
        op.drop_index("ix_TaskPrioritizerTasks_ownerId", table_name="TaskPrioritizerTasks")
        op.drop_table("TaskPrioritizerTasks")
