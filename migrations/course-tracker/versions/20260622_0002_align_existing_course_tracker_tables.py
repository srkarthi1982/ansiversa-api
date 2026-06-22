"""align_existing_course_tracker_tables

Revision ID: 20260622_0002
Revises: 20260622_0001
Create Date: 2026-06-22

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260622_0002"
down_revision: str | None = "20260622_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _column_names(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {column["name"] for column in inspector.get_columns(table_name)}


def _index_names(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {index["name"] for index in inspector.get_indexes(table_name)}


def upgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "Courses" not in table_names:
        return

    columns = _column_names("Courses")
    with op.batch_alter_table("Courses") as batch_op:
        if "ownerId" not in columns:
            batch_op.add_column(
                sa.Column(
                    "ownerId",
                    sa.String(length=36),
                    server_default="legacy",
                    nullable=False,
                )
            )
        if "category" not in columns:
            batch_op.add_column(sa.Column("category", sa.String(length=120), nullable=True))
        if "goal" not in columns:
            batch_op.add_column(
                sa.Column("goal", sa.Text(), server_default="", nullable=False)
            )
        if "startDate" not in columns:
            batch_op.add_column(sa.Column("startDate", sa.Date(), nullable=True))
        if "targetDate" not in columns:
            batch_op.add_column(sa.Column("targetDate", sa.Date(), nullable=True))

    indexes = _index_names("Courses")
    if "ix_Courses_ownerId" not in indexes:
        op.create_index("ix_Courses_ownerId", "Courses", ["ownerId"])


def downgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "Courses" not in table_names:
        return

    indexes = _index_names("Courses")
    if "ix_Courses_ownerId" in indexes:
        op.drop_index("ix_Courses_ownerId", table_name="Courses")

    columns = _column_names("Courses")
    with op.batch_alter_table("Courses") as batch_op:
        for column_name in ("targetDate", "startDate", "goal", "category", "ownerId"):
            if column_name in columns:
                batch_op.drop_column(column_name)
