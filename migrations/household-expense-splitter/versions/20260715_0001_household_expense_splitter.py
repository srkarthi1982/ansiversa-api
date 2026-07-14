"""Create Household Expense Splitter tables."""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260715_0001_household_expense_splitter"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "Members",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("userId", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("userId", "name", name="uq_household_members_owner_name"),
    )
    op.create_index("ix_household_members_user_id", "Members", ["userId"], unique=False)
    op.create_index("ix_household_members_user_name", "Members", ["userId", "name"], unique=False)
    op.create_index("ix_household_members_user_active", "Members", ["userId", "active"], unique=False)

    op.create_table(
        "Expenses",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("userId", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("category", sa.String(length=120), nullable=False),
        sa.Column("paidByMemberId", sa.String(length=36), nullable=False),
        sa.Column("splitMethod", sa.String(length=20), nullable=False),
        sa.Column("expenseDate", sa.String(length=40), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("archived", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["paidByMemberId"], ["Members.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_household_expenses_user_id", "Expenses", ["userId"], unique=False)
    op.create_index("ix_household_expenses_user_archived", "Expenses", ["userId", "archived"], unique=False)
    op.create_index("ix_household_expenses_user_category", "Expenses", ["userId", "category"], unique=False)
    op.create_index("ix_household_expenses_user_date", "Expenses", ["userId", "expenseDate"], unique=False)
    op.create_index("ix_household_expenses_user_paid_by", "Expenses", ["userId", "paidByMemberId"], unique=False)
    op.create_index("ix_household_expenses_user_split", "Expenses", ["userId", "splitMethod"], unique=False)
    op.create_index("ix_household_expenses_user_updated", "Expenses", ["userId", "updatedAt"], unique=False)

    op.create_table(
        "ExpenseParticipants",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("expenseId", sa.String(length=36), nullable=False),
        sa.Column("memberId", sa.String(length=36), nullable=False),
        sa.Column("shareAmount", sa.Numeric(12, 2), nullable=False),
        sa.ForeignKeyConstraint(["expenseId"], ["Expenses.id"]),
        sa.ForeignKeyConstraint(["memberId"], ["Members.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("expenseId", "memberId", name="uq_expense_participants_expense_member"),
    )
    op.create_index("ix_household_participants_expense_id", "ExpenseParticipants", ["expenseId"], unique=False)
    op.create_index("ix_household_participants_member_id", "ExpenseParticipants", ["memberId"], unique=False)

    op.create_table(
        "Settlements",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("userId", sa.String(length=36), nullable=False),
        sa.Column("fromMemberId", sa.String(length=36), nullable=False),
        sa.Column("toMemberId", sa.String(length=36), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("settlementDate", sa.String(length=40), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["fromMemberId"], ["Members.id"]),
        sa.ForeignKeyConstraint(["toMemberId"], ["Members.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_household_settlements_user_id", "Settlements", ["userId"], unique=False)
    op.create_index("ix_household_settlements_user_date", "Settlements", ["userId", "settlementDate"], unique=False)
    op.create_index("ix_household_settlements_user_from", "Settlements", ["userId", "fromMemberId"], unique=False)
    op.create_index("ix_household_settlements_user_to", "Settlements", ["userId", "toMemberId"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_household_settlements_user_to", table_name="Settlements")
    op.drop_index("ix_household_settlements_user_from", table_name="Settlements")
    op.drop_index("ix_household_settlements_user_date", table_name="Settlements")
    op.drop_index("ix_household_settlements_user_id", table_name="Settlements")
    op.drop_table("Settlements")
    op.drop_index("ix_household_participants_member_id", table_name="ExpenseParticipants")
    op.drop_index("ix_household_participants_expense_id", table_name="ExpenseParticipants")
    op.drop_table("ExpenseParticipants")
    op.drop_index("ix_household_expenses_user_updated", table_name="Expenses")
    op.drop_index("ix_household_expenses_user_split", table_name="Expenses")
    op.drop_index("ix_household_expenses_user_paid_by", table_name="Expenses")
    op.drop_index("ix_household_expenses_user_date", table_name="Expenses")
    op.drop_index("ix_household_expenses_user_category", table_name="Expenses")
    op.drop_index("ix_household_expenses_user_archived", table_name="Expenses")
    op.drop_index("ix_household_expenses_user_id", table_name="Expenses")
    op.drop_table("Expenses")
    op.drop_index("ix_household_members_user_active", table_name="Members")
    op.drop_index("ix_household_members_user_name", table_name="Members")
    op.drop_index("ix_household_members_user_id", table_name="Members")
    op.drop_table("Members")
