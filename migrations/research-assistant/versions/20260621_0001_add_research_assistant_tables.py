"""add_research_assistant_tables

Revision ID: 20260621_0001
Revises:
Create Date: 2026-06-21

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260621_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())

    if "ResearchTopics" not in table_names:
        op.create_table(
            "ResearchTopics",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("question", sa.Text(), nullable=True),
            sa.Column("summary", sa.Text(), nullable=True),
            sa.Column(
                "status",
                sa.String(length=40),
                server_default="collecting",
                nullable=False,
            ),
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
        op.create_index("ix_ResearchTopics_userId", "ResearchTopics", ["userId"])

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "ResearchNotes" not in table_names:
        op.create_table(
            "ResearchNotes",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("topicId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("body", sa.Text(), nullable=False),
            sa.Column("position", sa.Integer(), nullable=False),
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
            sa.ForeignKeyConstraint(["topicId"], ["ResearchTopics.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_ResearchNotes_topicId", "ResearchNotes", ["topicId"])

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "ResearchReferences" not in table_names:
        op.create_table(
            "ResearchReferences",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("topicId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("url", sa.Text(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("position", sa.Integer(), nullable=False),
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
            sa.ForeignKeyConstraint(["topicId"], ["ResearchTopics.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            "ix_ResearchReferences_topicId",
            "ResearchReferences",
            ["topicId"],
        )

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "ResearchJobs" not in table_names:
        op.create_table(
            "ResearchJobs",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("topicId", sa.String(length=36), nullable=False),
            sa.Column("jobType", sa.String(length=80), nullable=False),
            sa.Column(
                "status",
                sa.String(length=40),
                server_default="queued",
                nullable=False,
            ),
            sa.Column("payload", sa.Text(), nullable=True),
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
            sa.ForeignKeyConstraint(["topicId"], ["ResearchTopics.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_ResearchJobs_topicId", "ResearchJobs", ["topicId"])


def downgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())

    if "ResearchJobs" in table_names:
        op.drop_index("ix_ResearchJobs_topicId", table_name="ResearchJobs")
        op.drop_table("ResearchJobs")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "ResearchReferences" in table_names:
        op.drop_index(
            "ix_ResearchReferences_topicId",
            table_name="ResearchReferences",
        )
        op.drop_table("ResearchReferences")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "ResearchNotes" in table_names:
        op.drop_index("ix_ResearchNotes_topicId", table_name="ResearchNotes")
        op.drop_table("ResearchNotes")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "ResearchTopics" in table_names:
        op.drop_index("ix_ResearchTopics_userId", table_name="ResearchTopics")
        op.drop_table("ResearchTopics")
