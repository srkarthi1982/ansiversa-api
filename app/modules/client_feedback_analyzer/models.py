from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.client_feedback_analyzer.db import ClientFeedbackAnalyzerBase


class ClientProfile(ClientFeedbackAnalyzerBase):
    __tablename__ = "ClientProfiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    company_name: Mapped[str | None] = mapped_column("companyName", String(180), nullable=True)
    contact_name: Mapped[str | None] = mapped_column("contactName", String(180), nullable=True)
    email: Mapped[str | None] = mapped_column(String(180), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(120), nullable=True)
    segment: Mapped[str | None] = mapped_column(String(120), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    feedback: Mapped[list["ClientFeedback"]] = relationship(back_populates="client", cascade="all, delete-orphan")
    insights: Mapped[list["FeedbackInsight"]] = relationship(back_populates="client", cascade="all, delete-orphan")


class ClientFeedback(ClientFeedbackAnalyzerBase):
    __tablename__ = "ClientFeedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    client_id: Mapped[int] = mapped_column("clientId", Integer, ForeignKey("ClientProfiles.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    source: Mapped[str | None] = mapped_column(String(120), nullable=True)
    feedback_text: Mapped[str] = mapped_column("feedbackText", Text, nullable=False)
    sentiment: Mapped[str] = mapped_column(String(40), default="neutral", server_default="neutral", nullable=False)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="new", server_default="new", nullable=False)
    received_at: Mapped[str | None] = mapped_column("receivedAt", String(40), nullable=True)
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    client: Mapped[ClientProfile] = relationship(back_populates="feedback")
    insights: Mapped[list["FeedbackInsight"]] = relationship(back_populates="feedback", cascade="all, delete-orphan")


class FeedbackInsight(ClientFeedbackAnalyzerBase):
    __tablename__ = "FeedbackInsights"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    client_id: Mapped[int] = mapped_column("clientId", Integer, ForeignKey("ClientProfiles.id"), index=True, nullable=False)
    feedback_id: Mapped[int | None] = mapped_column("feedbackId", Integer, ForeignKey("ClientFeedback.id"), index=True, nullable=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    category: Mapped[str | None] = mapped_column(String(120), nullable=True)
    sentiment: Mapped[str] = mapped_column(String(40), default="neutral", server_default="neutral", nullable=False)
    priority: Mapped[str] = mapped_column(String(40), default="medium", server_default="medium", nullable=False)
    recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="open", server_default="open", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    client: Mapped[ClientProfile] = relationship(back_populates="insights")
    feedback: Mapped[ClientFeedback | None] = relationship(back_populates="insights")


class FeedbackReport(ClientFeedbackAnalyzerBase):
    __tablename__ = "FeedbackReports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    scope: Mapped[str | None] = mapped_column(String(120), nullable=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    period_start: Mapped[str | None] = mapped_column("periodStart", String(40), nullable=True)
    period_end: Mapped[str | None] = mapped_column("periodEnd", String(40), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="draft", server_default="draft", nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
