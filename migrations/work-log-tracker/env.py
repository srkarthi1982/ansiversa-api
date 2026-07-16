from logging.config import fileConfig
from alembic import context
from app.modules.work_log_tracker.constants import VERSION_TABLE
from app.modules.work_log_tracker.db import WorkLogBase,engine
from app.modules.work_log_tracker import models
if context.config.config_file_name:fileConfig(context.config.config_file_name)
with engine.connect()as c:
 context.configure(connection=c,target_metadata=WorkLogBase.metadata,version_table=VERSION_TABLE)
 with context.begin_transaction():context.run_migrations()
