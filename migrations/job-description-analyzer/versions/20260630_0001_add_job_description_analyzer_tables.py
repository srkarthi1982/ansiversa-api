"""add_job_description_analyzer_tables

Revision ID: 20260630_0001
Revises:
Create Date: 2026-06-30

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260630_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


INDEXES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("JobDescriptions_ownerId_updatedAt_companyName_idx", "JobDescriptions", ("ownerId", "updatedAt", "companyName")),
    ("JobDescriptions_ownerId_status_seniority_idx", "JobDescriptions", ("ownerId", "status", "seniority")),
    ("JobDescriptions_ownerId_companyName_title_idx", "JobDescriptions", ("ownerId", "companyName", "title")),
    ("JobAnalyses_ownerId_jobDescriptionId_updatedAt_idx", "JobAnalyses", ("ownerId", "jobDescriptionId", "updatedAt")),
    ("JobAnalyses_ownerId_status_matchScore_idx", "JobAnalyses", ("ownerId", "status", "matchScore")),
    ("JobAnalyses_jobDescriptionId_status_idx", "JobAnalyses", ("jobDescriptionId", "status")),
    ("SkillMatches_ownerId_analysisId_updatedAt_idx", "SkillMatches", ("ownerId", "analysisId", "updatedAt")),
    ("SkillMatches_ownerId_matchLevel_category_idx", "SkillMatches", ("ownerId", "matchLevel", "category")),
    ("SkillMatches_analysisId_matchLevel_idx", "SkillMatches", ("analysisId", "matchLevel")),
    ("AnalysisHistory_ownerId_analysisId_occurredAt_idx", "AnalysisHistory", ("ownerId", "analysisId", "occurredAt")),
    ("AnalysisHistory_ownerId_updatedAt_title_idx", "AnalysisHistory", ("ownerId", "updatedAt", "title")),
    ("AnalysisHistory_analysisId_eventType_idx", "AnalysisHistory", ("analysisId", "eventType")),
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
    if "JobDescriptions" not in table_names:
        op.create_table(
            "JobDescriptions",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("companyName", sa.String(length=180), nullable=False),
            sa.Column("location", sa.String(length=180), nullable=True),
            sa.Column("employmentType", sa.String(length=80), nullable=True),
            sa.Column("sourceUrl", sa.String(length=500), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="draft", nullable=False),
            sa.Column("seniority", sa.String(length=80), nullable=True),
            sa.Column("descriptionText", sa.Text(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_JobDescriptions_ownerId", "JobDescriptions", ["ownerId"])

    table_names = _table_names()
    if "JobAnalyses" not in table_names:
        op.create_table(
            "JobAnalyses",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("jobDescriptionId", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("status", sa.String(length=40), server_default="draft", nullable=False),
            sa.Column("matchScore", sa.Integer(), server_default="0", nullable=False),
            sa.Column("summary", sa.Text(), nullable=True),
            sa.Column("keywords", sa.Text(), nullable=True),
            sa.Column("responsibilities", sa.Text(), nullable=True),
            sa.Column("recommendations", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["jobDescriptionId"], ["JobDescriptions.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_JobAnalyses_ownerId", "JobAnalyses", ["ownerId"])
        op.create_index("ix_JobAnalyses_jobDescriptionId", "JobAnalyses", ["jobDescriptionId"])

    table_names = _table_names()
    if "SkillMatches" not in table_names:
        op.create_table(
            "SkillMatches",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("analysisId", sa.Integer(), nullable=False),
            sa.Column("skillName", sa.String(length=180), nullable=False),
            sa.Column("category", sa.String(length=120), nullable=True),
            sa.Column("matchLevel", sa.String(length=40), server_default="partial", nullable=False),
            sa.Column("evidence", sa.Text(), nullable=True),
            sa.Column("recommendation", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["analysisId"], ["JobAnalyses.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_SkillMatches_ownerId", "SkillMatches", ["ownerId"])
        op.create_index("ix_SkillMatches_analysisId", "SkillMatches", ["analysisId"])

    table_names = _table_names()
    if "AnalysisHistory" not in table_names:
        op.create_table(
            "AnalysisHistory",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("analysisId", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("eventType", sa.String(length=80), nullable=True),
            sa.Column("occurredAt", sa.String(length=40), nullable=True),
            sa.Column("summary", sa.Text(), nullable=True),
            sa.Column("nextSteps", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["analysisId"], ["JobAnalyses.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_AnalysisHistory_ownerId", "AnalysisHistory", ["ownerId"])
        op.create_index("ix_AnalysisHistory_analysisId", "AnalysisHistory", ["analysisId"])

    for name, table_name, columns in INDEXES:
        _create_index(name, table_name, columns)


def downgrade() -> None:
    for name, table_name, _columns in reversed(INDEXES):
        _drop_index(name, table_name)

    table_names = _table_names()
    if "AnalysisHistory" in table_names:
        op.drop_index("ix_AnalysisHistory_analysisId", table_name="AnalysisHistory")
        op.drop_index("ix_AnalysisHistory_ownerId", table_name="AnalysisHistory")
        op.drop_table("AnalysisHistory")
    table_names = _table_names()
    if "SkillMatches" in table_names:
        op.drop_index("ix_SkillMatches_analysisId", table_name="SkillMatches")
        op.drop_index("ix_SkillMatches_ownerId", table_name="SkillMatches")
        op.drop_table("SkillMatches")
    table_names = _table_names()
    if "JobAnalyses" in table_names:
        op.drop_index("ix_JobAnalyses_jobDescriptionId", table_name="JobAnalyses")
        op.drop_index("ix_JobAnalyses_ownerId", table_name="JobAnalyses")
        op.drop_table("JobAnalyses")
    table_names = _table_names()
    if "JobDescriptions" in table_names:
        op.drop_index("ix_JobDescriptions_ownerId", table_name="JobDescriptions")
        op.drop_table("JobDescriptions")
