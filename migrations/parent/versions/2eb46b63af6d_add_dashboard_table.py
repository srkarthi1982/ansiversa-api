"""add_dashboard_table

Revision ID: 2eb46b63af6d
Revises: d37955396b80
Create Date: 2026-05-29 18:41:12.913661

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "2eb46b63af6d"
down_revision: str | None = "d37955396b80"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "Dashboard" in table_names:
        return

    op.create_table(
        "Dashboard",
        sa.Column("_id", sa.String(length=36), nullable=False),
        sa.Column("userId", sa.String(length=36), nullable=False),
        sa.Column("appId", sa.String(length=36), nullable=False),
        sa.Column("lastActivityAt", sa.DateTime(timezone=True), nullable=True),
        sa.Column("summaryVersion", sa.Integer(), server_default="1", nullable=False),
        sa.Column(
            "createdAt",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updatedAt",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column("summaryJson", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["appId"], ["Apps.id"]),
        sa.ForeignKeyConstraint(["userId"], ["Users.id"]),
        sa.PrimaryKeyConstraint("_id"),
    )
    op.create_index(
        "Dashboard_userId_appId_idx",
        "Dashboard",
        ["userId", "appId"],
        unique=True,
    )
    op.create_index(
        "Dashboard_userId_lastActivityAt_idx",
        "Dashboard",
        ["userId", "lastActivityAt"],
        unique=False,
    )


def downgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "Dashboard" not in table_names:
        return

    op.drop_index("Dashboard_userId_lastActivityAt_idx", table_name="Dashboard")
    op.drop_index("Dashboard_userId_appId_idx", table_name="Dashboard")
    op.drop_table("Dashboard")
