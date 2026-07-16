"""Create Net Worth Tracker tables."""
from alembic import op
from app.modules.net_worth_tracker.db import Base
from app.modules.net_worth_tracker import models
revision="20260716_0008_net_worth_tracker";down_revision=None;branch_labels=None;depends_on=None
def upgrade():Base.metadata.create_all(op.get_bind())
def downgrade():
 for table in reversed(Base.metadata.sorted_tables):table.drop(op.get_bind())
