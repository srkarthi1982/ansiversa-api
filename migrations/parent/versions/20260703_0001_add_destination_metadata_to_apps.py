"""add_destination_metadata_to_apps

Revision ID: 20260703_0001
Revises: 20260628_0001
Create Date: 2026-07-03

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260703_0001"
down_revision: str | None = "20260628_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


DESTINATION_METADATA: tuple[tuple[str, int, str, str], ...] = (
    ("ai-job-interviewer", 60, "approved", "2026-07-03"),
    ("ai-notes-summarizer", 62, "approved", "2026-07-03"),
    ("ai-translator-and-tone-fixer", 60, "approved", "2026-07-03"),
    ("api-tester", 68, "approved", "2026-07-03"),
    ("book-summary-generator", 61, "approved", "2026-07-03"),
    ("browser-pdf-reader", 72, "approved", "2026-07-03"),
    ("career-planner", 62, "approved", "2026-07-03"),
    ("client-feedback-analyzer", 59, "approved", "2026-07-03"),
    ("clipboard-manager", 67, "approved", "2026-07-03"),
    ("concept-explainer", 63, "approved", "2026-07-03"),
    ("contract-generator", 60, "approved", "2026-07-03"),
    ("course-tracker", 64, "approved", "2026-07-03"),
    ("creative-title-generator", 62, "approved", "2026-07-03"),
    ("daily-word-challenge", 69, "approved", "2026-07-03"),
    ("dictionary-plus", 62, "approved", "2026-07-03"),
    ("eco-habit-tracker", 69, "approved", "2026-07-03"),
    ("email-assistant", 64, "approved", "2026-07-03"),
    ("file-optimizer", 66, "approved", "2026-07-03"),
    ("formula-finder", 74, "approved", "2026-07-03"),
    ("grammar-and-paraphrasing-assistant", 61, "approved", "2026-07-03"),
    ("interview-coach", 61, "approved", "2026-07-03"),
    ("interview-scheduler", 61, "approved", "2026-07-03"),
    ("invoice-receipt-maker", 64, "approved", "2026-07-03"),
    ("job-description-analyzer", 60, "approved", "2026-07-03"),
    ("job-tracker", 62, "approved", "2026-07-03"),
    ("json-formatter", 86, "approved", "2026-07-03"),
    ("lesson-builder", 63, "approved", "2026-07-03"),
    ("linkedin-bio-optimizer", 63, "approved", "2026-07-03"),
    ("markdown-editor", 79, "approved", "2026-07-03"),
    ("meeting-minutes-ai", 62, "approved", "2026-07-03"),
    ("memory-trainer", 64, "approved", "2026-07-03"),
    ("mood-journal", 70, "approved", "2026-07-03"),
    ("password-generator", 84, "approved", "2026-07-03"),
    ("portfolio-creator", 61, "approved", "2026-07-03"),
    ("presentation-designer", 60, "approved", "2026-07-03"),
    ("price-checker", 76, "approved", "2026-07-03"),
    ("prompt-builder", 62, "approved", "2026-07-03"),
    ("proposal-writer", 63, "approved", "2026-07-03"),
    ("qr-code-creator", 85, "approved", "2026-07-03"),
    ("quiz", 38, "approved", "2026-07-03"),
    ("research-assistant", 64, "approved", "2026-07-03"),
    ("resume-builder", 66, "approved", "2026-07-03"),
    ("smart-textbook-scanner", 59, "approved", "2026-07-03"),
    ("snippet-generator", 63, "approved", "2026-07-03"),
    ("social-caption-generator", 61, "approved", "2026-07-03"),
    ("speech-writer", 62, "approved", "2026-07-03"),
    ("study-planner", 65, "approved", "2026-07-03"),
    ("time-zone-scheduler", 70, "approved", "2026-07-03"),
    ("visiting-card-maker", 64, "approved", "2026-07-03"),
    ("voice-converter", 68, "approved", "2026-07-03"),
)


def _table_names() -> set[str]:
    return set(sa.inspect(op.get_bind()).get_table_names())


def _column_names(table_name: str) -> set[str]:
    return {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table_name)}


def _add_column_if_missing(table_name: str, column: sa.Column) -> None:
    if column.name in _column_names(table_name):
        return

    op.add_column(table_name, column)


def upgrade() -> None:
    if "Apps" not in _table_names():
        return

    _add_column_if_missing("Apps", sa.Column("destination_progress", sa.Integer(), nullable=True))
    _add_column_if_missing("Apps", sa.Column("destination_status", sa.Text(), nullable=True))
    _add_column_if_missing("Apps", sa.Column("destination_reviewed_at", sa.Date(), nullable=True))

    update_statement = sa.text(
        'UPDATE "Apps" '
        "SET destination_progress = :progress, "
        "destination_status = :status, "
        "destination_reviewed_at = :reviewed_at "
        "WHERE slug = :slug AND \"launchStatus\" = :launch_status"
    )
    for slug, progress, status, reviewed_at in DESTINATION_METADATA:
        op.execute(
            update_statement.bindparams(
                slug=slug,
                progress=progress,
                status=status,
                reviewed_at=reviewed_at,
                launch_status="live",
            )
        )


def downgrade() -> None:
    if "Apps" not in _table_names():
        return

    existing_columns = _column_names("Apps")
    with op.batch_alter_table("Apps") as batch_op:
        if "destination_reviewed_at" in existing_columns:
            batch_op.drop_column("destination_reviewed_at")
        if "destination_status" in existing_columns:
            batch_op.drop_column("destination_status")
        if "destination_progress" in existing_columns:
            batch_op.drop_column("destination_progress")
