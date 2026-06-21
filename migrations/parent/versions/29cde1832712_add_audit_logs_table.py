"""add_audit_logs_table

Revision ID: 29cde1832712
Revises: f77b530bd019
Create Date: 2026-05-29 19:10:37.203289

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "29cde1832712"
down_revision: str | None = "f77b530bd019"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "AuditLogs" in table_names:
        return

    op.create_table(
        "AuditLogs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("actorUserId", sa.String(length=36), nullable=True),
        sa.Column("actorEmail", sa.String(length=255), nullable=True),
        sa.Column("action", sa.String(length=120), nullable=False),
        sa.Column("entityType", sa.String(length=120), nullable=False),
        sa.Column("entityId", sa.String(length=255), nullable=True),
        sa.Column("entityLabel", sa.String(length=500), nullable=True),
        sa.Column("metadataJson", sa.Text(), nullable=True),
        sa.Column("ipAddress", sa.String(length=120), nullable=True),
        sa.Column("userAgent", sa.String(length=500), nullable=True),
        sa.Column(
            "createdAt",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["actorUserId"], ["Users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "AuditLogs_actorUserId_createdAt_idx",
        "AuditLogs",
        ["actorUserId", "createdAt"],
        unique=False,
    )
    op.create_index(
        "AuditLogs_entityType_entityId_idx",
        "AuditLogs",
        ["entityType", "entityId"],
        unique=False,
    )


def downgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "AuditLogs" not in table_names:
        return

    op.drop_index("AuditLogs_entityType_entityId_idx", table_name="AuditLogs")
    op.drop_index("AuditLogs_actorUserId_createdAt_idx", table_name="AuditLogs")
    op.drop_table("AuditLogs")
