"""rebuild_memory_trainer_tables

Revision ID: 20260616_memory_0002
Revises: 20260616_memory_0001
Create Date: 2026-06-16

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260616_memory_0002"
down_revision: str | None = "20260616_memory_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


EXPECTED_COLUMNS = {
    "MemoryGames": {
        "id",
        "userId",
        "title",
        "mode",
        "difficulty",
        "sequenceLength",
        "roundCount",
        "description",
        "createdAt",
        "updatedAt",
    },
    "MemorySessions": {
        "id",
        "userId",
        "gameId",
        "status",
        "startedAt",
        "completedAt",
    },
    "MemoryRounds": {
        "id",
        "sessionId",
        "roundNumber",
        "sequence",
        "userAnswer",
        "isCorrect",
        "responseTimeMs",
        "createdAt",
        "updatedAt",
    },
    "MemoryPerformance": {
        "id",
        "userId",
        "gameId",
        "sessionId",
        "totalRounds",
        "correctRounds",
        "wrongRounds",
        "accuracy",
        "averageResponseTimeMs",
        "completedAt",
    },
}


def _table_names() -> set[str]:
    return set(sa.inspect(op.get_bind()).get_table_names())


def _column_names(table_name: str) -> set[str]:
    return {
        column["name"]
        for column in sa.inspect(op.get_bind()).get_columns(table_name)
    }


def _schema_needs_rebuild() -> bool:
    table_names = _table_names()
    for table_name, expected_columns in EXPECTED_COLUMNS.items():
        if table_name not in table_names:
            return True
        if not expected_columns.issubset(_column_names(table_name)):
            return True

    return False


def _drop_existing_tables() -> None:
    table_names = _table_names()
    for table_name in [
        "MemoryPerformance",
        "MemoryRounds",
        "MemorySessions",
        "MemoryGames",
    ]:
        if table_name in table_names:
            op.drop_table(table_name)
            table_names.remove(table_name)


def _create_tables() -> None:
    op.create_table(
        "MemoryGames",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("userId", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("mode", sa.String(length=40), nullable=False),
        sa.Column("difficulty", sa.String(length=20), nullable=False),
        sa.Column("sequenceLength", sa.Integer(), nullable=False),
        sa.Column("roundCount", sa.Integer(), nullable=False),
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
    op.create_index("ix_MemoryGames_userId", "MemoryGames", ["userId"])

    op.create_table(
        "MemorySessions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("userId", sa.String(length=36), nullable=False),
        sa.Column("gameId", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
        sa.Column(
            "startedAt",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column("completedAt", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["gameId"], ["MemoryGames.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_MemorySessions_userId", "MemorySessions", ["userId"])
    op.create_index("ix_MemorySessions_gameId", "MemorySessions", ["gameId"])

    op.create_table(
        "MemoryRounds",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("sessionId", sa.String(length=36), nullable=False),
        sa.Column("roundNumber", sa.Integer(), nullable=False),
        sa.Column("sequence", sa.Text(), nullable=False),
        sa.Column("userAnswer", sa.Text(), nullable=True),
        sa.Column("isCorrect", sa.Boolean(), nullable=True),
        sa.Column("responseTimeMs", sa.Integer(), nullable=True),
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
        sa.ForeignKeyConstraint(["sessionId"], ["MemorySessions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "sessionId",
            "roundNumber",
            name="uq_MemoryRounds_sessionId_roundNumber",
        ),
    )
    op.create_index("ix_MemoryRounds_sessionId", "MemoryRounds", ["sessionId"])

    op.create_table(
        "MemoryPerformance",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("userId", sa.String(length=36), nullable=False),
        sa.Column("gameId", sa.String(length=36), nullable=False),
        sa.Column("sessionId", sa.String(length=36), nullable=False),
        sa.Column("totalRounds", sa.Integer(), nullable=False),
        sa.Column("correctRounds", sa.Integer(), nullable=False),
        sa.Column("wrongRounds", sa.Integer(), nullable=False),
        sa.Column("accuracy", sa.Integer(), nullable=False),
        sa.Column("averageResponseTimeMs", sa.Integer(), nullable=False),
        sa.Column(
            "completedAt",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["gameId"], ["MemoryGames.id"]),
        sa.ForeignKeyConstraint(["sessionId"], ["MemorySessions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sessionId"),
    )
    op.create_index("ix_MemoryPerformance_userId", "MemoryPerformance", ["userId"])
    op.create_index("ix_MemoryPerformance_gameId", "MemoryPerformance", ["gameId"])
    op.create_index(
        "ix_MemoryPerformance_sessionId",
        "MemoryPerformance",
        ["sessionId"],
        unique=True,
    )


def upgrade() -> None:
    if not _schema_needs_rebuild():
        return

    _drop_existing_tables()
    _create_tables()


def downgrade() -> None:
    _drop_existing_tables()
