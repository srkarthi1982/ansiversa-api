"""add vehicle maintenance tracker tables

Revision ID: 20260712_0001_vehicle_maintenance_tracker
Revises:
Create Date: 2026-07-12
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260712_0001_vehicle_maintenance_tracker"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

INDEXES = (
    ("VehicleMaintenanceVehicles_userId_status_updatedAt_idx", "VehicleMaintenanceVehicles", ("userId", "status", "updatedAt")),
    ("VehicleMaintenanceVehicles_userId_name_make_idx", "VehicleMaintenanceVehicles", ("userId", "name", "make")),
    ("VehicleMaintenanceRecords_userId_vehicleId_serviceDate_idx", "VehicleMaintenanceRecords", ("userId", "vehicleId", "serviceDate")),
    ("VehicleMaintenanceRecords_userId_category_serviceDate_idx", "VehicleMaintenanceRecords", ("userId", "category", "serviceDate")),
    ("VehicleMaintenanceRecords_userId_updatedAt_idx", "VehicleMaintenanceRecords", ("userId", "updatedAt")),
    ("VehicleMaintenanceReminders_userId_vehicleId_dueDate_idx", "VehicleMaintenanceReminders", ("userId", "vehicleId", "dueDate")),
    ("VehicleMaintenanceReminders_userId_status_dueDate_idx", "VehicleMaintenanceReminders", ("userId", "status", "dueDate")),
    ("VehicleMaintenanceReminders_userId_type_dueDate_idx", "VehicleMaintenanceReminders", ("userId", "reminderType", "dueDate")),
)


def _table_names() -> set[str]:
    return set(sa.inspect(op.get_bind()).get_table_names())


def _index_names(table_name: str) -> set[str]:
    return {index["name"] for index in sa.inspect(op.get_bind()).get_indexes(table_name)}


def _create_index_if_missing(name: str, table_name: str, columns: Sequence[str]) -> None:
    if name not in _index_names(table_name):
        op.create_index(name, table_name, list(columns))


def upgrade() -> None:
    table_names = _table_names()

    if "VehicleMaintenanceVehicles" not in table_names:
        op.create_table(
            "VehicleMaintenanceVehicles",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("name", sa.String(length=180), nullable=False),
            sa.Column("make", sa.String(length=120), nullable=True),
            sa.Column("model", sa.String(length=120), nullable=True),
            sa.Column("year", sa.Integer(), nullable=True),
            sa.Column("plateNumber", sa.String(length=60), nullable=True),
            sa.Column("vin", sa.String(length=80), nullable=True),
            sa.Column("odometer", sa.Integer(), server_default="0", nullable=False),
            sa.Column("fuelType", sa.String(length=40), server_default="gasoline", nullable=False),
            sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_VehicleMaintenanceVehicles_userId", "VehicleMaintenanceVehicles", ["userId"])

    if "VehicleMaintenanceRecords" not in table_names:
        op.create_table(
            "VehicleMaintenanceRecords",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("vehicleId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("serviceDate", sa.String(length=40), nullable=False),
            sa.Column("category", sa.String(length=60), server_default="general", nullable=False),
            sa.Column("odometer", sa.Integer(), server_default="0", nullable=False),
            sa.Column("cost", sa.Float(), server_default="0", nullable=False),
            sa.Column("currencyCode", sa.String(length=3), server_default="USD", nullable=False),
            sa.Column("provider", sa.String(length=160), nullable=True),
            sa.Column("nextDueDate", sa.String(length=40), nullable=True),
            sa.Column("nextDueOdometer", sa.Integer(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["vehicleId"], ["VehicleMaintenanceVehicles.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_VehicleMaintenanceRecords_userId", "VehicleMaintenanceRecords", ["userId"])
        op.create_index("ix_VehicleMaintenanceRecords_vehicleId", "VehicleMaintenanceRecords", ["vehicleId"])

    if "VehicleMaintenanceReminders" not in table_names:
        op.create_table(
            "VehicleMaintenanceReminders",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("vehicleId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("reminderType", sa.String(length=60), server_default="service", nullable=False),
            sa.Column("dueDate", sa.String(length=40), nullable=False),
            sa.Column("dueOdometer", sa.Integer(), nullable=True),
            sa.Column("priority", sa.String(length=40), server_default="normal", nullable=False),
            sa.Column("status", sa.String(length=40), server_default="upcoming", nullable=False),
            sa.Column("completedAt", sa.String(length=40), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["vehicleId"], ["VehicleMaintenanceVehicles.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_VehicleMaintenanceReminders_userId", "VehicleMaintenanceReminders", ["userId"])
        op.create_index("ix_VehicleMaintenanceReminders_vehicleId", "VehicleMaintenanceReminders", ["vehicleId"])

    for name, table_name, columns in INDEXES:
        _create_index_if_missing(name, table_name, columns)


def downgrade() -> None:
    table_names = _table_names()
    if "VehicleMaintenanceReminders" in table_names:
        op.drop_table("VehicleMaintenanceReminders")
    if "VehicleMaintenanceRecords" in table_names:
        op.drop_table("VehicleMaintenanceRecords")
    if "VehicleMaintenanceVehicles" in table_names:
        op.drop_table("VehicleMaintenanceVehicles")
