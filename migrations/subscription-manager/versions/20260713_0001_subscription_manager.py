"""add subscription manager tables

Revision ID: 20260713_0001_subscription_manager
Revises:
Create Date: 2026-07-13
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260713_0001_subscription_manager"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

INDEXES = (
    ("SubscriptionManagerCategories_userId_name_idx", "SubscriptionManagerCategories", ("userId", "name")),
    ("SubscriptionManagerCategories_userId_updatedAt_idx", "SubscriptionManagerCategories", ("userId", "updatedAt")),
    ("SubscriptionManagerSubscriptions_userId_status_nextBillingDate_idx", "SubscriptionManagerSubscriptions", ("userId", "status", "nextBillingDate")),
    ("SubscriptionManagerSubscriptions_userId_categoryId_status_idx", "SubscriptionManagerSubscriptions", ("userId", "categoryId", "status")),
    ("SubscriptionManagerSubscriptions_userId_billingFrequency_idx", "SubscriptionManagerSubscriptions", ("userId", "billingFrequency")),
    ("SubscriptionManagerSubscriptions_userId_updatedAt_idx", "SubscriptionManagerSubscriptions", ("userId", "updatedAt")),
    ("SubscriptionManagerRenewals_userId_subscriptionId_renewalDate_idx", "SubscriptionManagerRenewals", ("userId", "subscriptionId", "renewalDate")),
    ("SubscriptionManagerRenewals_userId_status_renewalDate_idx", "SubscriptionManagerRenewals", ("userId", "status", "renewalDate")),
    ("SubscriptionManagerRenewals_userId_updatedAt_idx", "SubscriptionManagerRenewals", ("userId", "updatedAt")),
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

    if "SubscriptionManagerCategories" not in table_names:
        op.create_table(
            "SubscriptionManagerCategories",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("name", sa.String(length=120), nullable=False),
            sa.Column("color", sa.String(length=40), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("userId", "name", name="uq_subscription_manager_categories_owner_name"),
        )
        op.create_index("ix_SubscriptionManagerCategories_userId", "SubscriptionManagerCategories", ["userId"])

    if "SubscriptionManagerSubscriptions" not in table_names:
        op.create_table(
            "SubscriptionManagerSubscriptions",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("categoryId", sa.String(length=36), nullable=False),
            sa.Column("name", sa.String(length=180), nullable=False),
            sa.Column("provider", sa.String(length=180), nullable=False),
            sa.Column("billingAmount", sa.Float(), nullable=False),
            sa.Column("currencyCode", sa.String(length=3), server_default="USD", nullable=False),
            sa.Column("billingFrequency", sa.String(length=40), server_default="monthly", nullable=False),
            sa.Column("startDate", sa.String(length=40), nullable=True),
            sa.Column("nextBillingDate", sa.String(length=40), nullable=False),
            sa.Column("trialEndDate", sa.String(length=40), nullable=True),
            sa.Column("paymentMethod", sa.String(length=120), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
            sa.Column("autoRenew", sa.Boolean(), server_default="1", nullable=False),
            sa.Column("cancellationNoticeDays", sa.Integer(), server_default="0", nullable=False),
            sa.Column("website", sa.String(length=500), nullable=True),
            sa.Column("reference", sa.String(length=180), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["categoryId"], ["SubscriptionManagerCategories.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("userId", "provider", "name", name="uq_subscription_manager_subscriptions_owner_provider_name"),
        )
        op.create_index("ix_SubscriptionManagerSubscriptions_userId", "SubscriptionManagerSubscriptions", ["userId"])
        op.create_index("ix_SubscriptionManagerSubscriptions_categoryId", "SubscriptionManagerSubscriptions", ["categoryId"])
        op.create_index("ix_SubscriptionManagerSubscriptions_billingFrequency", "SubscriptionManagerSubscriptions", ["billingFrequency"])
        op.create_index("ix_SubscriptionManagerSubscriptions_nextBillingDate", "SubscriptionManagerSubscriptions", ["nextBillingDate"])
        op.create_index("ix_SubscriptionManagerSubscriptions_status", "SubscriptionManagerSubscriptions", ["status"])

    if "SubscriptionManagerRenewals" not in table_names:
        op.create_table(
            "SubscriptionManagerRenewals",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("subscriptionId", sa.String(length=36), nullable=False),
            sa.Column("renewalDate", sa.String(length=40), nullable=False),
            sa.Column("amount", sa.Float(), nullable=False),
            sa.Column("currencyCode", sa.String(length=3), server_default="USD", nullable=False),
            sa.Column("status", sa.String(length=40), server_default="recorded", nullable=False),
            sa.Column("nextBillingDate", sa.String(length=40), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["subscriptionId"], ["SubscriptionManagerSubscriptions.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("userId", "subscriptionId", "renewalDate", name="uq_subscription_manager_renewals_owner_subscription_date"),
        )
        op.create_index("ix_SubscriptionManagerRenewals_userId", "SubscriptionManagerRenewals", ["userId"])
        op.create_index("ix_SubscriptionManagerRenewals_subscriptionId", "SubscriptionManagerRenewals", ["subscriptionId"])
        op.create_index("ix_SubscriptionManagerRenewals_renewalDate", "SubscriptionManagerRenewals", ["renewalDate"])
        op.create_index("ix_SubscriptionManagerRenewals_status", "SubscriptionManagerRenewals", ["status"])

    for name, table_name, columns in INDEXES:
        _create_index_if_missing(name, table_name, columns)


def downgrade() -> None:
    table_names = _table_names()
    if "SubscriptionManagerRenewals" in table_names:
        op.drop_table("SubscriptionManagerRenewals")
    if "SubscriptionManagerSubscriptions" in table_names:
        op.drop_table("SubscriptionManagerSubscriptions")
    if "SubscriptionManagerCategories" in table_names:
        op.drop_table("SubscriptionManagerCategories")
