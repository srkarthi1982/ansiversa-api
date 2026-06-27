"""add_parent_high_priority_indexes

Revision ID: 20260628_0001
Revises: 20260621_0003
Create Date: 2026-06-28

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260628_0001"
down_revision: str | None = "20260621_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


INDEXES: tuple[tuple[str, str, tuple[str, ...], bool], ...] = (
    ("Apps_status_featured_name_idx", "Apps", ("status", "isFeatured", "name"), False),
    ("Apps_launchStatus_status_idx", "Apps", ("launchStatus", "status"), False),
    ("Favorites_userId_appId_idx", "Favorites", ("userId", "appId"), False),
    ("Favorites_userId_createdAt_idx", "Favorites", ("userId", "createdAt"), False),
    ("Notifications_userId_createdAt_idx", "Notifications", ("userId", "createdAt"), False),
    (
        "Notifications_userId_isRead_createdAt_idx",
        "Notifications",
        ("userId", "isRead", "createdAt"),
        False,
    ),
)


def _table_names() -> set[str]:
    return set(sa.inspect(op.get_bind()).get_table_names())


def _index_names(table_name: str) -> set[str]:
    return {index["name"] for index in sa.inspect(op.get_bind()).get_indexes(table_name)}


def _create_index(name: str, table_name: str, columns: tuple[str, ...], unique: bool) -> None:
    if table_name not in _table_names() or name in _index_names(table_name):
        return

    op.create_index(name, table_name, list(columns), unique=unique)


def _drop_index(name: str, table_name: str) -> None:
    if table_name not in _table_names() or name not in _index_names(table_name):
        return

    op.drop_index(name, table_name=table_name)


def upgrade() -> None:
    for name, table_name, columns, unique in INDEXES:
        _create_index(name, table_name, columns, unique)


def downgrade() -> None:
    for name, table_name, _columns, _unique in reversed(INDEXES):
        _drop_index(name, table_name)
