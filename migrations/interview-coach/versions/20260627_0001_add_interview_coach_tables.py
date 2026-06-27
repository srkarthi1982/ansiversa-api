"""add_interview_coach_tables

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

    if "InterviewSessions" not in table_names:
        op.create_table(
            "InterviewSessions",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("roleTitle", sa.String(length=140), nullable=False),
            sa.Column("companyName", sa.String(length=140), nullable=True),
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
        op.create_index("ix_InterviewSessions_ownerId", "InterviewSessions", ["ownerId"])

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "InterviewQuestions" not in table_names:
        op.create_table(
            "InterviewQuestions",
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
            sa.ForeignKeyConstraint(["sessionId"], ["InterviewSessions.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_InterviewQuestions_ownerId", "InterviewQuestions", ["ownerId"])
        op.create_index("ix_InterviewQuestions_sessionId", "InterviewQuestions", ["sessionId"])

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "InterviewAnswers" not in table_names:
        op.create_table(
            "InterviewAnswers",
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
            sa.ForeignKeyConstraint(["questionId"], ["InterviewQuestions.id"]),
            sa.ForeignKeyConstraint(["sessionId"], ["InterviewSessions.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_InterviewAnswers_ownerId", "InterviewAnswers", ["ownerId"])
        op.create_index("ix_InterviewAnswers_questionId", "InterviewAnswers", ["questionId"])
        op.create_index("ix_InterviewAnswers_sessionId", "InterviewAnswers", ["sessionId"])

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "InterviewReviews" not in table_names:
        op.create_table(
            "InterviewReviews",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("sessionId", sa.Integer(), nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("readinessScore", sa.Integer(), server_default="3", nullable=False),
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
            sa.ForeignKeyConstraint(["sessionId"], ["InterviewSessions.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_InterviewReviews_ownerId", "InterviewReviews", ["ownerId"])
        op.create_index("ix_InterviewReviews_sessionId", "InterviewReviews", ["sessionId"])


def downgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())

    if "InterviewReviews" in table_names:
        op.drop_index("ix_InterviewReviews_sessionId", table_name="InterviewReviews")
        op.drop_index("ix_InterviewReviews_ownerId", table_name="InterviewReviews")
        op.drop_table("InterviewReviews")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "InterviewAnswers" in table_names:
        op.drop_index("ix_InterviewAnswers_sessionId", table_name="InterviewAnswers")
        op.drop_index("ix_InterviewAnswers_questionId", table_name="InterviewAnswers")
        op.drop_index("ix_InterviewAnswers_ownerId", table_name="InterviewAnswers")
        op.drop_table("InterviewAnswers")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "InterviewQuestions" in table_names:
        op.drop_index("ix_InterviewQuestions_sessionId", table_name="InterviewQuestions")
        op.drop_index("ix_InterviewQuestions_ownerId", table_name="InterviewQuestions")
        op.drop_table("InterviewQuestions")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "InterviewSessions" in table_names:
        op.drop_index("ix_InterviewSessions_ownerId", table_name="InterviewSessions")
        op.drop_table("InterviewSessions")
