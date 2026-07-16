"""Create Meeting Scheduler tables."""
from collections.abc import Sequence
from alembic import op
import sqlalchemy as sa

revision: str = "20260716_0001_meeting_scheduler"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table("Meetings", sa.Column("id", sa.String(36), primary_key=True), sa.Column("userId", sa.String(36), nullable=False), sa.Column("title", sa.String(180), nullable=False), sa.Column("description", sa.Text()), sa.Column("meetingDate", sa.Date(), nullable=False), sa.Column("startTime", sa.Time(), nullable=False), sa.Column("endTime", sa.Time(), nullable=False), sa.Column("timezone", sa.String(80), nullable=False), sa.Column("location", sa.String(300)), sa.Column("meetingType", sa.String(20), nullable=False), sa.Column("status", sa.String(20), nullable=False), sa.Column("notes", sa.Text()), sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False))
    op.create_index("ix_meetings_user_id", "Meetings", ["userId"])
    op.create_index("ix_meetings_status", "Meetings", ["status"])
    op.create_index("ix_meetings_date", "Meetings", ["meetingDate"])
    op.create_index("ix_meetings_user_date", "Meetings", ["userId", "meetingDate"])
    op.create_table("MeetingParticipants", sa.Column("id", sa.String(36), primary_key=True), sa.Column("meetingId", sa.String(36), sa.ForeignKey("Meetings.id", ondelete="CASCADE"), nullable=False), sa.Column("name", sa.String(160), nullable=False), sa.Column("email", sa.String(254)), sa.Column("role", sa.String(120)), sa.Column("responseStatus", sa.String(20), nullable=False), sa.Column("notes", sa.Text()), sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False))
    op.create_index("ix_meeting_participants_meeting", "MeetingParticipants", ["meetingId"])
    op.create_index("ix_meeting_participants_response", "MeetingParticipants", ["responseStatus"])
    op.create_table("MeetingAgendaItems", sa.Column("id", sa.String(36), primary_key=True), sa.Column("meetingId", sa.String(36), sa.ForeignKey("Meetings.id", ondelete="CASCADE"), nullable=False), sa.Column("title", sa.String(180), nullable=False), sa.Column("description", sa.Text()), sa.Column("durationMinutes", sa.Integer(), nullable=False), sa.Column("sortOrder", sa.Integer(), nullable=False), sa.Column("status", sa.String(20), nullable=False), sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False))
    op.create_index("ix_meeting_agenda_meeting", "MeetingAgendaItems", ["meetingId"])
    op.create_index("ix_meeting_agenda_status", "MeetingAgendaItems", ["status"])
    op.create_index("ix_meeting_agenda_order", "MeetingAgendaItems", ["meetingId", "sortOrder"])


def downgrade() -> None:
    op.drop_table("MeetingAgendaItems")
    op.drop_table("MeetingParticipants")
    op.drop_table("Meetings")
