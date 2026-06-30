"""add social caption generator tables

Revision ID: 20260630_0001
Revises:
Create Date: 2026-06-30
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260630_0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "CaptionProjects",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ownerId", sa.String(length=36), nullable=False),
        sa.Column("platformId", sa.String(length=120), nullable=True),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("platform", sa.String(length=80), nullable=True),
        sa.Column("audience", sa.String(length=180), nullable=True),
        sa.Column("tone", sa.String(length=80), nullable=True),
        sa.Column("status", sa.String(length=40), server_default="draft", nullable=False),
        sa.Column("campaignBrief", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_CaptionProjects_ownerId"), "CaptionProjects", ["ownerId"], unique=False)
    op.create_index("CaptionProjects_ownerId_updatedAt_title_idx", "CaptionProjects", ["ownerId", "updatedAt", "title"], unique=False)
    op.create_index("CaptionProjects_ownerId_status_platform_idx", "CaptionProjects", ["ownerId", "status", "platform"], unique=False)

    op.create_table(
        "SocialCaptions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ownerId", sa.String(length=36), nullable=False),
        sa.Column("platformId", sa.String(length=120), nullable=True),
        sa.Column("projectId", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("platform", sa.String(length=80), nullable=True),
        sa.Column("status", sa.String(length=40), server_default="draft", nullable=False),
        sa.Column("captionText", sa.Text(), nullable=True),
        sa.Column("hashtags", sa.Text(), nullable=True),
        sa.Column("callToAction", sa.String(length=240), nullable=True),
        sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["projectId"], ["CaptionProjects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_SocialCaptions_ownerId"), "SocialCaptions", ["ownerId"], unique=False)
    op.create_index(op.f("ix_SocialCaptions_projectId"), "SocialCaptions", ["projectId"], unique=False)
    op.create_index("SocialCaptions_ownerId_projectId_updatedAt_idx", "SocialCaptions", ["ownerId", "projectId", "updatedAt"], unique=False)
    op.create_index("SocialCaptions_ownerId_status_platform_idx", "SocialCaptions", ["ownerId", "status", "platform"], unique=False)
    op.create_index("SocialCaptions_projectId_status_idx", "SocialCaptions", ["projectId", "status"], unique=False)

    op.create_table(
        "CaptionTemplates",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ownerId", sa.String(length=36), nullable=False),
        sa.Column("platformId", sa.String(length=120), nullable=True),
        sa.Column("projectId", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("platform", sa.String(length=80), nullable=True),
        sa.Column("tone", sa.String(length=80), nullable=True),
        sa.Column("templateText", sa.Text(), nullable=True),
        sa.Column("usageNotes", sa.Text(), nullable=True),
        sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["projectId"], ["CaptionProjects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_CaptionTemplates_ownerId"), "CaptionTemplates", ["ownerId"], unique=False)
    op.create_index(op.f("ix_CaptionTemplates_projectId"), "CaptionTemplates", ["projectId"], unique=False)
    op.create_index("CaptionTemplates_ownerId_projectId_updatedAt_idx", "CaptionTemplates", ["ownerId", "projectId", "updatedAt"], unique=False)
    op.create_index("CaptionTemplates_projectId_platform_idx", "CaptionTemplates", ["projectId", "platform"], unique=False)

    op.create_table(
        "CaptionHistory",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ownerId", sa.String(length=36), nullable=False),
        sa.Column("platformId", sa.String(length=120), nullable=True),
        sa.Column("captionId", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("eventType", sa.String(length=80), nullable=True),
        sa.Column("occurredAt", sa.String(length=40), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("revisionNotes", sa.Text(), nullable=True),
        sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["captionId"], ["SocialCaptions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_CaptionHistory_captionId"), "CaptionHistory", ["captionId"], unique=False)
    op.create_index(op.f("ix_CaptionHistory_ownerId"), "CaptionHistory", ["ownerId"], unique=False)
    op.create_index("CaptionHistory_ownerId_captionId_occurredAt_idx", "CaptionHistory", ["ownerId", "captionId", "occurredAt"], unique=False)
    op.create_index("CaptionHistory_ownerId_updatedAt_title_idx", "CaptionHistory", ["ownerId", "updatedAt", "title"], unique=False)
    op.create_index("CaptionHistory_captionId_eventType_idx", "CaptionHistory", ["captionId", "eventType"], unique=False)


def downgrade() -> None:
    op.drop_index("CaptionHistory_captionId_eventType_idx", table_name="CaptionHistory")
    op.drop_index("CaptionHistory_ownerId_updatedAt_title_idx", table_name="CaptionHistory")
    op.drop_index("CaptionHistory_ownerId_captionId_occurredAt_idx", table_name="CaptionHistory")
    op.drop_index(op.f("ix_CaptionHistory_ownerId"), table_name="CaptionHistory")
    op.drop_index(op.f("ix_CaptionHistory_captionId"), table_name="CaptionHistory")
    op.drop_table("CaptionHistory")

    op.drop_index("CaptionTemplates_projectId_platform_idx", table_name="CaptionTemplates")
    op.drop_index("CaptionTemplates_ownerId_projectId_updatedAt_idx", table_name="CaptionTemplates")
    op.drop_index(op.f("ix_CaptionTemplates_projectId"), table_name="CaptionTemplates")
    op.drop_index(op.f("ix_CaptionTemplates_ownerId"), table_name="CaptionTemplates")
    op.drop_table("CaptionTemplates")

    op.drop_index("SocialCaptions_projectId_status_idx", table_name="SocialCaptions")
    op.drop_index("SocialCaptions_ownerId_status_platform_idx", table_name="SocialCaptions")
    op.drop_index("SocialCaptions_ownerId_projectId_updatedAt_idx", table_name="SocialCaptions")
    op.drop_index(op.f("ix_SocialCaptions_projectId"), table_name="SocialCaptions")
    op.drop_index(op.f("ix_SocialCaptions_ownerId"), table_name="SocialCaptions")
    op.drop_table("SocialCaptions")

    op.drop_index("CaptionProjects_ownerId_status_platform_idx", table_name="CaptionProjects")
    op.drop_index("CaptionProjects_ownerId_updatedAt_title_idx", table_name="CaptionProjects")
    op.drop_index(op.f("ix_CaptionProjects_ownerId"), table_name="CaptionProjects")
    op.drop_table("CaptionProjects")
