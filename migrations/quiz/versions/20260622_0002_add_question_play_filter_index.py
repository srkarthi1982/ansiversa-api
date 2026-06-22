"""add_question_play_filter_index

Revision ID: 20260622_0002
Revises: 20260607_0001
Create Date: 2026-06-22

"""
from collections.abc import Sequence

from alembic import op


revision: str = "20260622_0002"
down_revision: str | None = "20260607_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS "ix_Question_play_filter"
        ON "Question" (
            "platformId",
            "subjectId",
            "topicId",
            "roadmapId",
            "l",
            "isActive"
        )
        """
    )


def downgrade() -> None:
    op.execute('DROP INDEX IF EXISTS "ix_Question_play_filter"')
