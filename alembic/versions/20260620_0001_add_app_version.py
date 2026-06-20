"""add_app_version

Revision ID: 20260620_0001
Revises: 20260613_0001
Create Date: 2026-06-20 14:45:00.000000

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260620_0001"
down_revision: str | None = "20260613_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = inspector.get_table_names()

    if "Apps" not in table_names:
        return

    columns = {column["name"] for column in inspector.get_columns("Apps")}
    if "version" in columns:
        op.execute(
            sa.text(
                'UPDATE "Apps" SET version = :version '
                'WHERE version IS NULL OR version = ""'
            ).bindparams(version="1.0.0")
        )
        return

    op.add_column(
        "Apps",
        sa.Column(
            "version",
            sa.String(length=20),
            server_default="1.0.0",
            nullable=False,
        ),
    )
    op.execute(
        sa.text(
            'UPDATE "Apps" SET version = :version '
            'WHERE version IS NULL OR version = ""'
        ).bindparams(version="1.0.0")
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = inspector.get_table_names()

    if "Apps" not in table_names:
        return

    columns = {column["name"] for column in inspector.get_columns("Apps")}
    if "version" not in columns:
        return

    with op.batch_alter_table("Apps") as batch_op:
        batch_op.drop_column("version")
