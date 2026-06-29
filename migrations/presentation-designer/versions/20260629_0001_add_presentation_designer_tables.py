"""add_presentation_designer_tables

Revision ID: 20260629_0001
Revises:
Create Date: 2026-06-29

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260629_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


INDEXES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("PresentationProjects_ownerId_updatedAt_title_idx", "PresentationProjects", ("ownerId", "updatedAt", "title")),
    ("PresentationProjects_ownerId_status_updatedAt_idx", "PresentationProjects", ("ownerId", "status", "updatedAt")),
    ("PresentationSlides_ownerId_updatedAt_idx", "PresentationSlides", ("ownerId", "updatedAt")),
    ("PresentationSlides_projectId_sortOrder_idx", "PresentationSlides", ("projectId", "sortOrder")),
    ("PresentationSlides_projectId_layout_idx", "PresentationSlides", ("projectId", "layout")),
    ("PresentationAssets_ownerId_updatedAt_idx", "PresentationAssets", ("ownerId", "updatedAt")),
    ("PresentationAssets_projectId_sortOrder_idx", "PresentationAssets", ("projectId", "sortOrder")),
    ("PresentationAssets_projectId_assetType_idx", "PresentationAssets", ("projectId", "assetType")),
    ("PresentationReviewHistory_ownerId_createdAt_idx", "PresentationReviewHistory", ("ownerId", "createdAt")),
    ("PresentationReviewHistory_projectId_createdAt_idx", "PresentationReviewHistory", ("projectId", "createdAt")),
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

    if "PresentationProjects" not in table_names:
        op.create_table(
            "PresentationProjects",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("audience", sa.String(length=180), nullable=True),
            sa.Column("theme", sa.String(length=80), server_default="modern", nullable=False),
            sa.Column("status", sa.String(length=40), server_default="draft", nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_PresentationProjects_ownerId", "PresentationProjects", ["ownerId"])

    table_names = _table_names()
    if "PresentationSlides" not in table_names:
        op.create_table(
            "PresentationSlides",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("projectId", sa.Integer(), nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("layout", sa.String(length=80), server_default="title-body", nullable=False),
            sa.Column("headline", sa.String(length=240), nullable=True),
            sa.Column("body", sa.Text(), nullable=True),
            sa.Column("speakerNotes", sa.Text(), nullable=True),
            sa.Column("sortOrder", sa.Integer(), server_default="0", nullable=False),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["projectId"], ["PresentationProjects.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_PresentationSlides_ownerId", "PresentationSlides", ["ownerId"])
        op.create_index("ix_PresentationSlides_projectId", "PresentationSlides", ["projectId"])

    table_names = _table_names()
    if "PresentationAssets" not in table_names:
        op.create_table(
            "PresentationAssets",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("projectId", sa.Integer(), nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("assetType", sa.String(length=60), server_default="text", nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("source", sa.Text(), nullable=True),
            sa.Column("sortOrder", sa.Integer(), server_default="0", nullable=False),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["projectId"], ["PresentationProjects.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_PresentationAssets_ownerId", "PresentationAssets", ["ownerId"])
        op.create_index("ix_PresentationAssets_projectId", "PresentationAssets", ["projectId"])

    table_names = _table_names()
    if "PresentationReviewHistory" not in table_names:
        op.create_table(
            "PresentationReviewHistory",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("projectId", sa.Integer(), nullable=True),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("actionType", sa.String(length=60), server_default="reviewed", nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["projectId"], ["PresentationProjects.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_PresentationReviewHistory_ownerId", "PresentationReviewHistory", ["ownerId"])
        op.create_index("ix_PresentationReviewHistory_projectId", "PresentationReviewHistory", ["projectId"])

    for name, table_name, columns in INDEXES:
        _create_index(name, table_name, columns)


def downgrade() -> None:
    for name, table_name, _columns in reversed(INDEXES):
        _drop_index(name, table_name)

    table_names = _table_names()
    if "PresentationReviewHistory" in table_names:
        op.drop_index("ix_PresentationReviewHistory_projectId", table_name="PresentationReviewHistory")
        op.drop_index("ix_PresentationReviewHistory_ownerId", table_name="PresentationReviewHistory")
        op.drop_table("PresentationReviewHistory")

    table_names = _table_names()
    if "PresentationAssets" in table_names:
        op.drop_index("ix_PresentationAssets_projectId", table_name="PresentationAssets")
        op.drop_index("ix_PresentationAssets_ownerId", table_name="PresentationAssets")
        op.drop_table("PresentationAssets")

    table_names = _table_names()
    if "PresentationSlides" in table_names:
        op.drop_index("ix_PresentationSlides_projectId", table_name="PresentationSlides")
        op.drop_index("ix_PresentationSlides_ownerId", table_name="PresentationSlides")
        op.drop_table("PresentationSlides")

    table_names = _table_names()
    if "PresentationProjects" in table_names:
        op.drop_index("ix_PresentationProjects_ownerId", table_name="PresentationProjects")
        op.drop_table("PresentationProjects")
