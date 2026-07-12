"""add trip cost calculator tables

Revision ID: 20260712_0001_trip_cost_calculator
Revises:
Create Date: 2026-07-12
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260712_0001_trip_cost_calculator"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

INDEXES = (
    ("TripCostTrips_userId_startDate_updatedAt_idx", "TripCostTrips", ("userId", "startDate", "updatedAt")),
    ("TripCostTrips_userId_destination_idx", "TripCostTrips", ("userId", "destination")),
    ("TripCostExpenses_userId_tripId_date_idx", "TripCostExpenses", ("userId", "tripId", "date")),
    ("TripCostExpenses_userId_category_date_idx", "TripCostExpenses", ("userId", "category", "date")),
    ("TripCostExpenses_userId_updatedAt_idx", "TripCostExpenses", ("userId", "updatedAt")),
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

    if "TripCostTrips" not in table_names:
        op.create_table(
            "TripCostTrips",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("name", sa.String(length=180), nullable=False),
            sa.Column("startLocation", sa.String(length=180), nullable=True),
            sa.Column("destination", sa.String(length=180), nullable=False),
            sa.Column("startDate", sa.String(length=40), nullable=True),
            sa.Column("endDate", sa.String(length=40), nullable=True),
            sa.Column("travelers", sa.Integer(), server_default="1", nullable=False),
            sa.Column("vehicle", sa.String(length=120), nullable=True),
            sa.Column("distance", sa.Float(), server_default="0", nullable=False),
            sa.Column("currencyCode", sa.String(length=3), server_default="USD", nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_TripCostTrips_userId", "TripCostTrips", ["userId"])

    if "TripCostExpenses" not in table_names:
        op.create_table(
            "TripCostExpenses",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("tripId", sa.String(length=36), nullable=False),
            sa.Column("category", sa.String(length=40), server_default="miscellaneous", nullable=False),
            sa.Column("description", sa.String(length=220), nullable=False),
            sa.Column("amount", sa.Float(), server_default="0", nullable=False),
            sa.Column("currencyCode", sa.String(length=3), server_default="USD", nullable=False),
            sa.Column("date", sa.String(length=40), nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["tripId"], ["TripCostTrips.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_TripCostExpenses_userId", "TripCostExpenses", ["userId"])
        op.create_index("ix_TripCostExpenses_tripId", "TripCostExpenses", ["tripId"])

    for name, table_name, columns in INDEXES:
        _create_index_if_missing(name, table_name, columns)


def downgrade() -> None:
    table_names = _table_names()
    if "TripCostExpenses" in table_names:
        op.drop_table("TripCostExpenses")
    if "TripCostTrips" in table_names:
        op.drop_table("TripCostTrips")
