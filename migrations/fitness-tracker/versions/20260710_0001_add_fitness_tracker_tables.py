"""add fitness tracker tables

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
        "FitnessActivities",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("userId", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("activityType", sa.String(length=40), nullable=False),
        sa.Column("defaultDurationMinutes", sa.Integer(), nullable=True),
        sa.Column("intensity", sa.String(length=40), server_default="moderate", nullable=False),
        sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_FitnessActivities_userId", "FitnessActivities", ["userId"])
    op.create_index("ix_FitnessActivities_activityType", "FitnessActivities", ["activityType"])
    op.create_index("ix_FitnessActivities_updatedAt", "FitnessActivities", ["updatedAt"])

    op.create_table(
        "FitnessLogs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("userId", sa.String(length=36), nullable=False),
        sa.Column("activityId", sa.String(length=36), nullable=False),
        sa.Column("logDate", sa.String(length=40), nullable=False),
        sa.Column("durationMinutes", sa.Integer(), nullable=False),
        sa.Column("intensity", sa.String(length=40), server_default="moderate", nullable=False),
        sa.Column("effort", sa.Integer(), nullable=True),
        sa.Column("distanceValue", sa.Float(), nullable=True),
        sa.Column("distanceUnit", sa.String(length=20), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["activityId"], ["FitnessActivities.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_FitnessLogs_userId", "FitnessLogs", ["userId"])
    op.create_index("ix_FitnessLogs_activityId", "FitnessLogs", ["activityId"])
    op.create_index("ix_FitnessLogs_logDate", "FitnessLogs", ["logDate"])
    op.create_index("ix_FitnessLogs_updatedAt", "FitnessLogs", ["updatedAt"])


def downgrade() -> None:
    op.drop_index("ix_FitnessLogs_updatedAt", table_name="FitnessLogs")
    op.drop_index("ix_FitnessLogs_logDate", table_name="FitnessLogs")
    op.drop_index("ix_FitnessLogs_activityId", table_name="FitnessLogs")
    op.drop_index("ix_FitnessLogs_userId", table_name="FitnessLogs")
    op.drop_table("FitnessLogs")
    op.drop_index("ix_FitnessActivities_updatedAt", table_name="FitnessActivities")
    op.drop_index("ix_FitnessActivities_activityType", table_name="FitnessActivities")
    op.drop_index("ix_FitnessActivities_userId", table_name="FitnessActivities")
    op.drop_table("FitnessActivities")
