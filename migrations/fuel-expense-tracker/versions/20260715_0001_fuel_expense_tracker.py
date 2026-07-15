"""Create Fuel Expense Tracker tables."""
from collections.abc import Sequence
from alembic import op
import sqlalchemy as sa

revision: str = "20260715_0001_fuel_expense_tracker"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table("FuelVehicles", sa.Column("id", sa.String(36), nullable=False), sa.Column("userId", sa.String(36), nullable=False), sa.Column("vehicleName", sa.String(160), nullable=False), sa.Column("manufacturer", sa.String(120), nullable=True), sa.Column("model", sa.String(120), nullable=True), sa.Column("year", sa.Integer(), nullable=True), sa.Column("fuelType", sa.String(80), nullable=True), sa.Column("registrationNickname", sa.String(120), nullable=True), sa.Column("odometerUnit", sa.String(10), server_default="km", nullable=False), sa.Column("notes", sa.Text(), nullable=True), sa.Column("archived", sa.Boolean(), server_default=sa.text("0"), nullable=False), sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_fuel_vehicles_user_id", "FuelVehicles", ["userId"])
    op.create_index("ix_fuel_vehicles_user_archived", "FuelVehicles", ["userId", "archived"])
    op.create_index("ix_fuel_vehicles_user_name", "FuelVehicles", ["userId", "vehicleName"])
    op.create_index("ix_fuel_vehicles_user_updated", "FuelVehicles", ["userId", "updatedAt"])
    op.create_table("FuelEntries", sa.Column("id", sa.String(36), nullable=False), sa.Column("userId", sa.String(36), nullable=False), sa.Column("vehicleId", sa.String(36), nullable=False), sa.Column("purchaseDate", sa.Date(), nullable=False), sa.Column("odometer", sa.Numeric(12, 1), nullable=True), sa.Column("fuelQuantity", sa.Numeric(12, 3), nullable=False), sa.Column("fuelUnit", sa.String(10), server_default="L", nullable=False), sa.Column("totalCost", sa.Numeric(12, 2), nullable=False), sa.Column("currency", sa.String(3), server_default="USD", nullable=False), sa.Column("unitPrice", sa.Numeric(12, 4), nullable=False), sa.Column("stationName", sa.String(180), nullable=True), sa.Column("paymentMethod", sa.String(120), nullable=True), sa.Column("fullTank", sa.Boolean(), server_default=sa.text("0"), nullable=False), sa.Column("notes", sa.Text(), nullable=True), sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.ForeignKeyConstraint(["vehicleId"], ["FuelVehicles.id"]), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_fuel_entries_user_id", "FuelEntries", ["userId"])
    op.create_index("ix_fuel_entries_vehicle_id", "FuelEntries", ["vehicleId"])
    op.create_index("ix_fuel_entries_user_vehicle", "FuelEntries", ["userId", "vehicleId"])
    op.create_index("ix_fuel_entries_user_purchase_date", "FuelEntries", ["userId", "purchaseDate"])
    op.create_index("ix_fuel_entries_user_station", "FuelEntries", ["userId", "stationName"])
    op.create_index("ix_fuel_entries_user_created", "FuelEntries", ["userId", "createdAt"])
    op.create_index("ix_fuel_entries_user_cost", "FuelEntries", ["userId", "totalCost"])
    op.create_index("ix_fuel_entries_user_odometer", "FuelEntries", ["userId", "odometer"])


def downgrade() -> None:
    for name in ["ix_fuel_entries_user_odometer", "ix_fuel_entries_user_cost", "ix_fuel_entries_user_created", "ix_fuel_entries_user_station", "ix_fuel_entries_user_purchase_date", "ix_fuel_entries_user_vehicle", "ix_fuel_entries_vehicle_id", "ix_fuel_entries_user_id"]:
        op.drop_index(name, table_name="FuelEntries")
    op.drop_table("FuelEntries")
    for name in ["ix_fuel_vehicles_user_updated", "ix_fuel_vehicles_user_name", "ix_fuel_vehicles_user_archived", "ix_fuel_vehicles_user_id"]:
        op.drop_index(name, table_name="FuelVehicles")
    op.drop_table("FuelVehicles")
