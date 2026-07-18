from logging.config import fileConfig

from alembic import context

from app.modules.travel_itinerary_builder import models
from app.modules.travel_itinerary_builder.constants import VERSION_TABLE
from app.modules.travel_itinerary_builder.db import Base, engine

if context.config.config_file_name:
    fileConfig(context.config.config_file_name)

with engine.connect() as connection:
    context.configure(
        connection=connection,
        target_metadata=Base.metadata,
        version_table=VERSION_TABLE,
    )
    with context.begin_transaction():
        context.run_migrations()

