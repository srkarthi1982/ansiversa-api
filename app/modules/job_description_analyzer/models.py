from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.job_description_analyzer.db import JobDescriptionAnalyzerBase


class JobDescription(JobDescriptionAnalyzerBase):
    __tablename__ = "JobDescriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    company_name: Mapped[str] = mapped_column("companyName", String(180), nullable=False)
    location: Mapped[str | None] = mapped_column(String(180), nullable=True)
    employment_type: Mapped[str | None] = mapped_column("employmentType", String(80), nullable=True)
    source_url: Mapped[str | None] = mapped_column("sourceUrl", String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="draft", server_default="draft", nullable=False)
    seniority: Mapped[str | None] = mapped_column(String(80), nullable=True)
    description_text: Mapped[str | None] = mapped_column("descriptionText", Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    analyses: Mapped[list["JobAnalysis"]] = relationship(back_populates="job_description", cascade="all, delete-orphan")


class JobAnalysis(JobDescriptionAnalyzerBase):
    __tablename__ = "JobAnalyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    job_description_id: Mapped[int] = mapped_column("jobDescriptionId", Integer, ForeignKey("JobDescriptions.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="draft", server_default="draft", nullable=False)
    match_score: Mapped[int] = mapped_column("matchScore", Integer, default=0, server_default="0", nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    keywords: Mapped[str | None] = mapped_column(Text, nullable=True)
    responsibilities: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommendations: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    job_description: Mapped[JobDescription] = relationship(back_populates="analyses")
    skill_matches: Mapped[list["SkillMatch"]] = relationship(back_populates="analysis", cascade="all, delete-orphan")
    history: Mapped[list["AnalysisHistory"]] = relationship(back_populates="analysis", cascade="all, delete-orphan")


class SkillMatch(JobDescriptionAnalyzerBase):
    __tablename__ = "SkillMatches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    analysis_id: Mapped[int] = mapped_column("analysisId", Integer, ForeignKey("JobAnalyses.id"), index=True, nullable=False)
    skill_name: Mapped[str] = mapped_column("skillName", String(180), nullable=False)
    category: Mapped[str | None] = mapped_column(String(120), nullable=True)
    match_level: Mapped[str] = mapped_column("matchLevel", String(40), default="partial", server_default="partial", nullable=False)
    evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    analysis: Mapped[JobAnalysis] = relationship(back_populates="skill_matches")


class AnalysisHistory(JobDescriptionAnalyzerBase):
    __tablename__ = "AnalysisHistory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    analysis_id: Mapped[int] = mapped_column("analysisId", Integer, ForeignKey("JobAnalyses.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    event_type: Mapped[str | None] = mapped_column("eventType", String(80), nullable=True)
    occurred_at: Mapped[str | None] = mapped_column("occurredAt", String(40), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    next_steps: Mapped[str | None] = mapped_column("nextSteps", Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    analysis: Mapped[JobAnalysis] = relationship(back_populates="history")
