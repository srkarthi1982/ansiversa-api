"""add_meeting_minutes_ai_tables

Revision ID: 20260627_0001
Revises:
Create Date: 2026-06-27

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260627_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())

    if "MeetingMinutesMeetings" not in table_names:
        op.create_table(
            "MeetingMinutesMeetings",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("meetingDate", sa.Date(), nullable=True),
            sa.Column("participants", sa.Text(), nullable=True),
            sa.Column("context", sa.Text(), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="draft", nullable=False),
            sa.Column(
                "createdAt",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updatedAt",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            "ix_MeetingMinutesMeetings_ownerId",
            "MeetingMinutesMeetings",
            ["ownerId"],
        )

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "MeetingMinutesNotes" not in table_names:
        op.create_table(
            "MeetingMinutesNotes",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("meetingId", sa.Integer(), nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("noteType", sa.String(length=40), server_default="notes", nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column(
                "createdAt",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updatedAt",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["meetingId"], ["MeetingMinutesMeetings.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_MeetingMinutesNotes_meetingId", "MeetingMinutesNotes", ["meetingId"])
        op.create_index("ix_MeetingMinutesNotes_ownerId", "MeetingMinutesNotes", ["ownerId"])

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "MeetingMinutesActionItems" not in table_names:
        op.create_table(
            "MeetingMinutesActionItems",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("meetingId", sa.Integer(), nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("ownerName", sa.String(length=140), nullable=True),
            sa.Column("dueDate", sa.Date(), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="open", nullable=False),
            sa.Column(
                "createdAt",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updatedAt",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["meetingId"], ["MeetingMinutesMeetings.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            "ix_MeetingMinutesActionItems_meetingId",
            "MeetingMinutesActionItems",
            ["meetingId"],
        )
        op.create_index(
            "ix_MeetingMinutesActionItems_ownerId",
            "MeetingMinutesActionItems",
            ["ownerId"],
        )

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "MeetingMinutesSummaries" not in table_names:
        op.create_table(
            "MeetingMinutesSummaries",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("meetingId", sa.Integer(), nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("summaryText", sa.Text(), nullable=False),
            sa.Column("decisions", sa.Text(), nullable=True),
            sa.Column("risks", sa.Text(), nullable=True),
            sa.Column(
                "createdAt",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updatedAt",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["meetingId"], ["MeetingMinutesMeetings.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            "ix_MeetingMinutesSummaries_meetingId",
            "MeetingMinutesSummaries",
            ["meetingId"],
        )
        op.create_index(
            "ix_MeetingMinutesSummaries_ownerId",
            "MeetingMinutesSummaries",
            ["ownerId"],
        )


def downgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())

    if "MeetingMinutesSummaries" in table_names:
        op.drop_index(
            "ix_MeetingMinutesSummaries_ownerId",
            table_name="MeetingMinutesSummaries",
        )
        op.drop_index(
            "ix_MeetingMinutesSummaries_meetingId",
            table_name="MeetingMinutesSummaries",
        )
        op.drop_table("MeetingMinutesSummaries")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "MeetingMinutesActionItems" in table_names:
        op.drop_index(
            "ix_MeetingMinutesActionItems_ownerId",
            table_name="MeetingMinutesActionItems",
        )
        op.drop_index(
            "ix_MeetingMinutesActionItems_meetingId",
            table_name="MeetingMinutesActionItems",
        )
        op.drop_table("MeetingMinutesActionItems")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "MeetingMinutesNotes" in table_names:
        op.drop_index("ix_MeetingMinutesNotes_ownerId", table_name="MeetingMinutesNotes")
        op.drop_index("ix_MeetingMinutesNotes_meetingId", table_name="MeetingMinutesNotes")
        op.drop_table("MeetingMinutesNotes")

    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "MeetingMinutesMeetings" in table_names:
        op.drop_index(
            "ix_MeetingMinutesMeetings_ownerId",
            table_name="MeetingMinutesMeetings",
        )
        op.drop_table("MeetingMinutesMeetings")
