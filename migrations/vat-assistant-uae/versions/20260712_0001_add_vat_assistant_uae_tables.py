"""add vat assistant uae tables

Revision ID: 20260712_0001_vat_assistant_uae
Revises:
Create Date: 2026-07-12
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260712_0001_vat_assistant_uae"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

INDEXES = (
    ("VATRegistrations_userId_status_type_idx", "VATRegistrations", ("userId", "status", "registrationType")),
    ("VATRegistrations_userId_vatPeriod_idx", "VATRegistrations", ("userId", "vatPeriod")),
    ("VATRegistrations_userId_updatedAt_idx", "VATRegistrations", ("userId", "updatedAt")),
    ("VATReturns_userId_registrationId_status_period_idx", "VATReturns", ("userId", "registrationId", "filingStatus", "vatPeriod")),
    ("VATReturns_userId_dueDate_idx", "VATReturns", ("userId", "filingDueDate")),
    ("VATReturns_userId_updatedAt_idx", "VATReturns", ("userId", "updatedAt")),
    ("VATTransactions_userId_registrationId_type_rate_idx", "VATTransactions", ("userId", "registrationId", "transactionType", "vatRate")),
    ("VATTransactions_userId_returnId_idx", "VATTransactions", ("userId", "returnId")),
    ("VATTransactions_userId_date_idx", "VATTransactions", ("userId", "date")),
    ("VATTransactions_userId_updatedAt_idx", "VATTransactions", ("userId", "updatedAt")),
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

    if "VATRegistrations" not in table_names:
        op.create_table(
            "VATRegistrations",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("businessName", sa.String(length=180), nullable=False),
            sa.Column("trn", sa.String(length=30), nullable=True),
            sa.Column("registrationType", sa.String(length=60), server_default="standard", nullable=False),
            sa.Column("registrationDate", sa.String(length=40), nullable=True),
            sa.Column("vatPeriod", sa.String(length=80), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="draft", nullable=False),
            sa.Column("country", sa.String(length=80), server_default="United Arab Emirates", nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_VATRegistrations_userId", "VATRegistrations", ["userId"])

    if "VATReturns" not in table_names:
        op.create_table(
            "VATReturns",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("registrationId", sa.String(length=36), nullable=False),
            sa.Column("vatPeriod", sa.String(length=80), nullable=False),
            sa.Column("filingDueDate", sa.String(length=40), nullable=True),
            sa.Column("outputVAT", sa.Float(), server_default="0", nullable=False),
            sa.Column("inputVAT", sa.Float(), server_default="0", nullable=False),
            sa.Column("payableVAT", sa.Float(), server_default="0", nullable=False),
            sa.Column("refundAmount", sa.Float(), server_default="0", nullable=False),
            sa.Column("filingStatus", sa.String(length=40), server_default="draft", nullable=False),
            sa.Column("submissionDate", sa.String(length=40), nullable=True),
            sa.Column("currencyCode", sa.String(length=3), server_default="AED", nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["registrationId"], ["VATRegistrations.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_VATReturns_userId", "VATReturns", ["userId"])
        op.create_index("ix_VATReturns_registrationId", "VATReturns", ["registrationId"])

    if "VATTransactions" not in table_names:
        op.create_table(
            "VATTransactions",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("registrationId", sa.String(length=36), nullable=False),
            sa.Column("returnId", sa.String(length=36), nullable=True),
            sa.Column("date", sa.String(length=40), nullable=True),
            sa.Column("invoiceNumber", sa.String(length=120), nullable=True),
            sa.Column("counterparty", sa.String(length=180), nullable=False),
            sa.Column("transactionType", sa.String(length=40), server_default="sale", nullable=False),
            sa.Column("taxableAmount", sa.Float(), server_default="0", nullable=False),
            sa.Column("vatRate", sa.Float(), server_default="5", nullable=False),
            sa.Column("vatAmount", sa.Float(), server_default="0", nullable=False),
            sa.Column("currencyCode", sa.String(length=3), server_default="AED", nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["registrationId"], ["VATRegistrations.id"]),
            sa.ForeignKeyConstraint(["returnId"], ["VATReturns.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_VATTransactions_userId", "VATTransactions", ["userId"])
        op.create_index("ix_VATTransactions_registrationId", "VATTransactions", ["registrationId"])
        op.create_index("ix_VATTransactions_returnId", "VATTransactions", ["returnId"])

    for name, table_name, columns in INDEXES:
        _create_index_if_missing(name, table_name, columns)


def downgrade() -> None:
    table_names = _table_names()
    if "VATTransactions" in table_names:
        op.drop_table("VATTransactions")
    if "VATReturns" in table_names:
        op.drop_table("VATReturns")
    if "VATRegistrations" in table_names:
        op.drop_table("VATRegistrations")
