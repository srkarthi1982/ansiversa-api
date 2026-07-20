"""add activity timeline

Revision ID: 20260720_0002
Revises: 20260720_0001
"""
from collections.abc import Sequence
from alembic import op
import sqlalchemy as sa

revision: str = "20260720_0002"
down_revision: str | None = "20260720_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    if "ActivityTimeline" in set(sa.inspect(op.get_bind()).get_table_names()): return
    op.create_table("ActivityTimeline",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("userId", sa.String(36), nullable=False),
        sa.Column("activityType", sa.String(40), nullable=False),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("description", sa.String(300), nullable=True),
        sa.Column("source", sa.String(40), nullable=False),
        sa.Column("sourceAppId", sa.String(36), nullable=True),
        sa.Column("actionRoute", sa.String(500), nullable=True),
        sa.Column("actionLabel", sa.String(120), nullable=True),
        sa.Column("entityType", sa.String(80), nullable=True),
        sa.Column("entityId", sa.String(120), nullable=True),
        sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["userId"], ["Users.id"]),
        sa.ForeignKeyConstraint(["sourceAppId"], ["Apps.id"]),
    )
    op.create_index("ActivityTimeline_userId_createdAt_idx", "ActivityTimeline", ["userId", "createdAt"])
    op.create_index("ActivityTimeline_userId_activityType_createdAt_idx", "ActivityTimeline", ["userId", "activityType", "createdAt"])


def downgrade() -> None:
    if "ActivityTimeline" not in set(sa.inspect(op.get_bind()).get_table_names()): return
    op.drop_index("ActivityTimeline_userId_activityType_createdAt_idx", table_name="ActivityTimeline")
    op.drop_index("ActivityTimeline_userId_createdAt_idx", table_name="ActivityTimeline")
    op.drop_table("ActivityTimeline")
