"""add_faqs_table

Revision ID: f77b530bd019
Revises: 2eb46b63af6d
Create Date: 2026-05-29 18:52:22.174065

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "f77b530bd019"
down_revision: str | None = "2eb46b63af6d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "Faqs" in table_names:
        return

    op.create_table(
        "Faqs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("sortOrder", sa.Integer(), server_default="0", nullable=False),
        sa.Column("appKey", sa.String(length=120), nullable=True),
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
        sa.Column("audience", sa.String(length=80), server_default="user", nullable=False),
        sa.Column("category", sa.String(length=120), nullable=True),
        sa.Column("answer_md", sa.Text(), nullable=True),
        sa.Column("is_published", sa.Boolean(), server_default="0", nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "Faqs_appKey_audience_is_published_idx",
        "Faqs",
        ["appKey", "audience", "is_published"],
        unique=False,
    )
    op.create_index(
        "Faqs_sortOrder_createdAt_idx",
        "Faqs",
        ["sortOrder", "createdAt"],
        unique=False,
    )


def downgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "Faqs" not in table_names:
        return

    op.drop_index("Faqs_sortOrder_createdAt_idx", table_name="Faqs")
    op.drop_index("Faqs_appKey_audience_is_published_idx", table_name="Faqs")
    op.drop_table("Faqs")
