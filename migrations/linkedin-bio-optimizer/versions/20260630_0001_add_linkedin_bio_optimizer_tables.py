"""add_linkedin_bio_optimizer_tables

Revision ID: 20260630_0001
Revises:
Create Date: 2026-06-30

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260630_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


INDEXES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("LinkedInProfiles_ownerId_updatedAt_title_idx", "LinkedInProfiles", ("ownerId", "updatedAt", "title")),
    ("LinkedInProfiles_ownerId_platformId_idx", "LinkedInProfiles", ("ownerId", "platformId")),
    ("LinkedInProfiles_ownerId_industry_careerLevel_idx", "LinkedInProfiles", ("ownerId", "industry", "careerLevel")),
    ("BioTemplates_ownerId_updatedAt_name_idx", "BioTemplates", ("ownerId", "updatedAt", "name")),
    ("BioTemplates_ownerId_industry_careerLevel_idx", "BioTemplates", ("ownerId", "industry", "careerLevel")),
    ("BioTemplates_ownerId_isDefault_idx", "BioTemplates", ("ownerId", "isDefault")),
    ("BioVersions_ownerId_profileId_versionNumber_idx", "BioVersions", ("ownerId", "profileId", "versionNumber")),
    ("BioVersions_ownerId_createdAt_idx", "BioVersions", ("ownerId", "createdAt")),
)


def _table_names() -> set[str]:
    return set(sa.inspect(op.get_bind()).get_table_names())


def _index_names(table_name: str) -> set[str]:
    return {index["name"] for index in sa.inspect(op.get_bind()).get_indexes(table_name)}


def _create_index(name: str, table_name: str, columns: tuple[str, ...]) -> None:
    if table_name not in _table_names() or name in _index_names(table_name):
        return
    op.create_index(name, table_name, list(columns), unique=False)


def _drop_index(name: str, table_name: str) -> None:
    if table_name not in _table_names() or name not in _index_names(table_name):
        return
    op.drop_index(name, table_name=table_name)


def upgrade() -> None:
    table_names = _table_names()

    if "LinkedInProfiles" not in table_names:
        op.create_table(
            "LinkedInProfiles",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("industry", sa.String(length=120), nullable=True),
            sa.Column("careerLevel", sa.String(length=80), nullable=True),
            sa.Column("targetRole", sa.String(length=180), nullable=True),
            sa.Column("currentHeadline", sa.String(length=220), nullable=True),
            sa.Column("currentBio", sa.Text(), nullable=True),
            sa.Column("optimizedBio", sa.Text(), nullable=True),
            sa.Column("keywords", sa.Text(), nullable=True),
            sa.Column("tone", sa.String(length=80), nullable=True),
            sa.Column("language", sa.String(length=80), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_LinkedInProfiles_ownerId", "LinkedInProfiles", ["ownerId"])

    table_names = _table_names()
    if "BioTemplates" not in table_names:
        op.create_table(
            "BioTemplates",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("name", sa.String(length=180), nullable=False),
            sa.Column("industry", sa.String(length=120), nullable=True),
            sa.Column("careerLevel", sa.String(length=80), nullable=True),
            sa.Column("template", sa.Text(), nullable=False),
            sa.Column("isDefault", sa.Boolean(), server_default="0", nullable=False),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_BioTemplates_ownerId", "BioTemplates", ["ownerId"])

    table_names = _table_names()
    if "BioVersions" not in table_names:
        op.create_table(
            "BioVersions",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("profileId", sa.Integer(), nullable=False),
            sa.Column("versionNumber", sa.Integer(), nullable=False),
            sa.Column("headline", sa.String(length=220), nullable=True),
            sa.Column("bio", sa.Text(), nullable=False),
            sa.Column("changeSummary", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["profileId"], ["LinkedInProfiles.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_BioVersions_ownerId", "BioVersions", ["ownerId"])
        op.create_index("ix_BioVersions_profileId", "BioVersions", ["profileId"])

    for name, table_name, columns in INDEXES:
        _create_index(name, table_name, columns)


def downgrade() -> None:
    for name, table_name, _columns in reversed(INDEXES):
        _drop_index(name, table_name)

    table_names = _table_names()
    if "BioVersions" in table_names:
        op.drop_index("ix_BioVersions_profileId", table_name="BioVersions")
        op.drop_index("ix_BioVersions_ownerId", table_name="BioVersions")
        op.drop_table("BioVersions")

    table_names = _table_names()
    if "BioTemplates" in table_names:
        op.drop_index("ix_BioTemplates_ownerId", table_name="BioTemplates")
        op.drop_table("BioTemplates")

    table_names = _table_names()
    if "LinkedInProfiles" in table_names:
        op.drop_index("ix_LinkedInProfiles_ownerId", table_name="LinkedInProfiles")
        op.drop_table("LinkedInProfiles")
