from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.subscription_manager.db import SubscriptionManagerBase


def _uuid() -> str:
    return str(uuid4())


class SubscriptionCategory(SubscriptionManagerBase):
    __tablename__ = "SubscriptionManagerCategories"
    __table_args__ = (
        UniqueConstraint("userId", "name", name="uq_subscription_manager_categories_owner_name"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    color: Mapped[str | None] = mapped_column(String(40), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    subscriptions: Mapped[list["SubscriptionRecord"]] = relationship(back_populates="category")


class SubscriptionRecord(SubscriptionManagerBase):
    __tablename__ = "SubscriptionManagerSubscriptions"
    __table_args__ = (
        UniqueConstraint("userId", "provider", "name", name="uq_subscription_manager_subscriptions_owner_provider_name"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    category_id: Mapped[str] = mapped_column("categoryId", String(36), ForeignKey("SubscriptionManagerCategories.id"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    provider: Mapped[str] = mapped_column(String(180), nullable=False)
    billing_amount: Mapped[float] = mapped_column("billingAmount", Float, nullable=False)
    currency_code: Mapped[str] = mapped_column("currencyCode", String(3), default="USD", server_default="USD", nullable=False)
    billing_frequency: Mapped[str] = mapped_column("billingFrequency", String(40), default="monthly", server_default="monthly", index=True, nullable=False)
    start_date: Mapped[str | None] = mapped_column("startDate", String(40), nullable=True)
    next_billing_date: Mapped[str] = mapped_column("nextBillingDate", String(40), index=True, nullable=False)
    trial_end_date: Mapped[str | None] = mapped_column("trialEndDate", String(40), nullable=True)
    payment_method: Mapped[str | None] = mapped_column("paymentMethod", String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="active", server_default="active", index=True, nullable=False)
    auto_renew: Mapped[bool] = mapped_column("autoRenew", Boolean, default=True, server_default="1", nullable=False)
    cancellation_notice_days: Mapped[int] = mapped_column("cancellationNoticeDays", Integer, default=0, server_default="0", nullable=False)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    reference: Mapped[str | None] = mapped_column(String(180), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    category: Mapped[SubscriptionCategory] = relationship(back_populates="subscriptions")
    renewals: Mapped[list["SubscriptionRenewal"]] = relationship(back_populates="subscription", cascade="all, delete-orphan")


class SubscriptionRenewal(SubscriptionManagerBase):
    __tablename__ = "SubscriptionManagerRenewals"
    __table_args__ = (
        UniqueConstraint("userId", "subscriptionId", "renewalDate", name="uq_subscription_manager_renewals_owner_subscription_date"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    subscription_id: Mapped[str] = mapped_column("subscriptionId", String(36), ForeignKey("SubscriptionManagerSubscriptions.id"), index=True, nullable=False)
    renewal_date: Mapped[str] = mapped_column("renewalDate", String(40), index=True, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency_code: Mapped[str] = mapped_column("currencyCode", String(3), default="USD", server_default="USD", nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="recorded", server_default="recorded", index=True, nullable=False)
    next_billing_date: Mapped[str | None] = mapped_column("nextBillingDate", String(40), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    subscription: Mapped[SubscriptionRecord] = relationship(back_populates="renewals")
