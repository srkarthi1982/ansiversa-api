"""Create Local Services Finder tables."""
from alembic import op
from app.modules.local_services_finder.db import Base
from app.modules.local_services_finder import models
revision="20260716_0011_local_services_finder";down_revision=None;branch_labels=None;depends_on=None
def upgrade():Base.metadata.create_all(op.get_bind())
def downgrade():
 for table in reversed(Base.metadata.sorted_tables):table.drop(op.get_bind())
