"""add parking expense tracker tables

Revision ID: 20260712_0001_parking_expense_tracker
Revises:
Create Date: 2026-07-12
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260712_0001_parking_expense_tracker"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

INDEXES = (
    ("ParkingExpenseLocations_userId_type_updatedAt_idx", "ParkingExpenseLocations", ("userId", "parkingType", "updatedAt")),
    ("ParkingExpenseLocations_userId_name_city_idx", "ParkingExpenseLocations", ("userId", "name", "city")),
    ("ParkingExpenseEntries_userId_locationId_date_idx", "ParkingExpenseEntries", ("userId", "locationId", "date")),
    ("ParkingExpenseEntries_userId_paymentMethod_date_idx", "ParkingExpenseEntries", ("userId", "paymentMethod", "date")),
    ("ParkingExpenseEntries_userId_vehicle_date_idx", "ParkingExpenseEntries", ("userId", "vehicle", "date")),
    ("ParkingExpenseEntries_userId_updatedAt_idx", "ParkingExpenseEntries", ("userId", "updatedAt")),
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

    if "ParkingExpenseLocations" not in table_names:
        op.create_table(
            "ParkingExpenseLocations",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("name", sa.String(length=180), nullable=False),
            sa.Column("city", sa.String(length=120), nullable=True),
            sa.Column("area", sa.String(length=120), nullable=True),
            sa.Column("parkingType", sa.String(length=40), server_default="other", nullable=False),
            sa.Column("defaultHourlyRate", sa.Float(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_ParkingExpenseLocations_userId", "ParkingExpenseLocations", ["userId"])

    if "ParkingExpenseEntries" not in table_names:
        op.create_table(
            "ParkingExpenseEntries",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("locationId", sa.String(length=36), nullable=False),
            sa.Column("date", sa.String(length=40), nullable=False),
            sa.Column("startTime", sa.String(length=20), nullable=True),
            sa.Column("endTime", sa.String(length=20), nullable=True),
            sa.Column("durationMinutes", sa.Integer(), server_default="0", nullable=False),
            sa.Column("amount", sa.Float(), server_default="0", nullable=False),
            sa.Column("currencyCode", sa.String(length=3), server_default="USD", nullable=False),
            sa.Column("paymentMethod", sa.String(length=40), server_default="card", nullable=False),
            sa.Column("vehicle", sa.String(length=120), nullable=True),
            sa.Column("purpose", sa.String(length=180), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["locationId"], ["ParkingExpenseLocations.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_ParkingExpenseEntries_userId", "ParkingExpenseEntries", ["userId"])
        op.create_index("ix_ParkingExpenseEntries_locationId", "ParkingExpenseEntries", ["locationId"])

    for name, table_name, columns in INDEXES:
        _create_index_if_missing(name, table_name, columns)


def downgrade() -> None:
    table_names = _table_names()
    if "ParkingExpenseEntries" in table_names:
        op.drop_table("ParkingExpenseEntries")
    if "ParkingExpenseLocations" in table_names:
        op.drop_table("ParkingExpenseLocations")
