"""repair legacy meal plan week start

Revision ID: 20260706_0002
Revises: 20260706_0001
Create Date: 2026-07-06
"""
from alembic import op
import sqlalchemy as sa

revision = "20260706_0002"
down_revision = "20260706_0001"
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


def upgrade() -> None:
    meal_plan_columns = _columns("MealPlans")
    if "weekStartDate" not in meal_plan_columns:
        op.add_column(
            "MealPlans",
            sa.Column("weekStartDate", sa.String(length=40), server_default="", nullable=False),
        )
        bind = op.get_bind()
        if "planDate" in meal_plan_columns:
            bind.execute(
                sa.text(
                    'UPDATE "MealPlans" '
                    'SET "weekStartDate" = COALESCE(NULLIF("planDate", \'\'), date(\'now\')) '
                    'WHERE "weekStartDate" = \'\''
                )
            )
        else:
            bind.execute(
                sa.text('UPDATE "MealPlans" SET "weekStartDate" = date(\'now\') WHERE "weekStartDate" = \'\'')
            )

    if "ix_MealPlans_weekStartDate" not in _indexes("MealPlans"):
        op.create_index("ix_MealPlans_weekStartDate", "MealPlans", ["weekStartDate"])


def downgrade() -> None:
    if "ix_MealPlans_weekStartDate" in _indexes("MealPlans"):
        op.drop_index("ix_MealPlans_weekStartDate", table_name="MealPlans")
