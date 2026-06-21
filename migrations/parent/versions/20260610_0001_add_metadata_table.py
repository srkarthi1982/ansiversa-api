"""add_metadata_table

Revision ID: 20260610_0001
Revises: 29cde1832712
Create Date: 2026-06-10 00:00:00

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260610_0001"
down_revision: str | None = "29cde1832712"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    table_names = set(sa.inspect(bind).get_table_names())
    if "metadata" in table_names:
        return

    op.create_table(
        "Metadata",
        sa.Column("key", sa.String(length=255), nullable=False),
        sa.Column("content", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("key"),
    )


def downgrade() -> None:
    bind = op.get_bind()
    table_names = set(sa.inspect(bind).get_table_names())
    if "Metadata" not in table_names:
        return

    op.drop_table("Metadata")
