from logging.config import fileConfig
from alembic import context
from app.modules.leave_planner.constants import VERSION_TABLE
from app.modules.leave_planner.db import LeavePlannerBase, leave_planner_engine
from app.modules.leave_planner import models  # noqa: F401
config=context.config
if config.config_file_name: fileConfig(config.config_file_name)
target_metadata=LeavePlannerBase.metadata
def offline():
    context.configure(url=config.get_main_option("sqlalchemy.url"),target_metadata=target_metadata,literal_binds=True,version_table=VERSION_TABLE)
    with context.begin_transaction(): context.run_migrations()
def online():
    with leave_planner_engine.connect() as connection:
        context.configure(connection=connection,target_metadata=target_metadata,version_table=VERSION_TABLE)
        with context.begin_transaction(): context.run_migrations()
if context.is_offline_mode(): offline()
else: online()
