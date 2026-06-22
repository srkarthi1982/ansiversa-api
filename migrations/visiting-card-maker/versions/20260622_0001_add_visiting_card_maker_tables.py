"""add_visiting_card_maker_tables

Revision ID: 20260622_0001
Revises:
Create Date: 2026-06-22

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260622_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())

    if "CardProfiles" not in table_names:
        op.create_table(
            "CardProfiles",
            sa.Column("id", sa.Text(), nullable=False),
            sa.Column("userId", sa.Text(), nullable=False),
            sa.Column("fullName", sa.String(length=120), nullable=False),
            sa.Column("jobTitle", sa.String(length=120), server_default="", nullable=False),
            sa.Column("companyName", sa.String(length=140), server_default="", nullable=False),
            sa.Column("phoneNumber", sa.String(length=60), server_default="", nullable=False),
            sa.Column("email", sa.String(length=180), server_default="", nullable=False),
            sa.Column("website", sa.String(length=180), server_default="", nullable=False),
            sa.Column("address", sa.Text(), server_default="", nullable=False),
            sa.Column("tagline", sa.String(length=180), server_default="", nullable=False),
            sa.Column(
                "createdAt",
                sa.Text(),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.Column(
                "updatedAt",
                sa.Text(),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_CardProfiles_userId", "CardProfiles", ["userId"])

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "CardDesigns" not in table_names:
        op.create_table(
            "CardDesigns",
            sa.Column("id", sa.Text(), nullable=False),
            sa.Column("userId", sa.Text(), nullable=False),
            sa.Column("profileId", sa.Text(), nullable=False),
            sa.Column(
                "templateKey",
                sa.String(length=40),
                server_default="professional",
                nullable=False,
            ),
            sa.Column(
                "createdAt",
                sa.Text(),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.Column(
                "updatedAt",
                sa.Text(),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["profileId"], ["CardProfiles.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_CardDesigns_profileId", "CardDesigns", ["profileId"])
        op.create_index("ix_CardDesigns_userId", "CardDesigns", ["userId"])


def downgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())

    if "CardDesigns" in table_names:
        op.drop_index("ix_CardDesigns_userId", table_name="CardDesigns")
        op.drop_index("ix_CardDesigns_profileId", table_name="CardDesigns")
        op.drop_table("CardDesigns")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "CardProfiles" in table_names:
        op.drop_index("ix_CardProfiles_userId", table_name="CardProfiles")
        op.drop_table("CardProfiles")
