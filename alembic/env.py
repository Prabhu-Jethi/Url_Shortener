import os
import sys
from logging.config import fileConfig

from dotenv import load_dotenv
from alembic import context
from sqlalchemy import engine_from_config, pool


sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

load_dotenv()

'''
- It imports Base (which has the metadata registry) AND
- forces models.py to execute, which registers Url and Click on Base.metadata
'''
from app.db.models import Base

## alembic config object
config = context.config

# Override sqlalchemy.url from the environment variable
# This bypasses the %(DATABASE_URL)s interpolation issue in alembic.ini
config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])

''' Set python logging from alembic.init and tells which metadata to compare against'''
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migration_offline():
    """Run migrations in 'offline' mode — emits SQL without a live DB connection."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migration_online():
    """Run migrations in 'online' mode — connects to the DB and applies changes."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migration_offline()
else:
    run_migration_online()