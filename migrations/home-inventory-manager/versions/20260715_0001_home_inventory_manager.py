"""Create Home Inventory Manager tables."""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260715_0001_home_inventory_manager"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "Categories",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("userId", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("userId", "name", name="uq_home_inventory_categories_owner_name"),
    )
    op.create_index("ix_home_inventory_categories_user_id", "Categories", ["userId"], unique=False)
    op.create_index("ix_home_inventory_categories_user_name", "Categories", ["userId", "name"], unique=False)

    op.create_table(
        "Items",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("userId", sa.String(length=36), nullable=False),
        sa.Column("categoryId", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("room", sa.String(length=120), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("purchaseDate", sa.String(length=40), nullable=True),
        sa.Column("purchasePrice", sa.Numeric(12, 2), nullable=True),
        sa.Column("estimatedValue", sa.Numeric(12, 2), nullable=True),
        sa.Column("warrantyExpiry", sa.String(length=40), nullable=True),
        sa.Column("brand", sa.String(length=120), nullable=True),
        sa.Column("model", sa.String(length=120), nullable=True),
        sa.Column("serialNumber", sa.String(length=160), nullable=True),
        sa.Column("condition", sa.String(length=40), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("archived", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["categoryId"], ["Categories.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_home_inventory_items_user_id", "Items", ["userId"], unique=False)
    op.create_index("ix_home_inventory_items_category_id", "Items", ["categoryId"], unique=False)
    op.create_index("ix_home_inventory_items_room", "Items", ["room"], unique=False)
    op.create_index("ix_home_inventory_items_condition", "Items", ["condition"], unique=False)
    op.create_index("ix_home_inventory_items_archived", "Items", ["archived"], unique=False)
    op.create_index("ix_home_inventory_items_purchase_date", "Items", ["purchaseDate"], unique=False)
    op.create_index("ix_home_inventory_items_estimated_value", "Items", ["estimatedValue"], unique=False)
    op.create_index("ix_home_inventory_items_warranty_expiry", "Items", ["warrantyExpiry"], unique=False)
    op.create_index("ix_home_inventory_items_user_category", "Items", ["userId", "categoryId"], unique=False)
    op.create_index("ix_home_inventory_items_user_room", "Items", ["userId", "room"], unique=False)
    op.create_index("ix_home_inventory_items_user_condition", "Items", ["userId", "condition"], unique=False)
    op.create_index("ix_home_inventory_items_user_archived", "Items", ["userId", "archived"], unique=False)
    op.create_index("ix_home_inventory_items_user_warranty", "Items", ["userId", "warrantyExpiry"], unique=False)
    op.create_index("ix_home_inventory_items_user_updated", "Items", ["userId", "updatedAt"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_home_inventory_items_user_updated", table_name="Items")
    op.drop_index("ix_home_inventory_items_user_warranty", table_name="Items")
    op.drop_index("ix_home_inventory_items_user_archived", table_name="Items")
    op.drop_index("ix_home_inventory_items_user_condition", table_name="Items")
    op.drop_index("ix_home_inventory_items_user_room", table_name="Items")
    op.drop_index("ix_home_inventory_items_user_category", table_name="Items")
    op.drop_index("ix_home_inventory_items_warranty_expiry", table_name="Items")
    op.drop_index("ix_home_inventory_items_estimated_value", table_name="Items")
    op.drop_index("ix_home_inventory_items_purchase_date", table_name="Items")
    op.drop_index("ix_home_inventory_items_archived", table_name="Items")
    op.drop_index("ix_home_inventory_items_condition", table_name="Items")
    op.drop_index("ix_home_inventory_items_room", table_name="Items")
    op.drop_index("ix_home_inventory_items_category_id", table_name="Items")
    op.drop_index("ix_home_inventory_items_user_id", table_name="Items")
    op.drop_table("Items")
    op.drop_index("ix_home_inventory_categories_user_name", table_name="Categories")
    op.drop_index("ix_home_inventory_categories_user_id", table_name="Categories")
    op.drop_table("Categories")
