"""add_smart_textbook_scanner_tables

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

    if "TextbookScans" not in table_names:
        op.create_table(
            "TextbookScans",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("subject", sa.String(length=120), nullable=False),
            sa.Column("source", sa.String(length=180), nullable=True),
            sa.Column("goal", sa.Text(), nullable=False),
            sa.Column("status", sa.String(length=40), server_default="scanning", nullable=False),
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
        op.create_index("ix_TextbookScans_ownerId", "TextbookScans", ["ownerId"])

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "TextbookPages" not in table_names:
        op.create_table(
            "TextbookPages",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("scanId", sa.Integer(), nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("pageNumber", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=True),
            sa.Column("pageText", sa.Text(), nullable=False),
            sa.Column("status", sa.String(length=40), server_default="captured", nullable=False),
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
            sa.ForeignKeyConstraint(["scanId"], ["TextbookScans.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_TextbookPages_ownerId", "TextbookPages", ["ownerId"])
        op.create_index("ix_TextbookPages_scanId", "TextbookPages", ["scanId"])

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "ExtractedNotes" not in table_names:
        op.create_table(
            "ExtractedNotes",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("scanId", sa.Integer(), nullable=False),
            sa.Column("pageId", sa.Integer(), nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("heading", sa.String(length=180), nullable=False),
            sa.Column("keyPoints", sa.Text(), nullable=False),
            sa.Column("summary", sa.Text(), nullable=True),
            sa.Column("noteType", sa.String(length=40), server_default="keyPoints", nullable=False),
            sa.Column(
                "createdAt",
                sa.DateTime(timezone=True),
                server_default=sa.text("(CURRENT_TIMESTAMP)"),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["pageId"], ["TextbookPages.id"]),
            sa.ForeignKeyConstraint(["scanId"], ["TextbookScans.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_ExtractedNotes_ownerId", "ExtractedNotes", ["ownerId"])
        op.create_index("ix_ExtractedNotes_pageId", "ExtractedNotes", ["pageId"])
        op.create_index("ix_ExtractedNotes_scanId", "ExtractedNotes", ["scanId"])


def downgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())

    if "ExtractedNotes" in table_names:
        op.drop_index("ix_ExtractedNotes_scanId", table_name="ExtractedNotes")
        op.drop_index("ix_ExtractedNotes_pageId", table_name="ExtractedNotes")
        op.drop_index("ix_ExtractedNotes_ownerId", table_name="ExtractedNotes")
        op.drop_table("ExtractedNotes")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "TextbookPages" in table_names:
        op.drop_index("ix_TextbookPages_scanId", table_name="TextbookPages")
        op.drop_index("ix_TextbookPages_ownerId", table_name="TextbookPages")
        op.drop_table("TextbookPages")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "TextbookScans" in table_names:
        op.drop_index("ix_TextbookScans_ownerId", table_name="TextbookScans")
        op.drop_table("TextbookScans")
