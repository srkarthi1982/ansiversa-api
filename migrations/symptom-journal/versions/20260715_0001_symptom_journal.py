"""Create Symptom Journal tables."""
from collections.abc import Sequence
from alembic import op
import sqlalchemy as sa

revision: str = "20260715_0001_symptom_journal"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "SymptomCategories",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("userId", sa.String(36), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("sortOrder", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("isSystem", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("userId", "name", name="uq_symptom_categories_owner_name"),
    )
    op.create_index("ix_symptom_categories_user_id", "SymptomCategories", ["userId"])
    op.create_index("ix_symptom_categories_user_name", "SymptomCategories", ["userId", "name"])
    op.create_index("ix_symptom_categories_user_sort", "SymptomCategories", ["userId", "sortOrder"])
    op.create_index("ix_symptom_categories_is_system", "SymptomCategories", ["isSystem"])
    op.create_table(
        "SymptomEntries",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("userId", sa.String(36), nullable=False),
        sa.Column("categoryId", sa.String(36), nullable=True),
        sa.Column("entryDate", sa.Date(), nullable=False),
        sa.Column("entryTime", sa.Time(), nullable=True),
        sa.Column("symptomTitle", sa.String(180), nullable=False),
        sa.Column("severity", sa.Integer(), nullable=False),
        sa.Column("duration", sa.String(120), nullable=True),
        sa.Column("bodyLocation", sa.String(180), nullable=True),
        sa.Column("mood", sa.String(120), nullable=True),
        sa.Column("temperature", sa.Numeric(5, 2), nullable=True),
        sa.Column("triggers", sa.Text(), nullable=True),
        sa.Column("reliefMethods", sa.Text(), nullable=True),
        sa.Column("followUpNotes", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("archived", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["categoryId"], ["SymptomCategories.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_symptom_entries_user_id", "SymptomEntries", ["userId"])
    op.create_index("ix_symptom_entries_category_id", "SymptomEntries", ["categoryId"])
    op.create_index("ix_symptom_entries_user_category", "SymptomEntries", ["userId", "categoryId"])
    op.create_index("ix_symptom_entries_user_date", "SymptomEntries", ["userId", "entryDate"])
    op.create_index("ix_symptom_entries_user_severity", "SymptomEntries", ["userId", "severity"])
    op.create_index("ix_symptom_entries_user_archived", "SymptomEntries", ["userId", "archived"])
    op.create_index("ix_symptom_entries_user_title", "SymptomEntries", ["userId", "symptomTitle"])
    op.create_index("ix_symptom_entries_user_body_location", "SymptomEntries", ["userId", "bodyLocation"])
    op.create_index("ix_symptom_entries_user_created", "SymptomEntries", ["userId", "createdAt"])
    op.create_index("ix_symptom_entries_user_updated", "SymptomEntries", ["userId", "updatedAt"])


def downgrade() -> None:
    for name in [
        "ix_symptom_entries_user_updated",
        "ix_symptom_entries_user_created",
        "ix_symptom_entries_user_body_location",
        "ix_symptom_entries_user_title",
        "ix_symptom_entries_user_archived",
        "ix_symptom_entries_user_severity",
        "ix_symptom_entries_user_date",
        "ix_symptom_entries_user_category",
        "ix_symptom_entries_category_id",
        "ix_symptom_entries_user_id",
    ]:
        op.drop_index(name, table_name="SymptomEntries")
    op.drop_table("SymptomEntries")
    for name in [
        "ix_symptom_categories_is_system",
        "ix_symptom_categories_user_sort",
        "ix_symptom_categories_user_name",
        "ix_symptom_categories_user_id",
    ]:
        op.drop_index(name, table_name="SymptomCategories")
    op.drop_table("SymptomCategories")
