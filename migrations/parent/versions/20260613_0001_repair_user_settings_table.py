"""repair_user_settings_table

Revision ID: 20260613_0001
Revises: 20260612_0001
Create Date: 2026-06-13 00:00:00

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260613_0001"
down_revision: str | None = "20260612_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())

    if "UserSettings" not in table_names:
        op.create_table(
            "UserSettings",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column(
                "theme",
                sa.String(length=40),
                server_default="system",
                nullable=False,
            ),
            sa.Column(
                "language",
                sa.String(length=20),
                server_default="en",
                nullable=False,
            ),
            sa.Column(
                "marketingEmails",
                sa.Boolean(),
                server_default="0",
                nullable=False,
            ),
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
            sa.ForeignKeyConstraint(["userId"], ["Users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            op.f("ix_UserSettings_userId"),
            "UserSettings",
            ["userId"],
            unique=True,
        )


def downgrade() -> None:
    # The table may predate this corrective migration, so downgrade must not
    # remove user settings data.
    pass
