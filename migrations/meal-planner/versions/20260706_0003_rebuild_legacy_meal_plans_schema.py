"""rebuild legacy meal plans schema

Revision ID: 20260706_0003
Revises: 20260706_0002
Create Date: 2026-07-10
"""
from alembic import op
import sqlalchemy as sa

revision = "20260706_0003"
down_revision = "20260706_0002"
branch_labels = None
depends_on = None


def _columns(table_name: str) -> set[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return {column["name"] for column in inspector.get_columns(table_name)}


def _indexes(table_name: str) -> set[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return {index["name"] for index in inspector.get_indexes(table_name)}


def _create_meal_plans_table(table_name: str) -> None:
    op.create_table(
        table_name,
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("userId", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("weekStartDate", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), server_default="draft", nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def _create_current_indexes(table_name: str = "MealPlans") -> None:
    existing_indexes = _indexes(table_name)
    if "ix_MealPlans_userId" not in existing_indexes:
        op.create_index("ix_MealPlans_userId", table_name, ["userId"])
    if "ix_MealPlans_weekStartDate" not in existing_indexes:
        op.create_index("ix_MealPlans_weekStartDate", table_name, ["weekStartDate"])
    if "ix_MealPlans_updatedAt" not in existing_indexes:
        op.create_index("ix_MealPlans_updatedAt", table_name, ["updatedAt"])


def upgrade() -> None:
    meal_plan_columns = _columns("MealPlans")
    legacy_columns = {"planDate", "mealType", "category", "ingredientsText", "prepNotes", "sortOrder", "archivedAt"}
    if not legacy_columns.intersection(meal_plan_columns):
        _create_current_indexes()
        return

    bind = op.get_bind()
    op.rename_table("MealPlans", "MealPlans_legacy")
    _create_meal_plans_table("MealPlans")
    bind.execute(
        sa.text(
            """
            INSERT INTO "MealPlans" (
                "id",
                "userId",
                "title",
                "weekStartDate",
                "status",
                "notes",
                "createdAt",
                "updatedAt"
            )
            SELECT
                "id",
                "userId",
                "title",
                COALESCE(NULLIF("weekStartDate", ''), NULLIF("planDate", ''), date('now')),
                COALESCE(NULLIF("status", ''), 'draft'),
                "notes",
                COALESCE(NULLIF("createdAt", ''), CURRENT_TIMESTAMP),
                COALESCE(NULLIF("updatedAt", ''), CURRENT_TIMESTAMP)
            FROM "MealPlans_legacy"
            """
        )
    )
    op.drop_table("MealPlans_legacy")
    _create_current_indexes()


def downgrade() -> None:
    pass
