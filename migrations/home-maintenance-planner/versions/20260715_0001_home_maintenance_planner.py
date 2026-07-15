"""Create Home Maintenance Planner tables."""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260715_0001_home_maintenance_planner"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "MaintenanceAreas",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("userId", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("sortOrder", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("isSystem", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("userId", "name", name="uq_maintenance_areas_owner_name"),
    )
    op.create_index("ix_maintenance_areas_user_id", "MaintenanceAreas", ["userId"], unique=False)
    op.create_index("ix_maintenance_areas_user_name", "MaintenanceAreas", ["userId", "name"], unique=False)
    op.create_index("ix_maintenance_areas_user_sort", "MaintenanceAreas", ["userId", "sortOrder"], unique=False)
    op.create_index("ix_maintenance_areas_is_system", "MaintenanceAreas", ["isSystem"], unique=False)

    op.create_table(
        "MaintenanceCategories",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("userId", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("sortOrder", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("isSystem", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("userId", "name", name="uq_maintenance_categories_owner_name"),
    )
    op.create_index("ix_maintenance_categories_user_id", "MaintenanceCategories", ["userId"], unique=False)
    op.create_index("ix_maintenance_categories_user_name", "MaintenanceCategories", ["userId", "name"], unique=False)
    op.create_index("ix_maintenance_categories_user_sort", "MaintenanceCategories", ["userId", "sortOrder"], unique=False)
    op.create_index("ix_maintenance_categories_is_system", "MaintenanceCategories", ["isSystem"], unique=False)

    op.create_table(
        "MaintenanceTasks",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("userId", sa.String(length=36), nullable=False),
        sa.Column("areaId", sa.String(length=36), nullable=False),
        sa.Column("categoryId", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("dueDate", sa.Date(), nullable=False),
        sa.Column("recurrenceType", sa.String(length=40), server_default="one_time", nullable=False),
        sa.Column("recurrenceInterval", sa.Integer(), nullable=True),
        sa.Column("priority", sa.String(length=20), server_default="medium", nullable=False),
        sa.Column("estimatedCost", sa.Numeric(12, 2), nullable=True),
        sa.Column("actualCost", sa.Numeric(12, 2), nullable=True),
        sa.Column("currency", sa.String(length=3), server_default="USD", nullable=False),
        sa.Column("providerName", sa.String(length=180), nullable=True),
        sa.Column("providerPhone", sa.String(length=60), nullable=True),
        sa.Column("providerEmail", sa.String(length=180), nullable=True),
        sa.Column("referenceNumber", sa.String(length=120), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("completionNotes", sa.Text(), nullable=True),
        sa.Column("reminderLeadDays", sa.Integer(), server_default=sa.text("3"), nullable=False),
        sa.Column("completedAt", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["areaId"], ["MaintenanceAreas.id"]),
        sa.ForeignKeyConstraint(["categoryId"], ["MaintenanceCategories.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_maintenance_tasks_user_id", "MaintenanceTasks", ["userId"], unique=False)
    op.create_index("ix_maintenance_tasks_area_id", "MaintenanceTasks", ["areaId"], unique=False)
    op.create_index("ix_maintenance_tasks_category_id", "MaintenanceTasks", ["categoryId"], unique=False)
    op.create_index("ix_maintenance_tasks_user_area", "MaintenanceTasks", ["userId", "areaId"], unique=False)
    op.create_index("ix_maintenance_tasks_user_category", "MaintenanceTasks", ["userId", "categoryId"], unique=False)
    op.create_index("ix_maintenance_tasks_user_due", "MaintenanceTasks", ["userId", "dueDate"], unique=False)
    op.create_index("ix_maintenance_tasks_user_priority", "MaintenanceTasks", ["userId", "priority"], unique=False)
    op.create_index("ix_maintenance_tasks_user_archived", "MaintenanceTasks", ["userId", "archived"], unique=False)
    op.create_index("ix_maintenance_tasks_user_completed", "MaintenanceTasks", ["userId", "completedAt"], unique=False)
    op.create_index("ix_maintenance_tasks_user_updated", "MaintenanceTasks", ["userId", "updatedAt"], unique=False)
    op.create_index("ix_maintenance_tasks_user_recurrence", "MaintenanceTasks", ["userId", "recurrenceType"], unique=False)

    op.create_table(
        "MaintenanceTaskCompletions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("userId", sa.String(length=36), nullable=False),
        sa.Column("taskId", sa.String(length=36), nullable=False),
        sa.Column("completedDueDate", sa.Date(), nullable=False),
        sa.Column("completedAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("actualCost", sa.Numeric(12, 2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["taskId"], ["MaintenanceTasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_maintenance_completions_user_id", "MaintenanceTaskCompletions", ["userId"], unique=False)
    op.create_index("ix_maintenance_completions_task_id", "MaintenanceTaskCompletions", ["taskId"], unique=False)
    op.create_index("ix_maintenance_completions_user_completed", "MaintenanceTaskCompletions", ["userId", "completedAt"], unique=False)
    op.create_index("ix_maintenance_completions_task_due", "MaintenanceTaskCompletions", ["taskId", "completedDueDate"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_maintenance_completions_task_due", table_name="MaintenanceTaskCompletions")
    op.drop_index("ix_maintenance_completions_user_completed", table_name="MaintenanceTaskCompletions")
    op.drop_index("ix_maintenance_completions_task_id", table_name="MaintenanceTaskCompletions")
    op.drop_index("ix_maintenance_completions_user_id", table_name="MaintenanceTaskCompletions")
    op.drop_table("MaintenanceTaskCompletions")
    op.drop_index("ix_maintenance_tasks_user_recurrence", table_name="MaintenanceTasks")
    op.drop_index("ix_maintenance_tasks_user_updated", table_name="MaintenanceTasks")
    op.drop_index("ix_maintenance_tasks_user_completed", table_name="MaintenanceTasks")
    op.drop_index("ix_maintenance_tasks_user_archived", table_name="MaintenanceTasks")
    op.drop_index("ix_maintenance_tasks_user_priority", table_name="MaintenanceTasks")
    op.drop_index("ix_maintenance_tasks_user_due", table_name="MaintenanceTasks")
    op.drop_index("ix_maintenance_tasks_user_category", table_name="MaintenanceTasks")
    op.drop_index("ix_maintenance_tasks_user_area", table_name="MaintenanceTasks")
    op.drop_index("ix_maintenance_tasks_category_id", table_name="MaintenanceTasks")
    op.drop_index("ix_maintenance_tasks_area_id", table_name="MaintenanceTasks")
    op.drop_index("ix_maintenance_tasks_user_id", table_name="MaintenanceTasks")
    op.drop_table("MaintenanceTasks")
    op.drop_index("ix_maintenance_categories_is_system", table_name="MaintenanceCategories")
    op.drop_index("ix_maintenance_categories_user_sort", table_name="MaintenanceCategories")
    op.drop_index("ix_maintenance_categories_user_name", table_name="MaintenanceCategories")
    op.drop_index("ix_maintenance_categories_user_id", table_name="MaintenanceCategories")
    op.drop_table("MaintenanceCategories")
    op.drop_index("ix_maintenance_areas_is_system", table_name="MaintenanceAreas")
    op.drop_index("ix_maintenance_areas_user_sort", table_name="MaintenanceAreas")
    op.drop_index("ix_maintenance_areas_user_name", table_name="MaintenanceAreas")
    op.drop_index("ix_maintenance_areas_user_id", table_name="MaintenanceAreas")
    op.drop_table("MaintenanceAreas")

