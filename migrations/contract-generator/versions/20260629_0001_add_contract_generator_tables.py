"""add_contract_generator_tables

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
    ("ContractProjects_ownerId_updatedAt_title_idx", "ContractProjects", ("ownerId", "updatedAt", "title")),
    ("ContractProjects_ownerId_status_updatedAt_idx", "ContractProjects", ("ownerId", "status", "updatedAt")),
    ("ContractDocuments_ownerId_updatedAt_idx", "ContractDocuments", ("ownerId", "updatedAt")),
    ("ContractDocuments_projectId_status_updatedAt_idx", "ContractDocuments", ("projectId", "status", "updatedAt")),
    ("ContractDocuments_projectId_contractType_idx", "ContractDocuments", ("projectId", "contractType")),
    ("ContractClauses_ownerId_updatedAt_idx", "ContractClauses", ("ownerId", "updatedAt")),
    ("ContractClauses_documentId_category_idx", "ContractClauses", ("documentId", "category")),
    ("ContractClauses_documentId_sortOrder_idx", "ContractClauses", ("documentId", "sortOrder")),
    ("ContractHistory_ownerId_createdAt_idx", "ContractHistory", ("ownerId", "createdAt")),
    ("ContractHistory_projectId_createdAt_idx", "ContractHistory", ("projectId", "createdAt")),
    ("ContractHistory_documentId_createdAt_idx", "ContractHistory", ("documentId", "createdAt")),
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

    if "ContractProjects" not in table_names:
        op.create_table(
            "ContractProjects",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("counterpartyName", sa.String(length=180), nullable=True),
            sa.Column("contractType", sa.String(length=80), server_default="service", nullable=False),
            sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_ContractProjects_ownerId", "ContractProjects", ["ownerId"])

    table_names = _table_names()
    if "ContractDocuments" not in table_names:
        op.create_table(
            "ContractDocuments",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("projectId", sa.Integer(), nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("status", sa.String(length=40), server_default="draft", nullable=False),
            sa.Column("contractType", sa.String(length=80), server_default="service", nullable=False),
            sa.Column("effectiveDate", sa.String(length=40), nullable=True),
            sa.Column("expiryDate", sa.String(length=40), nullable=True),
            sa.Column("jurisdiction", sa.String(length=120), nullable=True),
            sa.Column("parties", sa.Text(), nullable=True),
            sa.Column("body", sa.Text(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["projectId"], ["ContractProjects.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_ContractDocuments_ownerId", "ContractDocuments", ["ownerId"])
        op.create_index("ix_ContractDocuments_projectId", "ContractDocuments", ["projectId"])

    table_names = _table_names()
    if "ContractClauses" not in table_names:
        op.create_table(
            "ContractClauses",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("documentId", sa.Integer(), nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("category", sa.String(length=80), server_default="general", nullable=False),
            sa.Column("body", sa.Text(), nullable=False),
            sa.Column("sortOrder", sa.Integer(), server_default="0", nullable=False),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["documentId"], ["ContractDocuments.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_ContractClauses_ownerId", "ContractClauses", ["ownerId"])
        op.create_index("ix_ContractClauses_documentId", "ContractClauses", ["documentId"])

    table_names = _table_names()
    if "ContractHistory" not in table_names:
        op.create_table(
            "ContractHistory",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("projectId", sa.Integer(), nullable=True),
            sa.Column("documentId", sa.Integer(), nullable=True),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("actionType", sa.String(length=60), server_default="updated", nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["projectId"], ["ContractProjects.id"]),
            sa.ForeignKeyConstraint(["documentId"], ["ContractDocuments.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_ContractHistory_ownerId", "ContractHistory", ["ownerId"])
        op.create_index("ix_ContractHistory_projectId", "ContractHistory", ["projectId"])
        op.create_index("ix_ContractHistory_documentId", "ContractHistory", ["documentId"])

    for name, table_name, columns in INDEXES:
        _create_index(name, table_name, columns)


def downgrade() -> None:
    for name, table_name, _columns in reversed(INDEXES):
        _drop_index(name, table_name)

    table_names = _table_names()
    if "ContractHistory" in table_names:
        op.drop_index("ix_ContractHistory_documentId", table_name="ContractHistory")
        op.drop_index("ix_ContractHistory_projectId", table_name="ContractHistory")
        op.drop_index("ix_ContractHistory_ownerId", table_name="ContractHistory")
        op.drop_table("ContractHistory")

    table_names = _table_names()
    if "ContractClauses" in table_names:
        op.drop_index("ix_ContractClauses_documentId", table_name="ContractClauses")
        op.drop_index("ix_ContractClauses_ownerId", table_name="ContractClauses")
        op.drop_table("ContractClauses")

    table_names = _table_names()
    if "ContractDocuments" in table_names:
        op.drop_index("ix_ContractDocuments_projectId", table_name="ContractDocuments")
        op.drop_index("ix_ContractDocuments_ownerId", table_name="ContractDocuments")
        op.drop_table("ContractDocuments")

    table_names = _table_names()
    if "ContractProjects" in table_names:
        op.drop_index("ix_ContractProjects_ownerId", table_name="ContractProjects")
        op.drop_table("ContractProjects")
