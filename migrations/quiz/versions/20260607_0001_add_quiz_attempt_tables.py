"""add_quiz_attempt_tables

Revision ID: 20260607_0001
Revises:
Create Date: 2026-06-07

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260607_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())

    if "QuizAttempt" not in table_names:
        op.create_table(
            "QuizAttempt",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.Integer(), nullable=False),
            sa.Column("subjectId", sa.Integer(), nullable=False),
            sa.Column("topicId", sa.Integer(), nullable=False),
            sa.Column("roadmapId", sa.Integer(), nullable=False),
            sa.Column("level", sa.String(length=1), nullable=False),
            sa.Column(
                "status",
                sa.String(length=20),
                server_default="in_progress",
                nullable=False,
            ),
            sa.Column("expiresAt", sa.DateTime(timezone=True), nullable=False),
            sa.Column("submittedAt", sa.DateTime(timezone=True), nullable=True),
            sa.Column("resultId", sa.Integer(), nullable=True),
            sa.Column(
                "createdAt",
                sa.DateTime(timezone=True),
                server_default=sa.text("(CURRENT_TIMESTAMP)"),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["resultId"], ["Result.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            "ix_QuizAttempt_userId",
            "QuizAttempt",
            ["userId"],
            unique=False,
        )

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "QuizAttemptQuestion" not in table_names:
        op.create_table(
            "QuizAttemptQuestion",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("attemptId", sa.Integer(), nullable=False),
            sa.Column("questionId", sa.Integer(), nullable=False),
            sa.Column("position", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["attemptId"], ["QuizAttempt.id"]),
            sa.ForeignKeyConstraint(["questionId"], ["Question.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "attemptId",
                "position",
                name="quiz_attempt_position_unique",
            ),
            sa.UniqueConstraint(
                "attemptId",
                "questionId",
                name="quiz_attempt_question_unique",
            ),
        )
        op.create_index(
            "ix_QuizAttemptQuestion_attemptId",
            "QuizAttemptQuestion",
            ["attemptId"],
            unique=False,
        )


def downgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())

    if "QuizAttemptQuestion" in table_names:
        op.drop_index(
            "ix_QuizAttemptQuestion_attemptId",
            table_name="QuizAttemptQuestion",
        )
        op.drop_table("QuizAttemptQuestion")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "QuizAttempt" in table_names:
        op.drop_index("ix_QuizAttempt_userId", table_name="QuizAttempt")
        op.drop_table("QuizAttempt")
