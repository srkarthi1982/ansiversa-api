"""add_dictionary_plus_tables

Revision ID: 20260621_dictionary_0001
Revises:
Create Date: 2026-06-21

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260621_dictionary_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())

    if "DictionaryLookups" not in table_names:
        op.create_table(
            "DictionaryLookups",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("word", sa.String(length=120), nullable=False),
            sa.Column("definition", sa.Text(), nullable=False),
            sa.Column("pronunciation", sa.String(length=120), nullable=True),
            sa.Column("partOfSpeech", sa.String(length=80), nullable=True),
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
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            "ix_DictionaryLookups_userId",
            "DictionaryLookups",
            ["userId"],
        )

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "SavedWords" not in table_names:
        op.create_table(
            "SavedWords",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("lookupId", sa.String(length=36), nullable=True),
            sa.Column("word", sa.String(length=120), nullable=False),
            sa.Column("definition", sa.Text(), nullable=False),
            sa.Column("pronunciation", sa.String(length=120), nullable=True),
            sa.Column("partOfSpeech", sa.String(length=80), nullable=True),
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
            sa.ForeignKeyConstraint(["lookupId"], ["DictionaryLookups.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_SavedWords_userId", "SavedWords", ["userId"])

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "WordLists" not in table_names:
        op.create_table(
            "WordLists",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=140), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column(
                "savedWordIds",
                sa.Text(),
                server_default="[]",
                nullable=False,
            ),
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
        op.create_index("ix_WordLists_userId", "WordLists", ["userId"])


def downgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())

    if "WordLists" in table_names:
        op.drop_index("ix_WordLists_userId", table_name="WordLists")
        op.drop_table("WordLists")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "SavedWords" in table_names:
        op.drop_index("ix_SavedWords_userId", table_name="SavedWords")
        op.drop_table("SavedWords")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "DictionaryLookups" in table_names:
        op.drop_index("ix_DictionaryLookups_userId", table_name="DictionaryLookups")
        op.drop_table("DictionaryLookups")
