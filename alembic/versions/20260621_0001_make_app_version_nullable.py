"""make_app_version_nullable

Revision ID: 20260621_0001
Revises: 20260620_0001
Create Date: 2026-06-21 09:08:00.000000

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260621_0001"
down_revision: str | None = "20260620_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "Apps" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("Apps")}
    op.execute(sa.text('DROP TABLE IF EXISTS "_alembic_tmp_Apps"'))
    op.execute(sa.text("PRAGMA foreign_keys=OFF"))
    try:
        if "version" not in columns:
            op.add_column("Apps", sa.Column("version", sa.String(length=20), nullable=True))
        else:
            with op.batch_alter_table("Apps") as batch_op:
                batch_op.alter_column(
                    "version",
                    existing_type=sa.String(length=20),
                    nullable=True,
                    server_default=None,
                )
    finally:
        op.execute(sa.text("PRAGMA foreign_keys=ON"))

    op.execute(
        sa.text(
            'UPDATE "Apps" '
            'SET version = CASE WHEN "launchStatus" = :live THEN :version ELSE NULL END'
        ).bindparams(live="live", version="1.0.0")
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "Apps" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("Apps")}
    if "version" not in columns:
        return

    op.execute(sa.text('DROP TABLE IF EXISTS "_alembic_tmp_Apps"'))
    op.execute(
        sa.text(
            'UPDATE "Apps" SET version = :version '
            'WHERE version IS NULL OR version = ""'
        ).bindparams(version="1.0.0")
    )
    op.execute(sa.text("PRAGMA foreign_keys=OFF"))
    try:
        with op.batch_alter_table("Apps") as batch_op:
            batch_op.alter_column(
                "version",
                existing_type=sa.String(length=20),
                nullable=False,
                server_default="1.0.0",
            )
    finally:
        op.execute(sa.text("PRAGMA foreign_keys=ON"))
