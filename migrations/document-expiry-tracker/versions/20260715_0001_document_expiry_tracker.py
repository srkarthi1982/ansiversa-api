"""add document expiry tracker tables

Revision ID: 20260715_0001_document_expiry_tracker
Revises:
Create Date: 2026-07-15
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260715_0001_document_expiry_tracker"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

INDEXES = (
    ("Documents_userId_expiryDate_idx", "Documents", ("userId", "expiryDate")),
    ("Documents_userId_createdAt_idx", "Documents", ("userId", "createdAt")),
    ("Documents_userId_updatedAt_idx", "Documents", ("userId", "updatedAt")),
    ("Documents_userId_documentType_idx", "Documents", ("userId", "documentType")),
    ("Documents_userId_country_idx", "Documents", ("userId", "country")),
    ("Documents_userId_archived_expiryDate_idx", "Documents", ("userId", "archived", "expiryDate")),
)


def _table_names() -> set[str]:
    return set(sa.inspect(op.get_bind()).get_table_names())


def _index_names(table_name: str) -> set[str]:
    return {index["name"] for index in sa.inspect(op.get_bind()).get_indexes(table_name)}


def _create_index_if_missing(name: str, table_name: str, columns: Sequence[str]) -> None:
    if name not in _index_names(table_name):
        op.create_index(name, table_name, list(columns))


def upgrade() -> None:
    table_names = _table_names()

    if "Documents" not in table_names:
        op.create_table(
            "Documents",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("documentType", sa.String(length=80), nullable=False),
            sa.Column("documentNumber", sa.String(length=120), nullable=True),
            sa.Column("issuingAuthority", sa.String(length=180), nullable=True),
            sa.Column("country", sa.String(length=120), nullable=False),
            sa.Column("issueDate", sa.String(length=40), nullable=True),
            sa.Column("expiryDate", sa.String(length=40), nullable=True),
            sa.Column("renewalReminderDays", sa.Integer(), server_default="30", nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("tags", sa.Text(), nullable=True),
            sa.Column("archived", sa.Boolean(), server_default="0", nullable=False),
            sa.Column("renewalCount", sa.Integer(), server_default="0", nullable=False),
            sa.Column("lastRenewedAt", sa.String(length=40), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("userId", "title", "documentType", name="uq_documents_owner_title_type"),
        )
        op.create_index("ix_Documents_userId", "Documents", ["userId"])
        op.create_index("ix_Documents_documentType", "Documents", ["documentType"])
        op.create_index("ix_Documents_country", "Documents", ["country"])
        op.create_index("ix_Documents_expiryDate", "Documents", ["expiryDate"])
        op.create_index("ix_Documents_archived", "Documents", ["archived"])

    for name, table_name, columns in INDEXES:
        _create_index_if_missing(name, table_name, columns)


def downgrade() -> None:
    table_names = _table_names()
    if "Documents" in table_names:
        op.drop_table("Documents")
