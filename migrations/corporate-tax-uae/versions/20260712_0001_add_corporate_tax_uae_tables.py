"""add corporate tax uae tables

Revision ID: 20260712_0001_corporate_tax_uae
Revises:
Create Date: 2026-07-12
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260712_0001_corporate_tax_uae"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

INDEXES = (
    ("CorporateTaxPeriods_userId_status_yearEnd_idx", "CorporateTaxPeriods", ("userId", "status", "financialYearEnd")),
    ("CorporateTaxPeriods_userId_filingDueDate_idx", "CorporateTaxPeriods", ("userId", "filingDueDate")),
    ("CorporateTaxPeriods_userId_updatedAt_idx", "CorporateTaxPeriods", ("userId", "updatedAt")),
    ("CorporateTaxAdjustments_userId_periodId_category_status_idx", "CorporateTaxAdjustments", ("userId", "periodId", "category", "treatmentStatus")),
    ("CorporateTaxAdjustments_userId_updatedAt_idx", "CorporateTaxAdjustments", ("userId", "updatedAt")),
    ("CorporateTaxObligations_userId_periodId_status_dueDate_idx", "CorporateTaxObligations", ("userId", "periodId", "status", "dueDate")),
    ("CorporateTaxObligations_userId_type_priority_idx", "CorporateTaxObligations", ("userId", "type", "priority")),
    ("CorporateTaxObligations_userId_updatedAt_idx", "CorporateTaxObligations", ("userId", "updatedAt")),
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

    if "CorporateTaxPeriods" not in table_names:
        op.create_table(
            "CorporateTaxPeriods",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("name", sa.String(length=180), nullable=False),
            sa.Column("financialYearStart", sa.String(length=40), nullable=True),
            sa.Column("financialYearEnd", sa.String(length=40), nullable=True),
            sa.Column("filingDueDate", sa.String(length=40), nullable=True),
            sa.Column("entityName", sa.String(length=180), nullable=False),
            sa.Column("tradeLicenceNumber", sa.String(length=120), nullable=True),
            sa.Column("taxRegistrationNumber", sa.String(length=120), nullable=True),
            sa.Column("entityType", sa.String(length=80), server_default="mainland_company", nullable=False),
            sa.Column("revenue", sa.Float(), server_default="0", nullable=False),
            sa.Column("accountingProfit", sa.Float(), server_default="0", nullable=False),
            sa.Column("taxableIncomeEstimate", sa.Float(), nullable=True),
            sa.Column("currencyCode", sa.String(length=3), server_default="AED", nullable=False),
            sa.Column("status", sa.String(length=40), server_default="draft", nullable=False),
            sa.Column("taxRatePercent", sa.Float(), server_default="9", nullable=False),
            sa.Column("taxThreshold", sa.Float(), server_default="375000", nullable=False),
            sa.Column("assumptionEffectiveDate", sa.String(length=40), nullable=True),
            sa.Column("assumptionReferenceNote", sa.String(length=500), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_CorporateTaxPeriods_userId", "CorporateTaxPeriods", ["userId"])

    if "CorporateTaxAdjustments" not in table_names:
        op.create_table(
            "CorporateTaxAdjustments",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("periodId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("category", sa.String(length=60), server_default="other", nullable=False),
            sa.Column("direction", sa.String(length=40), server_default="increase_taxable_income", nullable=False),
            sa.Column("amount", sa.Float(), server_default="0", nullable=False),
            sa.Column("currencyCode", sa.String(length=3), server_default="AED", nullable=False),
            sa.Column("reference", sa.String(length=180), nullable=True),
            sa.Column("explanation", sa.Text(), nullable=True),
            sa.Column("supportingDocumentNote", sa.String(length=500), nullable=True),
            sa.Column("treatmentStatus", sa.String(length=40), server_default="draft", nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["periodId"], ["CorporateTaxPeriods.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_CorporateTaxAdjustments_userId", "CorporateTaxAdjustments", ["userId"])
        op.create_index("ix_CorporateTaxAdjustments_periodId", "CorporateTaxAdjustments", ["periodId"])

    if "CorporateTaxObligations" not in table_names:
        op.create_table(
            "CorporateTaxObligations",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("periodId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("type", sa.String(length=60), server_default="other", nullable=False),
            sa.Column("dueDate", sa.String(length=40), nullable=True),
            sa.Column("priority", sa.String(length=20), server_default="medium", nullable=False),
            sa.Column("status", sa.String(length=40), server_default="upcoming", nullable=False),
            sa.Column("responsiblePerson", sa.String(length=140), nullable=True),
            sa.Column("externalReference", sa.String(length=180), nullable=True),
            sa.Column("completionDate", sa.String(length=40), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["periodId"], ["CorporateTaxPeriods.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_CorporateTaxObligations_userId", "CorporateTaxObligations", ["userId"])
        op.create_index("ix_CorporateTaxObligations_periodId", "CorporateTaxObligations", ["periodId"])

    for name, table_name, columns in INDEXES:
        _create_index_if_missing(name, table_name, columns)


def downgrade() -> None:
    table_names = _table_names()
    if "CorporateTaxObligations" in table_names:
        op.drop_table("CorporateTaxObligations")
    if "CorporateTaxAdjustments" in table_names:
        op.drop_table("CorporateTaxAdjustments")
    if "CorporateTaxPeriods" in table_names:
        op.drop_table("CorporateTaxPeriods")
