"""add meal planner tables

Revision ID: 20260706_0001
Revises:
Create Date: 2026-07-06
"""
from alembic import op
import sqlalchemy as sa

revision = "20260706_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "Recipes",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("userId", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=True),
        sa.Column("prepMinutes", sa.Integer(), nullable=True),
        sa.Column("cookMinutes", sa.Integer(), nullable=True),
        sa.Column("servings", sa.Integer(), nullable=True),
        sa.Column("ingredients", sa.Text(), nullable=True),
        sa.Column("instructions", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_Recipes_userId", "Recipes", ["userId"])
    op.create_index("ix_Recipes_updatedAt", "Recipes", ["updatedAt"])

    op.create_table(
        "MealPlans",
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
    op.create_index("ix_MealPlans_userId", "MealPlans", ["userId"])
    op.create_index("ix_MealPlans_weekStartDate", "MealPlans", ["weekStartDate"])
    op.create_index("ix_MealPlans_updatedAt", "MealPlans", ["updatedAt"])

    op.create_table(
        "MealPlanEntries",
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
    op.create_index("ix_MealPlanEntries_userId", "MealPlanEntries", ["userId"])
    op.create_index("ix_MealPlanEntries_mealPlanId", "MealPlanEntries", ["mealPlanId"])
    op.create_index("ix_MealPlanEntries_recipeId", "MealPlanEntries", ["recipeId"])
    op.create_index("ix_MealPlanEntries_entryDate", "MealPlanEntries", ["entryDate"])
    op.create_index("ix_MealPlanEntries_updatedAt", "MealPlanEntries", ["updatedAt"])


def downgrade() -> None:
    op.drop_index("ix_MealPlanEntries_updatedAt", table_name="MealPlanEntries")
    op.drop_index("ix_MealPlanEntries_entryDate", table_name="MealPlanEntries")
    op.drop_index("ix_MealPlanEntries_recipeId", table_name="MealPlanEntries")
    op.drop_index("ix_MealPlanEntries_mealPlanId", table_name="MealPlanEntries")
    op.drop_index("ix_MealPlanEntries_userId", table_name="MealPlanEntries")
    op.drop_table("MealPlanEntries")
    op.drop_index("ix_MealPlans_updatedAt", table_name="MealPlans")
    op.drop_index("ix_MealPlans_weekStartDate", table_name="MealPlans")
    op.drop_index("ix_MealPlans_userId", table_name="MealPlans")
    op.drop_table("MealPlans")
    op.drop_index("ix_Recipes_updatedAt", table_name="Recipes")
    op.drop_index("ix_Recipes_userId", table_name="Recipes")
    op.drop_table("Recipes")
