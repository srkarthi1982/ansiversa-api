"""Create Decision Maker tables."""
from alembic import op
from app.modules.decision_maker.db import Base
from app.modules.decision_maker import models
revision="20260716_0009_decision_maker";down_revision=None;branch_labels=None;depends_on=None
def upgrade():Base.metadata.create_all(op.get_bind())
def downgrade():
 for table in reversed(Base.metadata.sorted_tables):table.drop(op.get_bind())
