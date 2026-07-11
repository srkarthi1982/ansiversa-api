"""add rent a car tables

Revision ID: 20260711_0001_rent_a_car
Revises:
Create Date: 2026-07-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260711_0001_rent_a_car"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


INDEXES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("RentACarSearches_userId_status_pickupAt_idx", "RentACarSearches", ("userId", "status", "pickupAt")),
    ("RentACarSearches_userId_updatedAt_idx", "RentACarSearches", ("userId", "updatedAt")),
    ("RentACarVehicleOptions_userId_searchId_updatedAt_idx", "RentACarVehicleOptions", ("userId", "searchId", "updatedAt")),
    ("RentACarVehicleOptions_userId_availability_updatedAt_idx", "RentACarVehicleOptions", ("userId", "availabilityStatus", "updatedAt")),
    ("RentACarVehicleOptions_userId_provider_updatedAt_idx", "RentACarVehicleOptions", ("userId", "providerName", "updatedAt")),
    ("RentACarVehicleOptions_userId_class_updatedAt_idx", "RentACarVehicleOptions", ("userId", "vehicleClass", "updatedAt")),
    ("RentACarBookings_userId_searchId_bookingDate_idx", "RentACarBookings", ("userId", "searchId", "bookingDate")),
    ("RentACarBookings_userId_status_bookingDate_idx", "RentACarBookings", ("userId", "status", "bookingDate")),
    ("RentACarBookings_userId_cancellationDeadline_idx", "RentACarBookings", ("userId", "cancellationDeadline")),
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
    if "RentACarSearches" not in table_names:
        op.create_table(
            "RentACarSearches",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("pickupLocation", sa.String(length=180), nullable=False),
            sa.Column("dropoffLocation", sa.String(length=180), nullable=False),
            sa.Column("pickupAt", sa.String(length=40), nullable=False),
            sa.Column("returnAt", sa.String(length=40), nullable=False),
            sa.Column("driverAgeGroup", sa.String(length=60), server_default="30-64", nullable=False),
            sa.Column("vehicleType", sa.String(length=80), server_default="any", nullable=False),
            sa.Column("transmission", sa.String(length=40), server_default="any", nullable=False),
            sa.Column("passengers", sa.Integer(), server_default="1", nullable=False),
            sa.Column("luggage", sa.Integer(), server_default="0", nullable=False),
            sa.Column("budget", sa.Float(), nullable=True),
            sa.Column("currencyCode", sa.String(length=3), server_default="USD", nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="planning", nullable=False),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_RentACarSearches_userId", "RentACarSearches", ["userId"])

    table_names = _table_names()
    if "RentACarVehicleOptions" not in table_names:
        op.create_table(
            "RentACarVehicleOptions",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("searchId", sa.String(length=36), nullable=False),
            sa.Column("providerName", sa.String(length=160), nullable=False),
            sa.Column("vehicleName", sa.String(length=180), nullable=False),
            sa.Column("vehicleClass", sa.String(length=80), nullable=False),
            sa.Column("transmission", sa.String(length=40), server_default="automatic", nullable=False),
            sa.Column("fuelPolicy", sa.String(length=160), nullable=True),
            sa.Column("seats", sa.Integer(), server_default="4", nullable=False),
            sa.Column("luggageCapacity", sa.Integer(), server_default="1", nullable=False),
            sa.Column("dailyBaseRate", sa.Float(), server_default="0", nullable=False),
            sa.Column("rentalDays", sa.Integer(), server_default="1", nullable=False),
            sa.Column("taxesAndFees", sa.Float(), server_default="0", nullable=False),
            sa.Column("deposit", sa.Float(), nullable=True),
            sa.Column("addonEstimate", sa.Float(), server_default="0", nullable=False),
            sa.Column("mileagePolicy", sa.String(length=180), nullable=True),
            sa.Column("cancellationTerms", sa.String(length=220), nullable=True),
            sa.Column("pickupMethod", sa.String(length=160), nullable=True),
            sa.Column("referenceUrl", sa.String(length=600), nullable=True),
            sa.Column("lastChecked", sa.String(length=40), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("isPreferred", sa.Boolean(), server_default="0", nullable=False),
            sa.Column("availabilityStatus", sa.String(length=40), server_default="unconfirmed", nullable=False),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["searchId"], ["RentACarSearches.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_RentACarVehicleOptions_userId", "RentACarVehicleOptions", ["userId"])
        op.create_index("ix_RentACarVehicleOptions_searchId", "RentACarVehicleOptions", ["searchId"])

    table_names = _table_names()
    if "RentACarBookings" not in table_names:
        op.create_table(
            "RentACarBookings",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("searchId", sa.String(length=36), nullable=False),
            sa.Column("vehicleOptionId", sa.String(length=36), nullable=True),
            sa.Column("bookingReference", sa.String(length=160), nullable=False),
            sa.Column("providerName", sa.String(length=160), nullable=False),
            sa.Column("pickupInstructions", sa.Text(), nullable=True),
            sa.Column("dropoffInstructions", sa.Text(), nullable=True),
            sa.Column("confirmedTotal", sa.Float(), server_default="0", nullable=False),
            sa.Column("currencyCode", sa.String(length=3), server_default="USD", nullable=False),
            sa.Column("depositAmount", sa.Float(), nullable=True),
            sa.Column("contactInformation", sa.String(length=220), nullable=True),
            sa.Column("bookingDate", sa.String(length=40), nullable=False),
            sa.Column("cancellationDeadline", sa.String(length=40), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="confirmed", nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["searchId"], ["RentACarSearches.id"]),
            sa.ForeignKeyConstraint(["vehicleOptionId"], ["RentACarVehicleOptions.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_RentACarBookings_userId", "RentACarBookings", ["userId"])
        op.create_index("ix_RentACarBookings_searchId", "RentACarBookings", ["searchId"])
        op.create_index("ix_RentACarBookings_vehicleOptionId", "RentACarBookings", ["vehicleOptionId"])

    for name, table_name, columns in INDEXES:
        _create_index(name, table_name, columns)


def downgrade() -> None:
    for name, table_name, _columns in reversed(INDEXES):
        _drop_index(name, table_name)

    table_names = _table_names()
    if "RentACarBookings" in table_names:
        op.drop_index("ix_RentACarBookings_vehicleOptionId", table_name="RentACarBookings")
        op.drop_index("ix_RentACarBookings_searchId", table_name="RentACarBookings")
        op.drop_index("ix_RentACarBookings_userId", table_name="RentACarBookings")
        op.drop_table("RentACarBookings")
    table_names = _table_names()
    if "RentACarVehicleOptions" in table_names:
        op.drop_index("ix_RentACarVehicleOptions_searchId", table_name="RentACarVehicleOptions")
        op.drop_index("ix_RentACarVehicleOptions_userId", table_name="RentACarVehicleOptions")
        op.drop_table("RentACarVehicleOptions")
    table_names = _table_names()
    if "RentACarSearches" in table_names:
        op.drop_index("ix_RentACarSearches_userId", table_name="RentACarSearches")
        op.drop_table("RentACarSearches")
