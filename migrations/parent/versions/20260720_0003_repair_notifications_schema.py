"""repair notifications schema

Revision ID: 20260720_0003
Revises: 20260720_0002
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260720_0003"
down_revision: str | None = "20260720_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _column_names(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    if table_name not in set(inspector.get_table_names()):
        return set()
    return {column["name"] for column in inspector.get_columns(table_name)}


def _index_names(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    if table_name not in set(inspector.get_table_names()):
        return set()
    return {index["name"] for index in inspector.get_indexes(table_name)}


def upgrade() -> None:
    columns = _column_names("Notifications")
    if not columns:
        return

    if "message" not in columns:
        op.add_column("Notifications", sa.Column("message", sa.Text(), nullable=True))
    if "isRead" not in columns:
        op.add_column("Notifications", sa.Column("isRead", sa.Boolean(), server_default="0", nullable=False))
    if "metadataJson" not in columns:
        op.add_column("Notifications", sa.Column("metadataJson", sa.Text(), nullable=True))

    indexes = _index_names("Notifications")
    if "Notifications_userId_isRead_createdAt_idx" in indexes:
        op.drop_index("Notifications_userId_isRead_createdAt_idx", table_name="Notifications")
    if "Notifications_userId_isRead_idx" in indexes:
        op.drop_index("Notifications_userId_isRead_idx", table_name="Notifications")

    refreshed_columns = _column_names("Notifications")
    if {"body", "message"} <= refreshed_columns:
        op.execute(sa.text('UPDATE "Notifications" SET "message" = "body" WHERE "message" IS NULL'))
    if {"readAt", "isRead"} <= refreshed_columns:
        op.execute(sa.text('UPDATE "Notifications" SET "isRead" = 1 WHERE "readAt" IS NOT NULL'))

    indexes = _index_names("Notifications")
    if "Notifications_userId_isRead_idx" not in indexes:
        op.create_index("Notifications_userId_isRead_idx", "Notifications", ["userId", "isRead"])
    if "Notifications_userId_isRead_createdAt_idx" not in indexes:
        op.create_index(
            "Notifications_userId_isRead_createdAt_idx",
            "Notifications",
            ["userId", "isRead", "createdAt"],
        )


def downgrade() -> None:
    indexes = _index_names("Notifications")
    if "Notifications_userId_isRead_createdAt_idx" in indexes:
        op.drop_index("Notifications_userId_isRead_createdAt_idx", table_name="Notifications")
    if "Notifications_userId_isRead_idx" in indexes:
        op.drop_index("Notifications_userId_isRead_idx", table_name="Notifications")

    columns = _column_names("Notifications")
    for name in ("metadataJson", "isRead", "message"):
        if name in columns:
            op.drop_column("Notifications", name)
