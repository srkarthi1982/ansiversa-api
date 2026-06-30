"""add_job_tracker_tables

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
    ("JobListings_ownerId_updatedAt_companyName_idx", "JobListings", ("ownerId", "updatedAt", "companyName")),
    ("JobListings_ownerId_status_priority_idx", "JobListings", ("ownerId", "status", "priority")),
    ("JobListings_ownerId_companyName_title_idx", "JobListings", ("ownerId", "companyName", "title")),
    ("JobApplications_ownerId_jobId_updatedAt_idx", "JobApplications", ("ownerId", "jobId", "updatedAt")),
    ("JobApplications_ownerId_status_followUpDate_idx", "JobApplications", ("ownerId", "status", "followUpDate")),
    ("JobApplications_jobId_status_idx", "JobApplications", ("jobId", "status")),
    ("ApplicationInsights_ownerId_applicationId_updatedAt_idx", "ApplicationInsights", ("ownerId", "applicationId", "updatedAt")),
    ("ApplicationInsights_ownerId_priority_status_idx", "ApplicationInsights", ("ownerId", "priority", "status")),
    ("ApplicationInsights_applicationId_status_idx", "ApplicationInsights", ("applicationId", "status")),
    ("ApplicationHistory_ownerId_applicationId_occurredAt_idx", "ApplicationHistory", ("ownerId", "applicationId", "occurredAt")),
    ("ApplicationHistory_ownerId_updatedAt_title_idx", "ApplicationHistory", ("ownerId", "updatedAt", "title")),
    ("ApplicationHistory_applicationId_eventType_idx", "ApplicationHistory", ("applicationId", "eventType")),
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
    if "JobListings" not in table_names:
        op.create_table(
            "JobListings",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("companyName", sa.String(length=180), nullable=False),
            sa.Column("location", sa.String(length=180), nullable=True),
            sa.Column("employmentType", sa.String(length=80), nullable=True),
            sa.Column("sourceUrl", sa.String(length=500), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="tracking", nullable=False),
            sa.Column("priority", sa.String(length=40), server_default="medium", nullable=False),
            sa.Column("salaryRange", sa.String(length=120), nullable=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_JobListings_ownerId", "JobListings", ["ownerId"])

    table_names = _table_names()
    if "JobApplications" not in table_names:
        op.create_table(
            "JobApplications",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("jobId", sa.Integer(), nullable=False),
            sa.Column("roleTitle", sa.String(length=180), nullable=False),
            sa.Column("companyName", sa.String(length=180), nullable=False),
            sa.Column("status", sa.String(length=40), server_default="draft", nullable=False),
            sa.Column("appliedAt", sa.String(length=40), nullable=True),
            sa.Column("followUpDate", sa.String(length=40), nullable=True),
            sa.Column("contactName", sa.String(length=180), nullable=True),
            sa.Column("contactEmail", sa.String(length=180), nullable=True),
            sa.Column("resumeVersion", sa.String(length=120), nullable=True),
            sa.Column("coverLetterVersion", sa.String(length=120), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["jobId"], ["JobListings.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_JobApplications_ownerId", "JobApplications", ["ownerId"])
        op.create_index("ix_JobApplications_jobId", "JobApplications", ["jobId"])

    table_names = _table_names()
    if "ApplicationInsights" not in table_names:
        op.create_table(
            "ApplicationInsights",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("applicationId", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("category", sa.String(length=120), nullable=True),
            sa.Column("priority", sa.String(length=40), server_default="medium", nullable=False),
            sa.Column("status", sa.String(length=40), server_default="open", nullable=False),
            sa.Column("recommendation", sa.Text(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["applicationId"], ["JobApplications.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_ApplicationInsights_ownerId", "ApplicationInsights", ["ownerId"])
        op.create_index("ix_ApplicationInsights_applicationId", "ApplicationInsights", ["applicationId"])

    table_names = _table_names()
    if "ApplicationHistory" not in table_names:
        op.create_table(
            "ApplicationHistory",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("applicationId", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("eventType", sa.String(length=80), nullable=True),
            sa.Column("occurredAt", sa.String(length=40), nullable=True),
            sa.Column("summary", sa.Text(), nullable=True),
            sa.Column("nextSteps", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["applicationId"], ["JobApplications.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_ApplicationHistory_ownerId", "ApplicationHistory", ["ownerId"])
        op.create_index("ix_ApplicationHistory_applicationId", "ApplicationHistory", ["applicationId"])

    for name, table_name, columns in INDEXES:
        _create_index(name, table_name, columns)


def downgrade() -> None:
    for name, table_name, _columns in reversed(INDEXES):
        _drop_index(name, table_name)

    table_names = _table_names()
    if "ApplicationHistory" in table_names:
        op.drop_index("ix_ApplicationHistory_applicationId", table_name="ApplicationHistory")
        op.drop_index("ix_ApplicationHistory_ownerId", table_name="ApplicationHistory")
        op.drop_table("ApplicationHistory")
    table_names = _table_names()
    if "ApplicationInsights" in table_names:
        op.drop_index("ix_ApplicationInsights_applicationId", table_name="ApplicationInsights")
        op.drop_index("ix_ApplicationInsights_ownerId", table_name="ApplicationInsights")
        op.drop_table("ApplicationInsights")
    table_names = _table_names()
    if "JobApplications" in table_names:
        op.drop_index("ix_JobApplications_jobId", table_name="JobApplications")
        op.drop_index("ix_JobApplications_ownerId", table_name="JobApplications")
        op.drop_table("JobApplications")
    table_names = _table_names()
    if "JobListings" in table_names:
        op.drop_index("ix_JobListings_ownerId", table_name="JobListings")
        op.drop_table("JobListings")
