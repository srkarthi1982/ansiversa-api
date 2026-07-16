from logging.config import fileConfig
from alembic import context
from app.modules.errand_planner.constants import VERSION_TABLE
from app.modules.errand_planner.db import Base,engine
from app.modules.errand_planner import models
if context.config.config_file_name:fileConfig(context.config.config_file_name)
with engine.connect()as c:
 context.configure(connection=c,target_metadata=Base.metadata,version_table=VERSION_TABLE)
 with context.begin_transaction():context.run_migrations()
