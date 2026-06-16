"""reconcile_exam_tables

Revision ID: 20260616_exam_0002
Revises: 20260616_exam_0001
Create Date: 2026-06-16

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260616_exam_0002"
down_revision: str | None = "20260616_exam_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


EXPECTED_EXAM_QUESTIONS = {
    "id",
    "paperId",
    "questionText",
    "optionA",
    "optionB",
    "optionC",
    "optionD",
    "correctOption",
    "explanation",
    "marks",
    "createdAt",
    "updatedAt",
}
EXPECTED_EXAM_ATTEMPTS = {
    "id",
    "userId",
    "paperId",
    "totalQuestions",
    "totalMarks",
    "score",
    "percentage",
    "status",
    "startedAt",
    "submittedAt",
}
EXPECTED_EXAM_ANSWERS = {
    "id",
    "attemptId",
    "questionId",
    "selectedOption",
    "isCorrect",
    "createdAt",
    "updatedAt",
}


def _columns(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {column["name"] for column in inspector.get_columns(table_name)}


def _table_names() -> set[str]:
    return set(sa.inspect(op.get_bind()).get_table_names())


def _row_count(table_name: str) -> int:
    return int(op.get_bind().execute(sa.text(f'SELECT COUNT(*) FROM "{table_name}"')).scalar_one())


def _drop_index_if_exists(index_name: str, table_name: str) -> None:
    indexes = {
        index["name"]
        for index in sa.inspect(op.get_bind()).get_indexes(table_name)
        if index["name"]
    }
    if index_name in indexes:
        op.drop_index(index_name, table_name=table_name)


def _drop_table_if_empty(table_name: str) -> None:
    if table_name not in _table_names():
        return
    if _row_count(table_name) > 0:
        raise RuntimeError(
            f"{table_name} has rows; refusing to rebuild it automatically."
        )
    op.drop_table(table_name)


def _create_exam_questions() -> None:
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


def _create_exam_attempts() -> None:
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


def _create_exam_answers() -> None:
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


def upgrade() -> None:
    table_names = _table_names()
    questions_aligned = (
        "ExamQuestions" in table_names
        and _columns("ExamQuestions") == EXPECTED_EXAM_QUESTIONS
    )
    attempts_aligned = (
        "ExamAttempts" in table_names
        and _columns("ExamAttempts") == EXPECTED_EXAM_ATTEMPTS
    )
    answers_aligned = (
        "ExamAnswers" in table_names
        and _columns("ExamAnswers") == EXPECTED_EXAM_ANSWERS
    )

    if questions_aligned and attempts_aligned and answers_aligned:
        return

    if "ExamAnswers" in table_names:
        _drop_index_if_exists("ix_ExamAnswers_questionId", "ExamAnswers")
        _drop_index_if_exists("ix_ExamAnswers_attemptId", "ExamAnswers")
    _drop_table_if_empty("ExamAnswers")

    if "ExamAttempts" in table_names:
        _drop_index_if_exists("ix_ExamAttempts_userId", "ExamAttempts")
        _drop_index_if_exists("ix_ExamAttempts_paperId", "ExamAttempts")
    _drop_table_if_empty("ExamAttempts")

    if "ExamQuestions" in table_names:
        _drop_index_if_exists("ix_ExamQuestions_paperId", "ExamQuestions")
    _drop_table_if_empty("ExamQuestions")

    _create_exam_questions()
    _create_exam_attempts()
    _create_exam_answers()


def downgrade() -> None:
    table_names = _table_names()

    if "ExamAnswers" in table_names:
        op.drop_index("ix_ExamAnswers_questionId", table_name="ExamAnswers")
        op.drop_index("ix_ExamAnswers_attemptId", table_name="ExamAnswers")
        op.drop_table("ExamAnswers")

    table_names = _table_names()
    if "ExamAttempts" in table_names:
        op.drop_index("ix_ExamAttempts_userId", table_name="ExamAttempts")
        op.drop_index("ix_ExamAttempts_paperId", table_name="ExamAttempts")
        op.drop_table("ExamAttempts")

    table_names = _table_names()
    if "ExamQuestions" in table_names:
        op.drop_index("ix_ExamQuestions_paperId", table_name="ExamQuestions")
        op.drop_table("ExamQuestions")
