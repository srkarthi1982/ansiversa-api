"""align_existing_visiting_card_maker_tables

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


def _columns(table_name: str) -> set[str]:
    return {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table_name)}


def upgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "CardProfiles" not in table_names:
        return

    columns = _columns("CardProfiles")
    if "profileName" not in columns:
        op.add_column(
            "CardProfiles",
            sa.Column("profileName", sa.String(length=120), server_default="", nullable=False),
        )
        op.execute(
            sa.text('UPDATE "CardProfiles" SET "profileName" = COALESCE("fullName", "")')
        )

    columns = _columns("CardProfiles")
    if "phoneNumber" not in columns:
        op.add_column(
            "CardProfiles",
            sa.Column("phoneNumber", sa.String(length=60), server_default="", nullable=False),
        )
        if "phone" in columns:
            op.execute(
                sa.text('UPDATE "CardProfiles" SET "phoneNumber" = COALESCE("phone", "")')
            )

    columns = _columns("CardProfiles")
    if "address" not in columns:
        op.add_column(
            "CardProfiles",
            sa.Column("address", sa.Text(), server_default="", nullable=False),
        )
        if "addressLine1" in columns:
            op.execute(
                sa.text('UPDATE "CardProfiles" SET "address" = COALESCE("addressLine1", "")')
            )

    columns = _columns("CardProfiles")
    if "tagline" not in columns:
        op.add_column(
            "CardProfiles",
            sa.Column("tagline", sa.String(length=180), server_default="", nullable=False),
        )
        if "notes" in columns:
            op.execute(
                sa.text('UPDATE "CardProfiles" SET "tagline" = COALESCE("notes", "")')
            )


def downgrade() -> None:
    # SQLite/libSQL cannot safely drop columns without rebuilding the table.
    pass
