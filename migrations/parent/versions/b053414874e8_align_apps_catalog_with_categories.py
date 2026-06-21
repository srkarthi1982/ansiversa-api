"""align_apps_catalog_with_categories

Revision ID: b053414874e8
Revises: a7e246b7249d
Create Date: 2026-05-28 19:51:32.891671

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "b053414874e8"
down_revision: str | None = "a7e246b7249d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect_name = bind.dialect.name
    recreate = "always" if dialect_name == "sqlite" else "auto"

    if "Categories" not in sa.inspect(bind).get_table_names():
        op.create_table(
            "Categories",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("key", sa.String(length=120), nullable=True),
            sa.Column("slug", sa.String(length=120), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("sortOrder", sa.Integer(), server_default="0", nullable=False),
            sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
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
            sa.UniqueConstraint("slug"),
        )

    with op.batch_alter_table(
        "apps",
        recreate=recreate,
    ) as batch_op:
        batch_op.alter_column(
            "category",
            new_column_name="categoryId",
            existing_type=sa.String(length=120),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "is_featured",
            new_column_name="isFeatured",
            existing_type=sa.Boolean(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "website_url",
            new_column_name="websiteUrl",
            existing_type=sa.String(length=500),
            existing_nullable=True,
        )
        batch_op.alter_column(
            "admin_url",
            new_column_name="adminUrl",
            existing_type=sa.String(length=500),
            existing_nullable=True,
        )
        batch_op.alter_column(
            "created_at",
            new_column_name="createdAt",
            existing_type=sa.DateTime(timezone=True),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "updated_at",
            new_column_name="updatedAt",
            existing_type=sa.DateTime(timezone=True),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "launch_status",
            new_column_name="launchStatus",
            existing_type=sa.String(length=40),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "logo_key",
            new_column_name="logoKey",
            existing_type=sa.String(length=120),
            existing_nullable=True,
        )
        batch_op.add_column(
            sa.Column("capabilities", sa.Text(), server_default="[]", nullable=True)
        )
        batch_op.add_column(
            sa.Column(
                "pricingGate",
                sa.String(length=40),
                server_default="free",
                nullable=False,
            )
        )
        if dialect_name != "sqlite":
            batch_op.create_foreign_key(
                "fk_Apps_categoryId_Categories_id_fk",
                "Categories",
                ["categoryId"],
                ["id"],
            )

    if dialect_name == "sqlite":
        op.rename_table("apps", "apps_case_tmp")
        op.rename_table("apps_case_tmp", "Apps")
    else:
        op.rename_table("apps", "Apps")


def downgrade() -> None:
    bind = op.get_bind()
    dialect_name = bind.dialect.name
    recreate = "always" if dialect_name == "sqlite" else "auto"

    if dialect_name == "sqlite":
        op.rename_table("Apps", "apps_case_tmp")
        op.rename_table("apps_case_tmp", "apps")
    else:
        op.rename_table("Apps", "apps")

    with op.batch_alter_table("apps", recreate=recreate) as batch_op:
        if dialect_name != "sqlite":
            batch_op.drop_constraint(
                "fk_Apps_categoryId_Categories_id_fk",
                type_="foreignkey",
            )
        batch_op.drop_column("pricingGate")
        batch_op.drop_column("capabilities")
        batch_op.alter_column(
            "logoKey",
            new_column_name="logo_key",
            existing_type=sa.String(length=120),
            existing_nullable=True,
        )
        batch_op.alter_column(
            "launchStatus",
            new_column_name="launch_status",
            existing_type=sa.String(length=40),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "updatedAt",
            new_column_name="updated_at",
            existing_type=sa.DateTime(timezone=True),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "createdAt",
            new_column_name="created_at",
            existing_type=sa.DateTime(timezone=True),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "adminUrl",
            new_column_name="admin_url",
            existing_type=sa.String(length=500),
            existing_nullable=True,
        )
        batch_op.alter_column(
            "websiteUrl",
            new_column_name="website_url",
            existing_type=sa.String(length=500),
            existing_nullable=True,
        )
        batch_op.alter_column(
            "isFeatured",
            new_column_name="is_featured",
            existing_type=sa.Boolean(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "categoryId",
            new_column_name="category",
            existing_type=sa.String(length=120),
            existing_nullable=False,
        )

    op.drop_table("Categories")
