"""add_client_feedback_analyzer_tables

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
    ("ClientProfiles_ownerId_updatedAt_name_idx", "ClientProfiles", ("ownerId", "updatedAt", "name")),
    ("ClientProfiles_ownerId_platformId_idx", "ClientProfiles", ("ownerId", "platformId")),
    ("ClientProfiles_ownerId_industry_segment_idx", "ClientProfiles", ("ownerId", "industry", "segment")),
    ("ClientFeedback_ownerId_clientId_updatedAt_idx", "ClientFeedback", ("ownerId", "clientId", "updatedAt")),
    ("ClientFeedback_ownerId_sentiment_status_idx", "ClientFeedback", ("ownerId", "sentiment", "status")),
    ("ClientFeedback_clientId_status_idx", "ClientFeedback", ("clientId", "status")),
    ("FeedbackInsights_ownerId_clientId_updatedAt_idx", "FeedbackInsights", ("ownerId", "clientId", "updatedAt")),
    ("FeedbackInsights_ownerId_priority_status_idx", "FeedbackInsights", ("ownerId", "priority", "status")),
    ("FeedbackInsights_feedbackId_status_idx", "FeedbackInsights", ("feedbackId", "status")),
    ("FeedbackReports_ownerId_updatedAt_title_idx", "FeedbackReports", ("ownerId", "updatedAt", "title")),
    ("FeedbackReports_ownerId_status_updatedAt_idx", "FeedbackReports", ("ownerId", "status", "updatedAt")),
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

    if "ClientProfiles" not in table_names:
        op.create_table(
            "ClientProfiles",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("name", sa.String(length=180), nullable=False),
            sa.Column("companyName", sa.String(length=180), nullable=True),
            sa.Column("contactName", sa.String(length=180), nullable=True),
            sa.Column("email", sa.String(length=180), nullable=True),
            sa.Column("industry", sa.String(length=120), nullable=True),
            sa.Column("segment", sa.String(length=120), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_ClientProfiles_ownerId", "ClientProfiles", ["ownerId"])

    table_names = _table_names()
    if "ClientFeedback" not in table_names:
        op.create_table(
            "ClientFeedback",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("clientId", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("source", sa.String(length=120), nullable=True),
            sa.Column("feedbackText", sa.Text(), nullable=False),
            sa.Column("sentiment", sa.String(length=40), server_default="neutral", nullable=False),
            sa.Column("rating", sa.Integer(), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="new", nullable=False),
            sa.Column("receivedAt", sa.String(length=40), nullable=True),
            sa.Column("tags", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["clientId"], ["ClientProfiles.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_ClientFeedback_ownerId", "ClientFeedback", ["ownerId"])
        op.create_index("ix_ClientFeedback_clientId", "ClientFeedback", ["clientId"])

    table_names = _table_names()
    if "FeedbackInsights" not in table_names:
        op.create_table(
            "FeedbackInsights",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("clientId", sa.Integer(), nullable=False),
            sa.Column("feedbackId", sa.Integer(), nullable=True),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("category", sa.String(length=120), nullable=True),
            sa.Column("sentiment", sa.String(length=40), server_default="neutral", nullable=False),
            sa.Column("priority", sa.String(length=40), server_default="medium", nullable=False),
            sa.Column("recommendation", sa.Text(), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="open", nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["clientId"], ["ClientProfiles.id"]),
            sa.ForeignKeyConstraint(["feedbackId"], ["ClientFeedback.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_FeedbackInsights_ownerId", "FeedbackInsights", ["ownerId"])
        op.create_index("ix_FeedbackInsights_clientId", "FeedbackInsights", ["clientId"])
        op.create_index("ix_FeedbackInsights_feedbackId", "FeedbackInsights", ["feedbackId"])

    table_names = _table_names()
    if "FeedbackReports" not in table_names:
        op.create_table(
            "FeedbackReports",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ownerId", sa.String(length=36), nullable=False),
            sa.Column("platformId", sa.String(length=120), nullable=True),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("scope", sa.String(length=120), nullable=True),
            sa.Column("summary", sa.Text(), nullable=False),
            sa.Column("periodStart", sa.String(length=40), nullable=True),
            sa.Column("periodEnd", sa.String(length=40), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="draft", nullable=False),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_FeedbackReports_ownerId", "FeedbackReports", ["ownerId"])

    for name, table_name, columns in INDEXES:
        _create_index(name, table_name, columns)


def downgrade() -> None:
    for name, table_name, _columns in reversed(INDEXES):
        _drop_index(name, table_name)

    table_names = _table_names()
    if "FeedbackReports" in table_names:
        op.drop_index("ix_FeedbackReports_ownerId", table_name="FeedbackReports")
        op.drop_table("FeedbackReports")

    table_names = _table_names()
    if "FeedbackInsights" in table_names:
        op.drop_index("ix_FeedbackInsights_feedbackId", table_name="FeedbackInsights")
        op.drop_index("ix_FeedbackInsights_clientId", table_name="FeedbackInsights")
        op.drop_index("ix_FeedbackInsights_ownerId", table_name="FeedbackInsights")
        op.drop_table("FeedbackInsights")

    table_names = _table_names()
    if "ClientFeedback" in table_names:
        op.drop_index("ix_ClientFeedback_clientId", table_name="ClientFeedback")
        op.drop_index("ix_ClientFeedback_ownerId", table_name="ClientFeedback")
        op.drop_table("ClientFeedback")

    table_names = _table_names()
    if "ClientProfiles" in table_names:
        op.drop_index("ix_ClientProfiles_ownerId", table_name="ClientProfiles")
        op.drop_table("ClientProfiles")
