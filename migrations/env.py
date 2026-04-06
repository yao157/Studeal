from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# Імпортуємо Base та всі моделі
from src.database.models.base import Base
from src.database.models.users import User
from src.database.models.posts import Post
from config import config

# Це об'єкт конфігурації Alembic
config_alembic = context.config

# Підставляємо URL з нашої конфігурації
config_alembic.set_main_option("sqlalchemy.url", config.db.url)

# Інтерпретуємо конфігурацію файлу та налаштовуємо логування
if config_alembic.config_file_name is not None:
    fileConfig(config_alembic.config_file_name)

# Метадані для автогенерації
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Запускає міграції в 'offline' режимі."""
    url = config_alembic.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Запускає міграції в 'online' режимі."""
    connectable = async_engine_from_config(
        config_alembic.get_section(config_alembic.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio
    asyncio.run(run_migrations_online())
