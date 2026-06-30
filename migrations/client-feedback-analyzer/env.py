from logging.config import fileConfig

from alembic import context

from app.core.config import settings
from app.modules.client_feedback_analyzer import models  # noqa: F401
from app.modules.client_feedback_analyzer.db import (
    ClientFeedbackAnalyzerBase,
    client_feedback_analyzer_engine,
)


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = ClientFeedbackAnalyzerBase.metadata
VERSION_TABLE = "client_feedback_analyzer_alembic_version"
MANAGED_TABLES = {
    "ClientProfiles",
    "ClientFeedback",
    "FeedbackInsights",
    "FeedbackReports",
}


def get_database_url() -> str:
    return settings.CLIENT_FEEDBACK_ANALYZER_DATABASE_URL


def include_object(
    object_: object,
    name: str | None,
    type_: str,
    reflected: bool,
    compare_to: object | None,
) -> bool:
    _ = object_, reflected, compare_to
    if type_ == "table":
        return name in MANAGED_TABLES

    return True


def run_migrations_offline() -> None:
    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table=VERSION_TABLE,
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    with client_feedback_analyzer_engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table=VERSION_TABLE,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
