"""notifications center phase 1

Revision ID: 20260720_0001
Revises: 20260703_0001
"""
from collections.abc import Sequence
from alembic import op
import sqlalchemy as sa

revision: str = "20260720_0001"
down_revision: str | None = "20260703_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    preference_columns = {column["name"] for column in inspector.get_columns("UserPreferences")}
    for name in ("notificationsEnabled", "reminderNotificationsEnabled", "systemNotificationsEnabled"):
        if name not in preference_columns:
            op.add_column("UserPreferences", sa.Column(name, sa.Boolean(), server_default="1", nullable=False))
    indexes = {index["name"] for index in inspector.get_indexes("Notifications")}
    if "Notifications_userId_createdAt_idx" not in indexes:
        op.create_index("Notifications_userId_createdAt_idx", "Notifications", ["userId", "createdAt"])


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    indexes = {index["name"] for index in inspector.get_indexes("Notifications")}
    if "Notifications_userId_createdAt_idx" in indexes:
        op.drop_index("Notifications_userId_createdAt_idx", table_name="Notifications")
    preference_columns = {column["name"] for column in inspector.get_columns("UserPreferences")}
    for name in ("systemNotificationsEnabled", "reminderNotificationsEnabled", "notificationsEnabled"):
        if name in preference_columns:
            op.drop_column("UserPreferences", name)
