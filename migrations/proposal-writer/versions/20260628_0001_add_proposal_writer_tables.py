"""add_proposal_writer_tables

Revision ID: 20260628_0001
Revises:
Create Date: 2026-06-28

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260628_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


INDEXES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("ProposalWriterProjects_ownerId_updatedAt_title_idx", "ProposalWriterProjects", ("ownerId", "updatedAt", "title")),
    ("ProposalWriterProjects_ownerId_status_updatedAt_idx", "ProposalWriterProjects", ("ownerId", "status", "updatedAt")),
    ("ProposalWriterProjects_ownerId_createdAt_idx", "ProposalWriterProjects", ("ownerId", "createdAt")),
    ("ProposalWriterSections_ownerId_updatedAt_idx", "ProposalWriterSections", ("ownerId", "updatedAt")),
    ("ProposalWriterSections_projectId_sortOrder_idx", "ProposalWriterSections", ("projectId", "sortOrder")),
    ("ProposalWriterSections_projectId_status_idx", "ProposalWriterSections", ("projectId", "status")),
    ("ProposalWriterDrafts_ownerId_updatedAt_idx", "ProposalWriterDrafts", ("ownerId", "updatedAt")),
    ("ProposalWriterDrafts_projectId_status_idx", "ProposalWriterDrafts", ("projectId", "status")),
    ("ProposalWriterDrafts_projectId_updatedAt_idx", "ProposalWriterDrafts", ("projectId", "updatedAt")),
    ("ProposalWriterHistory_ownerId_createdAt_idx", "ProposalWriterHistory", ("ownerId", "createdAt")),
    ("ProposalWriterHistory_projectId_createdAt_idx", "ProposalWriterHistory", ("projectId", "createdAt")),
    ("ProposalWriterHistory_draftId_createdAt_idx", "ProposalWriterHistory", ("draftId", "createdAt")),
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

    if "ProposalWriterProjects" not in table_names:
        op.create_table(
            "ProposalWriterProjects",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("clientName", sa.String(length=180), nullable=False),
            sa.Column("opportunity", sa.Text(), nullable=True),
            sa.Column("budgetRange", sa.String(length=120), nullable=True),
            sa.Column("dueDate", sa.String(length=40), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="draft", nullable=False),
            sa.Column(
                "createdAt",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updatedAt",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_ProposalWriterProjects_ownerId", "ProposalWriterProjects", ["ownerId"])

    table_names = _table_names()
    if "ProposalWriterSections" not in table_names:
        op.create_table(
            "ProposalWriterSections",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("projectId", sa.Integer(), nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("sortOrder", sa.Integer(), server_default="0", nullable=False),
            sa.Column("status", sa.String(length=40), server_default="draft", nullable=False),
            sa.Column(
                "createdAt",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updatedAt",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["projectId"], ["ProposalWriterProjects.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_ProposalWriterSections_ownerId", "ProposalWriterSections", ["ownerId"])
        op.create_index("ix_ProposalWriterSections_projectId", "ProposalWriterSections", ["projectId"])

    table_names = _table_names()
    if "ProposalWriterDrafts" not in table_names:
        op.create_table(
            "ProposalWriterDrafts",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("projectId", sa.Integer(), nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("summary", sa.Text(), nullable=True),
            sa.Column("body", sa.Text(), nullable=False),
            sa.Column("status", sa.String(length=40), server_default="draft", nullable=False),
            sa.Column(
                "createdAt",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updatedAt",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["projectId"], ["ProposalWriterProjects.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_ProposalWriterDrafts_ownerId", "ProposalWriterDrafts", ["ownerId"])
        op.create_index("ix_ProposalWriterDrafts_projectId", "ProposalWriterDrafts", ["projectId"])

    table_names = _table_names()
    if "ProposalWriterHistory" not in table_names:
        op.create_table(
            "ProposalWriterHistory",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("projectId", sa.Integer(), nullable=True),
            sa.Column("draftId", sa.Integer(), nullable=True),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("actionType", sa.String(length=60), server_default="updated", nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column(
                "createdAt",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updatedAt",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["projectId"], ["ProposalWriterProjects.id"]),
            sa.ForeignKeyConstraint(["draftId"], ["ProposalWriterDrafts.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_ProposalWriterHistory_ownerId", "ProposalWriterHistory", ["ownerId"])
        op.create_index("ix_ProposalWriterHistory_projectId", "ProposalWriterHistory", ["projectId"])
        op.create_index("ix_ProposalWriterHistory_draftId", "ProposalWriterHistory", ["draftId"])

    for name, table_name, columns in INDEXES:
        _create_index(name, table_name, columns)


def downgrade() -> None:
    for name, table_name, _columns in reversed(INDEXES):
        _drop_index(name, table_name)

    table_names = _table_names()
    if "ProposalWriterHistory" in table_names:
        op.drop_index("ix_ProposalWriterHistory_draftId", table_name="ProposalWriterHistory")
        op.drop_index("ix_ProposalWriterHistory_projectId", table_name="ProposalWriterHistory")
        op.drop_index("ix_ProposalWriterHistory_ownerId", table_name="ProposalWriterHistory")
        op.drop_table("ProposalWriterHistory")

    table_names = _table_names()
    if "ProposalWriterDrafts" in table_names:
        op.drop_index("ix_ProposalWriterDrafts_projectId", table_name="ProposalWriterDrafts")
        op.drop_index("ix_ProposalWriterDrafts_ownerId", table_name="ProposalWriterDrafts")
        op.drop_table("ProposalWriterDrafts")

    table_names = _table_names()
    if "ProposalWriterSections" in table_names:
        op.drop_index("ix_ProposalWriterSections_projectId", table_name="ProposalWriterSections")
        op.drop_index("ix_ProposalWriterSections_ownerId", table_name="ProposalWriterSections")
        op.drop_table("ProposalWriterSections")

    table_names = _table_names()
    if "ProposalWriterProjects" in table_names:
        op.drop_index("ix_ProposalWriterProjects_ownerId", table_name="ProposalWriterProjects")
        op.drop_table("ProposalWriterProjects")
