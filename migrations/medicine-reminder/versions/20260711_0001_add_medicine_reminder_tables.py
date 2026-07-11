"""add medicine reminder tables

Revision ID: 20260711_0001_medicine_reminder
Revises:
Create Date: 2026-07-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260711_0001_medicine_reminder"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


INDEXES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("MedicineReminderMedicines_userId_status_updatedAt_idx", "MedicineReminderMedicines", ("userId", "status", "updatedAt")),
    ("MedicineReminderMedicines_userId_refillReminderDate_idx", "MedicineReminderMedicines", ("userId", "refillReminderDate")),
    ("MedicineReminderSchedules_userId_medicineId_timeOfDay_idx", "MedicineReminderSchedules", ("userId", "medicineId", "timeOfDay")),
    ("MedicineReminderSchedules_userId_status_timeOfDay_idx", "MedicineReminderSchedules", ("userId", "status", "timeOfDay")),
    ("MedicineReminderDoseLogs_userId_medicineId_scheduledFor_idx", "MedicineReminderDoseLogs", ("userId", "medicineId", "scheduledFor")),
    ("MedicineReminderDoseLogs_userId_status_scheduledFor_idx", "MedicineReminderDoseLogs", ("userId", "status", "scheduledFor")),
    ("MedicineReminderNotes_userId_medicineId_noteDate_idx", "MedicineReminderNotes", ("userId", "medicineId", "noteDate")),
    ("MedicineReminderNotes_userId_category_noteDate_idx", "MedicineReminderNotes", ("userId", "category", "noteDate")),
)


def _table_names() -> set[str]:
    return set(sa.inspect(op.get_bind()).get_table_names())


def _index_names(table_name: str) -> set[str]:
    return {index["name"] for index in sa.inspect(op.get_bind()).get_indexes(table_name)}


def _create_index(name: str, table_name: str, columns: tuple[str, ...]) -> None:
    if table_name not in _table_names() or name in _index_names(table_name):
        return
    op.create_index(name, table_name, list(columns), unique=False)


def _drop_index(name: str, table_name: str) -> None:
    if table_name not in _table_names() or name not in _index_names(table_name):
        return
    op.drop_index(name, table_name=table_name)


def upgrade() -> None:
    table_names = _table_names()
    if "MedicineReminderMedicines" not in table_names:
        op.create_table(
            "MedicineReminderMedicines",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("name", sa.String(length=180), nullable=False),
            sa.Column("dosage", sa.String(length=120), nullable=True),
            sa.Column("form", sa.String(length=40), server_default="tablet", nullable=False),
            sa.Column("purpose", sa.String(length=180), nullable=True),
            sa.Column("instructions", sa.Text(), nullable=True),
            sa.Column("prescribingDoctor", sa.String(length=120), nullable=True),
            sa.Column("startDate", sa.String(length=40), nullable=True),
            sa.Column("endDate", sa.String(length=40), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
            sa.Column("refillQuantity", sa.Integer(), nullable=True),
            sa.Column("refillReminderDate", sa.String(length=40), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_MedicineReminderMedicines_userId", "MedicineReminderMedicines", ["userId"])

    table_names = _table_names()
    if "MedicineReminderSchedules" not in table_names:
        op.create_table(
            "MedicineReminderSchedules",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("medicineId", sa.String(length=36), nullable=False),
            sa.Column("label", sa.String(length=120), nullable=False),
            sa.Column("timeOfDay", sa.String(length=20), nullable=False),
            sa.Column("frequency", sa.String(length=40), server_default="daily", nullable=False),
            sa.Column("daysOfWeek", sa.String(length=80), nullable=True),
            sa.Column("doseAmount", sa.String(length=80), nullable=True),
            sa.Column("instructions", sa.Text(), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["medicineId"], ["MedicineReminderMedicines.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_MedicineReminderSchedules_userId", "MedicineReminderSchedules", ["userId"])
        op.create_index("ix_MedicineReminderSchedules_medicineId", "MedicineReminderSchedules", ["medicineId"])

    table_names = _table_names()
    if "MedicineReminderDoseLogs" not in table_names:
        op.create_table(
            "MedicineReminderDoseLogs",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("medicineId", sa.String(length=36), nullable=False),
            sa.Column("scheduleId", sa.String(length=36), nullable=True),
            sa.Column("scheduledFor", sa.String(length=40), nullable=False),
            sa.Column("takenAt", sa.String(length=40), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="taken", nullable=False),
            sa.Column("note", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["medicineId"], ["MedicineReminderMedicines.id"]),
            sa.ForeignKeyConstraint(["scheduleId"], ["MedicineReminderSchedules.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_MedicineReminderDoseLogs_userId", "MedicineReminderDoseLogs", ["userId"])
        op.create_index("ix_MedicineReminderDoseLogs_medicineId", "MedicineReminderDoseLogs", ["medicineId"])
        op.create_index("ix_MedicineReminderDoseLogs_scheduleId", "MedicineReminderDoseLogs", ["scheduleId"])

    table_names = _table_names()
    if "MedicineReminderNotes" not in table_names:
        op.create_table(
            "MedicineReminderNotes",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("medicineId", sa.String(length=36), nullable=False),
            sa.Column("noteDate", sa.String(length=40), nullable=False),
            sa.Column("title", sa.String(length=160), nullable=False),
            sa.Column("body", sa.Text(), nullable=True),
            sa.Column("category", sa.String(length=40), server_default="general", nullable=False),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["medicineId"], ["MedicineReminderMedicines.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_MedicineReminderNotes_userId", "MedicineReminderNotes", ["userId"])
        op.create_index("ix_MedicineReminderNotes_medicineId", "MedicineReminderNotes", ["medicineId"])

    for name, table_name, columns in INDEXES:
        _create_index(name, table_name, columns)


def downgrade() -> None:
    for name, table_name, _columns in reversed(INDEXES):
        _drop_index(name, table_name)

    table_names = _table_names()
    if "MedicineReminderNotes" in table_names:
        op.drop_index("ix_MedicineReminderNotes_medicineId", table_name="MedicineReminderNotes")
        op.drop_index("ix_MedicineReminderNotes_userId", table_name="MedicineReminderNotes")
        op.drop_table("MedicineReminderNotes")
    table_names = _table_names()
    if "MedicineReminderDoseLogs" in table_names:
        op.drop_index("ix_MedicineReminderDoseLogs_scheduleId", table_name="MedicineReminderDoseLogs")
        op.drop_index("ix_MedicineReminderDoseLogs_medicineId", table_name="MedicineReminderDoseLogs")
        op.drop_index("ix_MedicineReminderDoseLogs_userId", table_name="MedicineReminderDoseLogs")
        op.drop_table("MedicineReminderDoseLogs")
    table_names = _table_names()
    if "MedicineReminderSchedules" in table_names:
        op.drop_index("ix_MedicineReminderSchedules_medicineId", table_name="MedicineReminderSchedules")
        op.drop_index("ix_MedicineReminderSchedules_userId", table_name="MedicineReminderSchedules")
        op.drop_table("MedicineReminderSchedules")
    table_names = _table_names()
    if "MedicineReminderMedicines" in table_names:
        op.drop_index("ix_MedicineReminderMedicines_userId", table_name="MedicineReminderMedicines")
        op.drop_table("MedicineReminderMedicines")
