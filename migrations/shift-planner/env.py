from logging.config import fileConfig
from alembic import context
from app.modules.shift_planner.constants import VERSION_TABLE
from app.modules.shift_planner.db import ShiftPlannerBase,shift_planner_engine
from app.modules.shift_planner import models  # noqa: F401
config=context.config
if config.config_file_name:fileConfig(config.config_file_name)
def run():
    with shift_planner_engine.connect() as connection:
        context.configure(connection=connection,target_metadata=ShiftPlannerBase.metadata,version_table=VERSION_TABLE)
        with context.begin_transaction():context.run_migrations()
run()
