"""add_favorites_table

Revision ID: f133792b51cc
Revises: 8e82dd41d8b5
Create Date: 2026-05-29 09:55:29.856611

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "f133792b51cc"
down_revision: str | None = "8e82dd41d8b5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "Favorites" in table_names:
        return

    op.create_table(
        "Favorites",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("userId", sa.String(length=36), nullable=False),
        sa.Column("appId", sa.String(length=36), nullable=False),
        sa.Column(
            "createdAt",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["appId"], ["Apps.id"]),
        sa.ForeignKeyConstraint(["userId"], ["Users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "Favorites_appId_userId_idx",
        "Favorites",
        ["appId", "userId"],
        unique=True,
    )


def downgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "Favorites" not in table_names:
        return

    op.drop_index("Favorites_appId_userId_idx", table_name="Favorites")
    op.drop_table("Favorites")
