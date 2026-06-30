"""add speech writer tables

Revision ID: 20260630_0001
Revises:
Create Date: 2026-06-30
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260630_0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    return bool(bind.dialect.has_table(bind, table_name))


def _index_exists(table_name: str, index_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    if any(index["name"] == index_name for index in inspector.get_indexes(table_name)):
        return True
    bind = op.get_bind()
    result = bind.execute(
        sa.text(
            "SELECT 1 FROM sqlite_master "
            "WHERE type = 'index' AND name = :index_name AND tbl_name = :table_name"
        ),
        {"index_name": index_name, "table_name": table_name},
    ).first()
    return result is not None


def _drop_index_if_attached_to_table(index_name: str, table_name: str) -> None:
    bind = op.get_bind()
    result = bind.execute(
        sa.text("SELECT tbl_name FROM sqlite_master WHERE type = 'index' AND name = :index_name"),
        {"index_name": index_name},
    ).first()
    if result is not None and result[0] == table_name:
        op.drop_index(index_name, table_name=table_name)


def _table_has_columns(table_name: str, required_columns: set[str]) -> bool:
    inspector = sa.inspect(op.get_bind())
    existing_columns = {column["name"] for column in inspector.get_columns(table_name)}
    return required_columns.issubset(existing_columns)


def _create_index_if_missing(index_name: str, table_name: str, columns: list[str]) -> None:
    if not _index_exists(table_name, index_name):
        op.create_index(index_name, table_name, columns, unique=False)


def upgrade() -> None:
    if not _table_exists("SpeechProjects"):
        op.create_table(
            "SpeechProjects",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("occasion", sa.String(length=120), nullable=True),
            sa.Column("eventDate", sa.String(length=40), nullable=True),
            sa.Column("audience", sa.String(length=180), nullable=True),
            sa.Column("tone", sa.String(length=80), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="draft", nullable=False),
            sa.Column("purpose", sa.Text(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
    _create_index_if_missing(op.f("ix_SpeechProjects_ownerId"), "SpeechProjects", ["ownerId"])
    _create_index_if_missing("SpeechProjects_ownerId_updatedAt_title_idx", "SpeechProjects", ["ownerId", "updatedAt", "title"])
    _create_index_if_missing("SpeechProjects_ownerId_status_eventDate_idx", "SpeechProjects", ["ownerId", "status", "eventDate"])

    if _table_exists("Speeches") and not _table_has_columns(
        "Speeches",
        {"ownerId", "projectId", "status", "speechText"},
    ):
        if _table_exists("SpeechesLegacy_20260630"):
            raise RuntimeError("Legacy Speeches table already exists; manual schema review is required.")
        op.rename_table("Speeches", "SpeechesLegacy_20260630")

    if not _table_exists("Speeches"):
        op.create_table(
            "Speeches",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("projectId", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("speakerName", sa.String(length=140), nullable=True),
            sa.Column("occasion", sa.String(length=120), nullable=True),
            sa.Column("durationMinutes", sa.Integer(), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="draft", nullable=False),
            sa.Column("keyMessage", sa.Text(), nullable=True),
            sa.Column("speechText", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["projectId"], ["SpeechProjects.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    for index_name in [
        op.f("ix_Speeches_ownerId"),
        op.f("ix_Speeches_projectId"),
        "Speeches_ownerId_projectId_updatedAt_idx",
        "Speeches_ownerId_status_updatedAt_idx",
        "Speeches_projectId_status_idx",
    ]:
        _drop_index_if_attached_to_table(index_name, "SpeechesLegacy_20260630")
    _create_index_if_missing(op.f("ix_Speeches_ownerId"), "Speeches", ["ownerId"])
    _create_index_if_missing(op.f("ix_Speeches_projectId"), "Speeches", ["projectId"])
    _create_index_if_missing("Speeches_ownerId_projectId_updatedAt_idx", "Speeches", ["ownerId", "projectId", "updatedAt"])
    _create_index_if_missing("Speeches_ownerId_status_updatedAt_idx", "Speeches", ["ownerId", "status", "updatedAt"])
    _create_index_if_missing("Speeches_projectId_status_idx", "Speeches", ["projectId", "status"])

    if not _table_exists("SpeechTemplates"):
        op.create_table(
            "SpeechTemplates",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("projectId", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("occasion", sa.String(length=120), nullable=True),
            sa.Column("tone", sa.String(length=80), nullable=True),
            sa.Column("templateText", sa.Text(), nullable=True),
            sa.Column("usageNotes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["projectId"], ["SpeechProjects.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    _create_index_if_missing(op.f("ix_SpeechTemplates_ownerId"), "SpeechTemplates", ["ownerId"])
    _create_index_if_missing(op.f("ix_SpeechTemplates_projectId"), "SpeechTemplates", ["projectId"])
    _create_index_if_missing("SpeechTemplates_ownerId_projectId_updatedAt_idx", "SpeechTemplates", ["ownerId", "projectId", "updatedAt"])
    _create_index_if_missing("SpeechTemplates_projectId_occasion_idx", "SpeechTemplates", ["projectId", "occasion"])

    if not _table_exists("SpeechHistory"):
        op.create_table(
            "SpeechHistory",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("speechId", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("eventType", sa.String(length=80), nullable=True),
            sa.Column("occurredAt", sa.String(length=40), nullable=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("revisionNotes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["speechId"], ["Speeches.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    _create_index_if_missing(op.f("ix_SpeechHistory_ownerId"), "SpeechHistory", ["ownerId"])
    _create_index_if_missing(op.f("ix_SpeechHistory_speechId"), "SpeechHistory", ["speechId"])
    _create_index_if_missing("SpeechHistory_ownerId_speechId_occurredAt_idx", "SpeechHistory", ["ownerId", "speechId", "occurredAt"])
    _create_index_if_missing("SpeechHistory_ownerId_updatedAt_title_idx", "SpeechHistory", ["ownerId", "updatedAt", "title"])
    _create_index_if_missing("SpeechHistory_speechId_eventType_idx", "SpeechHistory", ["speechId", "eventType"])


def downgrade() -> None:
    op.drop_index("SpeechHistory_speechId_eventType_idx", table_name="SpeechHistory")
    op.drop_index("SpeechHistory_ownerId_updatedAt_title_idx", table_name="SpeechHistory")
    op.drop_index("SpeechHistory_ownerId_speechId_occurredAt_idx", table_name="SpeechHistory")
    op.drop_index(op.f("ix_SpeechHistory_speechId"), table_name="SpeechHistory")
    op.drop_index(op.f("ix_SpeechHistory_ownerId"), table_name="SpeechHistory")
    op.drop_table("SpeechHistory")

    op.drop_index("SpeechTemplates_projectId_occasion_idx", table_name="SpeechTemplates")
    op.drop_index("SpeechTemplates_ownerId_projectId_updatedAt_idx", table_name="SpeechTemplates")
    op.drop_index(op.f("ix_SpeechTemplates_projectId"), table_name="SpeechTemplates")
    op.drop_index(op.f("ix_SpeechTemplates_ownerId"), table_name="SpeechTemplates")
    op.drop_table("SpeechTemplates")

    op.drop_index("Speeches_projectId_status_idx", table_name="Speeches")
    op.drop_index("Speeches_ownerId_status_updatedAt_idx", table_name="Speeches")
    op.drop_index("Speeches_ownerId_projectId_updatedAt_idx", table_name="Speeches")
    op.drop_index(op.f("ix_Speeches_projectId"), table_name="Speeches")
    op.drop_index(op.f("ix_Speeches_ownerId"), table_name="Speeches")
    op.drop_table("Speeches")

    op.drop_index("SpeechProjects_ownerId_status_eventDate_idx", table_name="SpeechProjects")
    op.drop_index("SpeechProjects_ownerId_updatedAt_title_idx", table_name="SpeechProjects")
    op.drop_index(op.f("ix_SpeechProjects_ownerId"), table_name="SpeechProjects")
    op.drop_table("SpeechProjects")
