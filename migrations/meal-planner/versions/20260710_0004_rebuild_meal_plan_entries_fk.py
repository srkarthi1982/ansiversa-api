"""rebuild meal plan entries foreign key

Revision ID: 20260710_0004
Revises: 20260706_0003
Create Date: 2026-07-10
"""
from alembic import op
import sqlalchemy as sa

revision = "20260710_0004"
down_revision = "20260706_0003"
branch_labels = None
depends_on = None


def _foreign_key_tables(table_name: str) -> set[str]:
    bind = op.get_bind()
    rows = bind.execute(sa.text(f'PRAGMA foreign_key_list("{table_name}")')).fetchall()
    return {row[2] for row in rows}


def _indexes(table_name: str) -> set[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return {index["name"] for index in inspector.get_indexes(table_name)}


def _create_entries_table(table_name: str) -> None:
    op.create_table(
        table_name,
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("userId", sa.String(length=36), nullable=False),
        sa.Column("mealPlanId", sa.String(length=36), nullable=False),
        sa.Column("recipeId", sa.String(length=36), nullable=True),
        sa.Column("entryDate", sa.String(length=40), nullable=False),
        sa.Column("mealType", sa.String(length=40), server_default="dinner", nullable=False),
        sa.Column("title", sa.String(length=180), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("sortOrder", sa.Integer(), server_default="0", nullable=False),
        sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["mealPlanId"], ["MealPlans.id"]),
        sa.ForeignKeyConstraint(["recipeId"], ["Recipes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def _create_current_indexes(table_name: str = "MealPlanEntries") -> None:
    existing_indexes = _indexes(table_name)
    if "ix_MealPlanEntries_userId" not in existing_indexes:
        op.create_index("ix_MealPlanEntries_userId", table_name, ["userId"])
    if "ix_MealPlanEntries_mealPlanId" not in existing_indexes:
        op.create_index("ix_MealPlanEntries_mealPlanId", table_name, ["mealPlanId"])
    if "ix_MealPlanEntries_recipeId" not in existing_indexes:
        op.create_index("ix_MealPlanEntries_recipeId", table_name, ["recipeId"])
    if "ix_MealPlanEntries_entryDate" not in existing_indexes:
        op.create_index("ix_MealPlanEntries_entryDate", table_name, ["entryDate"])
    if "ix_MealPlanEntries_updatedAt" not in existing_indexes:
        op.create_index("ix_MealPlanEntries_updatedAt", table_name, ["updatedAt"])


def upgrade() -> None:
    if "MealPlans_legacy" not in _foreign_key_tables("MealPlanEntries"):
        _create_current_indexes()
        return

    bind = op.get_bind()
    op.rename_table("MealPlanEntries", "MealPlanEntries_legacy")
    _create_entries_table("MealPlanEntries")
    bind.execute(
        sa.text(
            """
            INSERT INTO "MealPlanEntries" (
                "id",
                "userId",
                "mealPlanId",
                "recipeId",
                "entryDate",
                "mealType",
                "title",
                "notes",
                "sortOrder",
                "createdAt",
                "updatedAt"
            )
            SELECT
                entries."id",
                entries."userId",
                entries."mealPlanId",
                entries."recipeId",
                entries."entryDate",
                COALESCE(NULLIF(entries."mealType", ''), 'dinner'),
                entries."title",
                entries."notes",
                COALESCE(entries."sortOrder", 0),
                COALESCE(entries."createdAt", CURRENT_TIMESTAMP),
                COALESCE(entries."updatedAt", CURRENT_TIMESTAMP)
            FROM "MealPlanEntries_legacy" AS entries
            INNER JOIN "MealPlans" AS plans ON plans."id" = entries."mealPlanId"
            """
        )
    )
    op.drop_table("MealPlanEntries_legacy")
    _create_current_indexes()


def downgrade() -> None:
    pass
