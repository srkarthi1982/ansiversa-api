"""add creative title generator tables

Revision ID: 20260702_0002
Revises:
Create Date: 2026-07-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260702_0002"
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
    if not _table_exists("TitleProjects"):
        op.create_table(
            "TitleProjects",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("topic", sa.Text(), nullable=False),
            sa.Column("audience", sa.String(length=160), nullable=True),
            sa.Column("language", sa.String(length=80), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="draft", nullable=False),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
    _create_index_if_missing(op.f("ix_TitleProjects_ownerId"), "TitleProjects", ["ownerId"])
    _create_index_if_missing("TitleProjects_ownerId_updatedAt_title_idx", "TitleProjects", ["ownerId", "updatedAt", "title"])
    _create_index_if_missing("TitleProjects_ownerId_status_updatedAt_idx", "TitleProjects", ["ownerId", "status", "updatedAt"])

    if not _table_exists("GeneratedTitles"):
        op.create_table(
            "GeneratedTitles",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("projectId", sa.Integer(), nullable=False),
            sa.Column("generatedTitle", sa.String(length=220), nullable=False),
            sa.Column("category", sa.String(length=80), nullable=False),
            sa.Column("score", sa.Integer(), server_default="82", nullable=False),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["projectId"], ["TitleProjects.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    _create_index_if_missing(op.f("ix_GeneratedTitles_ownerId"), "GeneratedTitles", ["ownerId"])
    _create_index_if_missing(op.f("ix_GeneratedTitles_projectId"), "GeneratedTitles", ["projectId"])
    _create_index_if_missing("GeneratedTitles_ownerId_projectId_createdAt_idx", "GeneratedTitles", ["ownerId", "projectId", "createdAt"])
    _create_index_if_missing("GeneratedTitles_projectId_createdAt_idx", "GeneratedTitles", ["projectId", "createdAt"])
    _create_index_if_missing("GeneratedTitles_ownerId_category_createdAt_idx", "GeneratedTitles", ["ownerId", "category", "createdAt"])

    if not _table_exists("TitleJobs"):
        op.create_table(
            "TitleJobs",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("projectId", sa.Integer(), nullable=False),
            sa.Column("generationType", sa.String(length=40), server_default="blog", nullable=False),
            sa.Column("status", sa.String(length=40), server_default="completed", nullable=False),
            sa.Column("provider", sa.String(length=80), server_default="placeholder", nullable=False),
            sa.Column("startedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("completedAt", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["projectId"], ["TitleProjects.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    _create_index_if_missing(op.f("ix_TitleJobs_ownerId"), "TitleJobs", ["ownerId"])
    _create_index_if_missing(op.f("ix_TitleJobs_projectId"), "TitleJobs", ["projectId"])
    _create_index_if_missing("TitleJobs_ownerId_startedAt_idx", "TitleJobs", ["ownerId", "startedAt"])
    _create_index_if_missing("TitleJobs_projectId_status_startedAt_idx", "TitleJobs", ["projectId", "status", "startedAt"])


def downgrade() -> None:
    op.drop_index("TitleJobs_projectId_status_startedAt_idx", table_name="TitleJobs")
    op.drop_index("TitleJobs_ownerId_startedAt_idx", table_name="TitleJobs")
    op.drop_index(op.f("ix_TitleJobs_projectId"), table_name="TitleJobs")
    op.drop_index(op.f("ix_TitleJobs_ownerId"), table_name="TitleJobs")
    op.drop_table("TitleJobs")

    op.drop_index("GeneratedTitles_ownerId_category_createdAt_idx", table_name="GeneratedTitles")
    op.drop_index("GeneratedTitles_projectId_createdAt_idx", table_name="GeneratedTitles")
    op.drop_index("GeneratedTitles_ownerId_projectId_createdAt_idx", table_name="GeneratedTitles")
    op.drop_index(op.f("ix_GeneratedTitles_projectId"), table_name="GeneratedTitles")
    op.drop_index(op.f("ix_GeneratedTitles_ownerId"), table_name="GeneratedTitles")
    op.drop_table("GeneratedTitles")

    op.drop_index("TitleProjects_ownerId_status_updatedAt_idx", table_name="TitleProjects")
    op.drop_index("TitleProjects_ownerId_updatedAt_title_idx", table_name="TitleProjects")
    op.drop_index(op.f("ix_TitleProjects_ownerId"), table_name="TitleProjects")
    op.drop_table("TitleProjects")
