"""add emi loan calculator tables

Revision ID: 20260714_0001_emi_loan_calculator
Revises:
Create Date: 2026-07-14
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260714_0001_emi_loan_calculator"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

INDEXES = (
    ("LoanScenarios_userId_updatedAt_idx", "LoanScenarios", ("userId", "updatedAt")),
    ("LoanScenarios_userId_createdAt_idx", "LoanScenarios", ("userId", "createdAt")),
    ("LoanScenarios_userId_calculatedEmi_idx", "LoanScenarios", ("userId", "calculatedEmi")),
    ("LoanScenarios_userId_totalInterest_idx", "LoanScenarios", ("userId", "totalInterest")),
    ("LoanScenarios_userId_estimatedPayoffDate_idx", "LoanScenarios", ("userId", "estimatedPayoffDate")),
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

    if "LoanScenarios" not in table_names:
        op.create_table(
            "LoanScenarios",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("name", sa.String(length=180), nullable=False),
            sa.Column("loanAmount", sa.Numeric(14, 2), nullable=False),
            sa.Column("annualInterestRate", sa.Numeric(7, 4), nullable=False),
            sa.Column("durationValue", sa.Integer(), nullable=False),
            sa.Column("durationUnit", sa.String(length=20), server_default="years", nullable=False),
            sa.Column("repaymentFrequency", sa.String(length=20), server_default="monthly", nullable=False),
            sa.Column("startDate", sa.String(length=40), nullable=True),
            sa.Column("processingFee", sa.Numeric(14, 2), server_default="0", nullable=False),
            sa.Column("extraPayment", sa.Numeric(14, 2), server_default="0", nullable=False),
            sa.Column("currencyCode", sa.String(length=3), server_default="USD", nullable=False),
            sa.Column("calculatedEmi", sa.Numeric(14, 2), nullable=False),
            sa.Column("totalInterest", sa.Numeric(14, 2), nullable=False),
            sa.Column("totalRepayment", sa.Numeric(14, 2), nullable=False),
            sa.Column("overallLoanCost", sa.Numeric(14, 2), nullable=False),
            sa.Column("estimatedPayoffDate", sa.String(length=40), nullable=True),
            sa.Column("installmentCount", sa.Integer(), nullable=False),
            sa.Column("interestToPrincipalRatio", sa.Numeric(10, 4), nullable=False),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("userId", "name", name="uq_loan_scenarios_owner_name"),
        )
        op.create_index("ix_LoanScenarios_userId", "LoanScenarios", ["userId"])

    for name, table_name, columns in INDEXES:
        _create_index_if_missing(name, table_name, columns)


def downgrade() -> None:
    table_names = _table_names()
    if "LoanScenarios" in table_names:
        op.drop_table("LoanScenarios")
