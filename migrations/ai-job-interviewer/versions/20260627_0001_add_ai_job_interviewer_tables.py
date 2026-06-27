"""add_ai_job_interviewer_tables

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

    if "AiJobInterviewSessions" not in table_names:
        op.create_table(
            "AiJobInterviewSessions",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("roleTitle", sa.String(length=140), nullable=False),
            sa.Column("companyName", sa.String(length=140), nullable=True),
            sa.Column("experienceLevel", sa.String(length=40), server_default="mid", nullable=False),
            sa.Column(
                "interviewType",
                sa.String(length=40),
                server_default="behavioral",
                nullable=False,
            ),
            sa.Column("targetDate", sa.Date(), nullable=True),
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
        op.create_index("ix_AiJobInterviewSessions_ownerId", "AiJobInterviewSessions", ["ownerId"])

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "AiJobInterviewQuestions" not in table_names:
        op.create_table(
            "AiJobInterviewQuestions",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("sessionId", sa.Integer(), nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("prompt", sa.Text(), nullable=False),
            sa.Column(
                "category",
                sa.String(length=80),
                server_default="behavioral",
                nullable=False,
            ),
            sa.Column("position", sa.Integer(), server_default="1", nullable=False),
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
            sa.ForeignKeyConstraint(["sessionId"], ["AiJobInterviewSessions.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_AiJobInterviewQuestions_ownerId", "AiJobInterviewQuestions", ["ownerId"])
        op.create_index("ix_AiJobInterviewQuestions_sessionId", "AiJobInterviewQuestions", ["sessionId"])

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "AiJobInterviewAnswers" not in table_names:
        op.create_table(
            "AiJobInterviewAnswers",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("sessionId", sa.Integer(), nullable=False),
            sa.Column("questionId", sa.Integer(), nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("answerText", sa.Text(), nullable=False),
            sa.Column("confidence", sa.Integer(), server_default="3", nullable=False),
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
            sa.ForeignKeyConstraint(["questionId"], ["AiJobInterviewQuestions.id"]),
            sa.ForeignKeyConstraint(["sessionId"], ["AiJobInterviewSessions.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_AiJobInterviewAnswers_ownerId", "AiJobInterviewAnswers", ["ownerId"])
        op.create_index("ix_AiJobInterviewAnswers_questionId", "AiJobInterviewAnswers", ["questionId"])
        op.create_index("ix_AiJobInterviewAnswers_sessionId", "AiJobInterviewAnswers", ["sessionId"])

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "AiJobInterviewResults" not in table_names:
        op.create_table(
            "AiJobInterviewResults",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("sessionId", sa.Integer(), nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("progressScore", sa.Integer(), server_default="3", nullable=False),
            sa.Column("strengths", sa.Text(), nullable=True),
            sa.Column("improvements", sa.Text(), nullable=True),
            sa.Column("nextSteps", sa.Text(), nullable=True),
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
            sa.ForeignKeyConstraint(["sessionId"], ["AiJobInterviewSessions.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_AiJobInterviewResults_ownerId", "AiJobInterviewResults", ["ownerId"])
        op.create_index("ix_AiJobInterviewResults_sessionId", "AiJobInterviewResults", ["sessionId"])


def downgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())

    if "AiJobInterviewResults" in table_names:
        op.drop_index("ix_AiJobInterviewResults_sessionId", table_name="AiJobInterviewResults")
        op.drop_index("ix_AiJobInterviewResults_ownerId", table_name="AiJobInterviewResults")
        op.drop_table("AiJobInterviewResults")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "AiJobInterviewAnswers" in table_names:
        op.drop_index("ix_AiJobInterviewAnswers_sessionId", table_name="AiJobInterviewAnswers")
        op.drop_index("ix_AiJobInterviewAnswers_questionId", table_name="AiJobInterviewAnswers")
        op.drop_index("ix_AiJobInterviewAnswers_ownerId", table_name="AiJobInterviewAnswers")
        op.drop_table("AiJobInterviewAnswers")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "AiJobInterviewQuestions" in table_names:
        op.drop_index("ix_AiJobInterviewQuestions_sessionId", table_name="AiJobInterviewQuestions")
        op.drop_index("ix_AiJobInterviewQuestions_ownerId", table_name="AiJobInterviewQuestions")
        op.drop_table("AiJobInterviewQuestions")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "AiJobInterviewSessions" in table_names:
        op.drop_index("ix_AiJobInterviewSessions_ownerId", table_name="AiJobInterviewSessions")
        op.drop_table("AiJobInterviewSessions")
