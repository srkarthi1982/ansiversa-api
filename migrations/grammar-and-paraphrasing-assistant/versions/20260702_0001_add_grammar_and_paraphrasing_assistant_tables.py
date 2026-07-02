"""add grammar and paraphrasing assistant tables

Revision ID: 20260702_0001
Revises:
Create Date: 2026-07-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260702_0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    return bool(bind.dialect.has_table(bind, table_name))


def _index_exists(table_name: str, index_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return any(index["name"] == index_name for index in inspector.get_indexes(table_name))


def _create_index_if_missing(index_name: str, table_name: str, columns: list[str]) -> None:
    if not _index_exists(table_name, index_name):
        op.create_index(index_name, table_name, columns, unique=False)


def upgrade() -> None:
    if not _table_exists("GrammarProjects"):
        op.create_table(
            "GrammarProjects",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("originalText", sa.Text(), nullable=False),
            sa.Column("language", sa.String(length=80), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="draft", nullable=False),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
    _create_index_if_missing(op.f("ix_GrammarProjects_ownerId"), "GrammarProjects", ["ownerId"])
    _create_index_if_missing("GrammarProjects_ownerId_updatedAt_title_idx", "GrammarProjects", ["ownerId", "updatedAt", "title"])
    _create_index_if_missing("GrammarProjects_ownerId_status_updatedAt_idx", "GrammarProjects", ["ownerId", "status", "updatedAt"])

    if not _table_exists("GrammarResults"):
        op.create_table(
            "GrammarResults",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("projectId", sa.Integer(), nullable=False),
            sa.Column("correctedText", sa.Text(), nullable=False),
            sa.Column("paraphrasedText", sa.Text(), nullable=False),
            sa.Column("tone", sa.String(length=80), nullable=True),
            sa.Column("grammarScore", sa.Integer(), server_default="82", nullable=False),
            sa.Column("readabilityScore", sa.Integer(), server_default="78", nullable=False),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["projectId"], ["GrammarProjects.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    _create_index_if_missing(op.f("ix_GrammarResults_ownerId"), "GrammarResults", ["ownerId"])
    _create_index_if_missing(op.f("ix_GrammarResults_projectId"), "GrammarResults", ["projectId"])
    _create_index_if_missing("GrammarResults_ownerId_projectId_createdAt_idx", "GrammarResults", ["ownerId", "projectId", "createdAt"])
    _create_index_if_missing("GrammarResults_projectId_createdAt_idx", "GrammarResults", ["projectId", "createdAt"])

    if not _table_exists("GrammarJobs"):
        op.create_table(
            "GrammarJobs",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("projectId", sa.Integer(), nullable=False),
            sa.Column("status", sa.String(length=40), server_default="completed", nullable=False),
            sa.Column("provider", sa.String(length=80), server_default="placeholder", nullable=False),
            sa.Column("action", sa.String(length=40), server_default="improve", nullable=False),
            sa.Column("startedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("completedAt", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["projectId"], ["GrammarProjects.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    _create_index_if_missing(op.f("ix_GrammarJobs_ownerId"), "GrammarJobs", ["ownerId"])
    _create_index_if_missing(op.f("ix_GrammarJobs_projectId"), "GrammarJobs", ["projectId"])
    _create_index_if_missing("GrammarJobs_ownerId_startedAt_idx", "GrammarJobs", ["ownerId", "startedAt"])
    _create_index_if_missing("GrammarJobs_projectId_status_startedAt_idx", "GrammarJobs", ["projectId", "status", "startedAt"])


def downgrade() -> None:
    op.drop_index("GrammarJobs_projectId_status_startedAt_idx", table_name="GrammarJobs")
    op.drop_index("GrammarJobs_ownerId_startedAt_idx", table_name="GrammarJobs")
    op.drop_index(op.f("ix_GrammarJobs_projectId"), table_name="GrammarJobs")
    op.drop_index(op.f("ix_GrammarJobs_ownerId"), table_name="GrammarJobs")
    op.drop_table("GrammarJobs")

    op.drop_index("GrammarResults_projectId_createdAt_idx", table_name="GrammarResults")
    op.drop_index("GrammarResults_ownerId_projectId_createdAt_idx", table_name="GrammarResults")
    op.drop_index(op.f("ix_GrammarResults_projectId"), table_name="GrammarResults")
    op.drop_index(op.f("ix_GrammarResults_ownerId"), table_name="GrammarResults")
    op.drop_table("GrammarResults")

    op.drop_index("GrammarProjects_ownerId_status_updatedAt_idx", table_name="GrammarProjects")
    op.drop_index("GrammarProjects_ownerId_updatedAt_title_idx", table_name="GrammarProjects")
    op.drop_index(op.f("ix_GrammarProjects_ownerId"), table_name="GrammarProjects")
    op.drop_table("GrammarProjects")
