"""add_user_preferences

Revision ID: 8e82dd41d8b5
Revises: 37b6a413d876
Create Date: 2026-05-29 09:41:58.894413

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "8e82dd41d8b5"
down_revision: str | None = "37b6a413d876"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "UserPreferences" in table_names:
        return

    op.create_table(
        "UserPreferences",
        sa.Column("userId", sa.String(length=36), nullable=False),
        sa.Column("productUpdates", sa.Boolean(), server_default="0", nullable=False),
        sa.Column("securityAlerts", sa.Boolean(), server_default="1", nullable=False),
        sa.Column("theme", sa.String(length=40), nullable=True),
        sa.Column(
            "updatedAt",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["userId"], ["Users.id"]),
        sa.PrimaryKeyConstraint("userId"),
    )


def downgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "UserPreferences" in table_names:
        op.drop_table("UserPreferences")
