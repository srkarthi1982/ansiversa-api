"""add snippet generator tables

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


def _create_index_if_missing(index_name: str, table_name: str, columns: list[str]) -> None:
    if not _index_exists(table_name, index_name):
        op.create_index(index_name, table_name, columns, unique=False)


def upgrade() -> None:
    if not _table_exists("SnippetProjects"):
        op.create_table(
            "SnippetProjects",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("language", sa.String(length=120), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="draft", nullable=False),
            sa.Column("goal", sa.Text(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
    _create_index_if_missing(op.f("ix_SnippetProjects_ownerId"), "SnippetProjects", ["ownerId"])
    _create_index_if_missing("SnippetProjects_ownerId_updatedAt_title_idx", "SnippetProjects", ["ownerId", "updatedAt", "title"])
    _create_index_if_missing("SnippetProjects_ownerId_status_updatedAt_idx", "SnippetProjects", ["ownerId", "status", "updatedAt"])

    if not _table_exists("SnippetCategories"):
        op.create_table(
            "SnippetCategories",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("projectId", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=140), nullable=False),
            sa.Column("color", sa.String(length=40), nullable=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["projectId"], ["SnippetProjects.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    _create_index_if_missing(op.f("ix_SnippetCategories_ownerId"), "SnippetCategories", ["ownerId"])
    _create_index_if_missing(op.f("ix_SnippetCategories_projectId"), "SnippetCategories", ["projectId"])
    _create_index_if_missing("SnippetCategories_ownerId_projectId_updatedAt_idx", "SnippetCategories", ["ownerId", "projectId", "updatedAt"])
    _create_index_if_missing("SnippetCategories_projectId_name_idx", "SnippetCategories", ["projectId", "name"])

    if not _table_exists("SnippetLibrary"):
        op.create_table(
            "SnippetLibrary",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("projectId", sa.Integer(), nullable=False),
            sa.Column("categoryId", sa.Integer(), nullable=True),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("language", sa.String(length=120), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="draft", nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("snippetText", sa.Text(), nullable=True),
            sa.Column("usageNotes", sa.Text(), nullable=True),
            sa.Column("tags", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["categoryId"], ["SnippetCategories.id"]),
            sa.ForeignKeyConstraint(["projectId"], ["SnippetProjects.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    _create_index_if_missing(op.f("ix_SnippetLibrary_ownerId"), "SnippetLibrary", ["ownerId"])
    _create_index_if_missing(op.f("ix_SnippetLibrary_projectId"), "SnippetLibrary", ["projectId"])
    _create_index_if_missing(op.f("ix_SnippetLibrary_categoryId"), "SnippetLibrary", ["categoryId"])
    _create_index_if_missing("SnippetLibrary_ownerId_projectId_updatedAt_idx", "SnippetLibrary", ["ownerId", "projectId", "updatedAt"])
    _create_index_if_missing("SnippetLibrary_ownerId_status_updatedAt_idx", "SnippetLibrary", ["ownerId", "status", "updatedAt"])
    _create_index_if_missing("SnippetLibrary_projectId_status_idx", "SnippetLibrary", ["projectId", "status"])
    _create_index_if_missing("SnippetLibrary_categoryId_updatedAt_idx", "SnippetLibrary", ["categoryId", "updatedAt"])

    if not _table_exists("SnippetHistory"):
        op.create_table(
            "SnippetHistory",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("snippetId", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("eventType", sa.String(length=80), nullable=True),
            sa.Column("occurredAt", sa.String(length=40), nullable=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("revisionNotes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["snippetId"], ["SnippetLibrary.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    _create_index_if_missing(op.f("ix_SnippetHistory_ownerId"), "SnippetHistory", ["ownerId"])
    _create_index_if_missing(op.f("ix_SnippetHistory_snippetId"), "SnippetHistory", ["snippetId"])
    _create_index_if_missing("SnippetHistory_ownerId_snippetId_occurredAt_idx", "SnippetHistory", ["ownerId", "snippetId", "occurredAt"])
    _create_index_if_missing("SnippetHistory_ownerId_updatedAt_title_idx", "SnippetHistory", ["ownerId", "updatedAt", "title"])
    _create_index_if_missing("SnippetHistory_snippetId_eventType_idx", "SnippetHistory", ["snippetId", "eventType"])


def downgrade() -> None:
    op.drop_index("SnippetHistory_snippetId_eventType_idx", table_name="SnippetHistory")
    op.drop_index("SnippetHistory_ownerId_updatedAt_title_idx", table_name="SnippetHistory")
    op.drop_index("SnippetHistory_ownerId_snippetId_occurredAt_idx", table_name="SnippetHistory")
    op.drop_index(op.f("ix_SnippetHistory_snippetId"), table_name="SnippetHistory")
    op.drop_index(op.f("ix_SnippetHistory_ownerId"), table_name="SnippetHistory")
    op.drop_table("SnippetHistory")

    op.drop_index("SnippetLibrary_categoryId_updatedAt_idx", table_name="SnippetLibrary")
    op.drop_index("SnippetLibrary_projectId_status_idx", table_name="SnippetLibrary")
    op.drop_index("SnippetLibrary_ownerId_status_updatedAt_idx", table_name="SnippetLibrary")
    op.drop_index("SnippetLibrary_ownerId_projectId_updatedAt_idx", table_name="SnippetLibrary")
    op.drop_index(op.f("ix_SnippetLibrary_categoryId"), table_name="SnippetLibrary")
    op.drop_index(op.f("ix_SnippetLibrary_projectId"), table_name="SnippetLibrary")
    op.drop_index(op.f("ix_SnippetLibrary_ownerId"), table_name="SnippetLibrary")
    op.drop_table("SnippetLibrary")

    op.drop_index("SnippetCategories_projectId_name_idx", table_name="SnippetCategories")
    op.drop_index("SnippetCategories_ownerId_projectId_updatedAt_idx", table_name="SnippetCategories")
    op.drop_index(op.f("ix_SnippetCategories_projectId"), table_name="SnippetCategories")
    op.drop_index(op.f("ix_SnippetCategories_ownerId"), table_name="SnippetCategories")
    op.drop_table("SnippetCategories")

    op.drop_index("SnippetProjects_ownerId_status_updatedAt_idx", table_name="SnippetProjects")
    op.drop_index("SnippetProjects_ownerId_updatedAt_title_idx", table_name="SnippetProjects")
    op.drop_index(op.f("ix_SnippetProjects_ownerId"), table_name="SnippetProjects")
    op.drop_table("SnippetProjects")
