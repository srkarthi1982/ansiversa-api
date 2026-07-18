"""Create Travel Itinerary Builder tables."""

from alembic import op

from app.modules.travel_itinerary_builder import models
from app.modules.travel_itinerary_builder.db import Base

revision = "20260718_0001_travel_itinerary_builder"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(op.get_bind())


def downgrade() -> None:
    for table in reversed(Base.metadata.sorted_tables):
        table.drop(op.get_bind())

