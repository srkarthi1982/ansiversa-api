"""Create Leave Planner tables."""
from collections.abc import Sequence
from alembic import op
import sqlalchemy as sa
revision="20260716_0002_leave_planner"
down_revision=None
branch_labels: str | Sequence[str] | None=None
depends_on: str | Sequence[str] | None=None
def upgrade():
    op.create_table("LeaveTypes",sa.Column("id",sa.String(36),primary_key=True),sa.Column("userId",sa.String(36),nullable=False),sa.Column("name",sa.String(120),nullable=False),sa.Column("code",sa.String(30)),sa.Column("description",sa.Text()),sa.Column("annualAllowanceDays",sa.Float(),nullable=False),sa.Column("carryForwardDays",sa.Float(),nullable=False),sa.Column("colorKey",sa.String(30),nullable=False),sa.Column("isActive",sa.Boolean(),nullable=False),sa.Column("createdAt",sa.DateTime(timezone=True),server_default=sa.text("CURRENT_TIMESTAMP"),nullable=False),sa.Column("updatedAt",sa.DateTime(timezone=True),server_default=sa.text("CURRENT_TIMESTAMP"),nullable=False),sa.UniqueConstraint("userId","name",name="uq_leave_types_user_name"))
    op.create_index("ix_leave_types_user_id","LeaveTypes",["userId"]); op.create_index("ix_leave_types_user_active","LeaveTypes",["userId","isActive"])
    op.create_table("LeaveEntries",sa.Column("id",sa.String(36),primary_key=True),sa.Column("userId",sa.String(36),nullable=False),sa.Column("leaveTypeId",sa.String(36),sa.ForeignKey("LeaveTypes.id"),nullable=False),sa.Column("title",sa.String(180),nullable=False),sa.Column("startDate",sa.Date(),nullable=False),sa.Column("endDate",sa.Date(),nullable=False),sa.Column("durationDays",sa.Float(),nullable=False),sa.Column("dayType",sa.String(20),nullable=False),sa.Column("status",sa.String(20),nullable=False),sa.Column("reason",sa.String(500)),sa.Column("notes",sa.Text()),sa.Column("createdAt",sa.DateTime(timezone=True),server_default=sa.text("CURRENT_TIMESTAMP"),nullable=False),sa.Column("updatedAt",sa.DateTime(timezone=True),server_default=sa.text("CURRENT_TIMESTAMP"),nullable=False))
    for name,cols in [("ix_leave_entries_user_id",["userId"]),("ix_leave_entries_type_id",["leaveTypeId"]),("ix_leave_entries_start",["startDate"]),("ix_leave_entries_end",["endDate"]),("ix_leave_entries_status",["status"]),("ix_leave_entries_user_dates",["userId","startDate","endDate"]),("ix_leave_entries_user_status",["userId","status"]),("ix_leave_entries_user_type",["userId","leaveTypeId"])]: op.create_index(name,"LeaveEntries",cols)
def downgrade():
    op.drop_table("LeaveEntries"); op.drop_table("LeaveTypes")
