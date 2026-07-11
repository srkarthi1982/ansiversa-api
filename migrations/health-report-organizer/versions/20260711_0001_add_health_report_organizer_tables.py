"""add health report organizer tables

Revision ID: 20260711_0001_health_report_organizer
Revises:
Create Date: 2026-07-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260711_0001_health_report_organizer"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


INDEXES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("HealthReportCategories_userId_status_updatedAt_idx", "HealthReportCategories", ("userId", "status", "updatedAt")),
    ("HealthReportFacilities_userId_status_updatedAt_idx", "HealthReportFacilities", ("userId", "status", "updatedAt")),
    ("HealthReports_userId_reportDate_idx", "HealthReports", ("userId", "reportDate")),
    ("HealthReports_userId_status_reportDate_idx", "HealthReports", ("userId", "status", "reportDate")),
    ("HealthReports_userId_categoryId_reportDate_idx", "HealthReports", ("userId", "categoryId", "reportDate")),
    ("HealthReports_userId_facilityId_reportDate_idx", "HealthReports", ("userId", "facilityId", "reportDate")),
    ("HealthReportAttachments_userId_reportId_updatedAt_idx", "HealthReportAttachments", ("userId", "reportId", "updatedAt")),
    ("HealthReportAttachments_userId_status_updatedAt_idx", "HealthReportAttachments", ("userId", "status", "updatedAt")),
    ("HealthReportNotes_userId_reportId_noteDate_idx", "HealthReportNotes", ("userId", "reportId", "noteDate")),
    ("HealthReportNotes_userId_category_noteDate_idx", "HealthReportNotes", ("userId", "category", "noteDate")),
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
    if "HealthReportCategories" not in table_names:
        op.create_table(
            "HealthReportCategories",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("name", sa.String(length=140), nullable=False),
            sa.Column("color", sa.String(length=40), nullable=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_HealthReportCategories_userId", "HealthReportCategories", ["userId"])

    table_names = _table_names()
    if "HealthReportFacilities" not in table_names:
        op.create_table(
            "HealthReportFacilities",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("name", sa.String(length=180), nullable=False),
            sa.Column("facilityType", sa.String(length=60), server_default="clinic", nullable=False),
            sa.Column("phone", sa.String(length=80), nullable=True),
            sa.Column("website", sa.String(length=240), nullable=True),
            sa.Column("address", sa.Text(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_HealthReportFacilities_userId", "HealthReportFacilities", ["userId"])

    table_names = _table_names()
    if "HealthReports" not in table_names:
        op.create_table(
            "HealthReports",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("categoryId", sa.String(length=36), nullable=True),
            sa.Column("facilityId", sa.String(length=36), nullable=True),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("reportType", sa.String(length=80), server_default="lab", nullable=False),
            sa.Column("reportDate", sa.String(length=40), nullable=False),
            sa.Column("patientName", sa.String(length=140), nullable=True),
            sa.Column("doctorName", sa.String(length=140), nullable=True),
            sa.Column("summary", sa.Text(), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="new", nullable=False),
            sa.Column("priority", sa.String(length=40), server_default="routine", nullable=False),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["categoryId"], ["HealthReportCategories.id"]),
            sa.ForeignKeyConstraint(["facilityId"], ["HealthReportFacilities.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_HealthReports_userId", "HealthReports", ["userId"])
        op.create_index("ix_HealthReports_categoryId", "HealthReports", ["categoryId"])
        op.create_index("ix_HealthReports_facilityId", "HealthReports", ["facilityId"])

    table_names = _table_names()
    if "HealthReportAttachments" not in table_names:
        op.create_table(
            "HealthReportAttachments",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("reportId", sa.String(length=36), nullable=False),
            sa.Column("fileName", sa.String(length=220), nullable=False),
            sa.Column("fileType", sa.String(length=80), nullable=True),
            sa.Column("source", sa.String(length=120), nullable=True),
            sa.Column("referenceUrl", sa.String(length=500), nullable=True),
            sa.Column("storageLocation", sa.String(length=220), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="available", nullable=False),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["reportId"], ["HealthReports.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_HealthReportAttachments_userId", "HealthReportAttachments", ["userId"])
        op.create_index("ix_HealthReportAttachments_reportId", "HealthReportAttachments", ["reportId"])

    table_names = _table_names()
    if "HealthReportNotes" not in table_names:
        op.create_table(
            "HealthReportNotes",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("reportId", sa.String(length=36), nullable=False),
            sa.Column("noteDate", sa.String(length=40), nullable=False),
            sa.Column("title", sa.String(length=160), nullable=False),
            sa.Column("body", sa.Text(), nullable=True),
            sa.Column("category", sa.String(length=40), server_default="general", nullable=False),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["reportId"], ["HealthReports.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_HealthReportNotes_userId", "HealthReportNotes", ["userId"])
        op.create_index("ix_HealthReportNotes_reportId", "HealthReportNotes", ["reportId"])

    for name, table_name, columns in INDEXES:
        _create_index(name, table_name, columns)


def downgrade() -> None:
    for name, table_name, _columns in reversed(INDEXES):
        _drop_index(name, table_name)

    table_names = _table_names()
    if "HealthReportNotes" in table_names:
        op.drop_index("ix_HealthReportNotes_reportId", table_name="HealthReportNotes")
        op.drop_index("ix_HealthReportNotes_userId", table_name="HealthReportNotes")
        op.drop_table("HealthReportNotes")
    table_names = _table_names()
    if "HealthReportAttachments" in table_names:
        op.drop_index("ix_HealthReportAttachments_reportId", table_name="HealthReportAttachments")
        op.drop_index("ix_HealthReportAttachments_userId", table_name="HealthReportAttachments")
        op.drop_table("HealthReportAttachments")
    table_names = _table_names()
    if "HealthReports" in table_names:
        op.drop_index("ix_HealthReports_facilityId", table_name="HealthReports")
        op.drop_index("ix_HealthReports_categoryId", table_name="HealthReports")
        op.drop_index("ix_HealthReports_userId", table_name="HealthReports")
        op.drop_table("HealthReports")
    table_names = _table_names()
    if "HealthReportFacilities" in table_names:
        op.drop_index("ix_HealthReportFacilities_userId", table_name="HealthReportFacilities")
        op.drop_table("HealthReportFacilities")
    table_names = _table_names()
    if "HealthReportCategories" in table_names:
        op.drop_index("ix_HealthReportCategories_userId", table_name="HealthReportCategories")
        op.drop_table("HealthReportCategories")
