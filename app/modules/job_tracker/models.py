from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.job_tracker.db import JobTrackerBase


class JobListing(JobTrackerBase):
    __tablename__ = "JobListings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    company_name: Mapped[str] = mapped_column("companyName", String(180), nullable=False)
    location: Mapped[str | None] = mapped_column(String(180), nullable=True)
    employment_type: Mapped[str | None] = mapped_column("employmentType", String(80), nullable=True)
    source_url: Mapped[str | None] = mapped_column("sourceUrl", String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="tracking", server_default="tracking", nullable=False)
    priority: Mapped[str] = mapped_column(String(40), default="medium", server_default="medium", nullable=False)
    salary_range: Mapped[str | None] = mapped_column("salaryRange", String(120), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    applications: Mapped[list["JobApplication"]] = relationship(back_populates="job", cascade="all, delete-orphan")


class JobApplication(JobTrackerBase):
    __tablename__ = "JobApplications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    job_id: Mapped[int] = mapped_column("jobId", Integer, ForeignKey("JobListings.id"), index=True, nullable=False)
    role_title: Mapped[str] = mapped_column("roleTitle", String(180), nullable=False)
    company_name: Mapped[str] = mapped_column("companyName", String(180), nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="draft", server_default="draft", nullable=False)
    applied_at: Mapped[str | None] = mapped_column("appliedAt", String(40), nullable=True)
    follow_up_date: Mapped[str | None] = mapped_column("followUpDate", String(40), nullable=True)
    contact_name: Mapped[str | None] = mapped_column("contactName", String(180), nullable=True)
    contact_email: Mapped[str | None] = mapped_column("contactEmail", String(180), nullable=True)
    resume_version: Mapped[str | None] = mapped_column("resumeVersion", String(120), nullable=True)
    cover_letter_version: Mapped[str | None] = mapped_column("coverLetterVersion", String(120), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    job: Mapped[JobListing] = relationship(back_populates="applications")
    insights: Mapped[list["ApplicationInsight"]] = relationship(back_populates="application", cascade="all, delete-orphan")
    history: Mapped[list["ApplicationHistory"]] = relationship(back_populates="application", cascade="all, delete-orphan")


class ApplicationInsight(JobTrackerBase):
    __tablename__ = "ApplicationInsights"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    application_id: Mapped[int] = mapped_column("applicationId", Integer, ForeignKey("JobApplications.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    category: Mapped[str | None] = mapped_column(String(120), nullable=True)
    priority: Mapped[str] = mapped_column(String(40), default="medium", server_default="medium", nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="open", server_default="open", nullable=False)
    recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    application: Mapped[JobApplication] = relationship(back_populates="insights")


class ApplicationHistory(JobTrackerBase):
    __tablename__ = "ApplicationHistory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    application_id: Mapped[int] = mapped_column("applicationId", Integer, ForeignKey("JobApplications.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    event_type: Mapped[str | None] = mapped_column("eventType", String(80), nullable=True)
    occurred_at: Mapped[str | None] = mapped_column("occurredAt", String(40), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    next_steps: Mapped[str | None] = mapped_column("nextSteps", Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    application: Mapped[JobApplication] = relationship(back_populates="history")
