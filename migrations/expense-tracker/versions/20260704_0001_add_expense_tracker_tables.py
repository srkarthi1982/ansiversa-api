"""add expense tracker tables

Revision ID: 20260704_0001_expense_tracker
Revises:
Create Date: 2026-07-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260704_0001_expense_tracker"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


INDEXES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("ExpenseTrackerExpenses_ownerId_expenseDate_idx", "ExpenseTrackerExpenses", ("ownerId", "expenseDate")),
    ("ExpenseTrackerExpenses_ownerId_categoryId_expenseDate_idx", "ExpenseTrackerExpenses", ("ownerId", "categoryId", "expenseDate")),
    ("ExpenseTrackerExpenses_ownerId_currency_expenseDate_idx", "ExpenseTrackerExpenses", ("ownerId", "currency", "expenseDate")),
    ("ExpenseTrackerExpenses_ownerId_paymentMethod_expenseDate_idx", "ExpenseTrackerExpenses", ("ownerId", "paymentMethod", "expenseDate")),
    ("ExpenseTrackerExpenses_ownerId_updatedAt_title_idx", "ExpenseTrackerExpenses", ("ownerId", "updatedAt", "title")),
    ("ExpenseTrackerCategories_ownerId_name_idx", "ExpenseTrackerCategories", ("ownerId", "name")),
    ("ExpenseTrackerCategories_ownerId_isArchived_name_idx", "ExpenseTrackerCategories", ("ownerId", "isArchived", "name")),
    ("ExpenseTrackerHistory_ownerId_createdAt_idx", "ExpenseTrackerHistory", ("ownerId", "createdAt")),
    ("ExpenseTrackerHistory_ownerId_expenseId_createdAt_idx", "ExpenseTrackerHistory", ("ownerId", "expenseId", "createdAt")),
    ("ExpenseTrackerHistory_ownerId_categoryId_createdAt_idx", "ExpenseTrackerHistory", ("ownerId", "categoryId", "createdAt")),
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
    if "ExpenseTrackerCategories" not in table_names:
        op.create_table(
            "ExpenseTrackerCategories",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("name", sa.String(length=120), nullable=False),
            sa.Column("color", sa.String(length=40), server_default="#2f6f73", nullable=False),
            sa.Column("isArchived", sa.Boolean(), server_default="0", nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_ExpenseTrackerCategories_ownerId", "ExpenseTrackerCategories", ["ownerId"])

    table_names = _table_names()
    if "ExpenseTrackerExpenses" not in table_names:
        op.create_table(
            "ExpenseTrackerExpenses",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("categoryId", sa.Integer(), nullable=True),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("amount", sa.Float(), nullable=False),
            sa.Column("currency", sa.String(length=8), server_default="AED", nullable=False),
            sa.Column("expenseDate", sa.String(length=40), nullable=False),
            sa.Column("paymentMethod", sa.String(length=40), server_default="card", nullable=False),
            sa.Column("merchant", sa.String(length=160), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["categoryId"], ["ExpenseTrackerCategories.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_ExpenseTrackerExpenses_ownerId", "ExpenseTrackerExpenses", ["ownerId"])
        op.create_index("ix_ExpenseTrackerExpenses_categoryId", "ExpenseTrackerExpenses", ["categoryId"])

    table_names = _table_names()
    if "ExpenseTrackerHistory" not in table_names:
        op.create_table(
            "ExpenseTrackerHistory",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("expenseId", sa.Integer(), nullable=True),
            sa.Column("categoryId", sa.Integer(), nullable=True),
            sa.Column("actionType", sa.String(length=40), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=True),
            sa.Column("amount", sa.Float(), nullable=True),
            sa.Column("currency", sa.String(length=8), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["categoryId"], ["ExpenseTrackerCategories.id"]),
            sa.ForeignKeyConstraint(["expenseId"], ["ExpenseTrackerExpenses.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_ExpenseTrackerHistory_ownerId", "ExpenseTrackerHistory", ["ownerId"])
        op.create_index("ix_ExpenseTrackerHistory_expenseId", "ExpenseTrackerHistory", ["expenseId"])
        op.create_index("ix_ExpenseTrackerHistory_categoryId", "ExpenseTrackerHistory", ["categoryId"])

    for name, table_name, columns in INDEXES:
        _create_index(name, table_name, columns)


def downgrade() -> None:
    for name, table_name, _columns in reversed(INDEXES):
        _drop_index(name, table_name)

    table_names = _table_names()
    if "ExpenseTrackerHistory" in table_names:
        op.drop_index("ix_ExpenseTrackerHistory_categoryId", table_name="ExpenseTrackerHistory")
        op.drop_index("ix_ExpenseTrackerHistory_expenseId", table_name="ExpenseTrackerHistory")
        op.drop_index("ix_ExpenseTrackerHistory_ownerId", table_name="ExpenseTrackerHistory")
        op.drop_table("ExpenseTrackerHistory")
    table_names = _table_names()
    if "ExpenseTrackerExpenses" in table_names:
        op.drop_index("ix_ExpenseTrackerExpenses_categoryId", table_name="ExpenseTrackerExpenses")
        op.drop_index("ix_ExpenseTrackerExpenses_ownerId", table_name="ExpenseTrackerExpenses")
        op.drop_table("ExpenseTrackerExpenses")
    table_names = _table_names()
    if "ExpenseTrackerCategories" in table_names:
        op.drop_index("ix_ExpenseTrackerCategories_ownerId", table_name="ExpenseTrackerCategories")
        op.drop_table("ExpenseTrackerCategories")

