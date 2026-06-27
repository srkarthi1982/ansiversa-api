"""add_resume_builder_indexes

Revision ID: 20260628_0001
Revises:
Create Date: 2026-06-28

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260628_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


INDEXES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("ResumeProject_userId_updatedAt_title_idx", "ResumeProject", ("userId", "updatedAt", "title")),
    ("ResumeProject_userId_isDefault_updatedAt_idx", "ResumeProject", ("userId", "isDefault", "updatedAt")),
    ("ResumeSection_projectId_order_createdAt_idx", "ResumeSection", ("projectId", "order", "createdAt")),
    ("ResumeSection_projectId_isEnabled_order_idx", "ResumeSection", ("projectId", "isEnabled", "order")),
    ("ResumeItem_sectionId_order_createdAt_idx", "ResumeItem", ("sectionId", "order", "createdAt")),
    ("ResumeItem_sectionId_updatedAt_idx", "ResumeItem", ("sectionId", "updatedAt")),
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
    for name, table_name, columns in INDEXES:
        _create_index(name, table_name, columns)


def downgrade() -> None:
    for name, table_name, _columns in reversed(INDEXES):
        _drop_index(name, table_name)
