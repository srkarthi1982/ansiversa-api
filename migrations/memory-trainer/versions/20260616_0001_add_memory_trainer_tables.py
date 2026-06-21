"""add_memory_trainer_tables

Revision ID: 20260616_memory_0001
Revises:
Create Date: 2026-06-16

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260616_memory_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())

    if "MemoryGames" not in table_names:
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

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "MemorySessions" not in table_names:
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

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "MemoryRounds" not in table_names:
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

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "MemoryPerformance" not in table_names:
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


def downgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())

    if "MemoryPerformance" in table_names:
        op.drop_index(
            "ix_MemoryPerformance_sessionId",
            table_name="MemoryPerformance",
        )
        op.drop_index("ix_MemoryPerformance_gameId", table_name="MemoryPerformance")
        op.drop_index("ix_MemoryPerformance_userId", table_name="MemoryPerformance")
        op.drop_table("MemoryPerformance")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "MemoryRounds" in table_names:
        op.drop_index("ix_MemoryRounds_sessionId", table_name="MemoryRounds")
        op.drop_table("MemoryRounds")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "MemorySessions" in table_names:
        op.drop_index("ix_MemorySessions_gameId", table_name="MemorySessions")
        op.drop_index("ix_MemorySessions_userId", table_name="MemorySessions")
        op.drop_table("MemorySessions")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "MemoryGames" in table_names:
        op.drop_index("ix_MemoryGames_userId", table_name="MemoryGames")
        op.drop_table("MemoryGames")
