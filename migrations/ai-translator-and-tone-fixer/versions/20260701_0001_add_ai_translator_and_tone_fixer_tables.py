"""add ai translator and tone fixer tables

Revision ID: 20260701_0001
Revises:
Create Date: 2026-07-01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260701_0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    return bool(bind.dialect.has_table(bind, table_name))


def _index_exists(table_name: str, index_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    if any(index["name"] == index_name for index in inspector.get_indexes(table_name)):
        return True
    bind = op.get_bind()
    result = bind.execute(
        sa.text(
            "SELECT 1 FROM sqlite_master "
            "WHERE type = 'index' AND name = :index_name AND tbl_name = :table_name"
        ),
        {"index_name": index_name, "table_name": table_name},
    ).first()
    return result is not None


def _table_has_columns(table_name: str, required_columns: set[str]) -> bool:
    inspector = sa.inspect(op.get_bind())
    existing_columns = {column["name"] for column in inspector.get_columns(table_name)}
    return required_columns.issubset(existing_columns)


def _drop_index_if_attached_to_table(index_name: str, table_name: str) -> None:
    bind = op.get_bind()
    result = bind.execute(
        sa.text("SELECT tbl_name FROM sqlite_master WHERE type = 'index' AND name = :index_name"),
        {"index_name": index_name},
    ).first()
    if result is not None and result[0] == table_name:
        op.drop_index(index_name, table_name=table_name)


def _create_index_if_missing(index_name: str, table_name: str, columns: list[str]) -> None:
    if not _index_exists(table_name, index_name):
        op.create_index(index_name, table_name, columns, unique=False)


def upgrade() -> None:
    if not _table_exists("TranslationProjects"):
        op.create_table(
            "TranslationProjects",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("sourceLanguage", sa.String(length=80), nullable=True),
            sa.Column("targetLanguage", sa.String(length=80), nullable=True),
            sa.Column("tone", sa.String(length=80), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="draft", nullable=False),
            sa.Column("goal", sa.Text(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
    _create_index_if_missing(op.f("ix_TranslationProjects_ownerId"), "TranslationProjects", ["ownerId"])
    _create_index_if_missing("TranslationProjects_ownerId_updatedAt_title_idx", "TranslationProjects", ["ownerId", "updatedAt", "title"])
    _create_index_if_missing("TranslationProjects_ownerId_status_updatedAt_idx", "TranslationProjects", ["ownerId", "status", "updatedAt"])

    if not _table_exists("Translations"):
        op.create_table(
            "Translations",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("projectId", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("sourceLanguage", sa.String(length=80), nullable=True),
            sa.Column("targetLanguage", sa.String(length=80), nullable=True),
            sa.Column("tone", sa.String(length=80), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="draft", nullable=False),
            sa.Column("sourceText", sa.Text(), nullable=True),
            sa.Column("translatedText", sa.Text(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["projectId"], ["TranslationProjects.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    _create_index_if_missing(op.f("ix_Translations_ownerId"), "Translations", ["ownerId"])
    _create_index_if_missing(op.f("ix_Translations_projectId"), "Translations", ["projectId"])
    _create_index_if_missing("Translations_ownerId_projectId_updatedAt_idx", "Translations", ["ownerId", "projectId", "updatedAt"])
    _create_index_if_missing("Translations_ownerId_status_updatedAt_idx", "Translations", ["ownerId", "status", "updatedAt"])
    _create_index_if_missing("Translations_projectId_status_idx", "Translations", ["projectId", "status"])

    if _table_exists("TranslationTemplates") and not _table_has_columns(
        "TranslationTemplates",
        {"ownerId", "projectId", "templateText", "usageNotes"},
    ):
        if _table_exists("TranslationTemplatesLegacy_20260630"):
            raise RuntimeError("Legacy TranslationTemplates table already exists; manual schema review is required.")
        op.rename_table("TranslationTemplates", "TranslationTemplatesLegacy_20260630")

    if not _table_exists("TranslationTemplates"):
        op.create_table(
            "TranslationTemplates",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("projectId", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("sourceLanguage", sa.String(length=80), nullable=True),
            sa.Column("targetLanguage", sa.String(length=80), nullable=True),
            sa.Column("tone", sa.String(length=80), nullable=True),
            sa.Column("templateText", sa.Text(), nullable=True),
            sa.Column("usageNotes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["projectId"], ["TranslationProjects.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    for index_name in [
        op.f("ix_TranslationTemplates_ownerId"),
        op.f("ix_TranslationTemplates_projectId"),
        "TranslationTemplates_ownerId_projectId_updatedAt_idx",
        "TranslationTemplates_projectId_tone_idx",
    ]:
        _drop_index_if_attached_to_table(index_name, "TranslationTemplatesLegacy_20260630")
    _create_index_if_missing(op.f("ix_TranslationTemplates_ownerId"), "TranslationTemplates", ["ownerId"])
    _create_index_if_missing(op.f("ix_TranslationTemplates_projectId"), "TranslationTemplates", ["projectId"])
    _create_index_if_missing("TranslationTemplates_ownerId_projectId_updatedAt_idx", "TranslationTemplates", ["ownerId", "projectId", "updatedAt"])
    _create_index_if_missing("TranslationTemplates_projectId_tone_idx", "TranslationTemplates", ["projectId", "tone"])

    if not _table_exists("TranslationHistory"):
        op.create_table(
            "TranslationHistory",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("translationId", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("eventType", sa.String(length=80), nullable=True),
            sa.Column("occurredAt", sa.String(length=40), nullable=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("revisionNotes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["translationId"], ["Translations.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    _create_index_if_missing(op.f("ix_TranslationHistory_ownerId"), "TranslationHistory", ["ownerId"])
    _create_index_if_missing(op.f("ix_TranslationHistory_translationId"), "TranslationHistory", ["translationId"])
    _create_index_if_missing("TranslationHistory_ownerId_translationId_occurredAt_idx", "TranslationHistory", ["ownerId", "translationId", "occurredAt"])
    _create_index_if_missing("TranslationHistory_ownerId_updatedAt_title_idx", "TranslationHistory", ["ownerId", "updatedAt", "title"])
    _create_index_if_missing("TranslationHistory_translationId_eventType_idx", "TranslationHistory", ["translationId", "eventType"])


def downgrade() -> None:
    op.drop_index("TranslationHistory_translationId_eventType_idx", table_name="TranslationHistory")
    op.drop_index("TranslationHistory_ownerId_updatedAt_title_idx", table_name="TranslationHistory")
    op.drop_index("TranslationHistory_ownerId_translationId_occurredAt_idx", table_name="TranslationHistory")
    op.drop_index(op.f("ix_TranslationHistory_translationId"), table_name="TranslationHistory")
    op.drop_index(op.f("ix_TranslationHistory_ownerId"), table_name="TranslationHistory")
    op.drop_table("TranslationHistory")

    op.drop_index("TranslationTemplates_projectId_tone_idx", table_name="TranslationTemplates")
    op.drop_index("TranslationTemplates_ownerId_projectId_updatedAt_idx", table_name="TranslationTemplates")
    op.drop_index(op.f("ix_TranslationTemplates_projectId"), table_name="TranslationTemplates")
    op.drop_index(op.f("ix_TranslationTemplates_ownerId"), table_name="TranslationTemplates")
    op.drop_table("TranslationTemplates")

    op.drop_index("Translations_projectId_status_idx", table_name="Translations")
    op.drop_index("Translations_ownerId_status_updatedAt_idx", table_name="Translations")
    op.drop_index("Translations_ownerId_projectId_updatedAt_idx", table_name="Translations")
    op.drop_index(op.f("ix_Translations_projectId"), table_name="Translations")
    op.drop_index(op.f("ix_Translations_ownerId"), table_name="Translations")
    op.drop_table("Translations")

    op.drop_index("TranslationProjects_ownerId_status_updatedAt_idx", table_name="TranslationProjects")
    op.drop_index("TranslationProjects_ownerId_updatedAt_title_idx", table_name="TranslationProjects")
    op.drop_index(op.f("ix_TranslationProjects_ownerId"), table_name="TranslationProjects")
    op.drop_table("TranslationProjects")
