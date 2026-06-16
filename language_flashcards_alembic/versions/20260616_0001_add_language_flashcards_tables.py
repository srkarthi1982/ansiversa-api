"""add_language_flashcards_tables

Revision ID: 20260616_lang_0001
Revises:
Create Date: 2026-06-16

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260616_lang_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())

    if "LanguageDecks" not in table_names:
        op.create_table(
            "LanguageDecks",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("name", sa.String(length=160), nullable=False),
            sa.Column("language", sa.String(length=120), nullable=False),
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
            "ix_LanguageDecks_userId",
            "LanguageDecks",
            ["userId"],
            unique=False,
        )

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "LanguageCards" not in table_names:
        op.create_table(
            "LanguageCards",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("deckId", sa.String(length=36), nullable=False),
            sa.Column("front", sa.String(length=500), nullable=False),
            sa.Column("back", sa.String(length=500), nullable=False),
            sa.Column("exampleSentence", sa.Text(), nullable=True),
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
            sa.ForeignKeyConstraint(["deckId"], ["LanguageDecks.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            "ix_LanguageCards_deckId",
            "LanguageCards",
            ["deckId"],
            unique=False,
        )

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "StudySessions" not in table_names:
        op.create_table(
            "StudySessions",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("deckId", sa.String(length=36), nullable=False),
            sa.Column("totalCards", sa.Integer(), nullable=False),
            sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
            sa.Column(
                "startedAt",
                sa.DateTime(timezone=True),
                server_default=sa.text("(CURRENT_TIMESTAMP)"),
                nullable=False,
            ),
            sa.Column("completedAt", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["deckId"], ["LanguageDecks.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            "ix_StudySessions_deckId",
            "StudySessions",
            ["deckId"],
            unique=False,
        )
        op.create_index(
            "ix_StudySessions_userId",
            "StudySessions",
            ["userId"],
            unique=False,
        )

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "ReviewLogs" not in table_names:
        op.create_table(
            "ReviewLogs",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("sessionId", sa.String(length=36), nullable=False),
            sa.Column("cardId", sa.String(length=36), nullable=False),
            sa.Column("isKnown", sa.Boolean(), nullable=False),
            sa.Column(
                "createdAt",
                sa.DateTime(timezone=True),
                server_default=sa.text("(CURRENT_TIMESTAMP)"),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["cardId"], ["LanguageCards.id"]),
            sa.ForeignKeyConstraint(["sessionId"], ["StudySessions.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            "ix_ReviewLogs_cardId",
            "ReviewLogs",
            ["cardId"],
            unique=False,
        )
        op.create_index(
            "ix_ReviewLogs_sessionId",
            "ReviewLogs",
            ["sessionId"],
            unique=False,
        )


def downgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())

    if "ReviewLogs" in table_names:
        op.drop_index("ix_ReviewLogs_sessionId", table_name="ReviewLogs")
        op.drop_index("ix_ReviewLogs_cardId", table_name="ReviewLogs")
        op.drop_table("ReviewLogs")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "StudySessions" in table_names:
        op.drop_index("ix_StudySessions_userId", table_name="StudySessions")
        op.drop_index("ix_StudySessions_deckId", table_name="StudySessions")
        op.drop_table("StudySessions")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "LanguageCards" in table_names:
        op.drop_index("ix_LanguageCards_deckId", table_name="LanguageCards")
        op.drop_table("LanguageCards")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "LanguageDecks" in table_names:
        op.drop_index("ix_LanguageDecks_userId", table_name="LanguageDecks")
        op.drop_table("LanguageDecks")
