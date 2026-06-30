"""add_book_summary_generator_tables

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
    ("BookCollections_ownerId_updatedAt_title_idx", "BookCollections", ("ownerId", "updatedAt", "title")),
    ("BookCollections_ownerId_status_category_idx", "BookCollections", ("ownerId", "status", "category")),
    ("BookSummaries_ownerId_bookId_updatedAt_idx", "BookSummaries", ("ownerId", "bookId", "updatedAt")),
    ("BookSummaries_ownerId_status_summaryType_idx", "BookSummaries", ("ownerId", "status", "summaryType")),
    ("BookSummaries_bookId_status_idx", "BookSummaries", ("bookId", "status")),
    ("SummaryNotes_ownerId_summaryId_updatedAt_idx", "SummaryNotes", ("ownerId", "summaryId", "updatedAt")),
    ("SummaryNotes_summaryId_noteType_idx", "SummaryNotes", ("summaryId", "noteType")),
    ("SummaryHistory_ownerId_summaryId_occurredAt_idx", "SummaryHistory", ("ownerId", "summaryId", "occurredAt")),
    ("SummaryHistory_ownerId_updatedAt_title_idx", "SummaryHistory", ("ownerId", "updatedAt", "title")),
    ("SummaryHistory_summaryId_eventType_idx", "SummaryHistory", ("summaryId", "eventType")),
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
    if "BookCollections" not in table_names:
        op.create_table(
            "BookCollections",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("author", sa.String(length=180), nullable=True),
            sa.Column("category", sa.String(length=120), nullable=True),
            sa.Column("sourceType", sa.String(length=40), server_default="manual", nullable=False),
            sa.Column("status", sa.String(length=40), server_default="draft", nullable=False),
            sa.Column("sourceText", sa.Text(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_BookCollections_ownerId", "BookCollections", ["ownerId"])

    table_names = _table_names()
    if "BookSummaries" not in table_names:
        op.create_table(
            "BookSummaries",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("bookId", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("summaryType", sa.String(length=60), server_default="chapter", nullable=False),
            sa.Column("status", sa.String(length=40), server_default="draft", nullable=False),
            sa.Column("summaryText", sa.Text(), nullable=True),
            sa.Column("keyPoints", sa.Text(), nullable=True),
            sa.Column("actionItems", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["bookId"], ["BookCollections.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_BookSummaries_ownerId", "BookSummaries", ["ownerId"])
        op.create_index("ix_BookSummaries_bookId", "BookSummaries", ["bookId"])

    table_names = _table_names()
    if "SummaryNotes" not in table_names:
        op.create_table(
            "SummaryNotes",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("summaryId", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("noteType", sa.String(length=60), server_default="note", nullable=False),
            sa.Column("content", sa.Text(), nullable=True),
            sa.Column("highlight", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["summaryId"], ["BookSummaries.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_SummaryNotes_ownerId", "SummaryNotes", ["ownerId"])
        op.create_index("ix_SummaryNotes_summaryId", "SummaryNotes", ["summaryId"])

    table_names = _table_names()
    if "SummaryHistory" not in table_names:
        op.create_table(
            "SummaryHistory",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("summaryId", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("eventType", sa.String(length=80), nullable=True),
            sa.Column("occurredAt", sa.String(length=40), nullable=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("revisionNotes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["summaryId"], ["BookSummaries.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_SummaryHistory_ownerId", "SummaryHistory", ["ownerId"])
        op.create_index("ix_SummaryHistory_summaryId", "SummaryHistory", ["summaryId"])

    for name, table_name, columns in INDEXES:
        _create_index(name, table_name, columns)


def downgrade() -> None:
    for name, table_name, _columns in reversed(INDEXES):
        _drop_index(name, table_name)

    table_names = _table_names()
    if "SummaryHistory" in table_names:
        op.drop_index("ix_SummaryHistory_summaryId", table_name="SummaryHistory")
        op.drop_index("ix_SummaryHistory_ownerId", table_name="SummaryHistory")
        op.drop_table("SummaryHistory")
    table_names = _table_names()
    if "SummaryNotes" in table_names:
        op.drop_index("ix_SummaryNotes_summaryId", table_name="SummaryNotes")
        op.drop_index("ix_SummaryNotes_ownerId", table_name="SummaryNotes")
        op.drop_table("SummaryNotes")
    table_names = _table_names()
    if "BookSummaries" in table_names:
        op.drop_index("ix_BookSummaries_bookId", table_name="BookSummaries")
        op.drop_index("ix_BookSummaries_ownerId", table_name="BookSummaries")
        op.drop_table("BookSummaries")
    table_names = _table_names()
    if "BookCollections" in table_names:
        op.drop_index("ix_BookCollections_ownerId", table_name="BookCollections")
        op.drop_table("BookCollections")
