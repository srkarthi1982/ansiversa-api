from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import ParentBase


class Role(ParentBase):
    __tablename__ = "Roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    key: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    permissions_json: Mapped[str | None] = mapped_column(
        "permissionsJson",
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        "createdAt",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updatedAt",
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    users: Mapped[list["User"]] = relationship(back_populates="role")


class User(ParentBase):
    __tablename__ = "Users"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(
        "passwordHash",
        String(255),
        nullable=False,
    )
    role_id: Mapped[int] = mapped_column(
        "roleId",
        Integer,
        ForeignKey("Roles.id"),
        default=2,
        server_default="2",
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(40),
        default="active",
        server_default="active",
        nullable=False,
    )
    avatar_key: Mapped[str | None] = mapped_column("avatarKey", String(500), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column("avatarUrl", String(1000), nullable=True)
    avatar_updated_at: Mapped[datetime | None] = mapped_column(
        "avatarUpdatedAt",
        DateTime(timezone=True),
        nullable=True,
    )
    stripe_customer_id: Mapped[str | None] = mapped_column(
        "stripeCustomerId",
        String(255),
        nullable=True,
    )
    plan: Mapped[str | None] = mapped_column(String(120), nullable=True)
    plan_status: Mapped[str | None] = mapped_column("planStatus", String(120), nullable=True)
    country_code: Mapped[str | None] = mapped_column("countryCode", String(20), nullable=True)
    region_code: Mapped[str | None] = mapped_column("regionCode", String(120), nullable=True)
    city: Mapped[str | None] = mapped_column(String(255), nullable=True)
    timezone: Mapped[str | None] = mapped_column(String(120), nullable=True)
    location_source: Mapped[str] = mapped_column(
        "locationSource",
        String(120),
        default="unknown",
        server_default="unknown",
        nullable=False,
    )
    location_captured_at: Mapped[datetime | None] = mapped_column(
        "locationCapturedAt",
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        "createdAt",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updatedAt",
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    role: Mapped[Role] = relationship(back_populates="users")


class UserPreference(ParentBase):
    __tablename__ = "UserPreferences"

    user_id: Mapped[str] = mapped_column(
        "userId",
        String(36),
        ForeignKey("Users.id"),
        primary_key=True,
    )
    product_updates: Mapped[bool] = mapped_column(
        "productUpdates",
        Boolean,
        default=False,
        server_default="0",
        nullable=False,
    )
    security_alerts: Mapped[bool] = mapped_column(
        "securityAlerts",
        Boolean,
        default=True,
        server_default="1",
        nullable=False,
    )
    theme: Mapped[str | None] = mapped_column(String(40), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        "updatedAt",
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class PasswordResetToken(ParentBase):
    __tablename__ = "PasswordResetTokens"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        "userId",
        String(36),
        ForeignKey("Users.id"),
        index=True,
        nullable=False,
    )
    token_hash: Mapped[str] = mapped_column(
        "tokenHash",
        String(64),
        unique=True,
        index=True,
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        "expiresAt",
        DateTime(timezone=True),
        nullable=False,
    )
    used_at: Mapped[datetime | None] = mapped_column(
        "usedAt",
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        "createdAt",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
