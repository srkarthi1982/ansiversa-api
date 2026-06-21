"""align_auth_with_parent_schema

Revision ID: 37b6a413d876
Revises: b053414874e8
Create Date: 2026-05-29 09:27:47.168122

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "37b6a413d876"
down_revision: str | None = "b053414874e8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _table_names() -> set[str]:
    return set(sa.inspect(op.get_bind()).get_table_names())


def _create_roles_table() -> None:
    if "Roles" in _table_names():
        return

    op.create_table(
        "Roles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("key", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("permissionsJson", sa.Text(), nullable=True),
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key"),
        sa.UniqueConstraint("name"),
    )


def _create_users_table(table_name: str = "Users") -> None:
    op.create_table(
        table_name,
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("passwordHash", sa.String(length=255), nullable=False),
        sa.Column("roleId", sa.Integer(), server_default="2", nullable=False),
        sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
        sa.Column("avatarKey", sa.String(length=500), nullable=True),
        sa.Column("avatarUrl", sa.String(length=1000), nullable=True),
        sa.Column("avatarUpdatedAt", sa.DateTime(timezone=True), nullable=True),
        sa.Column("stripeCustomerId", sa.String(length=255), nullable=True),
        sa.Column("plan", sa.String(length=120), nullable=True),
        sa.Column("planStatus", sa.String(length=120), nullable=True),
        sa.Column("countryCode", sa.String(length=20), nullable=True),
        sa.Column("regionCode", sa.String(length=120), nullable=True),
        sa.Column("city", sa.String(length=255), nullable=True),
        sa.Column("timezone", sa.String(length=120), nullable=True),
        sa.Column(
            "locationSource",
            sa.String(length=120),
            server_default="unknown",
            nullable=False,
        ),
        sa.Column("locationCapturedAt", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(["roleId"], ["Roles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def _insert_default_member_role() -> None:
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    if dialect_name == "sqlite":
        op.execute(
            """
            INSERT OR IGNORE INTO "Roles" (
              id, name, key, description, permissionsJson, createdAt, updatedAt
            )
            VALUES (
              2,
              'Member',
              'member',
              'Default Ansiversa member role.',
              NULL,
              CURRENT_TIMESTAMP,
              CURRENT_TIMESTAMP
            )
            """
        )
        return

    op.execute(
        """
        INSERT INTO "Roles" (
          id, name, key, description, "permissionsJson", "createdAt", "updatedAt"
        )
        VALUES (
          2,
          'Member',
          'member',
          'Default Ansiversa member role.',
          NULL,
          CURRENT_TIMESTAMP,
          CURRENT_TIMESTAMP
        )
        ON CONFLICT (id) DO NOTHING
        """
    )


def _copy_legacy_users(target_table: str) -> None:
    op.execute(
        f"""
        INSERT INTO "{target_table}" (
          id,
          email,
          name,
          passwordHash,
          roleId,
          status,
          locationSource,
          createdAt,
          updatedAt
        )
        SELECT
          id,
          email,
          full_name,
          password_hash,
          2,
          CASE WHEN is_active THEN 'active' ELSE 'disabled' END,
          'unknown',
          created_at,
          updated_at
        FROM users
        """
    )


def upgrade() -> None:
    _create_roles_table()
    _insert_default_member_role()

    names = _table_names()
    has_legacy_users = "users" in names
    has_parent_users = "Users" in names
    dialect_name = op.get_bind().dialect.name

    if has_parent_users:
        return

    if has_legacy_users and dialect_name == "sqlite":
        _create_users_table("Users_new")
        _copy_legacy_users("Users_new")
        op.drop_index(op.f("ix_users_email"), table_name="users")
        op.drop_table("users")
        op.rename_table("Users_new", "Users")
        op.create_index(op.f("ix_Users_email"), "Users", ["email"], unique=True)
        return

    _create_users_table("Users")
    op.create_index(op.f("ix_Users_email"), "Users", ["email"], unique=True)

    if has_legacy_users:
        _copy_legacy_users("Users")
        op.drop_index(op.f("ix_users_email"), table_name="users")
        op.drop_table("users")


def downgrade() -> None:
    names = _table_names()

    if "users" not in names:
        op.create_table(
            "users",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("password_hash", sa.String(length=255), nullable=False),
            sa.Column("full_name", sa.String(length=255), nullable=False),
            sa.Column("is_active", sa.Boolean(), server_default="1", nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("(CURRENT_TIMESTAMP)"),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("(CURRENT_TIMESTAMP)"),
                nullable=False,
            ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

        if "Users" in names:
            op.execute(
                """
                INSERT INTO users (
                  id, email, password_hash, full_name, is_active, created_at, updated_at
                )
                SELECT
                  id,
                  email,
                  passwordHash,
                  name,
                  CASE WHEN status = 'active' THEN 1 ELSE 0 END,
                  createdAt,
                  updatedAt
                FROM "Users"
                """
            )

    if "Users" in names:
        op.drop_index(op.f("ix_Users_email"), table_name="Users")
        op.drop_table("Users")

    if "Roles" in names:
        op.drop_table("Roles")
