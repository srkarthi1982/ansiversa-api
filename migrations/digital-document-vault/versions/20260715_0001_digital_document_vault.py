"""Create Digital Document Vault tables."""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260715_0001_digital_document_vault"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "Categories",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("userId", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("userId", "name", name="uq_vault_categories_owner_name"),
    )
    op.create_index("ix_categories_user_id", "Categories", ["userId"], unique=False)
    op.create_index("ix_categories_user_name", "Categories", ["userId", "name"], unique=False)

    op.create_table(
        "Documents",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("userId", sa.String(length=36), nullable=False),
        sa.Column("categoryId", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("documentType", sa.String(length=80), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("tags", sa.Text(), nullable=True),
        sa.Column("fileName", sa.String(length=255), nullable=False),
        sa.Column("storedFileName", sa.String(length=255), nullable=False),
        sa.Column("mimeType", sa.String(length=120), nullable=False),
        sa.Column("fileSize", sa.Integer(), nullable=False),
        sa.Column("fileBlob", sa.LargeBinary(), nullable=False),
        sa.Column("issueDate", sa.String(length=40), nullable=True),
        sa.Column("expiryDate", sa.String(length=40), nullable=True),
        sa.Column("uploadedAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["categoryId"], ["Categories.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("userId", "storedFileName", name="uq_vault_documents_owner_stored_file"),
    )
    op.create_index("ix_documents_user_id", "Documents", ["userId"], unique=False)
    op.create_index("ix_documents_category_id", "Documents", ["categoryId"], unique=False)
    op.create_index("ix_documents_document_type", "Documents", ["documentType"], unique=False)
    op.create_index("ix_documents_expiry_date", "Documents", ["expiryDate"], unique=False)
    op.create_index("ix_documents_user_category", "Documents", ["userId", "categoryId"], unique=False)
    op.create_index("ix_documents_user_type", "Documents", ["userId", "documentType"], unique=False)
    op.create_index("ix_documents_user_expiry", "Documents", ["userId", "expiryDate"], unique=False)
    op.create_index("ix_documents_user_uploaded", "Documents", ["userId", "uploadedAt"], unique=False)
    op.create_index("ix_documents_user_updated", "Documents", ["userId", "updatedAt"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_documents_user_updated", table_name="Documents")
    op.drop_index("ix_documents_user_uploaded", table_name="Documents")
    op.drop_index("ix_documents_user_expiry", table_name="Documents")
    op.drop_index("ix_documents_user_type", table_name="Documents")
    op.drop_index("ix_documents_user_category", table_name="Documents")
    op.drop_index("ix_documents_expiry_date", table_name="Documents")
    op.drop_index("ix_documents_document_type", table_name="Documents")
    op.drop_index("ix_documents_category_id", table_name="Documents")
    op.drop_index("ix_documents_user_id", table_name="Documents")
    op.drop_table("Documents")
    op.drop_index("ix_categories_user_name", table_name="Categories")
    op.drop_index("ix_categories_user_id", table_name="Categories")
    op.drop_table("Categories")
