"""align_existing_smart_textbook_scanner_tables

Revision ID: 20260622_0002
Revises: 20260622_0001
Create Date: 2026-06-22

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260622_0002"
down_revision: str | None = "20260622_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _columns(table_name: str) -> dict[str, dict[str, object]]:
    inspector = sa.inspect(op.get_bind())
    return {column["name"]: column for column in inspector.get_columns(table_name)}


def _index_names(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {index["name"] for index in inspector.get_indexes(table_name)}


def upgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "TextbookPages" not in table_names:
        return

    columns = _columns("TextbookPages")
    with op.batch_alter_table("TextbookPages") as batch_op:
        if "scanId" not in columns:
            batch_op.add_column(
                sa.Column("scanId", sa.Integer(), server_default="0", nullable=False)
            )
        if "ownerId" not in columns:
            batch_op.add_column(
                sa.Column(
                    "ownerId",
                    sa.String(length=36),
                    server_default="legacy",
                    nullable=False,
                )
            )
        if "title" not in columns:
            batch_op.add_column(sa.Column("title", sa.String(length=180), nullable=True))
        if "pageText" not in columns:
            batch_op.add_column(
                sa.Column("pageText", sa.Text(), server_default="", nullable=False)
            )
        if "status" not in columns:
            batch_op.add_column(
                sa.Column(
                    "status",
                    sa.String(length=40),
                    server_default="captured",
                    nullable=False,
                )
            )
        document_id_column = columns.get("documentId")
        if document_id_column and not document_id_column["nullable"]:
            batch_op.alter_column(
                "documentId",
                existing_type=sa.String(length=36),
                nullable=True,
            )

    indexes = _index_names("TextbookPages")
    if "ix_TextbookPages_ownerId" not in indexes:
        op.create_index("ix_TextbookPages_ownerId", "TextbookPages", ["ownerId"])
    if "ix_TextbookPages_scanId" not in indexes:
        op.create_index("ix_TextbookPages_scanId", "TextbookPages", ["scanId"])


def downgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "TextbookPages" not in table_names:
        return

    indexes = _index_names("TextbookPages")
    if "ix_TextbookPages_scanId" in indexes:
        op.drop_index("ix_TextbookPages_scanId", table_name="TextbookPages")
    if "ix_TextbookPages_ownerId" in indexes:
        op.drop_index("ix_TextbookPages_ownerId", table_name="TextbookPages")

    columns = _columns("TextbookPages")
    with op.batch_alter_table("TextbookPages") as batch_op:
        if "documentId" in columns:
            batch_op.alter_column(
                "documentId",
                existing_type=sa.String(length=36),
                nullable=False,
            )
        for column_name in ("status", "pageText", "title", "ownerId", "scanId"):
            if column_name in columns:
                batch_op.drop_column(column_name)
