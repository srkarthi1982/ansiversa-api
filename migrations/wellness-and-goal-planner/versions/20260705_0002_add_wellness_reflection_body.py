"""add wellness reflection body

Revision ID: 20260705_0002_wellness_reflection_body
Revises: 20260705_0001_wellness_goal
Create Date: 2026-07-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260705_0002_wellness_reflection_body"
down_revision: str | Sequence[str] | None = "20260705_0001_wellness_goal"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _table_names() -> set[str]:
    return set(sa.inspect(op.get_bind()).get_table_names())


def _columns(table_name: str) -> set[str]:
    if table_name not in _table_names():
        return set()
    return {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table_name)}


def upgrade() -> None:
    columns = _columns("WellnessReflections")
    if "reflection" not in columns:
        op.add_column("WellnessReflections", sa.Column("reflection", sa.Text(), nullable=True))
        op.execute(
            """
            UPDATE WellnessReflections
            SET reflection = notes
            WHERE reflection IS NULL
              AND notes IS NOT NULL
            """
        )
        op.execute(
            """
            UPDATE WellnessReflections
            SET notes = NULL
            WHERE notes = reflection
            """
        )


def downgrade() -> None:
    pass
