"""add_ai_notes_summarizer_tables

Revision ID: 20260622_0001
Revises:
Create Date: 2026-06-22

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260622_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())

    if "NotesDocuments" not in table_names:
        op.create_table(
            "NotesDocuments",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.Text(), nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("sourceType", sa.String(length=40), server_default="paste", nullable=False),
            sa.Column("sourceMeta", sa.Text(), nullable=True),
            sa.Column("tags", sa.Text(), nullable=True),
            sa.Column(
                "createdAt",
                sa.DateTime(timezone=True),
                server_default=sa.text("(CURRENT_TIMESTAMP)"),
                nullable=False,
            ),
            sa.Column(
                "updatedAt",
                sa.DateTime(timezone=True),
                server_default=sa.text("(CURRENT_TIMESTAMP)"),
                nullable=False,
            ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_NotesDocuments_ownerId", "NotesDocuments", ["ownerId"])

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "NoteSummaries" not in table_names:
        op.create_table(
            "NoteSummaries",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("documentId", sa.Integer(), nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("summaryType", sa.String(length=40), server_default="standard", nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("originalLength", sa.Integer(), nullable=True),
            sa.Column("summaryLength", sa.Integer(), nullable=True),
            sa.Column("meta", sa.Text(), nullable=True),
            sa.Column(
                "createdAt",
                sa.DateTime(timezone=True),
                server_default=sa.text("(CURRENT_TIMESTAMP)"),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["documentId"], ["NotesDocuments.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_NoteSummaries_documentId", "NoteSummaries", ["documentId"])
        op.create_index("ix_NoteSummaries_ownerId", "NoteSummaries", ["ownerId"])

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "SummaryJobs" not in table_names:
        op.create_table(
            "SummaryJobs",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("documentId", sa.Integer(), nullable=True),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("jobType", sa.String(length=80), nullable=False),
            sa.Column("input", sa.Text(), nullable=True),
            sa.Column("output", sa.Text(), nullable=True),
            sa.Column("status", sa.String(length=40), nullable=False),
            sa.Column(
                "createdAt",
                sa.DateTime(timezone=True),
                server_default=sa.text("(CURRENT_TIMESTAMP)"),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["documentId"], ["NotesDocuments.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_SummaryJobs_documentId", "SummaryJobs", ["documentId"])
        op.create_index("ix_SummaryJobs_ownerId", "SummaryJobs", ["ownerId"])


def downgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())

    if "SummaryJobs" in table_names:
        op.drop_index("ix_SummaryJobs_ownerId", table_name="SummaryJobs")
        op.drop_index("ix_SummaryJobs_documentId", table_name="SummaryJobs")
        op.drop_table("SummaryJobs")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "NoteSummaries" in table_names:
        op.drop_index("ix_NoteSummaries_ownerId", table_name="NoteSummaries")
        op.drop_index("ix_NoteSummaries_documentId", table_name="NoteSummaries")
        op.drop_table("NoteSummaries")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "NotesDocuments" in table_names:
        op.drop_index("ix_NotesDocuments_ownerId", table_name="NotesDocuments")
        op.drop_table("NotesDocuments")
