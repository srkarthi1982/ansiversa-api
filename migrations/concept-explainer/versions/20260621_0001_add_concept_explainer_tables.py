"""add_concept_explainer_tables

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

    if "Concepts" not in table_names:
        op.create_table(
            "Concepts",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("topic", sa.String(length=140), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column(
                "status",
                sa.String(length=40),
                server_default="learning",
                nullable=False,
            ),
            sa.Column("reviewedAt", sa.DateTime(timezone=True), nullable=True),
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
        op.create_index("ix_Concepts_userId", "Concepts", ["userId"])

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "ConceptSteps" not in table_names:
        op.create_table(
            "ConceptSteps",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("conceptId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("explanation", sa.Text(), nullable=False),
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
            sa.ForeignKeyConstraint(["conceptId"], ["Concepts.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_ConceptSteps_conceptId", "ConceptSteps", ["conceptId"])

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "ConceptChecks" not in table_names:
        op.create_table(
            "ConceptChecks",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("conceptId", sa.String(length=36), nullable=False),
            sa.Column("question", sa.Text(), nullable=False),
            sa.Column("expectedAnswer", sa.Text(), nullable=False),
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
            sa.ForeignKeyConstraint(["conceptId"], ["Concepts.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_ConceptChecks_conceptId", "ConceptChecks", ["conceptId"])

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "ConceptJobs" not in table_names:
        op.create_table(
            "ConceptJobs",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("conceptId", sa.String(length=36), nullable=False),
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
            sa.ForeignKeyConstraint(["conceptId"], ["Concepts.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_ConceptJobs_conceptId", "ConceptJobs", ["conceptId"])


def downgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())

    if "ConceptJobs" in table_names:
        op.drop_index("ix_ConceptJobs_conceptId", table_name="ConceptJobs")
        op.drop_table("ConceptJobs")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "ConceptChecks" in table_names:
        op.drop_index("ix_ConceptChecks_conceptId", table_name="ConceptChecks")
        op.drop_table("ConceptChecks")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "ConceptSteps" in table_names:
        op.drop_index("ix_ConceptSteps_conceptId", table_name="ConceptSteps")
        op.drop_table("ConceptSteps")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "Concepts" in table_names:
        op.drop_index("ix_Concepts_userId", table_name="Concepts")
        op.drop_table("Concepts")
