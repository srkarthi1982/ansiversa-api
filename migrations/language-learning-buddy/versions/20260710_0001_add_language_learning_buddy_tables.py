"""add language learning buddy tables

Revision ID: 20260710_0001
Revises:
Create Date: 2026-07-10
"""
from alembic import op
import sqlalchemy as sa

revision = "20260710_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "LanguageVocabulary",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("userId", sa.String(length=36), nullable=False),
        sa.Column("word", sa.String(length=180), nullable=False),
        sa.Column("translation", sa.String(length=180), nullable=False),
        sa.Column("language", sa.String(length=80), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=True),
        sa.Column("difficulty", sa.String(length=40), server_default="new", nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_LanguageVocabulary_userId", "LanguageVocabulary", ["userId"])
    op.create_index("ix_LanguageVocabulary_language", "LanguageVocabulary", ["language"])
    op.create_index("ix_LanguageVocabulary_category", "LanguageVocabulary", ["category"])
    op.create_index("ix_LanguageVocabulary_updatedAt", "LanguageVocabulary", ["updatedAt"])

    op.create_table(
        "LanguagePracticeSessions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("userId", sa.String(length=36), nullable=False),
        sa.Column("vocabularyId", sa.String(length=36), nullable=False),
        sa.Column("practicedAt", sa.String(length=40), nullable=False),
        sa.Column("result", sa.String(length=40), nullable=False),
        sa.Column("confidence", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["vocabularyId"], ["LanguageVocabulary.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_LanguagePracticeSessions_userId", "LanguagePracticeSessions", ["userId"])
    op.create_index("ix_LanguagePracticeSessions_vocabularyId", "LanguagePracticeSessions", ["vocabularyId"])
    op.create_index("ix_LanguagePracticeSessions_practicedAt", "LanguagePracticeSessions", ["practicedAt"])
    op.create_index("ix_LanguagePracticeSessions_result", "LanguagePracticeSessions", ["result"])
    op.create_index("ix_LanguagePracticeSessions_updatedAt", "LanguagePracticeSessions", ["updatedAt"])


def downgrade() -> None:
    op.drop_index("ix_LanguagePracticeSessions_updatedAt", table_name="LanguagePracticeSessions")
    op.drop_index("ix_LanguagePracticeSessions_result", table_name="LanguagePracticeSessions")
    op.drop_index("ix_LanguagePracticeSessions_practicedAt", table_name="LanguagePracticeSessions")
    op.drop_index("ix_LanguagePracticeSessions_vocabularyId", table_name="LanguagePracticeSessions")
    op.drop_index("ix_LanguagePracticeSessions_userId", table_name="LanguagePracticeSessions")
    op.drop_table("LanguagePracticeSessions")
    op.drop_index("ix_LanguageVocabulary_updatedAt", table_name="LanguageVocabulary")
    op.drop_index("ix_LanguageVocabulary_category", table_name="LanguageVocabulary")
    op.drop_index("ix_LanguageVocabulary_language", table_name="LanguageVocabulary")
    op.drop_index("ix_LanguageVocabulary_userId", table_name="LanguageVocabulary")
    op.drop_table("LanguageVocabulary")
