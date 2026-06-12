"""add_contact_messages_table

Revision ID: 20260612_0001
Revises: 9e3789be923b
Create Date: 2026-06-12 00:00:00

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260612_0001"
down_revision: str | None = "9e3789be923b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "ContactMessages" in table_names:
        return

    op.create_table(
        "ContactMessages",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("subject", sa.String(length=200), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column(
            "createdAt",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "ContactMessages" in table_names:
        op.drop_table("ContactMessages")
