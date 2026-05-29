from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import settings
from app.core.database import ParentBase
from app.modules.audit import models as audit_models  # noqa: F401
from app.modules.auth import models  # noqa: F401
from app.modules.apps import models as apps_models  # noqa: F401
from app.modules.dashboard import models as dashboard_models  # noqa: F401
from app.modules.faqs import models as faqs_models  # noqa: F401
from app.modules.favorites import models as favorites_models  # noqa: F401
from app.modules.notifications import models as notifications_models  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = ParentBase.metadata


def get_database_url() -> str:
    return settings.PARENT_DATABASE_URL


def run_migrations_offline() -> None:
    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_database_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
