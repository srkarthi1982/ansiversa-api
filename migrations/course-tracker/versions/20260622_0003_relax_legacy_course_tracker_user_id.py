"""relax_legacy_course_tracker_user_id

Revision ID: 20260622_0003
Revises: 20260622_0002
Create Date: 2026-06-22

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260622_0003"
down_revision: str | None = "20260622_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _columns() -> dict[str, dict[str, object]]:
    inspector = sa.inspect(op.get_bind())
    return {column["name"]: column for column in inspector.get_columns("Courses")}


def upgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "Courses" not in table_names:
        return

    columns = _columns()
    user_id_column = columns.get("userId")
    if user_id_column and not user_id_column["nullable"]:
        with op.batch_alter_table("Courses") as batch_op:
            batch_op.alter_column(
                "userId",
                existing_type=sa.String(length=36),
                nullable=True,
            )


def downgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "Courses" not in table_names:
        return

    columns = _columns()
    if "userId" in columns:
        with op.batch_alter_table("Courses") as batch_op:
            batch_op.alter_column(
                "userId",
                existing_type=sa.String(length=36),
                nullable=False,
            )
