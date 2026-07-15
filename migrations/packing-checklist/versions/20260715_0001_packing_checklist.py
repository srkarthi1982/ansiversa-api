"""Create Packing Checklist tables."""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260715_0001_packing_checklist"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "PackingCategories",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("userId", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("sortOrder", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("isSystem", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("userId", "name", name="uq_packing_categories_owner_name"),
    )
    op.create_index("ix_packing_categories_user_id", "PackingCategories", ["userId"], unique=False)
    op.create_index("ix_packing_categories_user_name", "PackingCategories", ["userId", "name"], unique=False)
    op.create_index("ix_packing_categories_user_sort", "PackingCategories", ["userId", "sortOrder"], unique=False)
    op.create_index("ix_packing_categories_is_system", "PackingCategories", ["isSystem"], unique=False)

    op.create_table(
        "PackingChecklists",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("userId", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("destination", sa.String(length=180), nullable=True),
        sa.Column("tripType", sa.String(length=80), nullable=False),
        sa.Column("startDate", sa.Date(), nullable=True),
        sa.Column("endDate", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("archived", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_packing_checklists_user_id", "PackingChecklists", ["userId"], unique=False)
    op.create_index("ix_packing_checklists_user_archived", "PackingChecklists", ["userId", "archived"], unique=False)
    op.create_index("ix_packing_checklists_user_status", "PackingChecklists", ["userId", "status"], unique=False)
    op.create_index("ix_packing_checklists_user_trip_type", "PackingChecklists", ["userId", "tripType"], unique=False)
    op.create_index("ix_packing_checklists_user_start_date", "PackingChecklists", ["userId", "startDate"], unique=False)
    op.create_index("ix_packing_checklists_user_updated", "PackingChecklists", ["userId", "updatedAt"], unique=False)
    op.create_index("ix_packing_checklists_destination", "PackingChecklists", ["destination"], unique=False)

    op.create_table(
        "PackingItems",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("userId", sa.String(length=36), nullable=False),
        sa.Column("checklistId", sa.String(length=36), nullable=False),
        sa.Column("categoryId", sa.String(length=36), nullable=False),
        sa.Column("itemName", sa.String(length=180), nullable=False),
        sa.Column("quantity", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("packed", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["categoryId"], ["PackingCategories.id"]),
        sa.ForeignKeyConstraint(["checklistId"], ["PackingChecklists.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_packing_items_user_id", "PackingItems", ["userId"], unique=False)
    op.create_index("ix_packing_items_checklist_id", "PackingItems", ["checklistId"], unique=False)
    op.create_index("ix_packing_items_category_id", "PackingItems", ["categoryId"], unique=False)
    op.create_index("ix_packing_items_user_checklist", "PackingItems", ["userId", "checklistId"], unique=False)
    op.create_index("ix_packing_items_user_category", "PackingItems", ["userId", "categoryId"], unique=False)
    op.create_index("ix_packing_items_checklist_packed", "PackingItems", ["checklistId", "packed"], unique=False)
    op.create_index("ix_packing_items_checklist_priority", "PackingItems", ["checklistId", "priority"], unique=False)
    op.create_index("ix_packing_items_user_updated", "PackingItems", ["userId", "updatedAt"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_packing_items_user_updated", table_name="PackingItems")
    op.drop_index("ix_packing_items_checklist_priority", table_name="PackingItems")
    op.drop_index("ix_packing_items_checklist_packed", table_name="PackingItems")
    op.drop_index("ix_packing_items_user_category", table_name="PackingItems")
    op.drop_index("ix_packing_items_user_checklist", table_name="PackingItems")
    op.drop_index("ix_packing_items_category_id", table_name="PackingItems")
    op.drop_index("ix_packing_items_checklist_id", table_name="PackingItems")
    op.drop_index("ix_packing_items_user_id", table_name="PackingItems")
    op.drop_table("PackingItems")
    op.drop_index("ix_packing_checklists_destination", table_name="PackingChecklists")
    op.drop_index("ix_packing_checklists_user_updated", table_name="PackingChecklists")
    op.drop_index("ix_packing_checklists_user_start_date", table_name="PackingChecklists")
    op.drop_index("ix_packing_checklists_user_trip_type", table_name="PackingChecklists")
    op.drop_index("ix_packing_checklists_user_status", table_name="PackingChecklists")
    op.drop_index("ix_packing_checklists_user_archived", table_name="PackingChecklists")
    op.drop_index("ix_packing_checklists_user_id", table_name="PackingChecklists")
    op.drop_table("PackingChecklists")
    op.drop_index("ix_packing_categories_is_system", table_name="PackingCategories")
    op.drop_index("ix_packing_categories_user_sort", table_name="PackingCategories")
    op.drop_index("ix_packing_categories_user_name", table_name="PackingCategories")
    op.drop_index("ix_packing_categories_user_id", table_name="PackingCategories")
    op.drop_table("PackingCategories")
