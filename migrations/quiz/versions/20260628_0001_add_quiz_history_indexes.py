"""add_quiz_history_indexes

Revision ID: 20260628_0001
Revises: 20260622_0002
Create Date: 2026-06-28

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260628_0001"
down_revision: str | None = "20260622_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


INDEXES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("QuizAttempt_userId_createdAt_idx", "QuizAttempt", ("userId", "createdAt")),
    ("QuizAttempt_userId_status_expiresAt_idx", "QuizAttempt", ("userId", "status", "expiresAt")),
    ("QuizAttempt_resultId_idx", "QuizAttempt", ("resultId",)),
    ("Result_userId_createdAt_idx", "Result", ("userId", "createdAt")),
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
