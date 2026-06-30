"""correct caption templates table shape

Revision ID: 20260630_0002
Revises: 20260630_0001
Create Date: 2026-06-30
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260630_0002"
down_revision: str | Sequence[str] | None = "20260630_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

LEGACY_TABLE = "CaptionTemplatesLegacy_20260630"
TEMPLATE_INDEXES = [
    "ix_CaptionTemplates_ownerId",
    "ix_CaptionTemplates_projectId",
    "CaptionTemplates_ownerId_projectId_updatedAt_idx",
    "CaptionTemplates_projectId_platform_idx",
]


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    return bool(bind.dialect.has_table(bind, table_name))


def _columns(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {column["name"] for column in inspector.get_columns(table_name)}


def _index_exists(table_name: str, index_name: str) -> bool:
    row = op.get_bind().execute(
        sa.text("SELECT 1 FROM sqlite_master WHERE type = 'index' AND tbl_name = :table AND name = :name"),
        {"table": table_name, "name": index_name},
    ).first()
    return row is not None


def _drop_index_if_exists(index_name: str) -> None:
    row = op.get_bind().execute(
        sa.text("SELECT 1 FROM sqlite_master WHERE type = 'index' AND name = :name"),
        {"name": index_name},
    ).first()
    if row is not None:
        op.drop_index(index_name)


def _create_template_table() -> None:
    op.create_table(
        "CaptionTemplates",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ownerId", sa.String(length=36), nullable=False),
        sa.Column("platformId", sa.String(length=120), nullable=True),
        sa.Column("projectId", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("platform", sa.String(length=80), nullable=True),
        sa.Column("tone", sa.String(length=80), nullable=True),
        sa.Column("templateText", sa.Text(), nullable=True),
        sa.Column("usageNotes", sa.Text(), nullable=True),
        sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["projectId"], ["CaptionProjects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def _create_template_indexes() -> None:
    if not _index_exists("CaptionTemplates", "ix_CaptionTemplates_ownerId"):
        op.create_index("ix_CaptionTemplates_ownerId", "CaptionTemplates", ["ownerId"], unique=False)
    if not _index_exists("CaptionTemplates", "ix_CaptionTemplates_projectId"):
        op.create_index("ix_CaptionTemplates_projectId", "CaptionTemplates", ["projectId"], unique=False)
    if not _index_exists("CaptionTemplates", "CaptionTemplates_ownerId_projectId_updatedAt_idx"):
        op.create_index(
            "CaptionTemplates_ownerId_projectId_updatedAt_idx",
            "CaptionTemplates",
            ["ownerId", "projectId", "updatedAt"],
            unique=False,
        )
    if not _index_exists("CaptionTemplates", "CaptionTemplates_projectId_platform_idx"):
        op.create_index("CaptionTemplates_projectId_platform_idx", "CaptionTemplates", ["projectId", "platform"], unique=False)


def upgrade() -> None:
    if _table_exists("CaptionTemplates") and "projectId" not in _columns("CaptionTemplates"):
        for index_name in TEMPLATE_INDEXES:
            _drop_index_if_exists(index_name)
        if not _table_exists(LEGACY_TABLE):
            op.rename_table("CaptionTemplates", LEGACY_TABLE)
        else:
            op.drop_table("CaptionTemplates")

    if not _table_exists("CaptionTemplates"):
        _create_template_table()

    _create_template_indexes()


def downgrade() -> None:
    for index_name in reversed(TEMPLATE_INDEXES):
        _drop_index_if_exists(index_name)
    if _table_exists("CaptionTemplates"):
        op.drop_table("CaptionTemplates")
    if _table_exists(LEGACY_TABLE):
        op.rename_table(LEGACY_TABLE, "CaptionTemplates")
