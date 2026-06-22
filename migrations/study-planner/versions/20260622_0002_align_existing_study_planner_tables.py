"""align_existing_study_planner_tables

Revision ID: 20260622_0002
Revises: 20260622_0001
Create Date: 2026-06-22

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260622_0002"
down_revision: str | None = "20260622_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _columns(table_name: str) -> set[str]:
    return {
        column["name"]
        for column in sa.inspect(op.get_bind()).get_columns(table_name)
    }


def _add_column_if_missing(
    table_name: str,
    column_name: str,
    column: sa.Column,
) -> None:
    if column_name not in _columns(table_name):
        op.add_column(table_name, column)


def upgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())

    if "StudyPlans" in table_names:
        _add_column_if_missing("StudyPlans", "goal", sa.Column("goal", sa.Text(), nullable=True))
        _add_column_if_missing("StudyPlans", "startDate", sa.Column("startDate", sa.Date(), nullable=True))
        _add_column_if_missing("StudyPlans", "targetDate", sa.Column("targetDate", sa.Date(), nullable=True))
        op.execute(
            """
            UPDATE StudyPlans
            SET goal = COALESCE(goal, description, title),
                subject = COALESCE(subject, 'General study'),
                startDate = COALESCE(startDate, date(createdAt), date('now')),
                targetDate = COALESCE(targetDate, date(createdAt, '+7 days'), date('now', '+7 days'))
            """
        )

    if "StudyPlanTasks" in table_names:
        _add_column_if_missing("StudyPlanTasks", "ownerId", sa.Column("ownerId", sa.String(length=36), nullable=True))
        _add_column_if_missing("StudyPlanTasks", "notes", sa.Column("notes", sa.Text(), nullable=True))
        _add_column_if_missing("StudyPlanTasks", "priority", sa.Column("priority", sa.String(length=20), nullable=True))
        task_columns = _columns("StudyPlanTasks")
        if "ownerId" in task_columns:
            op.execute(
                """
                UPDATE StudyPlanTasks
                SET ownerId = (
                    SELECT StudyPlans.ownerId
                    FROM StudyPlans
                    WHERE StudyPlans.id = StudyPlanTasks.planId
                )
                WHERE ownerId IS NULL
                """
            )
        if "description" in task_columns:
            op.execute("UPDATE StudyPlanTasks SET notes = COALESCE(notes, description)")
        op.execute("UPDATE StudyPlanTasks SET priority = COALESCE(priority, 'medium')")
        if "ix_StudyPlanTasks_ownerId" not in {
            index["name"] for index in sa.inspect(op.get_bind()).get_indexes("StudyPlanTasks")
        }:
            op.create_index("ix_StudyPlanTasks_ownerId", "StudyPlanTasks", ["ownerId"])

    if "StudyLogs" in table_names:
        _add_column_if_missing("StudyLogs", "ownerId", sa.Column("ownerId", sa.String(length=36), nullable=True))
        _add_column_if_missing("StudyLogs", "studyDate", sa.Column("studyDate", sa.Date(), nullable=True))
        _add_column_if_missing("StudyLogs", "minutes", sa.Column("minutes", sa.Integer(), nullable=True))
        _add_column_if_missing("StudyLogs", "focus", sa.Column("focus", sa.String(length=180), nullable=True))
        _add_column_if_missing("StudyLogs", "reflection", sa.Column("reflection", sa.Text(), nullable=True))
        log_columns = _columns("StudyLogs")
        if "ownerId" in log_columns:
            op.execute(
                """
                UPDATE StudyLogs
                SET ownerId = (
                    SELECT StudyPlans.ownerId
                    FROM StudyPlans
                    WHERE StudyPlans.id = StudyLogs.planId
                )
                WHERE ownerId IS NULL
                """
            )
        op.execute(
            """
            UPDATE StudyLogs
            SET studyDate = COALESCE(studyDate, date(startedAt), date(createdAt), date('now')),
                minutes = COALESCE(minutes, durationMinutes, 1),
                focus = COALESCE(focus, notes, 'Study session'),
                reflection = COALESCE(reflection, notes)
            """
        )
        existing_indexes = {
            index["name"] for index in sa.inspect(op.get_bind()).get_indexes("StudyLogs")
        }
        if "ix_StudyLogs_ownerId" not in existing_indexes:
            op.create_index("ix_StudyLogs_ownerId", "StudyLogs", ["ownerId"])
        if "ix_StudyLogs_taskId" not in existing_indexes:
            op.create_index("ix_StudyLogs_taskId", "StudyLogs", ["taskId"])


def downgrade() -> None:
    pass
