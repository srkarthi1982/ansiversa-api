"""Create Emergency Contacts Organizer tables."""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260715_0001_emergency_contacts_organizer"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "Categories",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("userId", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=240), nullable=True),
        sa.Column("sortOrder", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("isSystem", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("userId", "name", name="uq_emergency_contacts_categories_owner_name"),
    )
    op.create_index("ix_emergency_contacts_categories_user_id", "Categories", ["userId"], unique=False)
    op.create_index("ix_emergency_contacts_categories_user_name", "Categories", ["userId", "name"], unique=False)
    op.create_index("ix_emergency_contacts_categories_user_sort", "Categories", ["userId", "sortOrder"], unique=False)
    op.create_index("ix_emergency_contacts_categories_is_system", "Categories", ["isSystem"], unique=False)

    op.create_table(
        "Contacts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("userId", sa.String(length=36), nullable=False),
        sa.Column("categoryId", sa.String(length=36), nullable=False),
        sa.Column("fullName", sa.String(length=180), nullable=False),
        sa.Column("relationship", sa.String(length=120), nullable=False),
        sa.Column("primaryPhone", sa.String(length=60), nullable=False),
        sa.Column("alternatePhone", sa.String(length=60), nullable=True),
        sa.Column("email", sa.String(length=180), nullable=True),
        sa.Column("countryOrRegion", sa.String(length=120), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("priority", sa.Integer(), nullable=False, server_default=sa.text("50")),
        sa.Column("isFavourite", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("isPrimary", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["categoryId"], ["Categories.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_emergency_contacts_contacts_user_id", "Contacts", ["userId"], unique=False)
    op.create_index("ix_emergency_contacts_contacts_category_id", "Contacts", ["categoryId"], unique=False)
    op.create_index("ix_emergency_contacts_contacts_relationship", "Contacts", ["relationship"], unique=False)
    op.create_index("ix_emergency_contacts_contacts_country", "Contacts", ["countryOrRegion"], unique=False)
    op.create_index("ix_emergency_contacts_contacts_priority", "Contacts", ["priority"], unique=False)
    op.create_index("ix_emergency_contacts_contacts_is_favourite", "Contacts", ["isFavourite"], unique=False)
    op.create_index("ix_emergency_contacts_contacts_is_primary", "Contacts", ["isPrimary"], unique=False)
    op.create_index("ix_emergency_contacts_contacts_user_category", "Contacts", ["userId", "categoryId"], unique=False)
    op.create_index("ix_emergency_contacts_contacts_user_favourite", "Contacts", ["userId", "isFavourite"], unique=False)
    op.create_index("ix_emergency_contacts_contacts_user_primary", "Contacts", ["userId", "isPrimary"], unique=False)
    op.create_index("ix_emergency_contacts_contacts_user_priority", "Contacts", ["userId", "priority"], unique=False)
    op.create_index("ix_emergency_contacts_contacts_user_updated", "Contacts", ["userId", "updatedAt"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_emergency_contacts_contacts_user_updated", table_name="Contacts")
    op.drop_index("ix_emergency_contacts_contacts_user_priority", table_name="Contacts")
    op.drop_index("ix_emergency_contacts_contacts_user_primary", table_name="Contacts")
    op.drop_index("ix_emergency_contacts_contacts_user_favourite", table_name="Contacts")
    op.drop_index("ix_emergency_contacts_contacts_user_category", table_name="Contacts")
    op.drop_index("ix_emergency_contacts_contacts_is_primary", table_name="Contacts")
    op.drop_index("ix_emergency_contacts_contacts_is_favourite", table_name="Contacts")
    op.drop_index("ix_emergency_contacts_contacts_priority", table_name="Contacts")
    op.drop_index("ix_emergency_contacts_contacts_country", table_name="Contacts")
    op.drop_index("ix_emergency_contacts_contacts_relationship", table_name="Contacts")
    op.drop_index("ix_emergency_contacts_contacts_category_id", table_name="Contacts")
    op.drop_index("ix_emergency_contacts_contacts_user_id", table_name="Contacts")
    op.drop_table("Contacts")
    op.drop_index("ix_emergency_contacts_categories_is_system", table_name="Categories")
    op.drop_index("ix_emergency_contacts_categories_user_sort", table_name="Categories")
    op.drop_index("ix_emergency_contacts_categories_user_name", table_name="Categories")
    op.drop_index("ix_emergency_contacts_categories_user_id", table_name="Categories")
    op.drop_table("Categories")
