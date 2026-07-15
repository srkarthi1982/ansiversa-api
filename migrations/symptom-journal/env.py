from logging.config import fileConfig
from alembic import context
from app.modules.symptom_journal.constants import VERSION_TABLE
from app.modules.symptom_journal.db import SymptomJournalBase, symptom_journal_engine
from app.modules.symptom_journal import models  # noqa: F401

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SymptomJournalBase.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"}, version_table=VERSION_TABLE)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    with symptom_journal_engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, version_table=VERSION_TABLE)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
