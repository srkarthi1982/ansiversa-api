"""add_invoice_receipt_maker_tables

Revision ID: 20260629_0001
Revises:
Create Date: 2026-06-29

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260629_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


INDEXES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("InvoiceReceiptProjects_ownerId_updatedAt_title_idx", "InvoiceReceiptProjects", ("ownerId", "updatedAt", "title")),
    ("InvoiceReceiptProjects_ownerId_status_updatedAt_idx", "InvoiceReceiptProjects", ("ownerId", "status", "updatedAt")),
    ("InvoiceReceiptDocuments_ownerId_updatedAt_idx", "InvoiceReceiptDocuments", ("ownerId", "updatedAt")),
    ("InvoiceReceiptDocuments_projectId_status_updatedAt_idx", "InvoiceReceiptDocuments", ("projectId", "status", "updatedAt")),
    ("InvoiceReceiptDocuments_projectId_documentType_idx", "InvoiceReceiptDocuments", ("projectId", "documentType")),
    ("InvoiceReceiptItems_ownerId_updatedAt_idx", "InvoiceReceiptItems", ("ownerId", "updatedAt")),
    ("InvoiceReceiptItems_documentId_sortOrder_idx", "InvoiceReceiptItems", ("documentId", "sortOrder")),
    ("InvoiceReceiptHistory_ownerId_createdAt_idx", "InvoiceReceiptHistory", ("ownerId", "createdAt")),
    ("InvoiceReceiptHistory_projectId_createdAt_idx", "InvoiceReceiptHistory", ("projectId", "createdAt")),
    ("InvoiceReceiptHistory_documentId_createdAt_idx", "InvoiceReceiptHistory", ("documentId", "createdAt")),
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

    if "InvoiceReceiptProjects" not in table_names:
        op.create_table(
            "InvoiceReceiptProjects",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("businessName", sa.String(length=180), nullable=False),
            sa.Column("clientName", sa.String(length=180), nullable=True),
            sa.Column("currency", sa.String(length=12), server_default="AED", nullable=False),
            sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_InvoiceReceiptProjects_ownerId", "InvoiceReceiptProjects", ["ownerId"])

    table_names = _table_names()
    if "InvoiceReceiptDocuments" not in table_names:
        op.create_table(
            "InvoiceReceiptDocuments",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("projectId", sa.Integer(), nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("documentType", sa.String(length=40), nullable=False),
            sa.Column("documentNumber", sa.String(length=80), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("clientName", sa.String(length=180), nullable=False),
            sa.Column("issueDate", sa.String(length=40), nullable=True),
            sa.Column("dueDate", sa.String(length=40), nullable=True),
            sa.Column("paidDate", sa.String(length=40), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="draft", nullable=False),
            sa.Column("subtotal", sa.Numeric(12, 2), server_default="0", nullable=False),
            sa.Column("taxTotal", sa.Numeric(12, 2), server_default="0", nullable=False),
            sa.Column("total", sa.Numeric(12, 2), server_default="0", nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("terms", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["projectId"], ["InvoiceReceiptProjects.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_InvoiceReceiptDocuments_ownerId", "InvoiceReceiptDocuments", ["ownerId"])
        op.create_index("ix_InvoiceReceiptDocuments_projectId", "InvoiceReceiptDocuments", ["projectId"])

    table_names = _table_names()
    if "InvoiceReceiptItems" not in table_names:
        op.create_table(
            "InvoiceReceiptItems",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("documentId", sa.Integer(), nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("quantity", sa.Numeric(10, 2), server_default="1", nullable=False),
            sa.Column("unitPrice", sa.Numeric(12, 2), server_default="0", nullable=False),
            sa.Column("taxRate", sa.Numeric(5, 2), server_default="0", nullable=False),
            sa.Column("lineTotal", sa.Numeric(12, 2), server_default="0", nullable=False),
            sa.Column("sortOrder", sa.Integer(), server_default="0", nullable=False),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["documentId"], ["InvoiceReceiptDocuments.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_InvoiceReceiptItems_ownerId", "InvoiceReceiptItems", ["ownerId"])
        op.create_index("ix_InvoiceReceiptItems_documentId", "InvoiceReceiptItems", ["documentId"])

    table_names = _table_names()
    if "InvoiceReceiptHistory" not in table_names:
        op.create_table(
            "InvoiceReceiptHistory",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("projectId", sa.Integer(), nullable=True),
            sa.Column("documentId", sa.Integer(), nullable=True),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("actionType", sa.String(length=60), server_default="updated", nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["projectId"], ["InvoiceReceiptProjects.id"]),
            sa.ForeignKeyConstraint(["documentId"], ["InvoiceReceiptDocuments.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_InvoiceReceiptHistory_ownerId", "InvoiceReceiptHistory", ["ownerId"])
        op.create_index("ix_InvoiceReceiptHistory_projectId", "InvoiceReceiptHistory", ["projectId"])
        op.create_index("ix_InvoiceReceiptHistory_documentId", "InvoiceReceiptHistory", ["documentId"])

    for name, table_name, columns in INDEXES:
        _create_index(name, table_name, columns)


def downgrade() -> None:
    for name, table_name, _columns in reversed(INDEXES):
        _drop_index(name, table_name)

    table_names = _table_names()
    if "InvoiceReceiptHistory" in table_names:
        op.drop_index("ix_InvoiceReceiptHistory_documentId", table_name="InvoiceReceiptHistory")
        op.drop_index("ix_InvoiceReceiptHistory_projectId", table_name="InvoiceReceiptHistory")
        op.drop_index("ix_InvoiceReceiptHistory_ownerId", table_name="InvoiceReceiptHistory")
        op.drop_table("InvoiceReceiptHistory")

    table_names = _table_names()
    if "InvoiceReceiptItems" in table_names:
        op.drop_index("ix_InvoiceReceiptItems_documentId", table_name="InvoiceReceiptItems")
        op.drop_index("ix_InvoiceReceiptItems_ownerId", table_name="InvoiceReceiptItems")
        op.drop_table("InvoiceReceiptItems")

    table_names = _table_names()
    if "InvoiceReceiptDocuments" in table_names:
        op.drop_index("ix_InvoiceReceiptDocuments_projectId", table_name="InvoiceReceiptDocuments")
        op.drop_index("ix_InvoiceReceiptDocuments_ownerId", table_name="InvoiceReceiptDocuments")
        op.drop_table("InvoiceReceiptDocuments")

    table_names = _table_names()
    if "InvoiceReceiptProjects" in table_names:
        op.drop_index("ix_InvoiceReceiptProjects_ownerId", table_name="InvoiceReceiptProjects")
        op.drop_table("InvoiceReceiptProjects")
