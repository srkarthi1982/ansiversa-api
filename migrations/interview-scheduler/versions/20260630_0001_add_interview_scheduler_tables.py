"""add_interview_scheduler_tables

Revision ID: 20260630_0001
Revises:
Create Date: 2026-06-30

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260630_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


INDEXES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("InterviewSchedules_ownerId_updatedAt_candidateName_idx", "InterviewSchedules", ("ownerId", "updatedAt", "candidateName")),
    ("InterviewSchedules_ownerId_status_targetDate_idx", "InterviewSchedules", ("ownerId", "status", "targetDate")),
    ("InterviewSchedules_ownerId_priority_updatedAt_idx", "InterviewSchedules", ("ownerId", "priority", "updatedAt")),
    ("InterviewRounds_ownerId_scheduleId_sequence_idx", "InterviewRounds", ("ownerId", "scheduleId", "sequence")),
    ("InterviewRounds_ownerId_status_scheduledAt_idx", "InterviewRounds", ("ownerId", "status", "scheduledAt")),
    ("InterviewRounds_scheduleId_status_idx", "InterviewRounds", ("scheduleId", "status")),
    ("InterviewCalendarEvents_ownerId_startsAt_idx", "InterviewCalendarEvents", ("ownerId", "startsAt")),
    ("InterviewCalendarEvents_ownerId_scheduleId_startsAt_idx", "InterviewCalendarEvents", ("ownerId", "scheduleId", "startsAt")),
    ("InterviewCalendarEvents_scheduleId_eventType_idx", "InterviewCalendarEvents", ("scheduleId", "eventType")),
    ("InterviewCalendarEvents_roundId_startsAt_idx", "InterviewCalendarEvents", ("roundId", "startsAt")),
    ("InterviewHistory_ownerId_updatedAt_title_idx", "InterviewHistory", ("ownerId", "updatedAt", "title")),
    ("InterviewHistory_ownerId_scheduleId_completedAt_idx", "InterviewHistory", ("ownerId", "scheduleId", "completedAt")),
    ("InterviewHistory_scheduleId_outcome_idx", "InterviewHistory", ("scheduleId", "outcome")),
)


def _table_names() -> set[str]:
    return set(sa.inspect(op.get_bind()).get_table_names())


def _index_names(table_name: str) -> set[str]:
    return {index["name"] for index in sa.inspect(op.get_bind()).get_indexes(table_name)}


def _create_index(name: str, table_name: str, columns: tuple[str, ...]) -> None:
    if table_name not in _table_names() or name in _index_names(table_name):
        return
    op.create_index(name, table_name, list(columns), unique=False)


def _drop_index(name: str, table_name: str) -> None:
    if table_name not in _table_names() or name not in _index_names(table_name):
        return
    op.drop_index(name, table_name=table_name)


def upgrade() -> None:
    table_names = _table_names()

    if "InterviewSchedules" not in table_names:
        op.create_table(
            "InterviewSchedules",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("candidateName", sa.String(length=180), nullable=False),
            sa.Column("roleTitle", sa.String(length=180), nullable=False),
            sa.Column("companyName", sa.String(length=180), nullable=True),
            sa.Column("interviewStage", sa.String(length=120), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="planned", nullable=False),
            sa.Column("priority", sa.String(length=40), server_default="medium", nullable=False),
            sa.Column("targetDate", sa.String(length=40), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_InterviewSchedules_ownerId", "InterviewSchedules", ["ownerId"])

    table_names = _table_names()
    if "InterviewRounds" not in table_names:
        op.create_table(
            "InterviewRounds",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("scheduleId", sa.Integer(), nullable=False),
            sa.Column("roundName", sa.String(length=180), nullable=False),
            sa.Column("interviewerName", sa.String(length=180), nullable=True),
            sa.Column("interviewType", sa.String(length=120), nullable=True),
            sa.Column("sequence", sa.Integer(), server_default="1", nullable=False),
            sa.Column("status", sa.String(length=40), server_default="planned", nullable=False),
            sa.Column("scheduledAt", sa.String(length=40), nullable=True),
            sa.Column("location", sa.String(length=240), nullable=True),
            sa.Column("preparationNotes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["scheduleId"], ["InterviewSchedules.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_InterviewRounds_ownerId", "InterviewRounds", ["ownerId"])
        op.create_index("ix_InterviewRounds_scheduleId", "InterviewRounds", ["scheduleId"])

    table_names = _table_names()
    if "InterviewCalendarEvents" not in table_names:
        op.create_table(
            "InterviewCalendarEvents",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("scheduleId", sa.Integer(), nullable=False),
            sa.Column("roundId", sa.Integer(), nullable=True),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("eventType", sa.String(length=80), server_default="interview", nullable=False),
            sa.Column("startsAt", sa.String(length=40), nullable=False),
            sa.Column("endsAt", sa.String(length=40), nullable=True),
            sa.Column("reminderMinutes", sa.Integer(), nullable=True),
            sa.Column("location", sa.String(length=240), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["roundId"], ["InterviewRounds.id"]),
            sa.ForeignKeyConstraint(["scheduleId"], ["InterviewSchedules.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_InterviewCalendarEvents_ownerId", "InterviewCalendarEvents", ["ownerId"])
        op.create_index("ix_InterviewCalendarEvents_scheduleId", "InterviewCalendarEvents", ["scheduleId"])
        op.create_index("ix_InterviewCalendarEvents_roundId", "InterviewCalendarEvents", ["roundId"])

    table_names = _table_names()
    if "InterviewHistory" not in table_names:
        op.create_table(
            "InterviewHistory",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("scheduleId", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("outcome", sa.String(length=120), nullable=True),
            sa.Column("completedAt", sa.String(length=40), nullable=True),
            sa.Column("summary", sa.Text(), nullable=True),
            sa.Column("nextSteps", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["scheduleId"], ["InterviewSchedules.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_InterviewHistory_ownerId", "InterviewHistory", ["ownerId"])
        op.create_index("ix_InterviewHistory_scheduleId", "InterviewHistory", ["scheduleId"])

    for name, table_name, columns in INDEXES:
        _create_index(name, table_name, columns)


def downgrade() -> None:
    for name, table_name, _columns in reversed(INDEXES):
        _drop_index(name, table_name)

    table_names = _table_names()
    if "InterviewHistory" in table_names:
        op.drop_index("ix_InterviewHistory_scheduleId", table_name="InterviewHistory")
        op.drop_index("ix_InterviewHistory_ownerId", table_name="InterviewHistory")
        op.drop_table("InterviewHistory")

    table_names = _table_names()
    if "InterviewCalendarEvents" in table_names:
        op.drop_index("ix_InterviewCalendarEvents_roundId", table_name="InterviewCalendarEvents")
        op.drop_index("ix_InterviewCalendarEvents_scheduleId", table_name="InterviewCalendarEvents")
        op.drop_index("ix_InterviewCalendarEvents_ownerId", table_name="InterviewCalendarEvents")
        op.drop_table("InterviewCalendarEvents")

    table_names = _table_names()
    if "InterviewRounds" in table_names:
        op.drop_index("ix_InterviewRounds_scheduleId", table_name="InterviewRounds")
        op.drop_index("ix_InterviewRounds_ownerId", table_name="InterviewRounds")
        op.drop_table("InterviewRounds")

    table_names = _table_names()
    if "InterviewSchedules" in table_names:
        op.drop_index("ix_InterviewSchedules_ownerId", table_name="InterviewSchedules")
        op.drop_table("InterviewSchedules")
