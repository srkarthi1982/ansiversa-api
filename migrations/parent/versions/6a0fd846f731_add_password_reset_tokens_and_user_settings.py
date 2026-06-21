"""add_password_reset_tokens_and_user_settings

Revision ID: 6a0fd846f731
Revises: 29cde1832712
Create Date: 2026-06-07

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "6a0fd846f731"
down_revision: str | None = "29cde1832712"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())

    if "PasswordResetTokens" not in table_names:
        op.create_table(
            "PasswordResetTokens",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("tokenHash", sa.String(length=64), nullable=False),
            sa.Column("expiresAt", sa.DateTime(timezone=True), nullable=False),
            sa.Column("usedAt", sa.DateTime(timezone=True), nullable=True),
            sa.Column(
                "createdAt",
                sa.DateTime(timezone=True),
                server_default=sa.text("(CURRENT_TIMESTAMP)"),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["userId"], ["Users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            op.f("ix_PasswordResetTokens_tokenHash"),
            "PasswordResetTokens",
            ["tokenHash"],
            unique=True,
        )
        op.create_index(
            op.f("ix_PasswordResetTokens_userId"),
            "PasswordResetTokens",
            ["userId"],
            unique=False,
        )

    if "UserSettings" not in table_names:
        op.create_table(
            "UserSettings",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("theme", sa.String(length=40), server_default="system", nullable=False),
            sa.Column("language", sa.String(length=20), server_default="en", nullable=False),
            sa.Column("marketingEmails", sa.Boolean(), server_default="0", nullable=False),
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
    table_names = set(sa.inspect(op.get_bind()).get_table_names())

    if "UserSettings" in table_names:
        op.drop_index(op.f("ix_UserSettings_userId"), table_name="UserSettings")
        op.drop_table("UserSettings")

    if "PasswordResetTokens" in table_names:
        op.drop_index(
            op.f("ix_PasswordResetTokens_userId"),
            table_name="PasswordResetTokens",
        )
        op.drop_index(
            op.f("ix_PasswordResetTokens_tokenHash"),
            table_name="PasswordResetTokens",
        )
        op.drop_table("PasswordResetTokens")
