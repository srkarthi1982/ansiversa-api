"""merge_metadata_and_user_settings

Revision ID: 9e3789be923b
Revises: 6a0fd846f731, 20260610_0001
Create Date: 2026-06-11 00:29:55.129622

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa



revision: str = '9e3789be923b'
down_revision: str | None = ('6a0fd846f731', '20260610_0001')
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
