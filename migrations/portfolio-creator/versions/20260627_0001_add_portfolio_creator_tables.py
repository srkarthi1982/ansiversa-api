"""add_portfolio_creator_tables

Revision ID: 20260627_0001
Revises:
Create Date: 2026-06-27

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260627_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())

    if "PortfolioProfiles" not in table_names:
        op.create_table(
            "PortfolioProfiles",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("displayName", sa.String(length=140), nullable=False),
            sa.Column("headline", sa.String(length=180), nullable=False),
            sa.Column("summary", sa.Text(), nullable=True),
            sa.Column("location", sa.String(length=140), nullable=True),
            sa.Column("websiteUrl", sa.String(length=240), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="draft", nullable=False),
            sa.Column(
                "createdAt",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updatedAt",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_PortfolioProfiles_ownerId", "PortfolioProfiles", ["ownerId"])

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "PortfolioProjects" not in table_names:
        op.create_table(
            "PortfolioProjects",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("profileId", sa.Integer(), nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("projectUrl", sa.String(length=240), nullable=True),
            sa.Column("role", sa.String(length=140), nullable=True),
            sa.Column("position", sa.Integer(), server_default="1", nullable=False),
            sa.Column("status", sa.String(length=40), server_default="draft", nullable=False),
            sa.Column(
                "createdAt",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updatedAt",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["profileId"], ["PortfolioProfiles.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_PortfolioProjects_ownerId", "PortfolioProjects", ["ownerId"])
        op.create_index("ix_PortfolioProjects_profileId", "PortfolioProjects", ["profileId"])

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "PortfolioSkills" not in table_names:
        op.create_table(
            "PortfolioSkills",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("profileId", sa.Integer(), nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("name", sa.String(length=120), nullable=False),
            sa.Column("category", sa.String(length=80), server_default="technical", nullable=False),
            sa.Column(
                "proficiency",
                sa.String(length=40),
                server_default="intermediate",
                nullable=False,
            ),
            sa.Column("position", sa.Integer(), server_default="1", nullable=False),
            sa.Column(
                "createdAt",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updatedAt",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["profileId"], ["PortfolioProfiles.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_PortfolioSkills_ownerId", "PortfolioSkills", ["ownerId"])
        op.create_index("ix_PortfolioSkills_profileId", "PortfolioSkills", ["profileId"])

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "PortfolioPublishSettings" not in table_names:
        op.create_table(
            "PortfolioPublishSettings",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("profileId", sa.Integer(), nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("visibility", sa.String(length=40), server_default="private", nullable=False),
            sa.Column("slug", sa.String(length=120), nullable=False),
            sa.Column("theme", sa.String(length=40), server_default="classic", nullable=False),
            sa.Column("isPublished", sa.Boolean(), server_default="0", nullable=False),
            sa.Column(
                "createdAt",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updatedAt",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["profileId"], ["PortfolioProfiles.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            "ix_PortfolioPublishSettings_ownerId",
            "PortfolioPublishSettings",
            ["ownerId"],
        )
        op.create_index(
            "ix_PortfolioPublishSettings_profileId",
            "PortfolioPublishSettings",
            ["profileId"],
        )


def downgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())

    if "PortfolioPublishSettings" in table_names:
        op.drop_index(
            "ix_PortfolioPublishSettings_profileId",
            table_name="PortfolioPublishSettings",
        )
        op.drop_index(
            "ix_PortfolioPublishSettings_ownerId",
            table_name="PortfolioPublishSettings",
        )
        op.drop_table("PortfolioPublishSettings")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "PortfolioSkills" in table_names:
        op.drop_index("ix_PortfolioSkills_profileId", table_name="PortfolioSkills")
        op.drop_index("ix_PortfolioSkills_ownerId", table_name="PortfolioSkills")
        op.drop_table("PortfolioSkills")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "PortfolioProjects" in table_names:
        op.drop_index("ix_PortfolioProjects_profileId", table_name="PortfolioProjects")
        op.drop_index("ix_PortfolioProjects_ownerId", table_name="PortfolioProjects")
        op.drop_table("PortfolioProjects")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "PortfolioProfiles" in table_names:
        op.drop_index("ix_PortfolioProfiles_ownerId", table_name="PortfolioProfiles")
        op.drop_table("PortfolioProfiles")
