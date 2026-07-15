"""Create Driver Logbook tables."""
from collections.abc import Sequence
from alembic import op
import sqlalchemy as sa

revision: str = "20260715_0001_driver_logbook"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table("DriverVehicles", sa.Column("id", sa.String(36), nullable=False), sa.Column("userId", sa.String(36), nullable=False), sa.Column("vehicleName", sa.String(160), nullable=False), sa.Column("manufacturer", sa.String(120), nullable=True), sa.Column("model", sa.String(120), nullable=True), sa.Column("year", sa.Integer(), nullable=True), sa.Column("registrationNickname", sa.String(120), nullable=True), sa.Column("odometerUnit", sa.String(10), server_default="km", nullable=False), sa.Column("notes", sa.Text(), nullable=True), sa.Column("archived", sa.Boolean(), server_default=sa.text("0"), nullable=False), sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_driver_vehicles_user_id", "DriverVehicles", ["userId"])
    op.create_index("ix_driver_vehicles_user_archived", "DriverVehicles", ["userId", "archived"])
    op.create_index("ix_driver_vehicles_user_name", "DriverVehicles", ["userId", "vehicleName"])
    op.create_index("ix_driver_vehicles_user_updated", "DriverVehicles", ["userId", "updatedAt"])
    op.create_table("DriverTrips", sa.Column("id", sa.String(36), nullable=False), sa.Column("userId", sa.String(36), nullable=False), sa.Column("vehicleId", sa.String(36), nullable=False), sa.Column("tripDate", sa.Date(), nullable=False), sa.Column("startTime", sa.Time(), nullable=True), sa.Column("endTime", sa.Time(), nullable=True), sa.Column("startOdometer", sa.Numeric(12, 1), nullable=True), sa.Column("endOdometer", sa.Numeric(12, 1), nullable=True), sa.Column("distance", sa.Numeric(12, 1), nullable=False), sa.Column("purpose", sa.String(40), server_default="personal", nullable=False), sa.Column("startLocation", sa.String(180), nullable=True), sa.Column("destination", sa.String(180), nullable=True), sa.Column("archived", sa.Boolean(), server_default=sa.text("0"), nullable=False), sa.Column("notes", sa.Text(), nullable=True), sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.ForeignKeyConstraint(["vehicleId"], ["DriverVehicles.id"]), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_driver_trips_user_id", "DriverTrips", ["userId"])
    op.create_index("ix_driver_trips_vehicle_id", "DriverTrips", ["vehicleId"])
    op.create_index("ix_driver_trips_user_vehicle", "DriverTrips", ["userId", "vehicleId"])
    op.create_index("ix_driver_trips_user_trip_date", "DriverTrips", ["userId", "tripDate"])
    op.create_index("ix_driver_trips_user_purpose", "DriverTrips", ["userId", "purpose"])
    op.create_index("ix_driver_trips_user_archived", "DriverTrips", ["userId", "archived"])
    op.create_index("ix_driver_trips_user_created", "DriverTrips", ["userId", "createdAt"])
    op.create_index("ix_driver_trips_user_distance", "DriverTrips", ["userId", "distance"])
    op.create_index("ix_driver_trips_user_start_odometer", "DriverTrips", ["userId", "startOdometer"])
    op.create_index("ix_driver_trips_user_end_odometer", "DriverTrips", ["userId", "endOdometer"])


def downgrade() -> None:
    for name in ["ix_driver_trips_user_end_odometer", "ix_driver_trips_user_start_odometer", "ix_driver_trips_user_distance", "ix_driver_trips_user_created", "ix_driver_trips_user_archived", "ix_driver_trips_user_purpose", "ix_driver_trips_user_trip_date", "ix_driver_trips_user_vehicle", "ix_driver_trips_vehicle_id", "ix_driver_trips_user_id"]:
        op.drop_index(name, table_name="DriverTrips")
    op.drop_table("DriverTrips")
    for name in ["ix_driver_vehicles_user_updated", "ix_driver_vehicles_user_name", "ix_driver_vehicles_user_archived", "ix_driver_vehicles_user_id"]:
        op.drop_index(name, table_name="DriverVehicles")
    op.drop_table("DriverVehicles")
