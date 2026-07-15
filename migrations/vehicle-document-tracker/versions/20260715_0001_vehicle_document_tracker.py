"""Create Vehicle Document Tracker tables."""
from collections.abc import Sequence
from alembic import op
import sqlalchemy as sa

revision: str = "20260715_0001_vehicle_document_tracker"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table("VehicleDocumentsVehicles", sa.Column("id", sa.String(36), nullable=False), sa.Column("userId", sa.String(36), nullable=False), sa.Column("vehicleName", sa.String(160), nullable=False), sa.Column("manufacturer", sa.String(120), nullable=True), sa.Column("model", sa.String(120), nullable=True), sa.Column("year", sa.Integer(), nullable=True), sa.Column("registrationNickname", sa.String(120), nullable=True), sa.Column("registrationNumber", sa.String(120), nullable=True), sa.Column("notes", sa.Text(), nullable=True), sa.Column("archived", sa.Boolean(), server_default=sa.text("0"), nullable=False), sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_vehicle_doc_vehicles_user_id", "VehicleDocumentsVehicles", ["userId"])
    op.create_index("ix_vehicle_doc_vehicles_user_archived", "VehicleDocumentsVehicles", ["userId", "archived"])
    op.create_index("ix_vehicle_doc_vehicles_user_name", "VehicleDocumentsVehicles", ["userId", "vehicleName"])
    op.create_index("ix_vehicle_doc_vehicles_user_updated", "VehicleDocumentsVehicles", ["userId", "updatedAt"])
    op.create_table("VehicleDocumentTypes", sa.Column("id", sa.String(36), nullable=False), sa.Column("userId", sa.String(36), server_default="system", nullable=False), sa.Column("name", sa.String(120), nullable=False), sa.Column("sortOrder", sa.Integer(), server_default="0", nullable=False), sa.Column("isSystem", sa.Boolean(), server_default=sa.text("0"), nullable=False), sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("userId", "name", name="uq_vehicle_document_types_user_name"))
    op.create_index("ix_vehicle_doc_types_user_id", "VehicleDocumentTypes", ["userId"])
    op.create_index("ix_vehicle_doc_types_user_order", "VehicleDocumentTypes", ["userId", "sortOrder"])
    op.create_index("ix_vehicle_doc_types_system_order", "VehicleDocumentTypes", ["isSystem", "sortOrder"])
    op.create_table("VehicleDocuments", sa.Column("id", sa.String(36), nullable=False), sa.Column("userId", sa.String(36), nullable=False), sa.Column("vehicleId", sa.String(36), nullable=False), sa.Column("documentTypeId", sa.String(36), nullable=False), sa.Column("documentNumber", sa.String(160), nullable=True), sa.Column("issueDate", sa.Date(), nullable=True), sa.Column("expiryDate", sa.Date(), nullable=True), sa.Column("reminderDate", sa.Date(), nullable=True), sa.Column("issuingAuthority", sa.String(180), nullable=True), sa.Column("status", sa.String(40), server_default="active", nullable=False), sa.Column("notes", sa.Text(), nullable=True), sa.Column("archived", sa.Boolean(), server_default=sa.text("0"), nullable=False), sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.ForeignKeyConstraint(["documentTypeId"], ["VehicleDocumentTypes.id"]), sa.ForeignKeyConstraint(["vehicleId"], ["VehicleDocumentsVehicles.id"]), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_vehicle_docs_user_id", "VehicleDocuments", ["userId"])
    op.create_index("ix_vehicle_docs_vehicle_id", "VehicleDocuments", ["vehicleId"])
    op.create_index("ix_vehicle_docs_type_id", "VehicleDocuments", ["documentTypeId"])
    op.create_index("ix_vehicle_docs_user_vehicle", "VehicleDocuments", ["userId", "vehicleId"])
    op.create_index("ix_vehicle_docs_user_type", "VehicleDocuments", ["userId", "documentTypeId"])
    op.create_index("ix_vehicle_docs_user_status", "VehicleDocuments", ["userId", "status"])
    op.create_index("ix_vehicle_docs_user_archived", "VehicleDocuments", ["userId", "archived"])
    op.create_index("ix_vehicle_docs_user_expiry", "VehicleDocuments", ["userId", "expiryDate"])
    op.create_index("ix_vehicle_docs_user_reminder", "VehicleDocuments", ["userId", "reminderDate"])
    op.create_index("ix_vehicle_docs_user_updated", "VehicleDocuments", ["userId", "updatedAt"])
    op.create_index("ix_vehicle_docs_user_number", "VehicleDocuments", ["userId", "documentNumber"])


def downgrade() -> None:
    for name in ["ix_vehicle_docs_user_number", "ix_vehicle_docs_user_updated", "ix_vehicle_docs_user_reminder", "ix_vehicle_docs_user_expiry", "ix_vehicle_docs_user_archived", "ix_vehicle_docs_user_status", "ix_vehicle_docs_user_type", "ix_vehicle_docs_user_vehicle", "ix_vehicle_docs_type_id", "ix_vehicle_docs_vehicle_id", "ix_vehicle_docs_user_id"]:
        op.drop_index(name, table_name="VehicleDocuments")
    op.drop_table("VehicleDocuments")
    for name in ["ix_vehicle_doc_types_system_order", "ix_vehicle_doc_types_user_order", "ix_vehicle_doc_types_user_id"]:
        op.drop_index(name, table_name="VehicleDocumentTypes")
    op.drop_table("VehicleDocumentTypes")
    for name in ["ix_vehicle_doc_vehicles_user_updated", "ix_vehicle_doc_vehicles_user_name", "ix_vehicle_doc_vehicles_user_archived", "ix_vehicle_doc_vehicles_user_id"]:
        op.drop_index(name, table_name="VehicleDocumentsVehicles")
    op.drop_table("VehicleDocumentsVehicles")
