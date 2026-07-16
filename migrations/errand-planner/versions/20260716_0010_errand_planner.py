"""Create Errand Planner tables."""
from alembic import op
from app.modules.errand_planner.db import Base
from app.modules.errand_planner import models
revision="20260716_0010_errand_planner";down_revision=None;branch_labels=None;depends_on=None
def upgrade():Base.metadata.create_all(op.get_bind())
def downgrade():
 for table in reversed(Base.metadata.sorted_tables):table.drop(op.get_bind())
