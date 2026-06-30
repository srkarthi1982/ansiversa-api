"""add prompt builder tables

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


def _table_has_columns(table_name: str, required_columns: set[str]) -> bool:
    inspector = sa.inspect(op.get_bind())
    existing_columns = {column["name"] for column in inspector.get_columns(table_name)}
    return required_columns.issubset(existing_columns)


def _drop_index_if_attached_to_table(index_name: str, table_name: str) -> None:
    bind = op.get_bind()
    result = bind.execute(
        sa.text("SELECT tbl_name FROM sqlite_master WHERE type = 'index' AND name = :index_name"),
        {"index_name": index_name},
    ).first()
    if result is not None and result[0] == table_name:
        op.drop_index(index_name, table_name=table_name)


def _create_index_if_missing(index_name: str, table_name: str, columns: list[str]) -> None:
    if not _index_exists(table_name, index_name):
        op.create_index(index_name, table_name, columns, unique=False)


def upgrade() -> None:
    if not _table_exists("PromptProjects"):
        op.create_table(
            "PromptProjects",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("category", sa.String(length=120), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="draft", nullable=False),
            sa.Column("goal", sa.Text(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
    _create_index_if_missing(op.f("ix_PromptProjects_ownerId"), "PromptProjects", ["ownerId"])
    _create_index_if_missing("PromptProjects_ownerId_updatedAt_title_idx", "PromptProjects", ["ownerId", "updatedAt", "title"])
    _create_index_if_missing("PromptProjects_ownerId_status_updatedAt_idx", "PromptProjects", ["ownerId", "status", "updatedAt"])

    if not _table_exists("PromptLibrary"):
        op.create_table(
            "PromptLibrary",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("projectId", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("category", sa.String(length=120), nullable=True),
            sa.Column("modelTarget", sa.String(length=120), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="draft", nullable=False),
            sa.Column("promptText", sa.Text(), nullable=True),
            sa.Column("contextText", sa.Text(), nullable=True),
            sa.Column("outputFormat", sa.Text(), nullable=True),
            sa.Column("tags", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["projectId"], ["PromptProjects.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    _create_index_if_missing(op.f("ix_PromptLibrary_ownerId"), "PromptLibrary", ["ownerId"])
    _create_index_if_missing(op.f("ix_PromptLibrary_projectId"), "PromptLibrary", ["projectId"])
    _create_index_if_missing("PromptLibrary_ownerId_projectId_updatedAt_idx", "PromptLibrary", ["ownerId", "projectId", "updatedAt"])
    _create_index_if_missing("PromptLibrary_ownerId_status_updatedAt_idx", "PromptLibrary", ["ownerId", "status", "updatedAt"])
    _create_index_if_missing("PromptLibrary_projectId_status_idx", "PromptLibrary", ["projectId", "status"])

    if _table_exists("PromptTemplates") and not _table_has_columns(
        "PromptTemplates",
        {"ownerId", "projectId", "templateText", "usageNotes"},
    ):
        if _table_exists("PromptTemplatesLegacy_20260630"):
            raise RuntimeError("Legacy PromptTemplates table already exists; manual schema review is required.")
        op.rename_table("PromptTemplates", "PromptTemplatesLegacy_20260630")

    if not _table_exists("PromptTemplates"):
        op.create_table(
            "PromptTemplates",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("projectId", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("category", sa.String(length=120), nullable=True),
            sa.Column("templateText", sa.Text(), nullable=True),
            sa.Column("usageNotes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["projectId"], ["PromptProjects.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    for index_name in [
        op.f("ix_PromptTemplates_ownerId"),
        op.f("ix_PromptTemplates_projectId"),
        "PromptTemplates_ownerId_projectId_updatedAt_idx",
        "PromptTemplates_projectId_category_idx",
    ]:
        _drop_index_if_attached_to_table(index_name, "PromptTemplatesLegacy_20260630")
    _create_index_if_missing(op.f("ix_PromptTemplates_ownerId"), "PromptTemplates", ["ownerId"])
    _create_index_if_missing(op.f("ix_PromptTemplates_projectId"), "PromptTemplates", ["projectId"])
    _create_index_if_missing("PromptTemplates_ownerId_projectId_updatedAt_idx", "PromptTemplates", ["ownerId", "projectId", "updatedAt"])
    _create_index_if_missing("PromptTemplates_projectId_category_idx", "PromptTemplates", ["projectId", "category"])

    if not _table_exists("PromptHistory"):
        op.create_table(
            "PromptHistory",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("promptId", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("eventType", sa.String(length=80), nullable=True),
            sa.Column("occurredAt", sa.String(length=40), nullable=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("revisionNotes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["promptId"], ["PromptLibrary.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    _create_index_if_missing(op.f("ix_PromptHistory_ownerId"), "PromptHistory", ["ownerId"])
    _create_index_if_missing(op.f("ix_PromptHistory_promptId"), "PromptHistory", ["promptId"])
    _create_index_if_missing("PromptHistory_ownerId_promptId_occurredAt_idx", "PromptHistory", ["ownerId", "promptId", "occurredAt"])
    _create_index_if_missing("PromptHistory_ownerId_updatedAt_title_idx", "PromptHistory", ["ownerId", "updatedAt", "title"])
    _create_index_if_missing("PromptHistory_promptId_eventType_idx", "PromptHistory", ["promptId", "eventType"])


def downgrade() -> None:
    op.drop_index("PromptHistory_promptId_eventType_idx", table_name="PromptHistory")
    op.drop_index("PromptHistory_ownerId_updatedAt_title_idx", table_name="PromptHistory")
    op.drop_index("PromptHistory_ownerId_promptId_occurredAt_idx", table_name="PromptHistory")
    op.drop_index(op.f("ix_PromptHistory_promptId"), table_name="PromptHistory")
    op.drop_index(op.f("ix_PromptHistory_ownerId"), table_name="PromptHistory")
    op.drop_table("PromptHistory")

    op.drop_index("PromptTemplates_projectId_category_idx", table_name="PromptTemplates")
    op.drop_index("PromptTemplates_ownerId_projectId_updatedAt_idx", table_name="PromptTemplates")
    op.drop_index(op.f("ix_PromptTemplates_projectId"), table_name="PromptTemplates")
    op.drop_index(op.f("ix_PromptTemplates_ownerId"), table_name="PromptTemplates")
    op.drop_table("PromptTemplates")

    op.drop_index("PromptLibrary_projectId_status_idx", table_name="PromptLibrary")
    op.drop_index("PromptLibrary_ownerId_status_updatedAt_idx", table_name="PromptLibrary")
    op.drop_index("PromptLibrary_ownerId_projectId_updatedAt_idx", table_name="PromptLibrary")
    op.drop_index(op.f("ix_PromptLibrary_projectId"), table_name="PromptLibrary")
    op.drop_index(op.f("ix_PromptLibrary_ownerId"), table_name="PromptLibrary")
    op.drop_table("PromptLibrary")

    op.drop_index("PromptProjects_ownerId_status_updatedAt_idx", table_name="PromptProjects")
    op.drop_index("PromptProjects_ownerId_updatedAt_title_idx", table_name="PromptProjects")
    op.drop_index(op.f("ix_PromptProjects_ownerId"), table_name="PromptProjects")
    op.drop_table("PromptProjects")
