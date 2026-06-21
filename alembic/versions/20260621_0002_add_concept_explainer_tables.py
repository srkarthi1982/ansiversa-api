"""add_concept_explainer_tables

Revision ID: 20260621_0002
Revises: 20260621_0001
Create Date: 2026-06-21 13:20:00.000000

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260621_0002"
down_revision: str | None = "20260621_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = set(inspector.get_table_names())

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
        op.create_index("ix_Concepts_userId", "Concepts", ["userId"])

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
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updatedAt",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["conceptId"], ["Concepts.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_ConceptSteps_conceptId", "ConceptSteps", ["conceptId"])

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
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updatedAt",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["conceptId"], ["Concepts.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_ConceptChecks_conceptId", "ConceptChecks", ["conceptId"])

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
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updatedAt",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["conceptId"], ["Concepts.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_ConceptJobs_conceptId", "ConceptJobs", ["conceptId"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = set(inspector.get_table_names())

    if "ConceptJobs" in table_names:
        op.drop_index("ix_ConceptJobs_conceptId", table_name="ConceptJobs")
        op.drop_table("ConceptJobs")
    if "ConceptChecks" in table_names:
        op.drop_index("ix_ConceptChecks_conceptId", table_name="ConceptChecks")
        op.drop_table("ConceptChecks")
    if "ConceptSteps" in table_names:
        op.drop_index("ix_ConceptSteps_conceptId", table_name="ConceptSteps")
        op.drop_table("ConceptSteps")
    if "Concepts" in table_names:
        op.drop_index("ix_Concepts_userId", table_name="Concepts")
        op.drop_table("Concepts")
