"""Create First Aid Guide tables."""
from collections.abc import Sequence
from alembic import op
import sqlalchemy as sa

revision: str = "20260715_0001_first_aid_guide"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table("FirstAidCategories", sa.Column("id", sa.String(36), nullable=False), sa.Column("name", sa.String(120), nullable=False), sa.Column("description", sa.Text(), nullable=True), sa.Column("sortOrder", sa.Integer(), server_default=sa.text("0"), nullable=False), sa.Column("isSystem", sa.Boolean(), server_default=sa.text("1"), nullable=False), sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("name", name="uq_first_aid_categories_name"))
    op.create_index("ix_first_aid_categories_name", "FirstAidCategories", ["name"])
    op.create_index("ix_first_aid_categories_sort", "FirstAidCategories", ["sortOrder"])
    op.create_index("ix_first_aid_categories_system", "FirstAidCategories", ["isSystem"])
    op.create_table("FirstAidGuides", sa.Column("id", sa.String(36), nullable=False), sa.Column("categoryId", sa.String(36), nullable=False), sa.Column("title", sa.String(180), nullable=False), sa.Column("summary", sa.Text(), nullable=False), sa.Column("overview", sa.Text(), nullable=False), sa.Column("firstAidSteps", sa.Text(), nullable=False), sa.Column("avoidActions", sa.Text(), nullable=False), sa.Column("emergencyWarning", sa.Text(), nullable=False), sa.Column("prevention", sa.Text(), nullable=True), sa.Column("relatedTopics", sa.Text(), nullable=True), sa.Column("displayOrder", sa.Integer(), server_default=sa.text("0"), nullable=False), sa.Column("lastReviewed", sa.Date(), nullable=True), sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.ForeignKeyConstraint(["categoryId"], ["FirstAidCategories.id"]), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("title", name="uq_first_aid_guides_title"))
    op.create_index("ix_first_aid_guides_category_id", "FirstAidGuides", ["categoryId"])
    op.create_index("ix_first_aid_guides_category_order", "FirstAidGuides", ["categoryId", "displayOrder"])
    op.create_index("ix_first_aid_guides_title", "FirstAidGuides", ["title"])
    op.create_index("ix_first_aid_guides_display", "FirstAidGuides", ["displayOrder"])
    op.create_index("ix_first_aid_guides_reviewed", "FirstAidGuides", ["lastReviewed"])
    op.create_table("UserGuideBookmarks", sa.Column("id", sa.String(36), nullable=False), sa.Column("userId", sa.String(36), nullable=False), sa.Column("guideId", sa.String(36), nullable=False), sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.ForeignKeyConstraint(["guideId"], ["FirstAidGuides.id"]), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("userId", "guideId", name="uq_user_guide_bookmarks_owner_guide"))
    op.create_index("ix_user_guide_bookmarks_user_id", "UserGuideBookmarks", ["userId"])
    op.create_index("ix_user_guide_bookmarks_guide_id", "UserGuideBookmarks", ["guideId"])
    op.create_index("ix_user_guide_bookmarks_user_created", "UserGuideBookmarks", ["userId", "createdAt"])
    op.create_table("UserGuideHistory", sa.Column("id", sa.String(36), nullable=False), sa.Column("userId", sa.String(36), nullable=False), sa.Column("guideId", sa.String(36), nullable=False), sa.Column("viewedAt", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.ForeignKeyConstraint(["guideId"], ["FirstAidGuides.id"]), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_user_guide_history_user_id", "UserGuideHistory", ["userId"])
    op.create_index("ix_user_guide_history_guide_id", "UserGuideHistory", ["guideId"])
    op.create_index("ix_user_guide_history_user_viewed", "UserGuideHistory", ["userId", "viewedAt"])
    op.create_index("ix_user_guide_history_user_guide", "UserGuideHistory", ["userId", "guideId"])


def downgrade() -> None:
    for name in ["ix_user_guide_history_user_guide", "ix_user_guide_history_user_viewed", "ix_user_guide_history_guide_id", "ix_user_guide_history_user_id"]:
        op.drop_index(name, table_name="UserGuideHistory")
    op.drop_table("UserGuideHistory")
    for name in ["ix_user_guide_bookmarks_user_created", "ix_user_guide_bookmarks_guide_id", "ix_user_guide_bookmarks_user_id"]:
        op.drop_index(name, table_name="UserGuideBookmarks")
    op.drop_table("UserGuideBookmarks")
    for name in ["ix_first_aid_guides_reviewed", "ix_first_aid_guides_display", "ix_first_aid_guides_title", "ix_first_aid_guides_category_order", "ix_first_aid_guides_category_id"]:
        op.drop_index(name, table_name="FirstAidGuides")
    op.drop_table("FirstAidGuides")
    for name in ["ix_first_aid_categories_system", "ix_first_aid_categories_sort", "ix_first_aid_categories_name"]:
        op.drop_index(name, table_name="FirstAidCategories")
    op.drop_table("FirstAidCategories")
