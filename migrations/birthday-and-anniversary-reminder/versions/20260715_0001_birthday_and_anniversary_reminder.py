"""Create Birthday & Anniversary Reminder tables."""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260715_0001_birthday_and_anniversary_reminder"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ReminderTypes",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("userId", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("sortOrder", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("isSystem", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("userId", "name", name="uq_reminder_types_owner_name"),
    )
    op.create_index("ix_reminder_types_user_id", "ReminderTypes", ["userId"], unique=False)
    op.create_index("ix_reminder_types_user_name", "ReminderTypes", ["userId", "name"], unique=False)
    op.create_index("ix_reminder_types_user_sort", "ReminderTypes", ["userId", "sortOrder"], unique=False)
    op.create_index("ix_reminder_types_is_system", "ReminderTypes", ["isSystem"], unique=False)

    op.create_table(
        "ReminderContacts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("userId", sa.String(length=36), nullable=False),
        sa.Column("reminderTypeId", sa.String(length=36), nullable=False),
        sa.Column("personName", sa.String(length=180), nullable=False),
        sa.Column("relationship", sa.String(length=120), nullable=True),
        sa.Column("eventDate", sa.Date(), nullable=False),
        sa.Column("phone", sa.String(length=60), nullable=True),
        sa.Column("email", sa.String(length=180), nullable=True),
        sa.Column("giftIdeas", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("favourite", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("archived", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["reminderTypeId"], ["ReminderTypes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reminder_contacts_user_id", "ReminderContacts", ["userId"], unique=False)
    op.create_index("ix_reminder_contacts_type_id", "ReminderContacts", ["reminderTypeId"], unique=False)
    op.create_index("ix_reminder_contacts_user_type", "ReminderContacts", ["userId", "reminderTypeId"], unique=False)
    op.create_index("ix_reminder_contacts_user_archived", "ReminderContacts", ["userId", "archived"], unique=False)
    op.create_index("ix_reminder_contacts_user_favourite", "ReminderContacts", ["userId", "favourite"], unique=False)
    op.create_index("ix_reminder_contacts_user_event_date", "ReminderContacts", ["userId", "eventDate"], unique=False)
    op.create_index("ix_reminder_contacts_user_relationship", "ReminderContacts", ["userId", "relationship"], unique=False)
    op.create_index("ix_reminder_contacts_user_updated", "ReminderContacts", ["userId", "updatedAt"], unique=False)

    op.create_table(
        "ReminderAcknowledgements",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("userId", sa.String(length=36), nullable=False),
        sa.Column("reminderContactId", sa.String(length=36), nullable=False),
        sa.Column("acknowledgementYear", sa.Integer(), nullable=False),
        sa.Column("acknowledgedAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["reminderContactId"], ["ReminderContacts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reminderContactId", "acknowledgementYear", name="uq_reminder_ack_contact_year"),
    )
    op.create_index("ix_reminder_ack_user_id", "ReminderAcknowledgements", ["userId"], unique=False)
    op.create_index("ix_reminder_ack_contact_id", "ReminderAcknowledgements", ["reminderContactId"], unique=False)
    op.create_index("ix_reminder_ack_contact_year", "ReminderAcknowledgements", ["reminderContactId", "acknowledgementYear"], unique=False)
    op.create_index("ix_reminder_ack_user_year", "ReminderAcknowledgements", ["userId", "acknowledgementYear"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_reminder_ack_user_year", table_name="ReminderAcknowledgements")
    op.drop_index("ix_reminder_ack_contact_year", table_name="ReminderAcknowledgements")
    op.drop_index("ix_reminder_ack_contact_id", table_name="ReminderAcknowledgements")
    op.drop_index("ix_reminder_ack_user_id", table_name="ReminderAcknowledgements")
    op.drop_table("ReminderAcknowledgements")
    op.drop_index("ix_reminder_contacts_user_updated", table_name="ReminderContacts")
    op.drop_index("ix_reminder_contacts_user_relationship", table_name="ReminderContacts")
    op.drop_index("ix_reminder_contacts_user_event_date", table_name="ReminderContacts")
    op.drop_index("ix_reminder_contacts_user_favourite", table_name="ReminderContacts")
    op.drop_index("ix_reminder_contacts_user_archived", table_name="ReminderContacts")
    op.drop_index("ix_reminder_contacts_user_type", table_name="ReminderContacts")
    op.drop_index("ix_reminder_contacts_type_id", table_name="ReminderContacts")
    op.drop_index("ix_reminder_contacts_user_id", table_name="ReminderContacts")
    op.drop_table("ReminderContacts")
    op.drop_index("ix_reminder_types_is_system", table_name="ReminderTypes")
    op.drop_index("ix_reminder_types_user_sort", table_name="ReminderTypes")
    op.drop_index("ix_reminder_types_user_name", table_name="ReminderTypes")
    op.drop_index("ix_reminder_types_user_id", table_name="ReminderTypes")
    op.drop_table("ReminderTypes")
