"""add car pool tables

Revision ID: 20260712_0001_car_pool
Revises:
Create Date: 2026-07-12
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260712_0001_car_pool"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

INDEXES = (
    ("CarPoolRides_userId_status_departureAt_idx", "CarPoolRides", ("userId", "status", "departureAt")),
    ("CarPoolRides_userId_updatedAt_idx", "CarPoolRides", ("userId", "updatedAt")),
    ("CarPoolRides_userId_origin_destination_idx", "CarPoolRides", ("userId", "origin", "destination")),
    ("CarPoolPassengers_userId_rideId_joinedAt_idx", "CarPoolPassengers", ("userId", "rideId", "joinedAt")),
    ("CarPoolPassengers_userId_status_joinedAt_idx", "CarPoolPassengers", ("userId", "status", "joinedAt")),
    ("CarPoolRequests_userId_rideId_requestedAt_idx", "CarPoolRequests", ("userId", "rideId", "requestedAt")),
    ("CarPoolRequests_userId_status_requestedAt_idx", "CarPoolRequests", ("userId", "status", "requestedAt")),
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

    if "CarPoolRides" not in table_names:
        op.create_table(
            "CarPoolRides",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("origin", sa.String(length=180), nullable=False),
            sa.Column("destination", sa.String(length=180), nullable=False),
            sa.Column("departureAt", sa.String(length=40), nullable=False),
            sa.Column("returnAt", sa.String(length=40), nullable=True),
            sa.Column("meetingPoint", sa.String(length=220), nullable=True),
            sa.Column("vehicleLabel", sa.String(length=160), nullable=True),
            sa.Column("driverName", sa.String(length=120), nullable=True),
            sa.Column("seatsOffered", sa.Integer(), server_default="1", nullable=False),
            sa.Column("seatsFilled", sa.Integer(), server_default="0", nullable=False),
            sa.Column("pricePerSeat", sa.Float(), nullable=True),
            sa.Column("currencyCode", sa.String(length=3), server_default="USD", nullable=False),
            sa.Column("recurrence", sa.String(length=40), server_default="one_time", nullable=False),
            sa.Column("status", sa.String(length=40), server_default="open", nullable=False),
            sa.Column("visibility", sa.String(length=40), server_default="private", nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_CarPoolRides_userId", "CarPoolRides", ["userId"])

    if "CarPoolPassengers" not in table_names:
        op.create_table(
            "CarPoolPassengers",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("rideId", sa.String(length=36), nullable=False),
            sa.Column("passengerName", sa.String(length=120), nullable=False),
            sa.Column("seats", sa.Integer(), server_default="1", nullable=False),
            sa.Column("contactNote", sa.String(length=220), nullable=True),
            sa.Column("joinedAt", sa.String(length=40), nullable=False),
            sa.Column("status", sa.String(length=40), server_default="joined", nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["rideId"], ["CarPoolRides.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_CarPoolPassengers_userId", "CarPoolPassengers", ["userId"])
        op.create_index("ix_CarPoolPassengers_rideId", "CarPoolPassengers", ["rideId"])

    if "CarPoolRequests" not in table_names:
        op.create_table(
            "CarPoolRequests",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("rideId", sa.String(length=36), nullable=False),
            sa.Column("requesterName", sa.String(length=120), nullable=False),
            sa.Column("seatsRequested", sa.Integer(), server_default="1", nullable=False),
            sa.Column("pickupNote", sa.String(length=220), nullable=True),
            sa.Column("message", sa.Text(), nullable=True),
            sa.Column("requestedAt", sa.String(length=40), nullable=False),
            sa.Column("status", sa.String(length=40), server_default="pending", nullable=False),
            sa.Column("responseNote", sa.String(length=500), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["rideId"], ["CarPoolRides.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_CarPoolRequests_userId", "CarPoolRequests", ["userId"])
        op.create_index("ix_CarPoolRequests_rideId", "CarPoolRequests", ["rideId"])

    for name, table_name, columns in INDEXES:
        _create_index_if_missing(name, table_name, columns)


def downgrade() -> None:
    table_names = _table_names()
    if "CarPoolRequests" in table_names:
        op.drop_table("CarPoolRequests")
    if "CarPoolPassengers" in table_names:
        op.drop_table("CarPoolPassengers")
    if "CarPoolRides" in table_names:
        op.drop_table("CarPoolRides")
