"""add_exam_tables

Revision ID: 20260616_exam_0001
Revises:
Create Date: 2026-06-16

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260616_exam_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())

    if "ExamPapers" not in table_names:
        op.create_table(
            "ExamPapers",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("subject", sa.String(length=140), nullable=False),
            sa.Column("durationMinutes", sa.Integer(), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
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
        op.create_index(
            "ix_ExamPapers_userId",
            "ExamPapers",
            ["userId"],
            unique=False,
        )

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "ExamQuestions" not in table_names:
        op.create_table(
            "ExamQuestions",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("paperId", sa.String(length=36), nullable=False),
            sa.Column("questionText", sa.Text(), nullable=False),
            sa.Column("optionA", sa.String(length=500), nullable=False),
            sa.Column("optionB", sa.String(length=500), nullable=False),
            sa.Column("optionC", sa.String(length=500), nullable=False),
            sa.Column("optionD", sa.String(length=500), nullable=False),
            sa.Column("correctOption", sa.String(length=1), nullable=False),
            sa.Column("explanation", sa.Text(), nullable=True),
            sa.Column("marks", sa.Integer(), server_default="1", nullable=False),
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
            sa.ForeignKeyConstraint(["paperId"], ["ExamPapers.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            "ix_ExamQuestions_paperId",
            "ExamQuestions",
            ["paperId"],
            unique=False,
        )

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "ExamAttempts" not in table_names:
        op.create_table(
            "ExamAttempts",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("paperId", sa.String(length=36), nullable=False),
            sa.Column("totalQuestions", sa.Integer(), nullable=False),
            sa.Column("totalMarks", sa.Integer(), nullable=False),
            sa.Column("score", sa.Integer(), nullable=True),
            sa.Column("percentage", sa.Integer(), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
            sa.Column(
                "startedAt",
                sa.DateTime(timezone=True),
                server_default=sa.text("(CURRENT_TIMESTAMP)"),
                nullable=False,
            ),
            sa.Column("submittedAt", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["paperId"], ["ExamPapers.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            "ix_ExamAttempts_paperId",
            "ExamAttempts",
            ["paperId"],
            unique=False,
        )
        op.create_index(
            "ix_ExamAttempts_userId",
            "ExamAttempts",
            ["userId"],
            unique=False,
        )

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "ExamAnswers" not in table_names:
        op.create_table(
            "ExamAnswers",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("attemptId", sa.String(length=36), nullable=False),
            sa.Column("questionId", sa.String(length=36), nullable=False),
            sa.Column("selectedOption", sa.String(length=1), nullable=False),
            sa.Column("isCorrect", sa.Boolean(), nullable=True),
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
            sa.ForeignKeyConstraint(["attemptId"], ["ExamAttempts.id"]),
            sa.ForeignKeyConstraint(["questionId"], ["ExamQuestions.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            "ix_ExamAnswers_attemptId",
            "ExamAnswers",
            ["attemptId"],
            unique=False,
        )
        op.create_index(
            "ix_ExamAnswers_questionId",
            "ExamAnswers",
            ["questionId"],
            unique=False,
        )


def downgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())

    if "ExamAnswers" in table_names:
        op.drop_index("ix_ExamAnswers_questionId", table_name="ExamAnswers")
        op.drop_index("ix_ExamAnswers_attemptId", table_name="ExamAnswers")
        op.drop_table("ExamAnswers")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "ExamAttempts" in table_names:
        op.drop_index("ix_ExamAttempts_userId", table_name="ExamAttempts")
        op.drop_index("ix_ExamAttempts_paperId", table_name="ExamAttempts")
        op.drop_table("ExamAttempts")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "ExamQuestions" in table_names:
        op.drop_index("ix_ExamQuestions_paperId", table_name="ExamQuestions")
        op.drop_table("ExamQuestions")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "ExamPapers" in table_names:
        op.drop_index("ix_ExamPapers_userId", table_name="ExamPapers")
        op.drop_table("ExamPapers")
