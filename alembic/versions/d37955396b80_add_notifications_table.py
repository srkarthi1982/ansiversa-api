"""add_notifications_table

Revision ID: d37955396b80
Revises: f133792b51cc
Create Date: 2026-05-29 10:07:46.247425

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "d37955396b80"
down_revision: str | None = "f133792b51cc"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "Notifications" in table_names:
        return

    op.create_table(
        "Notifications",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("userId", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("type", sa.String(length=120), nullable=False),
        sa.Column("isRead", sa.Boolean(), server_default="0", nullable=False),
        sa.Column(
            "createdAt",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column("readAt", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadataJson", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["userId"], ["Users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "Notifications_userId_idx",
        "Notifications",
        ["userId"],
        unique=False,
    )
    op.create_index(
        "Notifications_userId_isRead_idx",
        "Notifications",
        ["userId", "isRead"],
        unique=False,
    )


def downgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "Notifications" not in table_names:
        return

    op.drop_index("Notifications_userId_isRead_idx", table_name="Notifications")
    op.drop_index("Notifications_userId_idx", table_name="Notifications")
    op.drop_table("Notifications")
