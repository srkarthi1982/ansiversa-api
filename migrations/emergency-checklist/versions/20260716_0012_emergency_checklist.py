"""Create Emergency Checklist tables."""
from alembic import op
from app.modules.emergency_checklist.db import Base
from app.modules.emergency_checklist import models
revision="20260716_0012_emergency_checklist";down_revision=None;branch_labels=None;depends_on=None
def upgrade():Base.metadata.create_all(op.get_bind())
def downgrade():
 for table in reversed(Base.metadata.sorted_tables):table.drop(op.get_bind())
