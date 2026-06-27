"""add_email_assistant_tables

Revision ID: 20260627_0001
Revises:
Create Date: 2026-06-27

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260627_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())

    if "EmailAssistantProjects" not in table_names:
        op.create_table(
            "EmailAssistantProjects",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("audience", sa.String(length=180), nullable=True),
            sa.Column("goal", sa.Text(), nullable=True),
            sa.Column("tone", sa.String(length=40), server_default="professional", nullable=False),
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
        op.create_index("ix_EmailAssistantProjects_ownerId", "EmailAssistantProjects", ["ownerId"])

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "EmailAssistantTemplates" not in table_names:
        op.create_table(
            "EmailAssistantTemplates",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("category", sa.String(length=80), server_default="general", nullable=False),
            sa.Column("subjectPattern", sa.String(length=220), nullable=True),
            sa.Column("bodyPattern", sa.Text(), nullable=False),
            sa.Column("tone", sa.String(length=40), server_default="professional", nullable=False),
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
        op.create_index("ix_EmailAssistantTemplates_ownerId", "EmailAssistantTemplates", ["ownerId"])

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "EmailAssistantDrafts" not in table_names:
        op.create_table(
            "EmailAssistantDrafts",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("projectId", sa.Integer(), nullable=False),
            sa.Column("templateId", sa.Integer(), nullable=True),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("subject", sa.String(length=220), nullable=False),
            sa.Column("body", sa.Text(), nullable=False),
            sa.Column("tone", sa.String(length=40), server_default="professional", nullable=False),
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
            sa.ForeignKeyConstraint(["projectId"], ["EmailAssistantProjects.id"]),
            sa.ForeignKeyConstraint(["templateId"], ["EmailAssistantTemplates.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_EmailAssistantDrafts_ownerId", "EmailAssistantDrafts", ["ownerId"])
        op.create_index("ix_EmailAssistantDrafts_projectId", "EmailAssistantDrafts", ["projectId"])
        op.create_index("ix_EmailAssistantDrafts_templateId", "EmailAssistantDrafts", ["templateId"])

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "EmailAssistantHistory" not in table_names:
        op.create_table(
            "EmailAssistantHistory",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("projectId", sa.Integer(), nullable=True),
            sa.Column("draftId", sa.Integer(), nullable=True),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("actionType", sa.String(length=60), server_default="drafted", nullable=False),
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
            sa.ForeignKeyConstraint(["projectId"], ["EmailAssistantProjects.id"]),
            sa.ForeignKeyConstraint(["draftId"], ["EmailAssistantDrafts.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_EmailAssistantHistory_ownerId", "EmailAssistantHistory", ["ownerId"])
        op.create_index("ix_EmailAssistantHistory_projectId", "EmailAssistantHistory", ["projectId"])
        op.create_index("ix_EmailAssistantHistory_draftId", "EmailAssistantHistory", ["draftId"])


def downgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())

    if "EmailAssistantHistory" in table_names:
        op.drop_index("ix_EmailAssistantHistory_draftId", table_name="EmailAssistantHistory")
        op.drop_index("ix_EmailAssistantHistory_projectId", table_name="EmailAssistantHistory")
        op.drop_index("ix_EmailAssistantHistory_ownerId", table_name="EmailAssistantHistory")
        op.drop_table("EmailAssistantHistory")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "EmailAssistantDrafts" in table_names:
        op.drop_index("ix_EmailAssistantDrafts_templateId", table_name="EmailAssistantDrafts")
        op.drop_index("ix_EmailAssistantDrafts_projectId", table_name="EmailAssistantDrafts")
        op.drop_index("ix_EmailAssistantDrafts_ownerId", table_name="EmailAssistantDrafts")
        op.drop_table("EmailAssistantDrafts")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "EmailAssistantTemplates" in table_names:
        op.drop_index("ix_EmailAssistantTemplates_ownerId", table_name="EmailAssistantTemplates")
        op.drop_table("EmailAssistantTemplates")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "EmailAssistantProjects" in table_names:
        op.drop_index("ix_EmailAssistantProjects_ownerId", table_name="EmailAssistantProjects")
        op.drop_table("EmailAssistantProjects")
