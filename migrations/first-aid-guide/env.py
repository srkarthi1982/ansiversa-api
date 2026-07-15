from logging.config import fileConfig
from alembic import context
from app.modules.first_aid_guide.constants import VERSION_TABLE
from app.modules.first_aid_guide.db import FirstAidGuideBase, first_aid_guide_engine
from app.modules.first_aid_guide import models  # noqa: F401

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = FirstAidGuideBase.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"}, version_table=VERSION_TABLE)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    with first_aid_guide_engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, version_table=VERSION_TABLE)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
