from logging.config import fileConfig
import asyncio
import os
import sys
from pathlib import Path

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Add parent directory to path to import api modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# Import our models
from api.repositories.models import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Override sqlalchemy.url from environment variable if available
database_url = os.getenv('DATABASE_URL')
print(f"🔍 DATABASE_URL from environment: {database_url}")
if database_url and database_url.strip():
    print(f"🔍 Original DATABASE_URL: {database_url[:80]}...")
    # Convert postgresql:// to postgresql+asyncpg:// for async operations
    if database_url.startswith('postgresql://'):
        database_url = database_url.replace(
            'postgresql://', 'postgresql+asyncpg://', 1
        )
    # Remove sslmode parameter (asyncpg handles SSL differently)
    # SQLAlchemy with asyncpg will use SSL by default for remote connections
    if '?sslmode=require' in database_url:
        database_url = database_url.replace('?sslmode=require', '')
    elif '&sslmode=require' in database_url:
        database_url = database_url.replace('&sslmode=require', '')
    print(f"🔍 Converted DATABASE_URL: {database_url[:80]}...")
    if not database_url or not database_url.strip():
        print("⚠️  WARNING: DATABASE_URL became empty after processing!")
    else:
        config.set_main_option('sqlalchemy.url', database_url)
elif not config.get_main_option('sqlalchemy.url'):
    # Fallback to default SQLite database
    default_db = 'sqlite+aiosqlite:///./truledgr.db'
    config.set_main_option('sqlalchemy.url', default_db)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with the given connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
